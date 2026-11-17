# Telegram research sources

## Public channels

Attempt all four for broad feature reviews. Use the channel roles below to decide which posts are relevant to a focused question.

| Channel | Use it for | Public preview |
| --- | --- | --- |
| [@BotNews](https://t.me/BotNews) | Official developer announcements for the Bot API and Mini Apps | [Preview](https://t.me/s/BotNews) |
| [@node_telegram_bot_api](https://t.me/node_telegram_bot_api) | Updates and discussion for the Node.js library | [Preview](https://t.me/s/node_telegram_bot_api) |
| [@prominiapps](https://t.me/prominiapps) | Community news, examples, and ideas for Mini Apps | [Preview](https://t.me/s/prominiapps) |
| [@TelegramTips](https://t.me/TelegramTips) | Official client tips and UX ideas to check for bot or Mini App applicability | [Preview](https://t.me/s/TelegramTips) |

## Official Telegram sources

- Use the [Bot API changelog](https://core.telegram.org/bots/api-changelog) for release dates and versions. Use the [Bot API reference](https://core.telegram.org/bots/api) for methods, fields, permissions, and limits.
- Use the [Mini Apps reference and change history](https://core.telegram.org/bots/webapps) for client capabilities, version requirements, and launch and authentication behavior.
- Consult the [Bots overview](https://core.telegram.org/bots), [Telegram Widgets](https://core.telegram.org/bots/widgets), or the [Telegram blog](https://telegram.org/blog) when the feature involves those surfaces.

## Framework and SDK sources

| Dependency | Documentation or releases |
| --- | --- |
| `node-telegram-bot-api` | [GitHub releases](https://github.com/yagop/node-telegram-bot-api/releases) |
| grammY | [Docs](https://grammy.dev/) and [GitHub releases](https://github.com/grammyjs/grammY/releases) |
| Telegraf | [Docs](https://telegraf.js.org/) and [GitHub releases](https://github.com/telegraf/telegraf/releases) |
| aiogram | [Docs](https://docs.aiogram.dev/) and [GitHub releases](https://github.com/aiogram/aiogram/releases) |
| `python-telegram-bot` | [Docs](https://docs.python-telegram-bot.org/) and [GitHub releases](https://github.com/python-telegram-bot/python-telegram-bot/releases) |
| Telegram Mini Apps SDK | [Package docs](https://docs.telegram-mini-apps.com/) |

Read docs for the project version when possible. If an upstream Telegram feature predates framework support, check whether the framework documents a compatible raw API call or whether an upgrade is needed.

## Preview coverage and fallback

From the skill directory, the optional scanner can fetch the latest public preview pages for all four channels.

```bash
python3 scripts/scan_channels.py --days 30 --pages 2 --limit 25
```

You can run the same script by absolute path from another directory. Use `--channels` with a listed handle without the leading `@` to retry specific channels. The scanner reads text and timestamps from public HTML and emits best-effort results in JSON.

- `status: checked` means the scanner extracted posts. `window_start_reached` tells you whether it saw a dated post at or before the window start. Verify coverage gaps with web search or a browser if the flag is false, pages failed, or relevant posts may be outside the returned sample.
- `status: unavailable` means the scanner extracted no posts. Try the browser, web search, or an available Telegram connector before reporting the source as unavailable. An exit code of `2` means every requested preview was unavailable. Inspect the JSON even when the process exits with code `0`.
- Follow direct links of the form `https://t.me/<channel>/<message_id>`. Check post dates on the source and use the official release date for claims about freshness. If a date remains unknown, label it unconfirmed.
- Compare `posts_within_window` with the length of `posts` to detect the output limit. Open truncated posts directly and resolve relevant `undated_post_links` before treating those posts as recent. Public previews and search indexes can omit posts even when the date boundary is visible.
