---
name: env-no-jq
description: jq is NOT installed on local WSL; passwordless sudo unavailable
metadata: 
  node_type: memory
  type: feedback
  originSessionId: fee3bd16-6bc5-4e6f-84f5-3a1cf69f3015
---

`jq` is not installed anywhere on the local WSL machine, and passwordless `sudo`
is unavailable (so I can't `apt-get install` it myself). `python3` and `node`
exist only via miniconda (`/home/jeff/miniconda3/bin/`), which is not always on
the PATH that hooks/statusline run under.

**Why:** the statusline (`~/.claude/statusline-command.sh`) was silently broken
because it piped JSON through `jq` for every field — all calls failed and the
line collapsed to just `jeff@DESKTOP-QOJU0PM:`.

**How to apply:** don't write project scripts (e.g. planned `bin/jarvis-status`,
`bin/win-status`) that depend on `jq`. Parse JSON with `python3` located by
absolute path, or ask the user to run `! sudo apt-get install -y jq` if jq is
truly wanted. See [[environment]].
