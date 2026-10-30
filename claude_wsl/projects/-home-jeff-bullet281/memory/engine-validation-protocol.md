---
name: engine-validation-protocol
description: 새 엔진/규칙 검증은 부트스트랩+walk-forward 2단계 필수 — 프로토콜 문서 위치와 핵심 기준
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 214fe36d-405b-475d-b386-7fa939fbe78b
---

새 엔진·규칙·파라미터 검증 시 **반드시 2단계**: ① 부트스트랩(강건성, SEED=42·B=5000) → ② walk-forward(선택편향, expanding·시간순·축 분리). 정식 문서: `experiment_report/validation_protocol.md`, 재사용 코드: `back_test/walkforward.py`.

**Why:** 2026-07-19 실험 13~16에서 부트스트랩만 통과한 플립(개장 25분)이 WF에서 기각됨 — 인샘플 개선 +0.35%p 중 +0.40%p가 선택편향으로 정량화. 사용자가 "앞으로는 둘 다 해야 한다"고 확정.

**How to apply:** 스윕으로 후보를 고르는 실험이면 시도한 조합 수를 기록하고, WF의 후보 공간에 탐색한 축 전체를 넣는다(최종 1개만 넣으면 무의미). 무작위 분할 금지(레짐 뭉침 누수). P<95%면 채택이 아니라 "라이브 시뮬 전방 관찰" 등급.

관련: [[portfolio-allocation-lookahead]], [[live-cron-system]]
