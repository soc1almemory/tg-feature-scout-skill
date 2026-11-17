from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
from urllib.error import URLError

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "telegram-feature-scout"
    / "scripts"
    / "scan_channels.py"
)
spec = importlib.util.spec_from_file_location("scan_channels", SCRIPT)
scanner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scanner)


class PreviewTests(unittest.TestCase):
    NOW = datetime(2026, 11, 16, tzinfo=timezone.utc)
    RECENT_POST = '''
      <div class="tgme_widget_message js-widget_message" data-post="BotNews/123">
        <div class="tgme_widget_message_text js-message_text">New <b>Bot API</b>!<br>Now supports <a href="https://core.telegram.org/">widgets</a>.</div>
        <div><a class="tgme_widget_message_date"><time datetime="2026-11-09T14:30:00+00:00">14:30</time></a></div>
      </div>
    '''
    HTML = f'''
    <main>
      {RECENT_POST}
      <div class="tgme_widget_message js-widget_message" data-post="BotNews/122">
        <div class="tgme_widget_message_text">Old &amp; archived</div>
        <div><time datetime="2025-01-01T00:00:00Z">00:00</time></div>
      </div>
      <div data-post="BotNews/121"><div class="tgme_widget_message_text">Missing date</div></div>
    </main>
    '''

    def test_parser_extracts_text_date_and_post_url(self):
        posts = scanner.parse_preview(self.HTML)
        self.assertEqual(len(posts), 3)
        self.assertEqual(posts[0]["url"], "https://t.me/BotNews/123")
        self.assertIn("New Bot API!", posts[0]["text"])
        self.assertIn("Now supports widgets.", posts[0]["text"])
        self.assertEqual(posts[0]["date"], "2026-11-09T14:30:00+00:00")
        self.assertEqual(posts[1]["text"], "Old & archived")

    def test_scan_filters_old_and_undated(self):
        with patch.object(scanner, "fetch_preview", return_value=self.HTML):
            result = scanner.scan_channel("BotNews", self.NOW, days=30, pages=1)
        self.assertEqual(result["status"], "checked")
        self.assertTrue(result["window_start_reached"])
        self.assertEqual(result["posts_seen"], 3)
        self.assertEqual(result["posts_within_window"], 1)
        self.assertEqual(result["posts"][0]["url"], "https://t.me/BotNews/123")
        self.assertIn("https://t.me/BotNews/121", result["undated_post_links"])

    def test_network_error_is_transparent(self):
        with patch.object(scanner, "fetch_preview", side_effect=URLError("offline")):
            result = scanner.scan_channel("BotNews", self.NOW, pages=1)
        self.assertEqual(result["status"], "unavailable")
        self.assertFalse(result["window_start_reached"])
        self.assertTrue(result["errors"])
        self.assertEqual(result["posts"], [])

    def test_successful_response_with_no_posts_is_unavailable(self):
        with patch.object(scanner, "fetch_preview", return_value="<main>Join Telegram</main>"):
            result = scanner.scan_channel("BotNews", self.NOW)
        self.assertEqual(result["pages_read"], 1)
        self.assertEqual(result["status"], "unavailable")
        self.assertFalse(result["window_start_reached"])
        self.assertTrue(result["errors"])

    def test_page_budget_can_leave_window_partially_covered(self):
        with patch.object(scanner, "fetch_preview", return_value=self.RECENT_POST):
            result = scanner.scan_channel("BotNews", self.NOW, days=30, pages=1)
        self.assertEqual(result["status"], "checked")
        self.assertFalse(result["window_start_reached"])
        self.assertEqual(result["posts_within_window"], 1)

    def test_paginates_until_the_window_start(self):
        with patch.object(scanner, "fetch_preview", side_effect=[self.RECENT_POST, self.HTML]) as fetch:
            result = scanner.scan_channel("BotNews", self.NOW, days=30, pages=3)
        self.assertEqual(fetch.call_count, 2)
        fetch.assert_called_with("BotNews", before=123, timeout=10)
        self.assertTrue(result["window_start_reached"])
        self.assertEqual(result["posts_within_window"], 1)

    def test_scan_excludes_future_posts(self):
        future_html = self.HTML.replace("2026-11-09T14:30:00+00:00", "2026-11-16T14:30:00+00:00")
        with patch.object(scanner, "fetch_preview", return_value=future_html):
            result = scanner.scan_channel("BotNews", self.NOW)
        self.assertEqual(result["posts"], [])

    def test_rejects_invalid_post_id(self):
        posts = scanner.parse_preview('<div data-post="BotNews/script"></div>')
        self.assertEqual(posts, [])


if __name__ == "__main__":
    unittest.main()
