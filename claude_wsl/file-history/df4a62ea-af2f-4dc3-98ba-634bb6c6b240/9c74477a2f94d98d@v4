---
name: steady-3d-pipeline
description: "How to run the steady_3d fluid simulation (peak+low) on harvey for all cases — pre, 4-node dispatcher, post to wall csv"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4c5c939f-6472-457a-bbdc-757c03d64685
  modified: 2026-07-25T12:42:39.705Z
---

Steady-3D fluid sim on harvey for `65_final_0723`, **peak (systolic) + low (diastolic)** per case. Started 2026-07-25 after [[harvey-qramp-pipeline]] finished. Goal: `post_data/wall_0723/{peak,low}/wall_{ph}_case_{i}.csv` (7 cols: x,y,z,Tx,Ty,Tz,Pressure) per case per phase — the only downstream deliverable (user: "all I need is wall_pressure.csv").

**Input:** `post_data/1d_rst/_1d_rst_{i}.json` (384 files, case 0–383, keyed by "{i}") with `systolic`/`diastolic`/`mean` → each has `Q, Pin, Pout, R`. pre uses **Q** (inflow) + **R** (outlet resistance) only; **peak←systolic, low←diastolic, mean skipped**. R already present → no conversion.

**Three stages (all scripts in project root):**
1. **PRE** `steady_3D_pre_0723.py::process_case(i)` — builds `fluid_0723/case_{i}/steady_3d/{peak,low}/` (inflow.flow, model.svpre, solver.inp) then runs **svpre** (login node, no LD_LIBRARY_PATH needed, no modules). Overrides inp to 500 timesteps, dt 1e-4, Resistance=R. Its `Pool(5)` in `__main__` throws `daemonic processes are not allowed to have children` → **run per-case top-level instead**: `PYTHONPATH=<proj> python3 -c "import steady_3D_pre_0723 as m; m.process_case(i)"`. Driver `steady_pre_range.sh START END NPAR` does this xargs-parallel, skipping cases whose peak+low geombc.dat.1 exist.
2. **SOLVER** `steady_solve_one.sh` (generic, params via `--export=ALL,PROJ=<dir>,CASE=<i>,PHASE=<peak|low>`; node/name/-o on sbatch cmdline). `mpirun -np 96 svsolver solver.inp` in `steady_3d/{ph}/` → `96-procs_case/restart.500.1`. **Do NOT rely on SLURM_SUBMIT_DIR** (it = ssh login dir /home/jeff, not proj); pass PROJ explicitly. Runtime ~8 min/case @ 96c.
3. **POST** `steady_3D_post_0723.py::process_case(i)` — svpost (step 500) → rst_00500.vtp → `extract_wall_data` → wall csv. Needs `LD_LIBRARY_PATH+=/opt/cvbml/libraries/VTK-8.2.0/lib64` and `PYTHONPATH=<proj>`; uses master_python utils (pyvista) via `sys.path.insert(0,"/home/jeff/repo/master_python/src")`. ~20s svpost + pyvista extract per phase.

**Orchestration (daemons, launched with setsid nohup … & disown):**
- `steady_dispatch.sh` — nodes **harvey04-07**, up to 4 of our jobs = **2 cases** (peak+low interleaved). Ascending 5–383. Per node: skip if another user's job there (`squeue -w <node> -o %u` ≠ jeff); submit next `(case,phase)` that is pre-done (geombc) & not solved (no restart.500.1 / no csv). Job name `sd_c{i}_{ph}`. Stops when every pair solved. Log `steady_dispatch.log`.
- `steady_post_daemon.sh` — login node, `NPAR=3`. Posts a case only when **both** phases have restart.500.1 (avoids redundant peak re-svpost) and a csv is missing. Stops when all 758 csv present. Log `steady_post.log`.

**restart freq = 500 (final dump only):** edited template `pre_data/scripts/solver.inp` line `Number of Timesteps between Restarts: 20 → 500` (backup `.bak_20260725`). Post only needs step 500; matches q_ramp storage decision. Case-5 practice used 20 (26 dumps, 2.5GB); 500 shrinks it a lot. Disk: 21T fs, 3.7T free at start — monitor.

**cases 0–4 already done** (coarse g015, [[case-0-4-mesh-mismatch-ignored]]); **case 5 = verified practice** (peak→harvey06 low→harvey07, wall csv 7col 71113 rows, peak==low). New batch = **5–383**. Node/partition: `defaults` = harvey02–07; other user `yjchoi` (MDLMFIX4_96) often on harvey02-03. Report per [[reporting-format-mesh]]; Notion per [[notion-harvey-qramp-monitor]] (overwrite).

**COMPLETED 2026-07-25 21:35 KST** (runtime ~14.7 h from 06:54). All **758/758 wall csv** present (379 cases × peak+low), integrity 379/379 clean (7 cols, 0 NaN, peak rows==low rows, 0 mismatches). Physical check (5/10/20/28): 3D wall P brackets 1D Pin→Pout, peak≫low. case 150 (re-meshed) OK. ~2× faster past case 165 (lighter meshes). Disk stayed 3.6 T free. Completion email sent to user; Notion marked DONE. Both daemons exited cleanly (dispatch + post logged ALL DONE).
