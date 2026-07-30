---
name: solid-mesh-independence-0729
description: "LAP solid mesh independence study (2026-07-29) — findings, chosen metric, and where the record lives"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7745583c-3bb8-4ce1-82e6-81ae89d07345
  modified: 2026-07-29T13:07:30.843Z
---

Solid mesh independence for the LAP fibrous cap, run 2026-07-29 on ws1, case 0, Box recipe.
**Full record + every script: `54_analysis/mesh_independent_test_solid/` on ws2, harvey, and WSL.**

**Production mesh identified:** Box field, `mesh_size = 0.055` mm, algo2d = 5 (matched by
re-meshing case 0 to within 0.067% of the stored node count). Box cohort n=762, second-order
tets median **2.22e6** [1.73e6–2.85e6]. A separate 148-mesh cohort used the distance-field
recipe (~1.9× coarser); decision taken: **paper uses Box only**.

**Key result — the metric matters more than the mesh:**
- Radius-free cap stress (raw max / p99 / p99.9) is **converged**: successive changes
  1.13 % → 0.15 % → 0.04 %, so 0.05 is the coarsest grid on the plateau. The actual
  production mesh agrees with a 5.95e6-element reference to **0.053 %**.
- **PSS (fixed-radius unweighted nodal mean) is NOT converged** — 9.3 % spread, inverted
  (observed order p = −6.6). Cause: `n_sphere` runs 42 → 148 across the ladder, so the
  metric tracks mesh density. Persists after fixing [[utils-bc-ws1-stale-trap]], confirming
  it is a property of the definition, not the FE solution.
- Trade-off: raw max has stable *value* but bistable *location* (two maxima ~4.5 mm apart);
  PSS has unstable value but stable location (0.024 mm). Recommendation: value from
  **p99.9**, location from the ΔPSS/smoothed field.

**Open:** case 0 is only the 13.6th percentile of the cohort; **case 339** is the median case
and the fluid section says "a case at the cohort median". `scripts/run_case339.sh` is staged
but never ran — ws1's disk failed first. See [[ws1-disk-failure-0729]].

**Also note:** the draft's "approximately 3×10⁶ elements" is the NODE median, not the element
median (2nd-order tets carry ~1.48 nodes/element). PSS definition source is
`65_final_0723/post_processing_0727.py`, inside `ws1:~/project/65_final_0723.tar.gz`.
