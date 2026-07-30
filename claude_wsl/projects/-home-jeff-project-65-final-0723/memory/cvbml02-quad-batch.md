---
name: cvbml02-quad-batch
description: "cvbml02 batch Type2 quad meshing of all geo_0723 cases (run_type2_0723.py, size 0.06, msh-only)"
metadata: 
  node_type: memory
  type: project
  originSessionId: ee471b4a-e3b0-41ee-80bd-85771435f221
  modified: 2026-07-27T11:55:02.807Z
---

Batch Type-2 SOLID meshing of all 384 geo_0723 cases on **cvbml02**, started 2026-07-23.

- Runner: `65_final_0723/run_type2_0723.py <case> <nproc> [SOL=1] [SAVE_VTU=0] [MESH_SIZE=0.06]`. Resumable (skips if target .msh exists), HXT→Delaunay fallback, cleans intermediate cal files (keeps only final .msh). Params from parameter.csv, geometry from geo_0723, output to `solid_0723/case_<i>/type2_mesh/solid_type_2_quad.msh`.
- User settings: **quad (SOL=1, second_order_linear=True), mesh_size=0.06 (coarse — ~1.4-2.4M tets vs 3.6M @0.05), nproc=20, .msh ONLY (no .vtu), all 384 cases.**
- Driver: `run_batch_mesh.sh` — `seq 0 383 | xargs -P 3` (3-wide = 60 cores ≤ 64). Per-case logs `mesh_logs/case_N.log`, status log `mesh_batch_progress.log`. ~4 min/case.
- **CRITICAL: every case must be wrapped in `timeout -k 20 1800`.** gmsh 3D boundary recovery ("Recovering boundary" / "Recovering N missing facet(s)") can hang FOREVER, single-threaded, on bad geometry. On 2026-07-23 cases 13/43/48 hung 12-17h each and, with xargs -P 3, stalled the ENTIRE batch at 38/384 (load avg 3 on a 64-core box = the tell). Timed-out cases are killed, logged TIMEOUT, and their scratch removed. Sanity check when monitoring: if `%CPU`≈100 (not ~2000) and no new .msh for >30 min, it's hung.
- **RESULT 2026-07-24: 287/384 succeeded (74.7%), 97 failed.** Productive run was 10:23-13:00 (2h37m) at `-P 8`. Quality across 246 logged meshes: n_tet 0.96-3.5M (mean 1.69M), mean_q 0.855, **neg Jacobian 0 everywhere**; but min_q worst 0.0002 — 22 meshes have min_q<0.01, 32 more in 0.01-0.05 (check before ANSYS).
- Failure classification (`failure_class.txt`, list in `missing_cases.txt`, both in project root):
  - PLC_ERROR 28, STEP_FAILED 22, OCC_UNKNOWN_ENTITY 5, HXT3D_FAILED 2 → **geometry-side defects, retrying same settings will not help**.
  - HANG_BOUNDARY_RECOVERY 21 → gmsh stuck in "Recovering boundary"; needs a different 3D algorithm, not a longer timeout.
  - **TIMEOUT_OTHER 17 → NOT hung.** Killed mid Netgen-optimize / `setOrder(2)` (e.g. case 194 finished optimizing at 254s, was in "Meshing order 2" at 400s). These recover by simply raising TMO to ~900s. Cases: 58 69 72 137 172 194 205 215 260 261 286 326 355 364 366 368 378.
- Peak RSS per worker ~2-4.9GB (measured via /proc VmHWM); memory is NOT the constraint on a 503GB box. gmsh is mostly single-threaded outside HXT 3D, so nproc=20 x 8 workers only draws load ~9/64.
- **RETRY CAMPAIGN 2026-07-24 (final ~302/384):** Runner gained a 6th arg `algo_order` ("hxt"=(10,1) default, "delaunay"=(1,10)); backup `run_type2_0723.py.bak_prealgo`. Retry drivers: `run_retry_delaunay.sh`/`run_retry_hxt.sh`/`run_retry_big.sh` (logs in `mesh_logs_delaunay|hxt|big/`).
  - **Delaunay-first was the WRONG fix** — recovered only 5/97, and made TIMEOUT_OTHER worse (Delaunay is slower than HXT, so 13 that just needed more time hit the 900s wall). Lesson: for TIMEOUT_OTHER keep HXT, only raise TMO.
  - **TIMEOUT_OTHER cases are just BIG, not hung** — n_tet 5-7M (vs 1.7M median) at the same size 0.06 because fine calcification features force refinement; need 470-2100s. Recovered 10 of 17 with HXT + TMO 1500/2500. Their quality is poor (min_q down to 0.0008) — FLAG before ANSYS.
  - **Still unrecovered giants: 261** (Netgen optimize still churning >2500s), **286 & 364** (2D surface repair DIVERGING: "N invalid in surface 1" 62→100→338 — effectively hung). Not worth more compute; need geometry fix or larger mesh_size.
  - **IO gotcha:** 8 workers writing 200-600MB .msh at once can stall a write for 1000s+ (case 72 meshed fine at 247s but its write hung to 2500s, leaving a truncated 1.2MB file). `find -size +0` counts truncated files as done — use `-size +1M` AND check for the `$EndElements` trailer to count TRUE successes.
  - PLC_ERROR/STEP_FAILED/OCC/HXT3D (57 cases) confirmed geometry-side — Delaunay recovered ~1; these need CAD repair, not mesher tuning.
