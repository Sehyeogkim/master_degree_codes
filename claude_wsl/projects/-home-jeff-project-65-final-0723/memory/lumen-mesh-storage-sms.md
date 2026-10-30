---
name: lumen-mesh-storage-sms
description: Delete volume_mesh.sms after each lumen mesh — it is 63% of the output and unused downstream
metadata: 
  node_type: memory
  type: project
  originSessionId: f3f14530-1064-48cb-8a56-66f291e24cfb
  modified: 2026-07-24T00:53:47.913Z
---

In the 65_final_0723 lumen fluid meshing output (`fluid_0723/case_<i>/meshing/`), Simmetrix's native `volume_mesh.sms` is ~180 MB/case — **63% of the ~640 MB per-case footprint** — and is NOT used downstream (svSolver reads the `mesh-complete` tree). User approved deleting it (2026-07-24): 154 files / 59.5 GB reclaimed, `fluid_0723` went 96 GB → 38 GB.

`bin/mesh_all_g010.py` now calls `drop_sms(out_dir)` after each successful case and on the skip path, so it self-cleans on any restart. A batch already running keeps the old in-memory code — sweep manually until it restarts.

Only delete when `meshing/mesh-complete/mesh-complete.mesh.vtu` exists, and skip the case currently being meshed (find it via `pgrep -af mesh_generator`).

Matters most for the harvey rsync [[copy-mesh-to-harvey]]: full 384-case set is ~93 GB instead of ~243 GB. Keeps `discrete_model.smd` + `lumen.msh/vtk/vtp` (~28 MB/case, minor). See [[lumen-mesh-wsl-setup]].
