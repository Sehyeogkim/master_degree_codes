---
name: Server connection info
description: Hostnames, ports, and usernames for the 3 remote machines jarvis monitors
type: project
originSessionId: 09397dbb-5629-47d6-b63a-015b28e41479
---
| Alias | Host | Port | User | Notes |
|---|---|---|---|---|
| `harvey` | harvey.kaist.ac.kr | 10022 | jeff | KAIST HPC, Slurm scheduler |
| `ws1` (workstation1) | cvbml01.kaist.ac.kr | 22 | jeff | Linux workstation, CVBML lab |
| `ws2` (workstation2) | cvbml02.kaist.ac.kr | 22 | jeff | Linux workstation, CVBML lab |

**Why:** Provided by user 2026-05-07 in `.claude/commands/ssh.md`. The `cvbml` prefix and `kaist.ac.kr` domain suggest these are KAIST university machines (likely Computer Vision and Biomedical Lab).

**How to apply:** Use these aliases when SSH'ing or building monitoring polls. Auth is via SSH key (~/.ssh/id_ed25519). Once `~/.ssh/config` is set up, plain `ssh harvey` etc. should just work — no `-p` flag, no full hostname.

**No passwords stored anywhere** — keys only. If a server stops accepting the key, re-run `ssh-copy-id` rather than falling back to passwords.
