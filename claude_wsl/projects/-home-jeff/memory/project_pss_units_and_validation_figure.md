---
name: project-pss-units-and-validation-figure
description: PSS simulation output is in dyne/cm² (÷10000 → kPa); location of the 4-panel validation figure and its data
metadata: 
  node_type: memory
  type: project
  originSessionId: 18eb45ee-76a9-48f7-8822-e509a93a04f5
---

The plaque structural stress (PSS / ΔPSS) raw output from the simulations is in **dyne/cm²**, NOT Pa. To convert to kPa for plotting/reporting, **divide by 10,000** (÷10 for dyne/cm²→Pa since 10 dyne/cm² = 1 Pa, then ÷1000 for Pa→kPa). With this, the LAP dataset gives PSS median ≈ 101 kPa (range 43–247) and ΔPSS median ≈ 62 kPa (28–158), matching the literature (Milzi/Kadry/Zhao/Guo) — see [[project-output-dir]].

**Validation figure** (`Chapter 4.0` literature-consistency check) on ws2 cvbml02:
`/home/jeff/project/55c_final_defense_0512/Figure_final/figure_result0_validation/`
- `make_panels.py` builds 4 separate panels into `panels/` (A: PSS/ΔPSS hist; B: DOS–FFR sim median+IQR vs 4 refs; C: circumferential; D: axial). Run with `/home/jeff/miniconda3/bin/python` (system python3 lacks pandas).
- Data: `output_PSS_del_PSS.csv` (PSS/delta_PSS, dyne/cm²), `input.csv` (DOS, row-aligned with `FFR.csv` case_id), `FFR_reference/ref1-4.csv` (Kristensen/Dai/Nijjer/Lee curves). Rupture C/D data from `54_analysis/.../PSS_result_type1_expB_new_NoSuffix_tag5_with_circum.csv`.

Verified reference bibs + quantitative comparison written to Notion "new 4.0" page (3842a46dc68c806f934dd23689123d21). Note: "Hartman 2021" was a misattribution → actually Milzi et al. 2021 eLife; "Zhao D" → Zhao C.
