---
name: utils-bc-ws1-stale-trap
description: "ws1's utils_bc.Apply_Traction is a stale version that inflates cap stress ~100x; ws2's is correct"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7745583c-3bb8-4ce1-82e6-81ae89d07345
  modified: 2026-07-29T13:07:15.755Z
---

`~/repo/master_python/src/utils/utils_ansys/utils_bc.py` **differs between ws1 and ws2**.

- **ws2 (correct)**: writes the traction VECTOR — `sfe,e,1,PRES,0,Tx` + `sfe,e,2,…,Ty` + `sfe,e,3,…,Tz`
- **ws1 (stale/wrong)**: writes `sfe,e,1,PRES,0,‖T‖` — the whole magnitude on face 1 only

With `keyopt(7,2,1)` faces 1/2/3 are element local x/y/z, so ws1's version loads a thin
stiff cap **in-plane** instead of normally. Case 0, same mesh, same wall CSV:
ws2 → 115.4 kPa ✅ vs ws1 → 12 532 kPa ❌ (**108×**). ws1's file has the vector form
commented out beneath the magnitude form — easy to misread as "rejected". It was not.

**Why:** discovered 2026-07-29 while running the solid mesh independence study on ws1;
the absurd MPa-scale stresses were traced to this after ruling out mesh scale, geometry,
and material parameters.

**How to apply:** only `pymapdl_simulation_ver1.py` / `ver2.py` call `Apply_Traction`;
everything else (`pymapdl_sim_LAP_0728`, `pymapdl_sim_CP_0728`, `ver5_fibrous*`) uses the
`/MAP` → `mapped.sfe` path and is unaffected. Production LAP peak ran ver2 **on ws2**, so
the production dataset is clean. Before any ver1/ver2 run on ws1, `md5sum` the file
against ws2 and override `utils_bc.Apply_Traction` in the driver rather than editing the
shared repo. **Sanity check any cap-stress result: 1e2–1e3 kPa is physiological; MPa is a
bug.** Output arrays are CGS dyne/cm², ×0.1 → Pa. See [[solid-mesh-independence-0729]].
