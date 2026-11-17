# Example prompts

Use these prompts to try the skill against a project or to review its behavior after a change.

| Scenario | Prompt | Look for |
| --- | --- | --- |
| Python bot feature review | “Review my aiogram bot for Telegram updates from the last 30 days that would help users. Include source links and estimate the changes involved.” | Concrete links, a date range, coverage of all four channels, and compatibility tied to the project's aiogram version. |
| TypeScript Mini App review | “Use Telegram Feature Scout on my React and TypeScript Mini App. Suggest up to three ideas supported by official docs. Keep the review read-only.” | Recommendations specific to existing flows and relevant client requirements. |
| Planning without a repository | “I'm planning a Telegram bot in Node.js. Check @BotNews, @node_telegram_bot_api, @prominiapps, @TelegramTips, and the Bot API changelog before suggesting features.” | Explicit project assumptions and a status for each requested source. |
| Focused capability check | “Can my Mini App use Telegram's fullscreen API on my supported clients? Check the official requirements and show the fallback.” | A direct answer with version evidence and a fallback suited to the supported clients. |
| Authorized implementation | “Add a fullscreen toggle to this Mini App. Verify availability and handle older clients.” | A relevant evidence check followed by implementation and tests within the request. |
| Offline review | “Network access is disabled. Review my project for Telegram feature opportunities.” | Source coverage clearly marked unavailable, with freshness claims labeled unverified. |
