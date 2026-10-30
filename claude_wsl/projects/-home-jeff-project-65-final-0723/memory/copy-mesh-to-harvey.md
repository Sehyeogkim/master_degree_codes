---
name: copy-mesh-to-harvey
description: "Copy completed fluid mesh cases from local fluid_0723 to harvey, then chain q_ramp sim"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4c5c939f-6472-457a-bbdc-757c03d64685
  modified: 2026-07-24T00:59:10.321Z
---

Local meshing writes `fluid_0723/case_0..384/` (see [[focus-solid-not-lumen]] area, but this is the fluid/lumen mesh). A case is COMPLETE when `progress.csv` marks it done AND `case_N/{tree.dat,xyzts.dat}` + `case_N/meshing/mesh-complete/` all exist (= next case started).

**Task:** COPY (never move) each completed case ≥5 to harvey `/home/jeff/project/65_final_0723/fluid_0723/case_N/`: only `meshing/` (whole tree), `tree.dat`, `xyzts.dat`. Cases 0–4 already copied. Use rsync WITHOUT `--delete` — harvey case dir may already hold `q_ramp/`, `steady_3d/`, `wall/`, `pulsatile_1d/` which must NOT be touched.

Copy helpers live in the PROJECT (not scratchpad — scratchpad gets wiped between sessions): `/home/jeff/project/65_final_0723/harvey_sync/copy_case_to_harvey.sh <N>` (one case, idempotent, verifies artifacts first) and `harvey_sync/copy_backlog.sh` (all pending ≥5, numeric order, flock-guarded). ~180MB volume_mesh.sms per case → ~1–2 min/copy; run in background.

**Completeness marker = `xyzts.dat` on harvey** (it is rsynced LAST, after `meshing/`). Bug hit 2026-07-23: an interrupted copy left case_12 with a partial `meshing/mesh-complete/` but no xyzts.dat; the old "on-harvey" check looked only for the `mesh-complete/` dir, so it was mistaken for complete and q_ramp failed fast (Q_ramp_0723.py swallows the missing-file error, exits 0, no slab). copy_backlog + qramp_dispatch now both require `xyzts.dat` (and `mesh-complete.mesh.vtu`) before treating a case as copied/eligible.

Then chain q_ramp: [[harvey-qramp-pipeline]]. Driven by a `/loop` (dynamic pacing) that batch-copies newly-done cases and submits q_ramp jobs.
