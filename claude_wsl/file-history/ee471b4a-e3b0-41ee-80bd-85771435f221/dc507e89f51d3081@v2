---
name: cursor-worktree-disk
description: "On cvbml02, Cursor git-worktrees under ~/.cursor can silently eat ~1TB of disk"
metadata: 
  node_type: memory
  type: reference
  originSessionId: ee471b4a-e3b0-41ee-80bd-85771435f221
  modified: 2026-07-23T08:29:05.347Z
---

Disk-full culprit on **cvbml02** (2026-07-23): `~/.cursor/worktrees/jeff__SSH__cvbml02.kaist.ac.kr_` held **927GB** — Cursor background-agent git worktrees (full home checkouts). `/home/jeff` is a git repo there, so Cursor created worktrees (feat-* branches) that each materialize project/ + miniconda3/ (~464GB each).

**Why:** jeff's home is a git repo on cvbml02 (NOT on cvbml01 — cvbml01 `.cursor` was only 5.1MB, no worktrees).

**How to reclaim:** check none are active (`ps`/`lsof`, they were 8 months stale, same commit as master), then `git -C /home/jeff worktree remove --force <path>` + `git worktree prune`. Reclaimed 927GB (92%→58% full).

Also large on cvbml02: ANSYS sparse out-of-core `.DSPtri` scratch (see [[ansys-sim-cvbml02]]) — always clean `ansys_results_*` after solves. Per-user disk: `du -h -d1 /home/*`; jeff is the biggest user (~1.6TB of 3.6TB).
