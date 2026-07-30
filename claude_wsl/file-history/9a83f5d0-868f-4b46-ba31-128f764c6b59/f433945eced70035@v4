---
name: tradingview-perfw-formula
description: TradingView Perf.W(주간성능) 정확한 공식 — 최신종가 vs 7캘린더일전 바의 시가. 실측 검증됨.
metadata: 
  node_type: memory
  type: reference
  originSessionId: 0fbeebe5-9fae-4fab-8c5b-ed269017c39c
---

TradingView 스크리너 **Perf.W(Weekly Performance)** 정확한 공식 (실측 5종목 소수점까지 일치 검증):

```
Perf.W = (현재 종가 − 7캘린더일 전 일봉의 시가) / |그 시가| × 100
```

- **끝점 = 최신 종가**, **기준점 = 7일 전 바의 "시가"(종가 아님)** → 비대칭(close vs open 혼합).
- **7일 = 달력 7일**(거래일 7개 아님). 금요일 기준이면 지난 금요일로 떨어지고, 그날이 휴장이면 직전 거래일 봉의 시가.
- **롤링 창**이라 우리 선정 신호 chg와 기준점·창이 달라 같은 종목도 값이 다를 수 있음(버그 아님, 정의 차이).
- **우리 라이브 선정 chg 정의(2026-07-19 변경)**: `(직전 금종가 / 전전주 금종가 − 1)×100` = 주 대 주(금-금). ⚠️ 255주 부트스트랩 백테스트가 쓴 신호는 `(직전금종가/직전월시가−1)`(월→금)라서 **라이브 선정 신호가 백테스트 신호와 달라짐** — 재검증하려면 새 정의로 백테스트 재실행 필요.
- 스크리너 필드명은 `"Perf.W"` (한 번의 Query로 전 유니버스 조회 가능 → Perf.W 랭킹 선정도 1콜로 가능).
- 우리 파이프라인: 선정 chg는 그대로 두고 리포트/이메일에 Perf.W를 "참고"로 병기(`momentum_v1.resolve_perf_w`, `f_build_report`·`p_email`에 열 추가).
- 출처: tradingview.com/support/solutions/43000636536, 43000736064.

관련: [[live-cron-system]], [[portfolio-allocation-lookahead]].
