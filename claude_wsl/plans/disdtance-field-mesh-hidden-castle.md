# Plan: Batch distance-field solid meshing (case 1–383) on cvbml01 + Notion live dashboard

## Context
We validated the **distance-field** Type-1 solid mesh recipe (`HXT_meshing_I_dist.py`: fc-surface Distance+Threshold sizing, `Smoothing=10`, `optimize('HighOrder')`) on case 0 — it eliminates negative-Jacobian elements (min quality −0.46 → +0.02) and cuts element count ~43% vs the box field. The full geometry set (384 cases, case_0–383, stp-only, 170M) is now on cvbml01 at `65_final_0723/geo_0723/`.

Goal: mesh **case 1 through 383** with the dist recipe, **save only the `.msh`** (skip the ~130MB vtu per case to save disk), run **4 cases in parallel (nproc 12 each)**, skip cases already meshed, continue past failures — and report progress to the Notion page **"🥌 HXT meshing1"** (`3a62a46dc68c80db83bad8bee57a85f9`) every 5 minutes as a live dashboard.

Constraints confirmed: cvbml01 has 463G free (dist msh ≈ 289MB/case → ~110–160GB total, fits); `ansys_new` conda env; `parameter.csv` (1000 rows) supplies `lesion_length` for every case.

## Files to create (on cvbml01 `/home/jeff/project/65_final_0723/`)

### 1. `mesh_one_dist.py` — single-case worker (msh only)
- Args: `<case> <nproc> <mesh_size>`.
- Import `gmshing_solid` from `HXT_meshing_I_dist` (unchanged), call with `save_vtu=False`.
- Output dir `solid_0723/case_<c>/dist_run/`. **Skip** (exit 0, status `skipped`) if `solid_type_1_dist.msh` already exists.
- On success: rename `solid_type_1.msh` → `solid_type_1_dist.msh` (**no vtu conversion**); `gmshing_solid` already writes `quality.json` (num_elements, min_quality, avg_quality, neg_jacobian_count, poor_count) into that dir.
- Print a final one-line JSON status (`{"case":c,"status":"done","num_elements":...,"min_quality":...,"neg_jacobian":...,"seconds":...}`) so the orchestrator can capture it; on exception print status `failed` with the message.

### 2. `batch_dist_0723.py` — orchestrator (4-wide)
- Range `range(1, 384)`; `ThreadPoolExecutor(max_workers=4)`, each task runs `subprocess.run([py, "mesh_one_dist.py", str(c), "12", "0.05"], timeout=2400)` (40-min per-case cap).
- Skip-if-exists handled inside the worker (keeps resume trivial).
- Append one line per finished case to `solid_0723/batch_progress.jsonl` (`{case,status,num_elements,min_quality,neg_jacobian,seconds,ts}`); statuses: `done` / `failed` / `timeout` / `skipped`. `ts` passed in (avoid `Date.now` issues — orchestrator may use `time.time()` freely, this is real Python not a workflow script).
- Maintain `solid_0723/batch_status.json` summary (total, done, failed, timeout, running, start_time). Write a `batch_dist.marker` at the end.
- Launch with `nohup … &` under `PATH=/home/jeff/miniconda3/envs/ansys_new/bin:$PATH` (env activation, so any freecad/lib deps resolve), logging to `solid_0723/logs/batch_dist.log`; each case's gmsh stdout → `solid_0723/logs/case<c>_dist.log`.

Reuse (do **not** modify): `HXT_meshing_I_dist.py` (`gmshing_solid`), `54_analysis/pre_data/bin/parameter.csv`, the `ansys_new` env + `utils.utils_geo_mesh` editable install.

## Notion live dashboard — via `/loop 5m`
After the batch is launched, start `/loop 5m` with a report step that each cycle:
1. `ssh ws1` → read `batch_progress.jsonl` + count `solid_0723/case_*/dist_run/solid_type_1_dist.msh` + read running `case<c>_dist.log` tails → compute: done X/383, failed list, currently-running cases, recent ~10 completions (case, elem, min_q, neg_jac, sec), elapsed, ETA (remaining ÷ 4 × avg case time).
2. **Replace** the Notion page body (`notion-update-page`, id `3a62a46dc68c80db83bad8bee57a85f9`) with a fresh snapshot dashboard:
   - Header: last-updated time, elapsed, ETA.
   - Progress line: ✅ done / ❌ failed / ⏳ running / remaining out of 383.
   - Quality summary: how many meshes have neg-Jacobian = 0, worst min-quality seen.
   - Table: recent completions (case | #elem | min_q | neg-jac | sec).
   - Failures: list of failed/timeout cases (e.g. case_3 if it still fails STEP1).
- Stop the loop (and note it) once `batch_dist.marker` appears (all cases done) — final cycle posts the completed summary.

## Notes / expected issues
- **case_3** had a STEP1 boolean failure earlier; geometry was regenerated (14:59) and re-synced, so it will be re-attempted — logged as `failed` if it still fails, batch continues.
- Some long-lesion cases may hit the 40-min cap → `timeout`, logged, batch continues.
- Disk: monitor via the dashboard is out of scope, but ~110–160GB will be consumed; 463G free is enough.

## Verification
1. After launch: `ssh ws1 'tail solid_0723/logs/batch_dist.log; ls solid_0723/case_1/dist_run/'` → case_1 producing `solid_type_1_dist.msh` + `quality.json`, **no** `.vtu`.
2. Confirm 4 concurrent `mesh_one_dist.py` processes (`ssh ws1 'pgrep -af mesh_one_dist | wc -l'` ≈ 4).
3. `batch_progress.jsonl` grows with one JSON line per finished case; `neg_jacobian` should be 0 on successes.
4. Notion page "🥌 HXT meshing1" shows the dashboard and refreshes every ~5 min; failures (e.g. case_3) appear in the failures list.
5. Resume check: re-running the orchestrator skips cases whose `solid_type_1_dist.msh` exists.