- parameter.csv has 384 rows (case_id 0-383), matches geo_0723. See [[solid-mesh-two-types]] [[solid-mesh-env-cv1]].
- NOTE distinct from the cvbml01 dist-meshing batch [[batch-dist-meshing-0723]].

- **geo_0727 remesh 2026-07-27:** user regenerated 18 previously-failed geometries (`geo_0727/case_*`, 5 stp each: solid/fc/lipid/lumen/fc_offset). Copied 16 to cvbml02 geo_0723 (skipped 168,381 — already valid). Ran 5-wide (ANSYS sim `pymapdl_simulation_ver5_fibrous.py 0 384 30` was ALSO running on the box, ~125GB/load~30 — that's why load looked high, not our job). **Result: only 1/16 succeeded (case 240).** 15 still fail at the SAME stage: 9 STEP4_FAILED, 3 TIMEOUT(big/hang), 2 PLC, 1 OCC.
- **KEY: "STEP4 Failed" is NOT a STEP-file import error** — it's pipeline boolean stage 4 = inserting the calcification subdomain into lipid/fc (STEP1=lipid+fc, STEP3=fc+solid, STEP4=cal insertion). Regenerating vessel/fc/lipid geometry did NOT fix it because the defect is how the CALCIFICATION surface intersects fc/lipid. These need cal-generation/cal-geometry fixes, not mesher tuning. Grep `STEP4 Failed` to spot them.
- **DOUBLE-LAUNCH HAZARD:** a rejected Bash tool call whose command was `ssh ws2 'nohup ... &'` can STILL have started the remote nohup driver before the rejection registered. Always `pgrep -f <driver>` and kill leftovers BEFORE relaunching. Also: `pgrep -c -f "<name>"` counts the counting shell itself if your command string contains `<name>` unbracketed — use the `[n]ame` bracket trick or it false-reports +1 driver.

- **geo_0727 remesh REDONE 2026-07-27 evening (SUPERSEDES the "1/16" note above):** the earlier 1/16 result was a false negative from TWO bugs, not from geometry regen failing. (1) That run fired at **15:48** on cvbml02's geo_0723 = the **15:32** geometry, but cvbml01 kept tuning geo_0727 until **17:04–18:19** — so it meshed STALE geometry. (2) It ran with only `envs/ansys_new/bin` on PATH, so every case died at `stl_to_step` with **`freecadcmd not found`** (freecadcmd lives in BASE conda: `/home/jeff/miniconda3/bin/freecadcmd`, FreeCAD 1.0.0). **FIX for both:** rsync cvbml01's newest `geo_0727/case_*` → cvbml02 `geo_0723/case_*` (relay via local WSL — cvbml02 has no key to cvbml01; back up old to `geo_0723_bak_pre0727/`), delete stale `type2_mesh/solid_type_2_quad.msh` to force re-mesh, and launch with **`export PATH=/home/jeff/miniconda3/bin:$PATH`** so freecadcmd resolves.
- **RESULT with newest geometry + PATH fix: 12/16 succeeded** (10,27,114,151,215,240,250,287,305,343,376,380), all at rung1 size 0.06 HXT, **neg=0**, mean_q~0.86 (305 is huge: 8.7M tets). Driver `type2_geo0727_remesh.py` (4-wide×nproc8, size ladder 0.06→0.05→0.07, cap 30min). **cvbml02 Type2 quad total now 313/384.**
- **4 residuals are genuine geometry-side, NOT mesher-fixable** (all failed across HXT+Delaunay and all 3 sizes): **63** `CA is NOT fully inside the lipid` (calcification pokes outside lipid core); **231** `create_cal_mesh` IndexError — boolean Difference made an EMPTY volume (`BOPAlgo unused faces`); **127** PLC segment/facet at 3D boundary recovery; **65** STEP5 failed. 63 & 231 need the CALCIFICATION geometry regenerated (cal-vs-lipid params), consistent with the STEP4/cal-insertion lesson above.
