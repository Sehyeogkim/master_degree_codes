---
name: live-fetch-guard
description: 라이브 fetch 오염 버그(036930 0% 오보)와 단조 가드 수정 — yfinance는 KRX에서 부실
metadata: 
  node_type: memory
  type: project
  originSessionId: 5886e015-0155-4723-8ebd-f997cd714970
---

2026-07-13 주 최종보고서에서 036930(주성)이 `+0.00% · 0진입`으로 잘못 나감. 데이터 누락 아님.

**원인 (재현·확정):** 어느 update 틱에 tvDatafeed가 그 종목만 순간 공백 → `bars_5m`의
yfinance fallback이 KRX 종목에 **1봉만** 반환(yfinance는 KRX 5분봉이 사실상 무용지물) →
옛 로직 `len(yb) > len(bars)`가 "1봉 > 0봉"이라 그 1봉을 데이터로 채택 → 엔진이 1봉 위에서
0%·0진입을 확정 → `results.json`에 기록 → `p_email`이 그대로 발송. 이메일은 매 틱 덮어써지는
[[live-cron-system]] results.json을 발송시점에 그대로 읽을 뿐(자체계산 없음)이라 그 틱을 찍어감.

**수정 (커밋됨):**
- `data_source.bars_5m`: yfinance는 `MIN_WEEK_BARS(10)` 넘고 tv보다 길 때만 대체. 둘 다 미달이면 source='부실'.
- `data_source.load_bars_csv(path)`: 저장된 5분봉 CSV → [Bar] 로더 신설.
- `p_live._pick_bars(fresh, prior)` + update_one 단조 가드: 이번 fetch가 직전 틱 CSV보다 짧으면
  직전 데이터로 되돌려(reused) 엔진 재실행 → 오보 대신 마지막 정상 유지. 최종 봉수 < MIN이면 스킵.
- 회귀 테스트: `pipeline/test_fetch_guard.py` (pytest 아님, `python3`로 실행).

**Why:** 일시적/부분 fetch가 "0%짜리 가짜 행"으로 리포트·이메일까지 흘러가는 걸 차단.
**How to apply:** 라이브 fetch 관련 손볼 때 이 가드(단조성·최소봉수·부실신호) 깨지 말 것. [[tvdatafeed-nologin]]
