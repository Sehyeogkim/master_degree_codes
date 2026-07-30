---
name: lumen-mesh-wsl-setup
description: How to run 65_final_0723 lumen Simmetrix meshing (stp->vtk->vtp->mesh) locally in WSL
metadata: 
  node_type: memory
  type: project
  originSessionId: f3f14530-1064-48cb-8a56-66f291e24cfb
  modified: 2026-07-23T02:15:29.508Z
---

Running cvbml01's real lumen meshing pipeline `lumen_meshing_0723.py` in WSL, unchanged code — only path config swapped. Verified 2026-07-23: case_0 built end-to-end (grid_size 0.015, ~66s Simmetrix, 210,737 nodes / 1,153,827 tets); output tree matches cvbml01, `lumen_meshing_failed.txt` = `[]`.

Pipeline (per case geo_0723/case_i/lumen.stp):
1. `LumenMeshing._stp_to_vtk` — gmsh imports STEP via OCC, tags faces wall=1/inlet=2/outlet=3 (physical groups), triangulates surface -> lumen.vtk (ModelFaceID cell data)
2. `_vtk_to_vtp` -> lumen.vtp
3. `runner.run_simmetrix_meshing` (Simmetrix mesh_generator) -> volume mesh
4. `_assemble_mesh_tree` -> fluid_0723/case_i/meshing/mesh-complete/{mesh-complete.mesh.vtu, .exterior.vtp, walls_combined.vtp, mesh-surfaces/{wall,inlet,outlet}.vtp}
5. tree.dat + xyzts.dat from VesselCADModel (parameter.csv row == case_id)

Code lives in master_python: `lumen_codes.cad_meshing` (VesselCADModel, LumenMeshing) + `utils.utils_lumen.runner` (run_simmetrix_license/meshing), at `/home/jeff/repo/master_python/src` (editable install `master-degree-codes`). See [[solid-mesh-env-cv1]].

WSL setup (what was missing vs cvbml01):
- `master_python` repo absent -> `rsync -az jeff@cvbml01.kaist.ac.kr:/home/jeff/repo/master_python/ /home/jeff/repo/master_python/`, then `pip install -e /home/jeff/repo/master_python --no-deps` into conda env `ansys_new`.
- `gmsh` missing in WSL `ansys_new` -> `pip install gmsh` (meshio/vtk already present: meshio 5.3.5, vtk 9.6.1, gmsh 4.15.2, py3.10).
- Config: script reads `pre_data/solver_path.json` (NOT the older `simmetrix_path.json`). Created it in WSL with simmetrix.meshing=`/home/jeff/repo/SyntheticTreeGenerator/build/apps/MeshGenerator/mesh_generator`, simmetrix.license=`/home/jeff/repo/SyntheticTreeGenerator/apps/MeshGenerator/floating.lic`.
- Run one case: copy `lumen_meshing_0723.py` from cvbml01, set `CASE_IDS = [0]`, run with `/home/jeff/miniconda3/envs/ansys_new/bin/python lumen_meshing_0723.py`.

cvbml01 access: ssh key auth works but `Host cvbml01` alias / DNS `cvbml01` is flaky ("Temporary failure in name resolution"); use FQDN `jeff@cvbml01.kaist.ac.kr` (~/.ssh/id_ed25519). Env there: conda `ansys_new` py3.10.

Note: the WSL mesh_generator was hand-built earlier (tirpc link fix in apps/MeshGenerator/CMakeLists.txt — appended `/lib/x86_64-linux-gnu/libtirpc.so.3` to target_link_libraries, then cmake . + make). The old `lumen_simmetrix.py` (61-style, borrowed vtp, no STEP conversion) is superseded by this real pipeline.
