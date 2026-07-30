---
name: postproc-cp-0618
description: Post-processing of fibrous-cap sims → PSS/del-PSS merged CSV delivered to cvbml02 (done 2026-06-19)
metadata: 
  node_type: memory
  type: project
  originSessionId: 06e26fcb-e18a-46a8-8bff-e563b044f4f7
---

Post-processing of the CP_0618 fibrous-cap sims (the 756 solved cases from [[harvey-ansys-sim-run]]) — **done 2026-06-19**.

**Script:** `~/project/54_analysis/post_processing_CP_0618.py` on BOTH cvbml01 + harvey (adapted from `0519_claude_analysis/post_processing_final_version_0521.py`). CLI: `post_processing_CP_0618.py <solid_dir> <ansys_subdir> <start> <end> <out_csv> [nproc]`. Run from `~/project/54_analysis` (conda `base`). No MAPDL/license needed — pure pyvista+numpy read.
- **del_PSS = RAW (peak − low)** per Jeff (NOT /2); the (peak−low)/2 amplitude is kept ONLY for the SWT term.
- tag-5 lumen-FC interface mask = boolean `point_data["WALL_IN_FC"]` (our vtks have no "Group" field).
- 0.01 cm sphere-average, top-5% nodes, cKDTree — same method as base. Reads legacy `.vtk`. Param CSV `pre_data/input_0605.csv` (covers 0-999). Location/circum/SWT are best-effort (PSS/del_PSS always emitted if tag-5 nodes exist). `utils.utils_geo_mesh` is pip-installed on cvbml01 (`~/repo/master_python/src/`), local dir on harvey.

**3 parts (disjoint case-ids, verified no overlap):**
- A: cvbml01 `solid_data/ansys_results_type2_CP_0605_quad` ids 0-159 → 127 rows
- B: cvbml01 `solid_data_cal/ansys_results_type2_CP_0618` ids 166-961 → 49 rows (the recovery 14 + main 35)
- C: harvey `solid_data/ansys_CP_0610` ids 161-999 → 580 rows (first-sweep + harvey-retry)

**Merge (local):** pandas concat → dedup by case_id (0 dups) → sort → `PSS_all_CP_0618.csv` = **756 unique cases, 26 cols**, case_id 0-999. Sanity: 0 null PSS/del, all del_PSS<PSS, PSS_Principal 3.2e5-4.4e6.

**Delivered to:** `cvbml02:~/project/55c_final_defense_0512/Figure_final/data_CP_new_0618/PSS_all_CP_0618.csv` (size-verified match). Pushed from local — harvey/cvbml01 can't reach cvbml02 directly.
