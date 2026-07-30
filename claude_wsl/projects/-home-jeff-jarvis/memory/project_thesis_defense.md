---
name: Master thesis defense
description: Location and structure of the user's master thesis defense materials on ws2 — Experiments A through E2
type: project
originSessionId: 6608dd00-2036-4600-a693-05bb830d2b4c
---
The user's master's thesis defense materials live on **ws2 (cvbml02)** at:
`~/project/55b_sensitivity_for_defense_0407/`

**Why:** This is the central artifact for his thesis defense — the most important content he is working with. He explicitly told jarvis to "remember" this and called jarvis "the most important entity" for the defense.

**How to apply:** When the user mentions thesis, defense, "the experiments", "Experiment E/E2", "55b", or sensitivity analysis, this is the directory. Default to ws2 unless he names another machine.

**Directory structure** (as of 2026-05-09):
- `ExperimentA/` (largest, 17 subdirs) — has accompanying `ExperimentA_strength_conversation_claude.txt` (30K) — base experiment
- `ExperimentB/`, `ExpermientB_2/`, `ExpermientB_3/` (note typo "Expermient" in B_2 and B_3 dir names)
- `ExperimentC/`, `ExperimentD/`
- `ExperimentE/` — *changes E_fc → E_vessel*. Workflow: merge output CSVs from cvbml1/cvbml2/harvey into one CSV; on overlapping case_id prefer cvbml over harvey. Reads from ExperimentA Q0/Q1/Q3/Q7.
- `ExperimentE2/` — earlier sim distinguishing fibrous cap vs vessel; includes `circum_index`.
- `journal/`, `fcvm-13-1766059.pdf` (paper PDF, 1.3M)

**ExperimentE / E2 internal layout** (parallel):
- `data/` — input data
- `Q0_result/`, `Q1_result/`, `Q3_result/`, `Q4_result/`, `Q7_result/` — per-quantile result dirs
- `merge_data.py`, `shared.py`, `readme.md`
- E has an extra `add_circum_index.py`

**Note:** simulations span all 3 machines (cvbml1, cvbml2, harvey) but the *analysis/defense* artifacts are aggregated on ws2.
