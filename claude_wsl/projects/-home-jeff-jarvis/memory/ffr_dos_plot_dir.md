---
name: ffr_dos_plot_dir
description: Where the FFR vs DOS (degree of stenosis) plot with clinical reference curves is generated
metadata: 
  node_type: memory
  type: project
  originSessionId: 36036111-6367-4a72-be56-53b5c23db506
---

The FFR-vs-DOS plot (simulation scatter + 4 clinical-study reference curves: Kristensen, Dai, Nijjer, Lee) is generated on **ws2 (cvbml02)** at:

`/home/jeff/project/55c_final_defense_0512/Experiment_LAP/Q0_result/`

- `plot_DOS_vs_FFR_with_refs.py` — the plotting script
- `DOS_vs_FFR.png` — output figure
- `ref1_data.csv`–`ref4_data.csv` — the 4 clinical reference datasets
- `reference.md` — notes on the reference studies
- `Q0_analysis.py` — broader Q0 analysis (Pearson correlations, input/output distributions)

Part of the master thesis defense work — see [[project_thesis_defense]].
Note: grepping `/home/jeff/project` recursively is slow and hits binary .vtu false-positives; restrict with `--include="*.py"` etc.
