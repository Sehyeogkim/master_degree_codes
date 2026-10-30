---
name: 65-final-0723-workflow
description: "65_final_0723 lumen pipeline runs on the cvbml/harvey servers, not locally"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7fd6c708-4335-46a3-9255-369f4530546e
  modified: 2026-07-23T03:28:27.502Z
---

All 65_final_0723 work (lumen meshing → 1D → etc.) runs **on the servers** (cvbml01/cv1 primarily, also cv2 and harvey) — not on the local machine. See [[server-abbreviations]].

**Why:** the toolchain lives only on the servers — Simmetrix `mesh_generator` binary + floating license under `/opt/cvbml/repos/SyntheticTreeGenerator`, the `master_python` package (egg-link'd into the `ansys_new` conda env), and gmsh/meshio/vtk. Local machine has none of it.

**Key facts:**
- Working dir on cv1: `/home/jeff/project/65_final_0723/`
- Run with: `/home/jeff/miniconda3/envs/ansys_new/bin/python <script>.py` (has gmsh 4.14 / meshio 5.3.5 / vtk 9.5 + `lumen_codes`, `utils.utils_lumen`)
- Proven reference pipeline: `cv1:/home/jeff/project/54_analysis/lumen_Simmetrix_meshing.py` (fluid meshing + tree/xyzts) and `lumen_1D.py` (later 1D stage).
- Fluid meshing path: `lumen.stp` --gmsh+meshio--> `lumen.vtk` --vtk--> `lumen.vtp` --Simmetrix--> `mesh-complete/`. The mesher needs a triangulated `.vtp`, NOT raw CAD `.stp`.
- `tree.dat`/`xyzts.dat` are rebuilt from morphology params via `VesselCADModel.CAD_instance_from_idx(case_id, parameter_csv)` — so a `parameter.csv` (row order == case index) is required for those, though meshing alone only needs `lumen.stp`.
- Config: `pre_data/solver_path.json` holds simmetrix meshing+license, svSolver, and pul_1d solver paths.

The runner `lumen_meshing_0723.py` (case_0..4 of geo_0723 → fluid_0723/) is set up on cv1 as of 2026-07-23. grid_size 0.015 gave ~1.2M tetra/case (~6M total for 5); 0.01 gives ~2.4x.

**Q-ramp 3D stage runs on harvey (SLURM), not cv1.** As of 2026-07-23, case_0..4 slab/FlowHist all generated & validated.
- Mesh transfer cv1→harvey is via **local relay** (cv1 cannot SSH harvey directly — key not trusted). `cv1→local→harvey`.
- harvey working dir: `/home/jeff/project/65_final_0723/`. Q-ramp needs only ONE pre_data file: `pre_data/scripts/solver_ramp.inp` (copied into q_ramp_dir, then revised); model.svpre/inflow.flow are generated.
- Adapted runner: `Q_ramp_0723.py` (from user's `Q_ramp.py`; picks case via env `QRAMP_CASE`). Two fixes vs original: (1) copy `xyzts.dat` into the q_ramp run dir — **required** or svsolver won't write slab.txt; (2) `Path(__file__).resolve().parent` so svpre gets absolute mesh paths.
- svpre/svsolver binaries: `/home/wj0220/svSolverPrivate/build/svSolver-build/bin/` (world-exec). SLURM: partition `defaults` (harvey02-07, 96 cores each). Job needs `module load cmake/3.25.2 gcc/11.3.0 mpi/gcc-11.3.0/openmpi-4.1.5` + LD_LIBRARY_PATH to svSolver + VTK-8.2.0.
- Parallel run: `run_q_ramp_array.sh` (`#SBATCH --array=1-4`, one 96-core job per case per node). ~3.5 min/case. Outputs `post_data/{slab/slab_i.txt, flowhist/FlowHist_i.dat}`.
- slab.txt shape check: rows = n_timesteps/slab_store = 500/5 = 100; cols = num_tree_points = 50.
- Full pipeline order: meshing(cv1) → Q-ramp 3D(harvey, slab/FlowHist) → regression+ROM → tree_abc.dat → 1D ROM(cv1) → 3D steady → wall traction.

**1D ROM stage runs on cv1** via `bin/lumen_1D_0723.py` — a SINGLE unified argparse script (rest + hyperemia in one; the old separate `lumen_1D_0723_FFR.py` was deleted). Needs slab/FlowHist in `post_data/` (relayed from harvey via local). Binaries: pul_solver `/home/jeff/repo/SyntheticTreeGenerator/build/apps/PulsatileTreeSolver/pulsatile_tree_solver`, converter `/opt/cvbml/repos/.../PointDataConverter/point_data_converter`.
- Usage: `python bin/lumen_1D_0723.py [--hyperemia True|False] [--cases 0 1 2] [--workers 5]` (defaults: rest, cases 0-4, 5 workers).
- Output per case: rest → `fluid_0723/case_i/pulsatile_1d/_1d_rst.json`; hyperemia → `fluid_0723/case_i/pulsatile_1d_hyperemia/_1d_rst.json`. JSON = {systolic/diastolic/mean {Q,Pin,Pout,R}} (pressures dynes/cm²), plus **`FFR`** key when hyperemia. JSON is wrapped as `{"<case>": {...}}`.
- FFR = mean(P_distal)/mean(P_proximal); P_distal at z = lesion_length/2 + 3 cm. Computed only under hyperemia. case_0 FFR = 0.60 (DOS 0.66, < 0.80 ischemic threshold — sensible).
- **BUG fixed**: `post_processing_FFR()` does NOT accept a `hyperimia` kwarg — passing it makes all cases fail after post_processing_1d (json has systolic/diastolic/mean but no FFR). The unified script calls it without that kwarg.
- 1D solver (`RigidTreeSolver`) converges well: 10 sub-iters/timestep to ~1e-7, 5 cardiac cycles, limit-cycle reached.

**Coronary BC references (for paper), set in `lumen_codes/pulsatile_1d.py` create_bc_types (as of 2026-07-23):**
- Q_mean = 0.495 cc/s (29.7 ml/min LAD) — Johnson et al. 2007.
- R_total = P_mean/Q_mean (P_mean = 93 mmHg); split Ra:Ra_micro:Rv = 0.32:0.52:0.16.
- **Compliance C_total = 0.36** (written with E-5 ⇒ 3.6e-6, the PER-OUTLET value) — ratio **Ca:Cim = 0.11:0.89** (SimVascular). Ref: https://simvascular.github.io/clinical/coronary.html. SimVascular LCA total capacitance 3.6e-5 is the AGGREGATE over all LCA outlets; our single-vessel (1-outlet) model uses 3.6e-5/~10 ≈ 3.6e-6 ⇒ C_total=0.36.
- **DECISIVE FINDING (2026-07-23): compliance magnitude flips systolic/diastolic dominance.** C_total=0.36 (per-outlet) ⇒ diastolic-dominant flow, dia/sys phase-mean ≈ 2.0-2.2× (matches real LAD physiology, correct). C_total=3.6 (aggregate on single outlet) ⇒ systolic-dominant (unphysiological). **Use 0.36.** (An earlier "compliance doesn't matter" conclusion was invalid — the 0.36 edit had gone to a different output dir `pulsatile_1d/` while comparison read stale `pulsatile_1d_B_new/`.)
- NOTE: systolic/diastolic in post_processing_1d are sampled at argmax/argmin(P_in) (aortic pressure extremes), NOT the flow-waveform phases — so the point-sampled Qsys/Qdia can mislead; use phase-averaged flow rate to judge dominance. Output dir is now `pulsatile_1d/` (user renamed from `pulsatile_1d_B_new`).
- **hyperemia** = arg `hyperimia` of create_bc_types (default False = rest, the MAIN case). True ⇒ R_total/=3.5 (adenosine), needed only for FFR. Two runs required: rest (main) + hyperemia (FFR).
- rest run of case_0-4 done 2026-07-23; ΔP(Pin−Pout) tracks DOS as expected; Pin_sys matches input SBP.

**Scripts & layout on cv1 (as of 2026-07-23, all under `65_final_0723/bin/`):**
- `bin/lumen_meshing_0723.py` — Simmetrix meshing (geo_0723 → fluid_0723).
- `bin/lumen_1D_0723.py` — unified 1D ROM (rest/hyperemia via `--hyperemia`).
- `bin/collect_1d_json.py` — collects per-case `_1d_rst.json` into one dir as `_1d_rst_<i>.json`. Usage: `python bin/collect_1d_json.py [--hyperemia True] [--cases ...] [--out ...]`; default out = `post_data/1d_rst/` (rest) or `post_data/1d_rst_hyperemia/`.
- `bin/*.log` — run logs. Scripts anchor paths to project ROOT via `Path(__file__).resolve().parent.parent` (so they work from `bin/`).

**Steady 3D fluid stage runs on harvey — 3 sub-stages: svpre (python) → svsolver (SLURM) → svpost+extract (python).** Purpose: wall traction at two instants (peak=systolic, low=diastolic; **av intentionally dropped**) → input to the solid/elastic sim. Uses the 1D result `post_data/1d_rst/_1d_rst_{i}.json`: Q→inflow.flow, R→outlet Resistance BC (peak from systolic, low from diastolic). svSolver bins: `/opt/cvbml/repos/svSolverPrivate/build/svSolver-build/bin/` (svpre/svsolver/svpost; run bare on login node, RPATH baked). nproc=96 (⇒ `96-procs_case/`), num_timesteps=500, dt=1e-4, restart interval 20.
- Scripts (harvey `65_final_0723/`): `steady_3D_pre_0723.py` (peak/low svpre), `_3D_steady_peak.sh`→harvey05 / `_3D_steady_low.sh`→harvey06 (svsolver loop over cases 0-4, `mpirun -np 96`), `steady_3D_post_0723.py` (svpost `-sn 500 -vtp rst -indir 96-procs_case` then wall extract). Run pre/post with `/home/jeff/miniconda3/bin/python3` (has master_python + pyvista).
- **GOTCHAS**: (1) `Steady_3d` helper methods hardcode peak/low/av AND use `multiprocessing.Process` → conflicts with an outer `Pool` (daemonic "not allowed to have children"). Our scripts BYPASS the helpers and call utils directly (`utils_paths.create_flow_file/create_svpre_file/revise_inp_file`, `runner.run_svpre/run_svpost`) with subprocess — no daemonic issue, peak/low only. (2) Use `Path(__file__).resolve().parent` (absolute) so svpre/svpost get absolute mesh paths. (3) svpost is a SEPARATE step after svsolver (NOT inside the SLURM job, NOT inside pre). (4) `extract_wall_data_pressure` no longer exists in master_python — use `extract_wall_data` (computes **Total_traction = pressure*normal + in-plane traction**, cols x,y,z,Tx,Ty,Tz; excludes ModelFaceID 2,3 caps). Added a backward-compatible `include_pressure=False` param to it (our post passes True → extra `Pressure` col). Backup: `extract_wall_csv.py.bak_0723`.
- Output: `post_data/wall_0723/{peak,low}/wall_{name}_case_{i}.csv` (cols x,y,z,Tx,Ty,Tz,Pressure). Sanity: case_0/peak Pressure≈208635 dyn/cm²=156 mmHg = case_0 systolic Pin ✓.

**Solid FEA stage runs on cv1** (pyMAPDL + ANSYS MAPDL v251 at `/opt/cvbml/softwares/ansys_inc/v251/ansys/bin/ansys251`; license server `1055@143.248.174.50`; env = `ansys_new` which has pymapdl 0.70.2 + master_python egg-link). Script: `pymapdl_simulation_ver5_fibrous.py` (`PYMAPDL_worker`) — reads a solid `.msh` (gmsh, quadratic tet) → cdb → for peak/low: /MAP-interpolate wall Pressure onto SURF154 → linear-static solve (multi-material vessel/lipid/fc[/cal]) → extract fibrous-cap (FC, mat_id=3) stress → `FC_case_{i}_{bc}.vtk` (EQV, **Principal_stress S1**, EQV_strain).
- Wall load = PRESSURE only (scalar normal). ANSYS `/MAP` READ maps ONE value column; can't do a 3-vector traction (would need equivalent nodal forces). For arterial wall pressure dominates (shear ~1000× smaller) so pressure-only is standard.
- **Wall CSV integration (edited into the script):** wall_0723 CSV is `x,y,z,Tx,Ty,Tz,Pressure` so Pressure is **col 7** — `/MAP read(...,1,2,3,7)`; wall_dir=`post_data/wall_0723`, filename `wall_{bc}_case_{i}.csv`. parameter.csv (E_vessel/lipid/fc/cal), `pre_data/material.json` (mat_id/rho/ν; E overridden by csv; vessel1/lipid2/fc3/cal8).
- **UNITS gotcha:** solid `.msh` is in **mm** (z ~ -20..80); code does `mesh.points *= 0.1` → cm (z -2..8) to match wall CSV (cm). The `.vtu` sibling is ALREADY ×0.1 (cm) — check the `.msh` not the `.vtu`. Keep the ×0.1.
- **Solid mesh tags:** volume physical 1=vessel,2=lipid,3=fc (this box mesh has NO cal); surface 4=wall_in_vessel,5=wall_in_fc,6=sides,7=unused. Script uses tags 4/5/6.
- Runner used: `run_solid_case0.py` (`--mesh <.msh> --ansys-dir <dir> --nproc 32`). Calls `utils_prep.wipe_out_useless_data(ansys_dir)` at end → keeps only .vtk/.msh/.vtu/.csv/.json/_0.err, removes rst/cdb/db/esav. So set ansys-dir to a DEDICATED subdir (e.g. `case_0/ansys_results_dist_0723/`). cv1 has 128 cores / 503G RAM (plenty for ~13M DOF).
- **box vs dist mesh (case_0):** dist (distance-to-fc-field refinement) = **43% fewer elements** (1.69M vs 2.98M vol tets) at equal quality (avg~0.79, 0 neg-Jac) and ~2× faster solve, with FC S1 within 2% (peak 2.07 vs 2.03 MPa; low 1.31 vs 1.34 MPa). **→ use dist.** Meshes: `solid_0723/case_<i>/{box_run,dist_run}/solid_type_1_{box,dist}.msh` + `.vtu`.

**Progress state (2026-07-23):** case_0 FULL pipeline validated end-to-end (mesh → Q-ramp → 1D rest C_total=0.36 → steady 3D peak/low wall pressure → solid FEA FC stress). 5 fluid cases done through steady-3D wall CSVs; 1D hyperemia only case_0 (FFR=0.60).

**BIG PLAN (user going to do this next, will return): scale to ALL ~384 cases.** Sobol input in `Sobol_sampling/input_sobol_0000-0127.csv` (+0128-0255, +0256-0383) = 384 cases total. Full per-case chain: solid mesh gen (dist) + fluid mesh → Q-ramp(harvey) → 1D → steady-3D → peak/low wall pressure CSV → solid FEA (FC S1). All stage scripts are already case-parameterized; scaling is orchestration/repetition, not new logic. The hard part (validating each stage) is DONE for case_0.
