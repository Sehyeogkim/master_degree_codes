---
name: kosdaq-yfinance-suffix-bug
description: yfinance는 코스피=.KS/코스닥=.KQ (다름) — .KS-only는 코스닥 전량 누락. momentum_v1 선정 버그였고 수정됨.
metadata: 
  node_type: memory
  type: reference
  originSessionId: 0fbeebe5-9fae-4fab-8c5b-ed269017c39c
---

**yfinance 한국 종목 접미사: 코스피 = `.KS`, 코스닥 = `.KQ` (서로 다름).** `.KS`로 코스닥 코드를 받으면 **0봉 반환**(에러 아님, 빈 데이터).

- **버그(2026-07-19 발견·수정, jeff가 로킷·온코닉 누락으로 포착):** `momentum_v1.select_stocks`가 유니버스 전 종목에 `.KS`만 붙여 다운로드 → 코스닥은 빈 데이터 → 루프 `try/except pass`가 **조용히 드롭**. 결과: 코스닥 전량(유니버스의 ~20%, **일봉 391 vs 485개**)이 랭킹에서 통째로 사라짐. 선정이 코스피만 보고 있었음.
- **증상:** 코스닥 상승주가 Top20에서 실종 — 로킷헬스케어(376900) 주-주 +31.9%(실제 1위), 온코닉테라퓨틱스(476060) +23.9%가 안 뽑힘.
- **수정:** `momentum_v1._dl_daily(codes, start, end)` — `.KS` 벌크 다운로드 → **데이터 없는 종목만 `.KQ` 벌크 폴백** → code→DataFrame 딕셔너리 반환. `_prior_days`도 df를 직접 받도록 변경.
- **거래소 구분 불가:** TradingView 스크리너 `exchange` 필드는 코스닥도 `'KRX'`로 반환(`type`/`subtype`/`listed_exchange`도 구분 못 함) → 접미사를 사전에 못 정함 → **.KS 실패 시 .KQ 폴백**이 유일하게 견고한 방법.
- **tvDatafeed는 무관:** `exchange="KRX"`로 코스피·코스닥 둘 다 커버 → F0/5분봉(`data_source`)은 원래 정상. 버그는 **yfinance 유니버스 랭킹에만** 있었음.

관련: [[live-cron-system]], [[tvdatafeed-nologin]].
