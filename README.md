# Telegram Feature Scout

Telegram Feature Scout is an [Agent Skill](https://agentskills.io/) for Claude Code, Codex, and other compatible agents. It researches recent Telegram Bot API and Mini App updates, checks them against official documentation, and looks at your JavaScript, TypeScript, or Python project to find changes worth adopting. The default deliverable is a short, sourced report ranked by value to your project.

## Skills

| Skill | What it does |
| --- | --- |
| [`telegram-feature-scout`](skills/telegram-feature-scout/SKILL.md) | Checks Telegram release notes and public channels, verifies client and library compatibility, and recommends up to three relevant changes. |

## Install

### Skills CLI

Run this from the project where you want to use the skill. The [Skills CLI](https://github.com/vercel-labs/skills#install-a-skill) prompts you to choose your agent. Add `-g` to install for all projects.

```bash
npx skills add soc1almemory/tg-feature-scout-skill --skill telegram-feature-scout
```

While working in a local clone of this repository, use `npx skills add . --skill telegram-feature-scout` to install the current checkout.

### Manual copy

Clone or download this repository, then copy the entire [`skills/telegram-feature-scout/`](skills/telegram-feature-scout/) directory into one of these locations. Keep `SKILL.md`, `references/`, and `scripts/` together.

| Agent | Project | Personal |
| --- | --- | --- |
| Claude Code | `.claude/skills/telegram-feature-scout/` | `~/.claude/skills/telegram-feature-scout/` |
| Codex | `.agents/skills/telegram-feature-scout/` | `~/.agents/skills/telegram-feature-scout/` |

## Usage

Open your Telegram project in the agent and ask for a feature review. You can invoke the skill explicitly or describe the task in plain language.

| Agent | Example |
| --- | --- |
| Claude Code | `/telegram-feature-scout Review my Telegram bot for useful Bot API updates from the last 30 days. Cite your sources.` |
| Codex | `$telegram-feature-scout Check my TypeScript Mini App and suggest up to three improvements supported by official Telegram docs.` |

The agent needs web or network access to check current releases. Scouting takes place during the task and project review is read-only. See [more prompts](examples/example-prompts.md) for focused compatibility checks, implementation requests, and offline reviews.

## Optional channel scanner

The Python 3 scanner reads public Telegram previews and returns JSON. It uses the standard library and requires no Telegram account or bot token. From the repository root, run:

```bash
python3 skills/telegram-feature-scout/scripts/scan_channels.py --days 30 --pages 2 --limit 25
python3 -m unittest discover -s tests -v
```

Use `python` if that is how you run Python 3 on your system. The first command fetches previews over the network. The second runs offline. See [preview coverage and fallback](skills/telegram-feature-scout/references/sources.md#preview-coverage-and-fallback) for how to interpret the JSON and verify gaps.

## Reference

- [Source directory](skills/telegram-feature-scout/references/sources.md) lists the four channels, official Telegram documentation, and framework release notes.
- [Report template](skills/telegram-feature-scout/references/report-template.md) shows how to report source coverage, compatibility, and recommendations.
- [Bot API changelog](https://core.telegram.org/bots/api-changelog) and [Mini Apps documentation](https://core.telegram.org/bots/webapps) cover Telegram platform changes.

## License

[MIT](LICENSE)
