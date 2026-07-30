---
name: todo-scheduler-cron
description: 매일 7am 구글 캘린더 → 오늘+7일 일정 브리핑 → 텔레그램. whatshouldIdo 스킬 + Windows 스케줄러.
metadata: 
  node_type: memory
  type: project
  originSessionId: fa5a04f8-0e33-4982-8683-b399d4c66033
---

매일 오전 7시 구글 캘린더 기반 일정 브리핑 cron. 6am 스킬 리포트([[daily-skill-report-cron]])와 같은 패턴.

- 스킬: `.claude/skills/whatshouldIdo/SKILL.md` — 캘린더 읽고 "오늘 할 일 + 다가오는 7일" 한국어 브리핑. MCP(`mcp__claude_ai_Google_Calendar__*`) 우선, 비대화형 cron이면 ICS fallback.
- 에이전트 정의: `.claude/agents/todo_scheduler.md`
- cron: `settings/cron/todo_scheduler_cron.sh` (ics_to_events.py로 calendar-events.json 생성 → claude -p → 텔레그램 curl)
- ICS fallback: `settings/cron/ics_to_events.py` (stdlib only, RRULE 전개 포함). `.env`의 `GCAL_ICS_URL`(구글 캘린더 iCal 비공개 주소) 필요.
- 스케줄러: Windows 작업 `JeffSoul-TodoScheduler` 매일 07:00.

- **2026-06-22 상태**: 스크립트 `.claude/cron/`로 이동(state는 `settings/cron/state`). cron이 `SCRIPT_DIR`로 ics_to_events.py 호출, 텔레그램 크리덴셜은 `~/.claude/channels/telegram/`에서 읽음(같은 패턴 [[youtube-digest-cron]]). ⚠️ **Windows 작업 `JeffSoul-TodoScheduler`(7am)가 현재 스케줄러에 없음** — restructure 중 사라진 듯. 재등록 필요(Jeff 확인 대기). 등록 시 옛 경로 forwarder도 같이.

**Why:** agent .md는 정의일 뿐 스스로 안 돈다 — 7시 자동 실행은 스케줄러가 트리거. claude.ai 캘린더 MCP은 대화형 인증이라 헤드리스 cron에서 못 뜰 수 있어 ICS를 fallback으로 둠.
