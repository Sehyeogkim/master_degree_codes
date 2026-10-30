---
name: batch-dist-meshing-0723
description: Batch distance-field solid meshing of case 1-383 on cvbml01 + Notion live dashboard (launched 2026-07-23)
metadata: 
  node_type: memory
  type: project
  originSessionId: 9f7a5359-4da2-4098-a81a-7674efa09d6e
  modified: 2026-07-23T06:40:39.617Z
---

Launched 2026-07-23 ~15:37 KST on cvbml01 (`ws1`): batch distance-field Type-1 solid meshing for **case 1..383**, .msh only (no vtu, disk), **4 parallel, nproc 12**, mesh_size 0.05, skip-if-msh-exists (resumable).

Files in `cvbml01:/home/jeff/project/65_final_0723/`:
- `mesh_one_dist.py <case> <nproc> <mesh_size>` — one case via `HXT_meshing_I_dist.gmshing_solid` (save_vtu=False), output `solid_0723/case_<c>/dist_run/solid_type_1_dist.msh` + `quality.json`; prints `STATUS {json}`.
- `batch_dist_0723.py` — orchestrator (ThreadPoolExecutor 4-wide, per-case timeout 2400s). Progress → `solid_0723/batch_progress.jsonl`, summary → `solid_0723/batch_status.json`, `batch_dist.marker` on completion. Per-case gmsh log `solid_0723/logs/case<c>_dist.log`, orchestrator log `solid_0723/logs/batch_dist.log`. Launched via `nohup` under `PATH=…/ansys_new/bin:$PATH`.
- `dash_report.py` — prints the Notion-markdown dashboard from batch_progress/status.

**Resume:** re-run `nohup python batch_dist_0723.py` — already-meshed cases skip. **Monitor:** `ssh ws1 python .../dash_report.py`.

**Notion dashboard:** page "🥌 HXT meshing1" id `3a62a46dc68c80db83bad8bee57a85f9`, refreshed every 5 min by CronCreate job (session-only cron `*/5 * * * *`) that runs dash_report.py → notion-update-page replace_content. **The cron dies when this Claude session ends; the nohup meshing batch keeps running regardless** — rerun the /loop to resume dashboard updates.

Recipe details in [[solid-mesh-negjacobian-fix]]; env in [[solid-mesh-env-cv1]]; reporting format [[reporting-format-mesh]]. Note: case_3 previously failed STEP1 boolean; geometry regenerated — watch whether it now passes.
