#!/usr/bin/env python3
"""Read public Telegram channel previews without Telegram credentials.

The results cover a sample of the public web previews. Use official Telegram
documentation to verify API claims.
"""

import argparse
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
import json
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

CHANNELS = ("BotNews", "node_telegram_bot_api", "prominiapps", "TelegramTips")
USER_AGENT = "Mozilla/5.0 (compatible; TelegramFeatureScout/1.0; public-preview-reader)"


class TelegramPreviewParser(HTMLParser):
    """Extract a limited set of data from Telegram's HTML public preview."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.current = None
        self.message_depth = None
        self.text_depth = None
        self.posts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "div":
            self.depth += 1
            post_id = attrs.get("data-post", "")
            if self.current is None and re.fullmatch(r"[A-Za-z0-9_]+/[0-9]+", post_id):
                channel, number = post_id.split("/", 1)
                self.current = {
                    "channel": channel,
                    "id": int(number),
                    "url": f"https://t.me/{channel}/{number}",
                    "date": None,
                    "_text": [],
                }
                self.message_depth = self.depth
            classes = set(attrs.get("class", "").split())
            if self.current is not None and "tgme_widget_message_text" in classes:
                self.text_depth = self.depth

        if self.current is None:
            return
        if tag == "time" and attrs.get("datetime"):
            self.current["date"] = attrs["datetime"]
        if self.text_depth is not None and tag in ("br", "p", "li", "blockquote"):
            self.current["_text"].append("\n")

    def handle_endtag(self, tag):
        if tag != "div":
            return
        if self.current is not None and self.text_depth == self.depth:
            self.text_depth = None
        if self.current is not None and self.message_depth == self.depth:
            self._finalize()
        self.depth = max(0, self.depth - 1)

    def handle_data(self, data):
        if self.current is not None and self.text_depth is not None:
            self.current["_text"].append(data)

    def _finalize(self):
        item = self.current
        raw = "".join(item.pop("_text"))
        # Preserve paragraph breaks and normalize whitespace within each line.
        lines = [re.sub(r"\s+", " ", line).strip() for line in raw.splitlines()]
        item["text"] = "\n".join(line for line in lines if line)
        self.posts.append(item)
        self.current = None
        self.message_depth = None
        self.text_depth = None


def parse_preview(html):
    parser = TelegramPreviewParser()
    parser.feed(html)
    parser.close()
    # Keep one entry per channel+post id, even when preview HTML repeats cards.
    unique = {}
    for post in parser.posts:
        unique[(post["channel"], post["id"])] = post
    return list(unique.values())


def normalize_datetime(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def fetch_preview(channel, before=None, timeout=10):
    url = f"https://t.me/s/{channel}"
    if before is not None:
        url += "?" + urlencode({"before": before})
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    with urlopen(request, timeout=timeout) as response:
        html = response.read(8 * 1024 * 1024)
    return html.decode("utf-8", errors="replace")


def scan_channel(channel, now, days=30, pages=2, limit=25, timeout=10):
    threshold = now - timedelta(days=days)
    found = {}
    errors = []
    pages_read = 0
    window_start_reached = False
    before = None
    for _ in range(pages):
        try:
            html = fetch_preview(channel, before=before, timeout=timeout)
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            errors.append(f"Public preview request failed: {type(error).__name__}: {error}")
            break
        parsed = [post for post in parse_preview(html) if post["channel"].lower() == channel.lower()]
        pages_read += 1
        if not parsed:
            errors.append("No posts for this channel could be extracted from the public preview.")
            break
        for item in parsed:
            found[item["id"]] = item

        dates = (normalize_datetime(item["date"]) for item in parsed)
        window_start_reached = any(date is not None and date <= threshold for date in dates)
        if window_start_reached:
            break

        oldest = min(item["id"] for item in parsed)
        if before is not None and oldest >= before:
            errors.append("Preview pagination returned no older posts.")
            break
        before = oldest

    recent = []
    undated = []
    for item in found.values():
        date = normalize_datetime(item["date"])
        if date is None:
            undated.append(item["url"])
        elif threshold <= date <= now:
            recent.append({
                "date_utc": date.isoformat(),
                "url": item["url"],
                "text": item["text"][:2500],
                "truncated": len(item["text"]) > 2500,
            })

    recent.sort(key=lambda p: p["date_utc"], reverse=True)
    return {
        "channel": "@" + channel,
        "status": "checked" if found else "unavailable",
        "pages_read": pages_read,
        "window_start_reached": window_start_reached,
        "posts_seen": len(found),
        "posts_within_window": len(recent),
        "posts": recent[:limit],
        "undated_post_links": undated[:limit],
        "errors": errors,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Scan public Telegram channel previews and emit JSON.")
    parser.add_argument("--days", type=int, default=30, help="Freshness window, default: 30")
    parser.add_argument("--pages", type=int, default=2, help="Maximum preview pages per channel, default: 2")
    parser.add_argument("--limit", type=int, default=25, help="Maximum recent posts per channel, default: 25")
    parser.add_argument("--timeout", type=float, default=10.0, help="HTTP timeout in seconds")
    parser.add_argument("--channels", nargs="+", choices=CHANNELS, default=list(CHANNELS))
    args = parser.parse_args(argv)
    if not 1 <= args.days <= 365 or not 1 <= args.pages <= 5 or not 1 <= args.limit <= 100 or args.timeout <= 0:
        parser.error("Use days=1..365, pages=1..5, limit=1..100, timeout>0")

    now = datetime.now(timezone.utc)
    channels = [scan_channel(name, now, args.days, args.pages, args.limit, args.timeout) for name in args.channels]
    print(json.dumps({
        "checked_at_utc": now.isoformat(),
        "requested_window_days": args.days,
        "source_kind": "best-effort sample of public Telegram channel previews",
        "channels": channels,
        "verification_required": [
            "Confirm release facts in https://core.telegram.org/bots/api-changelog",
            "Confirm Mini Apps API in https://core.telegram.org/bots/webapps",
            "Verify client/platform and framework versions before recommending implementation",
        ],
    }, indent=2))
    return 0 if any(item["status"] == "checked" for item in channels) else 2


if __name__ == "__main__":
    sys.exit(main())
