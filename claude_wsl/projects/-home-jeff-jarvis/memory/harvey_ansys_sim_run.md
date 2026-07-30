---
name: harvey-ansys-sim-run
description: "How to run ANSYS/PyMAPDL fibrous-cap sims on harvey (env, license, switches, sbatch template)"
metadata: 
  node_type: memory
  type: project
  originSessionId: e54223a6-ed49-45f6-846e-8800eb64c2fa
---

Running ANSYS sims on harvey for cases cvbml01/02 don't have (harvey-meshed ranges: 161–499 = ws1 replacement, 506–999 = ws2 replacement). Driver script: `~/project/54_analysis/pymapdl_simulation_ver5_fibrous_hpc.py` — args `start end nproc`, iterates `range(start,end)`, so one case = `CASE CASE+1 nproc`.

**Per-case inputs required** (else skipped/fails): mesh `solid_data/case_{i}/type2_mesh/solid_type_2_quad.msh` + wall CSVs `post_data/wall_0430/{peak,low}/wall_{bc}_case_{i}_pressure.csv`. Skips if both `ansys_CP_0610/FC_case_{i}_{peak,low}.vtk` already exist.

**Critical runtime config (got these wrong first, fixed by matching `bin2/slrum_h06_948_989.sh`):**
- conda env **`base`** — NOT `mesh` (mesh env lacks pymapdl/reader/meshio/pyvista). Meshing batches use `mesh`; sims use `base`.
- `export ANSYSLMD_LICENSE_FILE=1055@143.248.174.50` — NOT set globally, MUST export or MAPDL launch fails. See [[ansys_license]].
- `export MAPDL_SWITCHES="-smp"` (shared-mem, single node) — default would be `-mpi intelmpi`.
- `export RUNNING_ON_HPC=0` (NOT 1).
- Also: `module purge`, `KMP_AFFINITY=disabled`, `OMP_PROC_BIND=false`, `OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK`, `MAPDL_PORT=$((50100 + CASE%1000))`, cleanup trap to pkill stray ansys procs on exit.

**Template:** `~/project/54_analysis/sim_one.sh` (one case per node). Submit one per node:
`sbatch -J sim161 --nodelist=harvey03 --export=ALL,CASE=161 sim_one.sh`. Nodes harvey03/04 are in partition `harvey02` (also `defaults`); 96 cpu / 257G each. goal.md: nproc=30 OK. Logs in `batch_logs_sim_0610/`.

2026-06-10 test: cases 161 (harvey03) + 162 (harvey04) ran 2-up, validated end-to-end. See [[simulations]].

**Live full batch (started 2026-06-10 ~12:00 KST):** `sim_array.sh` job array over `sim_caselist.txt` (638 cases w/ msh, not done), `--array=0-637%4`, partition `defaults`, `--exclude=harvey02,03,04,05` (leaves harvey06+07), `--cpus-per-task=40` forces exactly **2 cases/node** (cluster packs by CPU not mem; 3×40>96). nproc=30. Each task reads its case from caselist line `SLURM_ARRAY_TASK_ID+1`. Cleanup trap pkills only its own MAPDL by port (spares co-tenant). Array JobID stored in `.sim_array_jobid`. ETA ~2.7 days. Monitor: session cron `*/30 * * * *` (job 11620c18) refreshes Notion page `37b2a46dc68c80c9b2bfd122d3391dbf` ("ansys simulation monitor") — completed/running/failed/pending, auto-resubmits if array vanishes. Failed cases (e.g. corrupt msh like case 167) get bin auto-wiped + listed on the page. The except-block bin cleanup was already in the .py (Jeff added it).

**Sweep finished 2026-06-12 19:14 KST (~31h):** 551/638 completed (peak+low VTKs in `ansys_CP_0610/`), 87 failed = 86 retriable + case 167 (corrupt msh). The 86 retriable were **MAPDL mid-solve drops** (gRPC "connection refused" — one of two co-tenant solves OOM-killed under 2-per-node memory contention; ~16% rate), plus case **975** which timed out (90GB model, peak solve alone took 5.15h > fit poorly in 8h --time). **Cleanup-pass lesson:** re-run the 86 retriable at **1 sim/node** (or higher --mem) to avoid OOM contention; give 975 its own node + longer --time. The 86 retriable case ids are listed on the Notion page. Monitor cron (11620c18) deleted at completion.

**Retry sweep + recovery finished 2026-06-19 05:14 KST.** The ~82 failures were split 41 harvey (job 14896, harvey06+07, `--exclusive` 1-per-node) / 41 cvbml01 (single-process nproc 20). Outcome: harvey 27/41 (still 14 gRPC drops even at 1-per-node + exclusive → cause is **concurrency/license contention, not node memory**); cvbml01 single-process = **0 failures** (the control). Lesson confirmed: **cvbml01 single-process is the reliable fallback.** Auto-recovery relayed the 14 harvey-failures' meshes harvey→local→cvbml01 (`/tmp/relay_recovery.sh`, rsync+size-verify; harvey can't SSH cvbml01 directly) into `solid_data_cal/case_C/type2_mesh/`, re-ran single-process via `pymapdl_simulation_ver5_fibrous.py` → recovery output in `ansys_results_type2_CP_0618/` → **14/14 recovered, 0 failures.** Final solved = **76/82.** NOT solved: 974+975 (monsters ~90GB, meshes removed, intentionally skipped); 979/986/991/996 (cvbml01 disk-full casualties during main run — case 974 wrote 192GB sparse scratch → disk 100% → MPI I/O error; freed by removing case_974 dir; per Jeff's resilience rule NOT auto-restarted). Monitor cron (f653bd21) deleted at completion. Notion report page `3832a46dc68c80c4a6ecd1dda582110f`.
