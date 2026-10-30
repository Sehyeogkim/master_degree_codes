---
name: gmail-send-tool
description: Claude Code가 실제 메일을 보내는 도구 — Gmail SMTP + 앱 비밀번호 (.claude/tools/send_email.py)
metadata: 
  node_type: memory
  type: project
  originSessionId: ddda541b-31f0-43a5-998e-01659a16b4c0
---

claude.ai Gmail MCP은 초안(draft)만 만들고 **발송은 못 한다**. 실제 발송이 필요하면 `.claude/tools/send_email.py` 를 쓴다(2026-06-22 Jeff 요청으로 추가).

- **방식**: Gmail SMTP_SSL(smtp.gmail.com:465) + 앱 비밀번호. 유료 API 불필요. 개인 Gmail 하루 500통 한도.
- **크리덴셜**: repo `.env` 의 `GMAIL_ADDRESS`(kimse991228@gmail.com) + `GMAIL_APP_PASSWORD`(16자리 앱 비번, 공백 제거). `.env` 는 gitignore. 토큰 회전: myaccount.google.com/apppasswords 에서 재발급 후 .env 교체.
- **전제**: 구글 계정 2FA 켜져 있어야 앱 비번 발급 가능.
- **사용**: `python3 .claude/tools/send_email.py --to a@b.com --subject "제목" --body "본문"` (본문 생략 시 stdin). 옵션 --cc/--bcc/--html/--reply-to/--from-name. load_env()는 .env+os.environ 병합(환경변수 우선) — cron에서도 export로 주입 가능.
- **검증됨**: 2026-06-22 본인 계정으로 테스트 발송 → INBOX 도착 확인.

**Why:** Jeff가 "초안 말고 실제 발송"을 원함. SMTP 앱 비번이 무료·최단 경로(Resend 등 외부 API는 커스텀 도메인/대량발송용이라 오버킬).
**How to apply:** 메일 보내달라 하면 이 스크립트. 같은 .env 크리덴셜 패턴 = cron들([[youtube-digest-cron]]).
