---
name: live-cron-system
description: 라이브 자동매매 시뮬 cron 파이프라인 — 설치 상태·구조·이메일 설정
metadata: 
  node_type: memory
  type: project
  originSessionId: 0fbeebe5-9fae-4fab-8c5b-ed269017c39c
---

라이브 시뮬레이터(①)가 **cron으로 실제 가동 중**. 2026-07-09(목) 등록 완료.

- **crontab 설치됨** (`crontab -l`로 확인, 파일은 `deploy/crontab`). WSL2가 systemd=true + cron.service 상시가동이라 등록만으로 백그라운드 실행.
- **구조**: 프로젝트 = `report/live/{project}/` 폴더. `config.yaml`(순수 yaml)이 engine·screener·선정기준·가설(desc)·수신이메일. 매 토요일 `{다음주 월요일}/` 날짜 폴더 생성 → `_top5.json`·`selection.html`·`live.html`·`results.json`·`bars/{code}_5m.csv`(백테스터 포맷).
- **선정 로직 = screeners/ 레지스트리** (engines처럼 plug-in). 현재 `momentum_v1`. 폴더명이 selectors 아닌 이유: stdlib selectors 충돌 회피.
- **이메일 = 순수 코드** `pipeline/p_email.py` (smtplib+Gmail, MCP 아님 — cron/headless에서 MCP 못 씀). 발신 자격증명 `pipeline/.gmail_creds`(앱 비밀번호, gitignore). `--to`로 수신자 override 가능(데모용).
- **수신자**: config.yaml emails = kimse991228@gmail.com(본인) + limsung7969@naver.com(cofounder).
- ⚠️ **엔진 15:15 조기청산 이슈** 미해결: `engine.py:244`가 데이터 마지막 날 15:15에 강제청산 → 주중(월~목) 라이브 평가엔 그날 조기청산이 섞임. 완전한 주(금요일=마지막날)엔 정상.

관련: [[tvdatafeed-nologin]]
