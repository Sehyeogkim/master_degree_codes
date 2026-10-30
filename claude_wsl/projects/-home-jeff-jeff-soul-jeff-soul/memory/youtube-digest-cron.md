---
name: youtube-digest-cron
description: Daily 8am cron that summarizes YouTube videos via Gemini and curates a digest with Claude
metadata: 
  node_type: memory
  type: project
  originSessionId: 03aa8262-e855-4211-be4e-5f778ecb37cf
---

매일 오전 8시, 등록 유튜브 채널의 최신 영상을 요약·큐레이션하는 자동화가 live (youtube_summarizer 에이전트의 실행체).

- **트리거**: Windows 작업 스케줄러 `JeffSoul-YoutubeDigest` (매일 08:00, `wsl.exe -e bash` → 스크립트). 06:00 skill / 07:00 todo 와 안 겹치게 08:00.
- **3계층 (Model B)**: ① `settings/cron/youtube_brain.py` 워커 = **Gemini가 유튜브 URL 직접 시청·요약**(영상별 .md를 `jeff_brain/youtube/`에 저장, video id로 dedup, `state/youtube/new-today.json` manifest). ② `.claude/agents/youtube_summarizer.md` = **Claude 큐레이터**(`claude --agent youtube_summarizer`로 호출, 새 노트+soul.md 읽고 다이제스트 작성 → `reports/{date}/youtube-digest.md` + telegram). ③ `settings/cron/youtube_daily.sh` 오케스트레이터. 새 영상 0이면 claude 건너뜀(토큰 절약).
- **핵심 패턴 교훈**: cron이 Claude 에이전트를 쓰는 법 = `claude -p "트리거" --agent <name> --allowedTools ... < /dev/null`. 에이전트 .md(frontmatter+프롬프트)가 두뇌, cron은 얇은 래퍼. 결정적 작업(요약)은 코드, 판단(큐레이션)은 에이전트.
- **환경**: 파이썬 = `/home/jeff/miniconda3/bin/python3` (yt-dlp + google-genai 설치됨). `.env`에 `GEMINI_API_KEY` 있음. 채널당 개수 = env `YT_LATEST`(기본 3, 테스트는 1).
- **2026-06-22 대수리(restructure 후 끊김 복구)**: ① 스크립트는 `.claude/cron/`으로 이동(youtube_daily.sh, youtube_brain.py 등). state는 그대로 `settings/cron/state/youtube`. cron 안에서 `SCRIPT_DIR`(스크립트 실제 위치) vs `CRON_DIR`(=$REPO/settings/cron, state 베이스) 분리. ② **텔레그램 토큰/CHAT_ID는 repo `.env`에 없음** — cron 래퍼가 `~/.claude/channels/telegram/.env`(봇 토큰)+`access.json`(allowFrom[0]=chat_id)에서 읽어 export. 즉 이 세션 채널 봇(@jeff_sould1_bot)과 같은 봇으로 같은 chat(8534914623=Jeff DM)에 전송. 토큰 회전/재페어링 자동 추종. ③ `youtube_brain.py:load_env()`가 repo .env만 읽던 버그 → `os.environ` 병합(override)으로 수정. ④ Windows 스케줄러 작업은 옛 경로(`settings/cron/*.sh`)를 그대로 가리킴 → 비번 없이 못 고쳐서 옛 경로에 forwarder 스크립트(`exec bash .claude/cron/...`) 생성으로 우회.
- **채널**: YC, Silicon Valley Girl, EO (`CHANNELS` dict). 공개 영상만. Gemini 영상 입력은 토큰 비용.

**Why:** Jeff가 뉴스보다 빠른 전문가 인사이트를 매일 흡수하려 함. 영상별 노트는 repo memory.
**How to apply:** 문제 시 `settings/cron/state/youtube/run.log`. 같은 cron+agent+telegram 패턴 = [[daily-skill-report-cron]], [[todo-scheduler-cron]].
