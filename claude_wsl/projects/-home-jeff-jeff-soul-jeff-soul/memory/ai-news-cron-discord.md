---
name: ai-news-cron-discord
description: AI-news cron now posts to Discord (was dead Telegram); Discord bot send needs a User-Agent header
metadata: 
  node_type: memory
  type: project
  originSessionId: 62f21681-6096-43ce-b57e-27cf1bce7ba8
---

`.claude/cron/ai_news_cron.sh` (jeff_soul) was rerouted from Telegram → **Discord** on 2026-06-22. It had been a silent no-op: the script sourced only `$REPO/.env`, which has no `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID`.

Now it loads the Discord bot token from `~/.claude/channels/discord/.env` and POSTs to `https://discord.com/api/v10/channels/<id>/messages` with 2000-char chunking. Channel id hardcoded (overridable via `DISCORD_CHANNEL_ID`).

**Gotcha worth remembering:** sending to the Discord API from a script with Python `urllib` gets **HTTP 403** unless you set a `User-Agent` header (Cloudflare blocks the default `Python-urllib` UA). `curl`'s default UA works. The cron's Python sender sets `User-Agent: DiscordBot (...)`.

The other 3 crons (skill-report, todo, github-trending) still use the same dead-Telegram pattern — Jeff declined migrating them. Related: [[paperflow-mvp]].
