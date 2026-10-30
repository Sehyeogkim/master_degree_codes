---
name: steady3d-300-timesteps
description: "steady 3D fluid runs converge by ~300 steps, not 500 — use 300 from now on (user decision 2026-07-29)"
metadata: 
  node_type: memory
  type: project
  originSessionId: eb46bfa4-2274-4ce2-8973-81686381b623
  modified: 2026-07-29T08:48:18.142Z
---

Steady 3D fluid (svSolver, DT=1e-4) settles well before the 500 timesteps used in production. Measured on 54_analysis case 0 mesh-independence runs (2026-07-29), reading `FlowHist.dat` in `<NP>-procs_case`:

| run | 0.1% converged | 0.01% converged | last-10-step variation |
|---|---|---|---|
| grid 0.02 / peak | step 90 | 225 | 0.00001% |
| grid 0.02 / low | 77 | 287 | 0.00076% |
| grid 0.015 / peak | 51 | 193 | 0.00006% |

Final Q matched the prescribed BC exactly (peak 0.151553, low 0.537509), so this doubles as a BC sanity check.

**User decision: use `Number of Timesteps: 300` for all future steady 3D runs** (~40% wall-clock saving vs 500).

**Why:** 500 was ~1.7–2× more than needed; the wall traction field is fully settled by 300.

**How to apply:** in `steady_3D_pre_no_hyperemia.py` / `mi_steady_pre.py`, set `NUM_TIMESTEPS = 300` **and** `RESTART_FREQ = 300`, and set `STEP = 300` in the matching post script — svpost reads `restart.<STEP>.1`, so pre/post must agree or post finds nothing. Note restart is written **only** at the restart frequency, so a run killed mid-flight leaves nothing to post-process; never plan to harvest a run early without having lowered the restart frequency first.

Convergence check recipe: `np.loadtxt(FlowHist.dat, skiprows=1)` (line 1 is the count) → compare tail to final value. Same idea for `PressHist.dat`.

Related: [[steady3d-nohyperemia-54analysis]], [[steady-3d-pipeline]], [[fluid-mesh-independence-54analysis]]
