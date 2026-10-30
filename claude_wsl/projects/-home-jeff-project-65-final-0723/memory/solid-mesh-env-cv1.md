---
name: solid-mesh-env-cv1
description: "How to run the solid (HXT) meshing pipeline on cv1 — conda env, utils package origin, run recipe"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9f7a5359-4da2-4098-a81a-7674efa09d6e
  modified: 2026-07-23T00:38:20.467Z
---

Solid mesh pipeline lives in `/home/jeff/project/54_analysis` (cv1 = ssh alias `ws1` = cvbml01; there is NO `cv1` ssh alias).

**Both cvbml01 (`ws1`) and cvbml02 (`ws2`) are set up IDENTICALLY** for solid/HXT meshing: same conda `ansys_new` with version-identical deps (numpy 2.0.1, pandas 2.3.1, scipy 1.15.3, gmsh 4.14.0, pyvista 0.46.0), same `utils.utils_geo_mesh` via `/home/jeff/repo/master_python/src` editable install, same HXT scripts in 54_analysis. Type1 & Type2 import OK on both. On cvbml02 only the input geometry (geo_0723 / solid_data) is not yet copied — env needs nothing installed. cvbml02 needs HXT meshing only, no lumen/Simmetrix.

**Run env: conda `ansys_new` (py3.10)** — `/home/jeff/miniconda3/envs/ansys_new/bin/python`. Has gmsh 4.14 / meshio / numpy / pandas / scipy / pyvista, and the `utils.utils_geo_mesh` package.

**Key gotcha (I got this wrong once):** the `utils.utils_geo_mesh` package is NOT inside 54_analysis. It resolves from `/home/jeff/repo/master_python/src/utils/utils_geo_mesh/` (contains utils_gmsh, utils_CAD, main_CAD, smooth_vtu_to_stl), installed EDITABLE into ansys_new via `easy-install.pth`. So it imports from any cwd. Both `HXT_meshing_I.py` (Type 1) and `HXT_type2_utils.py` (Type 2) import cleanly under ansys_new.

Do NOT use `/home/jeff/project/.venv` (py3.8) — it only has gmsh/meshio/numpy, missing pandas/scipy/pyvista.

"총 2개 메쉬" = two solid mesh types: [[solid-mesh-two-types]]. Focus is solid only; lumen/Simmetrix is out of scope [[focus-solid-not-lumen]].
