---
name: final-selection-method
description: bullet281 최종 종목선정 방법 (2026-07-19 확정) — 시총→주-주 변동율 Top20→일 거래대금 Top5
metadata: 
  node_type: memory
  type: project
  originSessionId: 0fbeebe5-9fae-4fab-8c5b-ed269017c39c
---

**bullet281 최종 종목선정 방법 — 2026-07-19 jeff 확정.** (`pipeline/screeners/momentum_v1.py`, 커밋 167ce28)

매주 토요일, 매매 시작 월요일의 **직전 주** 기준 3단계 깔때기:

1. **시총 필터** — 시가총액 ≥ 5,000억 (TradingView 스크리너, **코스피+코스닥 모두**).
2. **주간변동율 상승 Top20** — `주 대 주 변동율 = (직전 금요일 종가 / 전전주 금요일 종가 − 1) × 100`. 상승(up) 상위 20. (숏 실험은 하락 Top.)
3. **일 거래대금 Top5** — 그 20종목 중 **TradingView `Value.Traded`(최신 거래일 종가×거래량)** 상위 5종목이 최종 선정.

세부:
- **F0(엔진 돌파기준선) = 직전 금요일 종가**, tvDatafeed 기준. 주간변동율·F0 모두 tvDatafeed 단일 소스로 통일(5분봉과 일치).
- **코스닥 포함 필수**: yfinance 코스피=.KS/코스닥=.KQ → `_dl_daily` 폴백. 이전 .KS-only는 코스닥 전량 누락 버그였음 → [[kosdaq-yfinance-suffix-bug]].
- **참고 병기(선정에 미사용)**: TradingView Perf.W(주간성능) — 정의 다름(최신종가/7일전바 시가−1, 롤링) → [[tradingview-perfw-formula]].
- **유동성 필터 특성**: 일 거래대금 Top5라, 최대 상승주라도 유동성 얇은 소형 코스닥(예: 로킷 +31.9%·온코닉 +23.9%)은 걸러짐 — 체결 안정성 우선. 원하면 이 규칙만 별도 조정.
- **백테스트 divergence 주의**: 255주 부트스트랩이 쓴 신호는 (금종가/월시가) — 이 최종 정의(금-금 주대주)와 다름 → 재검증하려면 새 정의로 백테스트 재실행.
- 라이브 운영: 토 선정 → live.html 5분 갱신 → 장마감 이메일. [[live-cron-system]].

수신 이메일: jeff(kimse991228@gmail.com) + cofounder(limsung7969@naver.com).
