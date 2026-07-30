---
name: solid-mesh-two-types
description: "The \"2 meshes\" for project 65_final_0723 = Type 1 (no calcification) and Type 2 (calcification)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9f7a5359-4da2-4098-a81a-7674efa09d6e
  modified: 2026-07-23T05:15:36.504Z
---

For 65_final_0723, "총 2개의 메쉬" refers to two SOLID mesh types (not fluid):

- **Type 1** — no calcification, lipid core only. Script `HXT_meshing_I.py` (`gmshing_solid`), gmsh OCC boolean on `{lumen,solid,lipid,fc}.stp`, output `solid_type_1.msh`. Reads `pre_data/parameter.csv` for `lesion_length` — but actual file is at `pre_data/bin/parameter.csv` (path mismatch to fix if running Type 1 as-is).
- **Type 2** — calcification inside lipid core. `HXT_meshing_II_main.py` (+ `HXT_meshing_II_cal_generation.py`) driving `HXT_type2_utils.HXT_mesh_II`. Generates cal from (lipid − fc_offset), Voronoi/KDTree, smooth→stl→step, then `solid_gmshing_production`. Type 2 is the production path.

**geo_0723 runners (65_final_0723, verified working on cvbml02 2026-07-23):**
- Type 1: `run_solid_0723.py <case> <nproc> <mesh_size>` → `solid_0723/case_<i>/solid_type_1.msh` (+.vtu). Reuses `HXT_meshing_I.gmshing_solid` unchanged; lesion_length from `54_analysis/pre_data/bin/parameter.csv`.
- Type 2: `run_type2_0723.py <case> <nproc> [SOL]` → `solid_0723/case_<i>/type2_mesh/solid_type_2_quad{,_curved}.msh` (+.vtu). Leaves `HXT_type2_utils.py` UNCHANGED; monkeypatches `CAD_instance_from_idx` to read params from `65_final_0723/pre_data/parameter.csv` (same schema as input_0605.csv — CAD reads PI/alpha/lipid_length_ratio/fc_av_th/d_fc_ca/fraction/ca_axial+shoulder_skewness/ca_strength_ratio/DOS/lesion_length/lumen_axial_skewness), and redirects geometry→geo_0723/case_i, output→solid_0723.
  - Both types produce **quadratic (order 2, tetra10)** meshes. `solid_gmshing` sets `ElementOrder=1` only to build+optimize a linear base, then `setOrder(2)` raises to 10-node — final mesh is 2nd order, NOT linear.
  - `SOL` arg (default 1): 1 = straight-edge quadratic (`SecondOrderLinear=True`, production default, robust); 0 = curved quadratic (`SecondOrderLinear=False` + `high_order_optimize=2`, mid-side nodes follow CAD surfaces — geometrically most accurate but lower worst-element quality). case_0 verified on cvbml02: straight → min_q 0.12, neg 0, ~411s; curved → min_q 0.052, neg 0, ~549s (HOO=2 kept all elements valid). Curved needs HOO>=2 or mid-side nodes invert on the fibrous cap.
- **freecadcmd gotcha:** Type 2's `stl_to_step` calls bare `freecadcmd`. It lives in `ansys_new/bin` but is NOT found when launching via the python ABSOLUTE path without env activation. Launch with `PATH=/home/jeff/miniconda3/envs/ansys_new/bin:$PATH` (or `conda activate ansys_new`).

Env + run recipe: [[solid-mesh-env-cv1]].
