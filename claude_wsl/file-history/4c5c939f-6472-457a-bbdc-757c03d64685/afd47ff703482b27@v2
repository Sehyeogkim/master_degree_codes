---
name: case-150-mesh-lost
description: "case 150 q_ramp mesh is unrecoverable (deleted locally + truncated on harvey) — skipped in dispatch, needs re-mesh"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4c5c939f-6472-457a-bbdc-757c03d64685
  modified: 2026-07-24T10:35:28.360Z
---

In `65_final_0723`, **case 150 has no valid q_ramp mesh anywhere** (found 2026-07-24):
- Local `fluid_0723/case_150/meshing/` was emptied by WSL disk-cleanup (only tree.dat + xyzts.dat remain) — cleanup deletes local meshes for cases ≥~100 assuming harvey has a good copy.
- harvey's `mesh-complete.mesh.vtu` is **truncated to exactly 160.0 MiB (167772160 bytes)** → svpre fails in ~5s: `vtkXMLUnstructuredGridReader returned failure` / `Must specify number of nodes before you read them in!` → no slab → dispatch retry-looped it forever.

**Fix applied:** added `declare -A SKIP=( [150]=1 )` to `qramp_dispatch.sh` (skips it in the eligibility loop) so it no longer wastes slots. Case 150 is the ONLY unrecoverable case — a full harvey vtu scan (384 files) found only case 150 truncated; case 313 is genuinely small (~44MB, local==harvey, valid); case 0–4 are the known coarse g015 ([[case-0-4-mesh-mismatch-ignored]]).

**To recover 150:** re-run the meshing for case 150 (dense g010 range since 150 < 165), copy to harvey, then remove 150 from SKIP and dispatch. Until then the final q_ramp set will be 383/384. Relates to [[copy-mesh-to-harvey]], [[harvey-qramp-pipeline]].
