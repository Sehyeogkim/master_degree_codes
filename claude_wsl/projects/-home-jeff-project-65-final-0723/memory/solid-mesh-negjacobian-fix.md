---
name: solid-mesh-negjacobian-fix
description: Recipe that eliminates negative-Jacobian elements in the Type-1 solid mesh (fc cap inversions)
metadata: 
  node_type: memory
  type: project
  originSessionId: 9f7a5359-4da2-4098-a81a-7674efa09d6e
  modified: 2026-07-23T04:45:57.556Z
---

Type-1 solid mesh (case 0) had persistent negative-Jacobian (inverted quadratic) volume elements. Diagnosis (per-element minSICN via gmsh `getElementQualities`): the ~12 inverted elements cluster in the **fibrous cap (fc)** — thin, curved shell — near the lumen wall (r≈0.4-0.65mm) at the axial cap-end stations (z≈±6-9mm). NOT the lipid body. Note: fc = `fc.stp − lumen`, so it is **independent of the lipid.stp variant** — swapping lipid_sharp / lipid_less_round did NOT help (and raised the count).

**What FIXED it (neg-Jacobian → 0, min quality −0.46 → +0.02):**
- `gmsh.option.setNumber("Mesh.Smoothing", 10)`  (Laplacian)
- `gmsh.model.mesh.optimize('HighOrder')`  after `generate(3)`  — HighOrder ONLY
- keep quadratic (ElementOrder=2), SecondOrderLinear=0

**What did NOT work / made it worse:**
- `optimize("Netgen")` after order-2 generation — downgrades volume tets to LINEAR (breaks the quadratic mesh) and does not remove inversions. Never enable Netgen after order-2. See the failed `HXT_meshing_I_opt.py`.
- lipid geometry variants (sharp / less_round) — wrong lever (fc is independent of lipid).
- mesh size (0.055↔0.05) and 2D algorithm (2/5/6) — small effects, never reached 0.

**Element-count win:** replacing the Box size field with a **Distance field from the fc surfaces** (`fc_surfaces`) + Threshold (SizeMin=mesh_size near fc, SizeMax=0.2, DistMin=0, DistMax=3.0) → 1.69M elems vs 2.98M for box, same quality (both neg-Jac 0). Fine only near fc, coarse elsewhere (far field has no stress concentration).

Recommended production config: **dist(fc) + Smoothing=10 + HighOrder, mesh_size 0.05.** Modules on cvbml01 `65_final_0723`: `HXT_meshing_I_dist.py` (distance) / `HXT_meshing_I_box.py` (box+smooth), runner `run_solid_0723_mod.py` (env MOD, TAG). Hint origin: `62_mesh_test_lipid_0418/HXT_meshing_3_distance.py`. See [[solid-mesh-env-cv1]] [[solid-mesh-two-types]] [[reporting-format-mesh]].
