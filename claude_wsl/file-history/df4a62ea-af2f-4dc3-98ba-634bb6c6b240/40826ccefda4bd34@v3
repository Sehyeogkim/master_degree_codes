---
name: case-0-4-mesh-mismatch-ignored
description: "harvey's case 0-4 use a coarser mesh than 5-164 — known and deliberately ignored, do not re-raise"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4c5c939f-6472-457a-bbdc-757c03d64685
  modified: 2026-07-24T04:43:17.760Z
---

In `65_final_0723`, harvey's `fluid_0723/case_0..4` hold the **coarse g015 mesh** (~82MB `mesh-complete.mesh.vtu`, copied 2026-07-23 09:18), while local has a denser g010 regeneration (~190MB, 2026-07-23 11:41) that was never copied. So case 0–4 q_ramp results came from a coarser mesh than case 5–164 (dense g010, ~195MB). Case 165+ are coarse g015 everywhere, matching.

**Why:** user was told about the inconsistency 2026-07-24 and answered "JUST IGNORE ABOUT THIS."

**How to apply:** do not re-copy case 0–4 meshes, do not re-run their q_ramp, and do not flag this again in tick reports or the Notion page. Cases 5+ are verified consistent between local and harvey. Relates to [[copy-mesh-to-harvey]], [[harvey-qramp-pipeline]], [[notion-harvey-qramp-monitor]].
