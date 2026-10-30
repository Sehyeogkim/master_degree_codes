---
name: Project jarvis
description: Centralized monitoring tool the user is building in /home/jeff/jarvis to track simulations across 4 machines
type: project
originSessionId: 09397dbb-5629-47d6-b63a-015b28e41479
---
User is building "jarvis" — a centralized monitoring tool that runs from WSL Ubuntu and pulls simulation status from 4 environments:
1. local (this WSL Ubuntu)
2. workstation1 (remote, via SSH)
3. workstation2 (remote, via SSH)
4. harvey (HPC cluster, via SSH)

User will provide a JSON file with hostnames/users (and originally proposed passwords, but we settled on SSH keys instead).

**Why:** User runs many simulations across these machines and wants one place to see "how's it going, how are the results."

**How to apply:** All monitoring code lives in /home/jeff/jarvis/. Centralized model — jarvis runs locally and reaches out to remotes; no agents on remotes (decided 2026-05-07). First specific feature to monitor is TBD — user said "I'll tell u hold on."

**Out of scope (confirmed 2026-05-07):** No GUI/screen capture. Cannot watch Chrome or Windows GUI programs. Can shell to powershell.exe for text-based Windows process info if needed.
