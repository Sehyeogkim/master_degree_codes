---
name: reporting-format-mesh
description: How the user wants mesh-run results reported
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9f7a5359-4da2-4098-a81a-7674efa09d6e
  modified: 2026-07-23T02:52:35.789Z
---

When reporting a meshing run to the user, always report these three, concisely: **mesh quality**, **# of mesh (element/node count)**, **total time**.

**Why:** user asked for a consistent, minimal status format (2026-07-23) instead of long logs.

**How to apply:** lead with those three metrics (a short table is fine); keep extra detail (warnings, negative-Jacobian counts, file sizes) brief/secondary. Applies to solid HXT runs [[solid-mesh-env-cv1]].
