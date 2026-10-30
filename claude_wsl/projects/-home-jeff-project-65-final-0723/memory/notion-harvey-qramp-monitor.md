---
name: notion-harvey-qramp-monitor
description: Notion page for reporting the mesh-copy + Q_ramp pipeline status
metadata: 
  node_type: memory
  type: reference
  originSessionId: 4c5c939f-6472-457a-bbdc-757c03d64685
  modified: 2026-07-24T00:59:05.091Z
---

Report pipeline status to Notion page **"⛸️ Harvey Q ramp monitor"**:
https://app.notion.com/p/3a62a46dc68c803dac13f122172d4180 (id `3a62a46d-c68c-803d-ac13-f122172d4180`, under Plaque > monitoring).

**OVERWRITE, don't accumulate** (user 2026-07-24): each tick uses `notion-update-page` with `command: "replace_content"` so ONLY the newest report remains. Do NOT use `insert_content` at page start (that was the old, now-rejected behavior).

**Why:** user only cares about current state; a growing log of past ticks is noise.

Each report includes BOTH mesh copy AND Q_ramp status: KST timestamp, table of meshing / copy→harvey / Q_ramp progress (range + count + %), which Q_ramp cases are running/pending, per-node usage, and the bottleneck. Relates to [[copy-mesh-to-harvey]], [[harvey-qramp-pipeline]], [[reporting-format-mesh]].
