---
name: portfolio-allocation-lookahead
description: bullet281 배분 로직(portfolio_281)은 사후 look-ahead이며 라이브에선 호출 안 됨 — 실시간 실행정책 미정
metadata: 
  node_type: memory
  type: project
  originSessionId: 0fbeebe5-9fae-4fab-8c5b-ed269017c39c
---

bullet281 281전략의 **포트폴리오 배분(`engines/engine281/strategy281.py:portfolio_281`)은 사후(주말) 계산이라 look-ahead가 박혀 있고, 코드 어디서도 호출되지 않는다.**

- 배분식: `gap ≥ 3%` 종목만 편입(없으면 최고갭 1종목 fallback) → 비중 ∝ **gap⁴** → deploy=k/max(k,1)=100% 무레버. gap = 방향×(진입가/F0−1), 진입가=신고점 돌파 5분봉 종가.
- **look-ahead 문제(jeff가 정확히 지적)**: gap⁴ 가중은 5종목 gap을 동시에 알아야 계산됨. 근데 진입 시점이 제각각(월~목, 혹은 미발생)이라 실시간엔 나머지 gap을 모른다 → `portfolio_281`은 주 종료 후 전 gap 확정 시점에 도는 **사후 측정**. +2.81%/주 백테스트 숫자도 이 사후 가중 기준.
- **라이브 현황**: `grep` 결과 `portfolio_281`은 정의만 있고 **호출 0**. `p_live.py`/`p_backtest.py`는 배분을 안 하고 **종목별 개별 weekly_return만** 리포트에 표시 → 라이브는 배분 문제를 "시뮬 안 함"으로 회피 중.
- **실시간 충실 버전 옵션(정하면 백테스트와 다른 전략이 됨)**: (A)예약+리밸런싱, (B)순차 gap⁴×남은현금(순서의존), (C)스냅샷 컷오프, (D)3%게이트+균등(초집중 상실). 아직 **미결정** — 라이브의 핵심 설계 결정.
- **실험 완료(2026-07-10, `back_test/`)**: causal 배분 부트스트랩(255주, SEED42/B5000, 원자=주). 신호=직전주 주간변동율(매매주 전 확정, causal). F0·직전주변동율은 데이터에 없어 yfinance 일봉으로 조달(CREON 5분봉 시가와 일치). 결과 — **causal 규칙 +0.59~+0.73%/주(최고 square², 균등과 거의 무차이), lookahead gap⁴ = +2.33%.** 즉 **옛 "+2.81"의 정체 = look-ahead**(실행불가). 실시간 실행가능 엣지는 **~+0.7%/주**, 강집중(quartic⁴·softmax)은 오히려 손해(직전주 모멘텀=이번주 약한 예측자). 리포트 `report/backtest_allocation_bootstrap.html`, 커밋 cc8d604.
- 원엔진(`engines/engine281/`)은 불변. `run_281`/`run`은 이미 causal(봉순서). look-ahead는 배분 한 곳뿐이었고 대체 완료.
- 관련: [[live-cron-system]]. 다음: walk-forward로 과적합 검증(부트스트랩은 같은 255주 재조합이라 과적합 못 고침).
