---
name: lumen-mesh-mixed-grid-0723
description: "fluid_0723 lumen meshes are mixed-resolution — case_0-164 @ grid 0.01, case_165-383 @ 0.015"
metadata: 
  node_type: memory
  type: project
  originSessionId: f3f14530-1064-48cb-8a56-66f291e24cfb
  modified: 2026-07-24T09:14:42.447Z
---

**UPDATE 2026-07-24 (later): user reversed the mixed-resolution decision — going UNIFORM 0.015.** The downstream fluid work uses the **0.015** set. case_0–164 (originally 0.01) were re-meshed at 0.015; their original 0.01 output was archived (mv, same filesystem) to `fluid_0723_g010_backup/case_<i>/{meshing,tree.dat,xyzts.dat}` (165 cases, ~40 GB) — keep it, do not delete. So the historical "mixed by design, don't fix" note below is SUPERSEDED; `fluid_0723/` is now all 0.015.

Note on `.sms`: the only `.sms` left per case is `input_model_mesh.sms` (~1.6 KB, negligible). The big `volume_mesh.sms` (~180 MB) is already auto-dropped by `drop_sms` after each case — there is no meaningful space to reclaim from `.sms`.

--- historical (superseded) ---
The `65_final_0723` lumen fluid mesh set in `fluid_0723/` was **mixed resolution by the user's decision (2026-07-24)**:

| 구간 | grid | 평균 nodes | 평균 tets | case당 |
|---|---|---|---|---|
| case_0 – case_164 | **0.01** | 537,792 | 2,976,595 | 144 s |
| case_165 – case_383 | **0.015** | ~221,000 | ~1,210,000 | 77 s |

The 0.01 batch ran to case_164, then the user switched to 0.015 for the rest rather than re-meshing. 0.015 gives ~59% fewer elements and ~1.9× faster meshing. I flagged that this makes cross-case CFD comparison inconsistent; the user chose it anyway — do not "fix" it unsolicited.

**COMPLETE 2026-07-24: 384/384 meshed, no gaps.** node/tet min·avg·max = 134k·358k·567k / 682k·1.97M·3.14M; total meshing compute ~11.3 h (sum of per-case).

Runners: `bin/mesh_all_g010.py` (GRID=0.01, done) and `bin/mesh_all_g015.py` (GRID=0.015, done). Both iterate all geo_0723 cases and skip any with `meshing/mesh-complete/mesh-complete.mesh.vtu`, so they compose safely and are freely re-runnable. Separate progress CSVs: `lumen_meshing_g0{10,15}_progress.csv`.

⚠️ **Simmetrix is a single floating seat (`geomsim_core` 1 seat, license server cvbml01:2800).** When another machine (cvbml02/harvey) runs Simmetrix concurrently, cases fail with `No license for feature discrete` → downstream `FileNotFoundError: surface_with_id_1.vtp`. This is **transient license contention, NOT geometry** — the exact same case meshes fine on a later pass when the seat frees. It's intermittent (mid-sweep some cases fail, next case succeeds), so a single pass won't converge. Fix pattern: `bin/retry_until_done.sh` re-runs the resumable batch until 384/384 or a pass adds 0 new meshes (persistent-failure stop). On 2026-07-24 this cleared 29 then 8 license-failed cases with zero geometry fixes. Before diagnosing a "meshing failure," grep the per-case `meshing/simmetrix.log` for `No license` first.

Launch detached: `setsid nohup $PY -u bin/mesh_all_g015.py > mesh_all_g015.log 2>&1 < /dev/null &`. Survives terminal close but **not** a WSL shutdown (happened 7/24 overnight, cost 1 case).

⚠️ When killing the batch, `pkill -f mesh_all_g015.py` also matches the killing shell's own command line — use a bracket pattern (`mesh_all_g015[.]py`) or kill by PID. Always kill the orphaned `mesh_generator` too or it keeps the Simmetrix license. See [[lumen-mesh-wsl-setup]], [[lumen-mesh-storage-sms]].
