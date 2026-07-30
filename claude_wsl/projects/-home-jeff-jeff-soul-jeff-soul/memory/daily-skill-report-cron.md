---
name: daily-skill-report-cron
description: "Daily 6am cron that reports new Claude Code skills/plugins relevant to Jeff's work"
metadata: 
  node_type: memory
  type: project
  originSessionId: 03aa8262-e855-4211-be4e-5f778ecb37cf
---

매일 오전 6시, Claude Code 플러그인/스킬 마켓 변화를 감지해 연구자 AI-platform 작업에 도움될 스킬을 골라 리포트하는 자동화가 live.

- **트리거**: Windows 작업 스케줄러 task `JeffSoul-DailySkillReport` (매일 06:00, `wsl.exe -e bash` → 스크립트). WSL cron이 아니라 Windows 스케줄러를 쓴 이유 = WSL은 터미널 다 닫으면 꺼져서 cron도 죽음. 대안(B) WSL cron은 README에 문서화만.
- **코드**: `settings/cron/daily_skill_check.sh`(오케스트레이터) + `catalog_diff.py`(스냅샷 diff, stdlib). 출력 리포트는 `projects/reports/{날짜}/skill-report.md`.
- **감지 소스**: `~/.claude/plugins/plugin-catalog-cache.json` vs `state/catalog-snapshot.json` 어제 스냅샷.
- **텔레그램**: `.env`의 `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID` 확인됨(전송 http 200). curl 직접 전송.
- **Phase 2 TODO**: Notion 페이지 생성(위치 미정 + headless MCP 미검증으로 보류), HTML 워크플로우 시각화.

- **2026-06-22 경로/크리덴셜 통일**: 스크립트는 `.claude/cron/`로 이동(state는 `settings/cron/state` 유지). cron이 `SCRIPT_DIR`로 sibling `.py`(catalog_diff.py) 호출. 텔레그램 토큰/CHAT_ID는 repo `.env`가 아니라 `~/.claude/channels/telegram/`(채널 플러그인 봇)에서 읽음. Windows 작업 `JeffSoul-DailySkillReport`는 옛 경로 가리켜서 `settings/cron/daily_skill_check.sh` forwarder로 우회. 같은 패턴 [[youtube-digest-cron]].

**Why:** Jeff가 직접 요청한 일일 자동화. soul.md 현재 작업(연구자 AI agent platform)과의 관련성으로 스킬 선별.
**How to apply:** cron 동작 안 하면 `settings/cron/state/run.log` 먼저 확인. [[telegram-tokens-working]]
