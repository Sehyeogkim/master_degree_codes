---
name: server-abbreviations
description: "User's shorthand aliases for the 3 SSH servers (cv1/cv2/hy)"
metadata: 
  node_type: memory
  type: user
  originSessionId: 7fd6c708-4335-46a3-9255-369f4530546e
  modified: 2026-07-22T23:55:31.617Z
---

The user refers to the SSH servers with these shorthands:

- **cv1** = cvbml01 → SSH alias `ws1` (cvbml01.kaist.ac.kr:22, user jeff)
- **cv2** = cvbml02 → SSH alias `ws2` (cvbml02.kaist.ac.kr:22, user jeff)
- **hy** / **하비** (harvey) → SSH alias `harvey` (harvey.kaist.ac.kr:10022, user jeff)

Auth is SSH key only (`~/.ssh/id_ed25519`). Use the config aliases (`ws1`/`ws2`/`harvey`) in commands, never hardcode hosts. Main tasks with these servers: running code and moving files. See the [[ssh]] skill.
