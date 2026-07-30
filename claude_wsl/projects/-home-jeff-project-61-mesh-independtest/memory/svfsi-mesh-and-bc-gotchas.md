---
name: svfsi-mesh-and-bc-gotchas
description: "Critical svFSI gotchas — Simmetrix ASCII VTU must be converted to binary, Resistance BC must be Neu, convergence output files"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 33e5ae63-e425-452d-807e-1e223f480745
---

Hard-won fixes when feeding Simmetrix meshes into **svFSI** (binary
`/opt/cvbml/repos/svFSI/build/svFSI-build/bin/svFSI`, driven by a `fluid.inp`; NO svpre/.svpre —
svFSI reads `mesh-complete.mesh.vtu` + `mesh-surfaces/*.vtp` directly via `Add mesh`/`Add face`).

1. **Simmetrix writes ASCII VTU/VTP but declares a zlib compressor** → svFSI's XML parser mis-reads
   the connectivity and dies with `ERROR: VTU file read error (ien)` / `mismatch in IEN params`.
   FIX: rewrite every `.vtu` and `.vtp` as **binary** (vtk reader→writer with
   `SetDataModeToBinary()` + `SetCompressorTypeToZLib()`); see scratchpad `to_binary.py`. Working
   reference meshes show `format="binary"`; bad ones show `format="ascii"` in the DataArray header.
   Check element types first (`inspect_vtu.py`) — but the IEN error here was encoding, not mixed elements
   (meshes were pure tetra even with boundary layers on).

2. **svFSI Resistance outlet must be `Type: Neu`**, not `Dir`. A `Type: Dir` + `Time dependence:
   Resistance` block aborts at BC setup: `ERROR: Resistance is only defined for Neu BC`. Fix the
   outlet to `Type: Neu` (value unchanged).

3. **Convergence output files** (written into the "Save results in folder"): for the fluid/NS equation
   svFSI writes `B_NS_Velocity_flux.txt` (flow rate per face) and `B_NS_Pressure_average.txt`
   (avg pressure per face), plus `B_NS_WSS_average.txt`, `histor.dat`, `result_*.vtu`. Format:
   line1 = face names (e.g. `lumen_inlet lumen_outlet lumen_wall`), line2 = face areas, blank line,
   then one row per timestep. NOTE: `FlowHist.dat`/`PressHist.dat` are the OLD **svSolver/PHASTA**
   equivalents — svFSI does NOT write those (the prefix is `B_<eqname>_`, e.g. `B_NS_`).

4. A benign `FSILS: Singular matrix detected` can appear when both inlet & outlet are Neumann
   (pressure level weakly constrained); the run still converged fine.

See [[mesh-independence-workflow]].
