---
name: User's simulation workload
description: What jeff actually runs on harvey/ws1/ws2 — software, scripts, patterns
type: project
originSessionId: 09397dbb-5629-47d6-b63a-015b28e41479
---
User runs **ANSYS / PyMAPDL** simulations across all 3 servers.

**On harvey (Slurm HPC):**
- Job submission script: `slrum_pymapdl_smp_array.sh` (note: typo "slrum" not "slurm" — kept as-is, this is the actual filename)
- Submits as Slurm **job array** (e.g. job 11161 has tasks 1–499 with `%5` concurrency limit)
- Default partition: `defaults`, mostly lands on node `harvey05`
- Output files: `slurm_smp_<jobid>_<idx>.out` style (or `slrum_smp_*` due to script typo)

**On ws1 (cvbml01):**
- Runs `ansys.e` directly (no scheduler, raw process)
- Also has `python3` long-runners (likely the pymapdl driver)
- 128 CPUs, NVIDIA T1000 GPU (low-end, mostly idle in observed runs)

**On ws2 (cvbml02):**
- Runs `ansys.e` directly, often very long (37h+ observed)
- 64 CPUs, no GPU
- Frequently under heavy load (76 observed) — shared with other users

**Coworkers/labmates seen on shared machines:**
- `jan`, `chan`, `hyeoksul`, `cmlee`, `yjchoi` — KAIST CVBML lab members
- `jan` is a heavy CPU user (4000%+ frequently) — note for resource contention

**Why:** Observed via sim-monitor on 2026-05-07. ANSYS/PyMAPDL workflow is the entire focus of jarvis monitoring.

**How to apply:** When user asks about "my sims" or "jobs", these are the patterns. Look for `ansys.e` and `python3` processes on workstations, and `slrum_pymapdl*` jobs in Slurm. Output files follow Slurm convention. Don't kill or modify other users' jobs (jan, hyeoksul, etc.) — only observe.
