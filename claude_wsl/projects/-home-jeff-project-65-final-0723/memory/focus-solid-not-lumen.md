---
name: focus-solid-not-lumen
description: "For 65_final_0723 meshing work, focus on solid mesh only; ignore lumen/Simmetrix"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9f7a5359-4da2-4098-a81a-7674efa09d6e
  modified: 2026-07-23T00:21:02.568Z
---

User directive (2026-07-23): for the 65_final_0723 meshing task, focus ONLY on the solid mesh. "lumen은 신경쓰지마 너는 고체 메쉬만 집중해".

**Why:** the local `lumen_simmetrix.py` + `utils/{meshing,runner}.py` + `simmetrix_path.json` (Simmetrix/fluid path) is a separate concern the user handles elsewhere.

**How to apply:** ignore lumen/Simmetrix pipeline; work the solid (HXT/gmsh) pipeline [[solid-mesh-two-types]] on cv1 [[solid-mesh-env-cv1]]. Also: user handles copying local→cv1 themselves ("따로 진행할 예정") — do not run the copy unless asked.
