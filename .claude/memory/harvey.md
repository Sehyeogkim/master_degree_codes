---
name: harvey-server-memory
description: Consolidated memory of all Claude work by Jeff on the ETRI Harvey HPC server — user profile, cluster reference, and per-project learnings (coronary artery FEA/FSI: PyMAPDL, svFSI, FEniCSx)
metadata:
  type: reference
  compiled: 2026-07-30
  sources: /home/jeff/.claude/projects/* (per-project memory/ + session transcripts)
---

# Harvey Server — Consolidated Claude Memory

This file consolidates everything worked on with Claude across all projects on the
ETRI **Harvey** HPC server, compiled 2026-07-30 from the per-project `memory/`
directories and session transcripts under `/home/jeff/.claude/projects/`.

---

## 1. User Profile — Jeff

- Computational **biomechanics** researcher (master's degree work): **coronary artery**
  structural + fluid simulations (FEA / FSI), plaque mechanics.
- Deep experience with **ANSYS MAPDL (PyMAPDL)**, **Gmsh** meshing; also **svFSI**
  (cardiac/vascular FSI) and now migrating to **FEniCSx (DOLFINx 0.9.0)**.
- Tissue domains modeled: vessel wall, lipid core, fibrous cap, calcification.
- Works in **CGS units**, linear elasticity + hyperelastic tissue.
- Environment: Linux (CentOS/RHEL 8), **conda** envs, **SLURM** scheduler, Python.
- Email: kimse991228@gmail.com · GitHub: Sehyeogkim.

## 2. Working Preference (feedback)

- **Reply in Korean.** Jeff may ask in English (or mixed EN/KO), but responses should be
  in **Korean**. Code comments / variable names may stay English; explanations in Korean.
  *(Why: explicit, repeated request across projects 64 & 65.)*
- Prefers a run-a-few-experiments → discuss results → next-batch cadence (esp. HPC tuning:
  3 parallel experiments at a time, keep a `tried_method.txt` log).
- Wants robust batch runners that log errors, skip failed cases, and send push
  notifications on completion.

---

## 3. Harvey Cluster Reference

### Nodes / partitions

| Partition | Nodes | Cores | RAM | Notes |
|---|---|---|---|---|
| `harvey01` | harvey01 | 72 | ~251–257 GB | older CPU, lower memory BW → 30–50% slower on same mesh |
| `defaults*` | harvey02, harvey03, harvey04 | 96 | ~257 GB | |
| `harvey05` | harvey05, harvey06, harvey07 | 96 | ~376–386 GB | Granite Rapids, fastest |

- Standard `ntasks-per-node`: 96 (72 on harvey01).
- Recommended concurrent SMP tasks/node: **harvey05 = 5**, **harvey01 = 2**
  (5 is unstable on harvey01 due to memory-BW pressure).

### Common SLURM commands
- `pestat` — node status overview (look for `State=idle` + no user = available).
- `squeue -u jeff` — running/queued jobs · `scancel <jobid>` — cancel.
- Job submit workflow: `pestat` → edit `-p`/`--nodelist` in the `.sh` → `sbatch` → verify.

### Key binaries / paths
- ANSYS exec: `/opt/cvbml/softwares/ansys_inc/v251/ansys/bin/ansys251`
- svFSI binary (Trilinos ON): `/opt/cvbml/repos/svFSI/build/svFSI-build/bin/svFSI`
- svFSI source (read-only ref): `/home/jeff/repo/svFSI/Code/Source/svFSI/`
- Modules — FSILS/RCS: `module load cmake/3.25.2 gcc/11.3.0 mpi/gcc-11.3.0/openmpi-4.1.5`
  · Trilinos precond: add `trilinos/14.4.0`.

---

## 4. PyMAPDL — Coronary Plaque Structural Sims (projects 54, 60, 64)

**Goal:** run ~1000 coronary artery plaque FEA cases, two BCs each (**peak** + **low**),
output `FC_case_{id}_{peak|low}.vtk`. Main pipeline:
`/home/jeff/project/54_analysis/`, `pymapdl_simulation_ver5_fibrous_hpc.py`
(+ `_500.py` for cases 500–999).

### Parallelism: use SMP, not DMP
- **DMP (`-dis`, distributed) does NOT work** for this SURF154 / `/MAP` SFE-pressure +
  SOLID187 model on Intel CPUs — **segfaults at SOLVE** ("MAPDL internal data corrupted")
  regardless of solver (DPCG/DSPARSE), node size, or in-core vs out-of-core. It is *not*
  a memory issue and *not* a solver-choice issue — distributed mode itself corrupts the model.
- The MPI single-node networking fix (still valid if DMP is ever revisited):
  `I_MPI_FABRICS=shm` + `I_MPI_HYDRA_BOOTSTRAP=fork` (intra-node shm, spawn ranks locally,
  never ssh). This got `-dis` to *launch*, but solve still segfaults.
- **→ Stick with SMP (`-smp`, nproc=10).** SMP solves fine; DMP gives no speedup because it
  doesn't complete. SMP scales only to ~8–16 cores.

### SMP mesh-size limits (25-min cap, nproc=10)
- **< 300 MB mesh**: safe, throttle 5, 25-min cap.
- **300–500 MB**: SMP, 40-min cap, throttle 3.
- **500+ MB**: consider DMP (won't work here) or standalone run, throttle 1, 60+ min.
- **1000+ MB** (e.g. cases 947, 975, 993): 25 min insufficient — needs standalone 60–90 min;
  **do not try SMP**. Pre-classify with `du -m solid_data/case_*/solid_type_1.msh`.
- Cost scales **exponentially** (not linearly) with mesh size. Timeout cases in the
  700–999 batch were all ≥500 MB. Decision (2026-05-08): timed-out cases held, not retried.

### case161 (type-2, 4.4 M nodes / 13.1 M eqns) fails on harvey05
- **PCG never converges** (stiffness contrast E_cal≈9.1e10 / E_lipid≈6.1e5, ratio ~1.5e5)
  → ANSYS falls back to sparse direct → in-core needs ≥354 GiB > 377 GiB node → OOM-kill;
  out-of-core (`--mem=0`) → segfault in distributed OOC solver. Neither completes on this node.
- Candidate fixes (undecided): tune PCG via `PCGOPT Lev_Diff 3–5` [recommended];
  force OOC with `DSPOPTION,,OOC`; or coarsen mesh.
- Bug fixed while testing: msh path was `type2/` but every case uses `type2_mesh/`.

### MAPDL launch latency (project 64)
- `launch_mapdl` takes ~2 s on login node but **~100 s on SLURM compute nodes**
  (harvey04/06/07) — a real bottleneck for parallel case runs. Ruled out (round 1):
  MPI bootstrap, DNS, license pre-connect. Lowering `nproc` shaves a little.

### Batch monitoring workflow (sim_monitor)
- Launchers: `slrum_pymapdl_smp_array*.sh`; per-task SMP nproc=10, mem=40G, peak+low,
  12–15 min cap, cleanup trap (`pkill` on TimeLimit).
- Monitor = bash infinite loop over `squeue`+grep, emits BLOCKER/STATS/DONE, push only on DONE.
- Results: `solid_data/case_XXX/ansys_ver5_0430_smp_np10_cXXX/FC_case_XXX_{peak,low}.vtk`.
- `.out` classification greps: `Finished case:` / `Segmentation Violation` /
  `Connection refused` (ANSYS died under memory/cgroup pressure → gRPC drop) /
  `msh_path does not exist` / `Failed to read gmsh` / `FATAL` / else = timeout.
- Bug fixed: `utils_prep.wipe_out_useless_data` was deleting `.vtk` → added `.vtk` to keep list.

### Result cleanup (LAP_0728, 2026-07-28)
- `/home/jeff/project/54_analysis/ansys_LAP_0728/`: cases produce only `FC_case_{id}_low.vtk`
  (low BC; peak not always present). After cleanup: 239 case dirs = 207 with completed
  `_low.vtk` + 32 empty. 36 cases with no result (resubmittable; `sim_low_array.sh` is
  resumable — skips cases whose vtk already exists).

---

## 5. Physiological Framing — 54_analysis dataset

- `fluid_data*/case_*/steady_3d_expB_new/{peak,low}/` sims are **hyperemia** (max
  vasodilation, FFR/iFR-style), **not resting** flow. So CSVs under `post_data/wss/{peak,low}/`
  and `post_data/wall_expB_new/{peak,low}/` (pressure) are hyperemic peak/low values.
  A future "rest" batch would live under a sibling `steady_3d_*` suffix — don't conflate.

### wall_expB vs wall_expB_new (pressure quantity change)
- `wall_expB` = scalar **pressure P**; `wall_expB_new` = **traction-vector magnitude ‖T‖**.
- Spatial pattern / rank almost identical (corr 0.998+). Absolute values differ by pressure band:
  **LOW** ‖T‖ ≈ **−18%** vs P (two-branch relationship — shear contribution + reference-pressure
  offset matter more at low pressure); **PEAK** ‖T‖ ≈ P (**+0.4%**).
- Comparison plot: `post_data/compare_case0_P_vs_T.png`.

---

## 6. svFSI — Solid & Fluid FSI (project 59, and 71 mesh-independence)

Working dir e.g. `/home/jeff/project/59_solid_simulation_practice/solid_case_0/`.

### Equation / solver settings (259K nodes, 1.2M elem, 3 domains)
- `struct` = nonlinear (Newton iters even for linear material); `lElas` = dedicated linear
  elasticity, Newton converges in 1–2 iters but **does not support `Cauchy_stress`** output
  (use Displacement, VonMises_stress, Strain).
- **Best for production (1000 samples): CG + FSILS + 500 iter** with the `struct` equation
  (inexact Newton — LS doesn't fully converge but Newton does). `lElas` is faster if linear.
- GMRES + FSILS mostly converges but far slower (~10–20 s/iter). `trilinos-ic` + CG **diverges**
  on this problem.
- Preconditioners: built-in `FSILS` (Jacobi), `RCS`; Trilinos (`module load trilinos/14.4.0`):
  `trilinos-ic/ict/ml/ilu/ilut/diagonal/blockjacobi`.

### Mesh-independence study (project 71, ideal coronary lumen fluid)
- Steady outlet flow (cm³/s) converges with mesh: 0.015 (226K nodes) → 0.46122;
  0.01 (574K) → 0.46125; **0.008 (883K nodes / 4.9M elem) → 0.46130** (~0.01% vs 0.01 →
  fully mesh-converged). 0.008 solve: harvey07, job 15271, 100 steps, ~1h54m.
- Gotcha: **ASCII-VTU crashes svFSI read** — convert mesh to **binary** VTU first.
- Metric = mean-subtracted wall-pressure L2 error between successive meshes;
  results in `metrics/mesh_independent_result.md` + overlay plot.

---

## 7. FEniCSx / DOLFINx Migration (project 67)

- Migrating the coronary structural analysis from **PyMAPDL (ANSYS) → FEniCSx (DOLFINx 0.9.0)**
  because of ANSYS licensing limits; FEniCSx is open-source + scriptable.
- New sim code should use the DOLFINx API; validate against the ANSYS workflow
  (`pymapdl_simulation.py`). Prior FEniCSx work in `~/project/41_FENICS/` and
  `~/project/master_codes/FENICS/`.
- This repo's `FENICS/` holds: `fenics_LU.py`, `fenics_LU_linear.py`, `fenics_post.py`,
  `run_dolfinx.sh`.

---

## 8. This Repo — master_degree_codes

`https://github.com/Sehyeogkim/master_degree_codes` (main). Consolidated code:
- `pymapdl/` — `lumen_meshing_0723.py`, `pymapdl_simulation_ver2.py`,
  `pymapdl_simulation_ver5_fibrous.py`, `..._hpc.py`.
- `FENICS/` — DOLFINx migration scripts (see §7).
- `svFSI/` — `1D/` results, `Q_ramp/`, `svFSI_heart/` (FSI mesh + logs).
- Git identity for this repo set to `Se Hyeog Kim <kimse991228@gmail.com>`.
  HTTPS push needs a PAT or SSH key (password auth unsupported); SSH pubkey exists at
  `~/.ssh/id_rsa.pub` but is **not yet registered** on GitHub.
