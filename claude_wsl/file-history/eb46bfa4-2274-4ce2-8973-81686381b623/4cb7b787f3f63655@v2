---
name: steady3d-nohyperemia-54analysis
description: 54_analysis steady-3D (non-hyperemia) peak/low on harvey; 2-node per-case pre→solve→post→wall csv
metadata: 
  node_type: memory
  type: project
  originSessionId: eb46bfa4-2274-4ce2-8973-81686381b623
  modified: 2026-07-28T02:36:30.219Z
---

54_analysis project (distinct from 65_final_0723). Big 1000-case Sobol DOE. On **harvey** cases are split `fluid_data/case_{i}` (0-499) + `fluid_data_500/case_{i}` (500-999); on **cvbml01 (ws1)** it's a single `fluid_data/case_{i}` (0-999). parameter file = `pre_data/parameter_0728.csv` (1000 rows, NO case_id col — first col DOS, index is positional row = case id).

**Rest 1D** (done 2026-07-28): ws1 `lumen_1D_0728.py` (copy of 65's lumen_1D_0723, paths retargeted; single fluid_data), `--hyperemia False --workers 20`, runner.py `prescribe_resistances=1`. Results per case `fluid_data/case_{i}/pulsatile_1d/_1d_rst.json`, then aggregated to `post_data/_1d_no_hyperemia/_1d_json_{i}.json` (1000/1000) and copied to harvey same path. Missing-tree cases regenerated via `make_tree_only.py` (VesselCADModel.CAD_instance_from_idx + tree_xyzts_generator, no mesh needed). case 438 fully rebuilt: Inventor `33_0605_final_analysis/main_CAD.py` (edit `for i in [438]`, csv→parameter_0728.csv) → new lumen.stp → ws1 re-mesh 0.015 → harvey q_ramp (job) → slab/flowhist → 1D. 438 hyperemia FFR = 0.631.

**Steady 3D non-hyperemia** (started 2026-07-28): scripts in harvey `~/project/54_analysis/`, copied from 65's steady_3D_pre_0723/post_0723 and retargeted:
- `steady_3D_pre_no_hyperemia.py <i>`: reads `post_data/_1d_no_hyperemia/_1d_json_{i}.json` [key str(i)] → peak←systolic(Q,R), low←diastolic(Q,R); builds `case_{i}/steady_3d_no_hyperemia/{peak,low}/` (inflow.flow, model.svpre from meshing/mesh-complete, solver.inp from pre_data/scripts/solver.inp), revise **Timesteps=500, DT=0.0001, Restarts=500, Resistance=R**, run svpre. Skips if 1d json or mesh-complete missing.
- `steady_3D_post_no_hyperemia.py <i>`: svpost step 500 in `96-procs_case` → rst_00500.vtp → `extract_wall_data(...,include_pressure=True)` → `post_data/wall_no_hyperemia/{peak,low}/wall_{ph}_case_{i}.csv`.
- `steady_nohyp_node.sh`: per-node loop over [START,END]; per case **pre → svsolver peak (-np 96) → svsolver low → post → next**; resumable (skip if both wall csv exist); cleans stale 96-procs_case before each solve.
- Submitted 2 nodes: `sbatch -p defaults --nodelist=harvey04 --export=ALL,START=0,END=499` and `--nodelist=harvey07 START=500 END=999`. NP=96 must match post's 96-procs_case.

Imports resolve via `sys.path.insert("/home/jeff/repo/master_python/src")` (utils.utils_lumen.paths/runner/extract_wall_csv). harvey python `/home/jeff/miniconda3/bin/python3` has numpy+vtk. svSolver bins `/opt/cvbml/repos/svSolverPrivate/build/svSolver-build/bin/{svpre,svsolver,svpost}`. ws1↔harvey no direct route — relay files via local WSL. See [[steady-3d-pipeline]] (65's version).
