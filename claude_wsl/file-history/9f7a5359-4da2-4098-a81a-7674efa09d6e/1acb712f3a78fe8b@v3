---
name: mesh-timeout-2d-meshadapt
description: "gmsh solid-mesh failures in 65_final_0723 were all 2D surface-mesh problems — fix ladder is Algorithm 5 → 6, plus a 0.05 → 0.06 size rung"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9f7a5359-4da2-4098-a81a-7674efa09d6e
  modified: 2026-07-24T03:52:57.755Z
---

For the 65_final_0723 Type-1 dist meshing, **almost every failure mode traced back to the 2D surface mesh, not the 3D volume mesher.** Final result: **367/383 (95.8%)**, up from 322 (84.1%), neg-Jacobian 0 on all.

**`Mesh.Algorithm=2` (Automatic) silently falls back to MeshAdapt on the BSpline faces** and thrashes in edge recovery (`8-| Splitting those edges and trying again`) — that was the entire 40-min-timeout population (35 cases), which never reached 3D at all. It also produced self-intersecting boundary meshes that made 3D die with `Invalid boundary mesh (overlapping facets)` / `PLC Error: A segment and a facet intersect` — which *look* like 3D failures but are not. Changing `Algorithm3D` does nothing for either.

**Escalation ladder that worked (each rung capped at 20 min):**
1. `Mesh.Algorithm=5` (Delaunay) @ 0.05 — recovers most timeouts, 40 min → ~1 min
2. `Mesh.Algorithm=6` (Frontal-Delaunay) @ 0.06 — for faces where 5 *also* falls back to MeshAdapt. Recovered case 3 (54.3 s) and 72 (71.7 s) after both had exhausted 0.05 **and** 0.06 with algo 5.

Use `algo3d=1` (Delaunay) only paired with `algo2d=5`; its boundary-recovery step is slow. `algo2d=2 + algo3d=1` is the one combination to avoid.

**Coarsening is cheap and safe**: elements scale ~(1/h)³, so 0.05 → 0.06 gives ~58%. Time and element count correlate at **r = 0.815**, so a time cap is really an element cap. Do NOT use a short flat cap — on the 322-mesh baseline a 5-min cap would have discarded 93.5% of good meshes, 10-min 12.4% (median 6.3 min, p90 15.3 min). Quality does not suffer: case 14 went 5.08M → 1.57M elements (−69%) and min_q *improved* 0.106 → 0.146.

18 cases were built at 0.06 instead of 0.05 — listed in `solid_0723/coarsened_cases.json`; **flag them in the parameter study**, discretisation differs.

`STEP4 Failed` is NOT a corrupt STEP file: `gmshing_solid` raises when `volumes - {lipid,fc,lumen}` has length ≠ 1, and the boolean leaves **sliver volumes** (0.0001–0.01 against a 150–290 body). Only 3 of the 13 CAD failures (65, 114, 240) show real `BOPAlgo_AlertSelfInterferingShape` and need geo regeneration; the other 10 should be recoverable with a sliver filter. case 151 additionally has a negative-volume solid.

Scripts on cvbml01: `mesh_one_dist.py <case> <nproc> <size> [algo2d] [algo3d]`, `batch_retry{,2,3}_0723.py`, records in `retry_progress.jsonl`. Batch context [[batch-dist-meshing-0723]]; quality recipe [[solid-mesh-negjacobian-fix]]; reporting format [[reporting-format-mesh]].
