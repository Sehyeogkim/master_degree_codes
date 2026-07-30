---
name: tvdatafeed-nologin
description: bullet281 실시간 데이터 소스 — tvDatafeed는 로그인이 깨지지만 nologin으로 충분
metadata: 
  node_type: memory
  type: project
  originSessionId: 0fbeebe5-9fae-4fab-8c5b-ed269017c39c
---

bullet281 실시간 파이프라인에서 5분봉 데이터는 **tvDatafeed**로 받는다 (yfinance보다 지연 적고 깊음).

- 심볼: `symbol="005930", exchange="KRX", interval=Interval.in_5_minute`.
- **로그인 실패(`error while signin`)의 진짜 원인**: tvDatafeed가 로그인 POST에 `User-Agent` 헤더를 안 붙여서 TradingView WAF가 봇으로 차단(`{"code":"rate_limit"}`). **비번 오류 아님** — UA만 붙이면 첫 시도에 로그인 성공(user.id 112354465 확인). 정정: 자격증명은 유효함.
- **고치는 법(3줄 몽키패치)**: `from tvDatafeed import main; main.TvDatafeed._TvDatafeed__signin_headers = {"Referer":"https://www.tradingview.com","User-Agent":"Mozilla/5.0 ... Chrome/126.0 Safari/537.36"}` 후 `TvDatafeed(u,p)`.
- 다만 **nologin으로도 5000봉(약 3개월) + 당일 실시간이 다 나와서** 이번 주 5분봉 용도엔 로그인 불필요. 정식 로그인은 실시간 스트리밍/긴 히스토리 필요 시에만. `pipeline/.tv_creds`(username\npassword)에 유효한 자격증명 있음.
- ⚠️ **장 초반 게시 지연 ~15-20분**: 개장(09:00) 직후 당일 봉이 tvDatafeed(·yfinance)에 바로 안 뜬다. 09:00 봉이 ~09:20에야 올라옴. 그래서 장 초반 5분 update는 "어제 종가까지"만 반복해 보이다가 피드가 따라잡으면 채워진다(코드 정상, 데이터 지연). live.html에 '데이터 최신봉' + 지연 15분 초과 경고를 표시해 이 간극을 가시화함.
- `.tv_creds`는 gitignore로 보호됨 (커밋 금지).
- 설치: `pip install "git+https://github.com/rongardF/tvdatafeed.git"` (PyPI에서 내려감).
- 다음 작업: `pipeline/run_live_report.py`의 `fetch5m()`를 yfinance→tvDatafeed로 교체 + 날짜/F0 하드코딩 제거 + cron 5분 주기. 관련 [[live-weekly-pipeline]].
