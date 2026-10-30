---
name: 0519-claude-analysis-layout
description: "ws2 0519_claude_analysis/ folder convention — top level for active 0521 work, bin/ for archived stale artifacts"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9e4f74e9-ce86-4ab0-892e-082c5de2b3ae
---

`ws2:/home/jeff/project/54_analysis/0519_claude_analysis/` 의 정리 컨벤션 (확인 2026-05-21):

- **top level**: 현재 활성 0521 work만 둔다.
  - `post_processing_final_version_0521.py` — ANSYS VTU→CSV post-processing (PSS/ΔPSS + axial/circum 분류)
  - `plot_axial_rupture_0521.py` — output_0521/ CSV → axial rupture distribution PNG
  - `plan_0521.md` — 사용자 노트
- **`bin/`**: 아카이브. 더 이상 안 쓰는 5/19~5/20 산물.
  - 구 plot 스크립트들 (`plot_axial_rupture_all.py`, `plot_axial_rupture_distribution.py`) — z_trials/ 하드코딩, 안 씀
  - 구 PNG 결과들
  - 실행 로그 (`output_0521_run.log`, `output_0521_run_wk2.log`)
  - 구 멀티 설정 서브폴더 (`PSS_delPSS_multi/`)
- **`output_0521/`**: 결과물 — CSV (combined + per-machine parts) + PNG plot.

**Why:** 유저가 활성/비활성을 명확히 분리하고 싶어함. 새 작업을 top level에 두고 stale 한 것은 bin/으로 옮긴다.

**How to apply:** 이 폴더에서 새 산출물 만들 때 top level에 두고, 더 이상 안 쓰는 스크립트·로그·중간 PNG는 `bin/`으로 mv. 새 plot/post-processing 스크립트는 `*_0521.py` 같은 datestamp 패턴을 따른다. CSV 출력은 `output_0521/` 안에. 다른 머신에서 만든 결과를 합칠 때는 `_wk1.csv`/`_wk2.csv` suffix로 part 파일 보존하고 unsuffixed canonical 파일로 concat.
