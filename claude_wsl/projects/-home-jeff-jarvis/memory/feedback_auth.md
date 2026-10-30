---
name: Auth method for jarvis remotes
description: Use SSH keys instead of password files when connecting to user's remote servers
type: feedback
originSessionId: 09397dbb-5629-47d6-b63a-015b28e41479
---
For jarvis (and any other tool that connects to user's workstation1/workstation2/harvey), prefer SSH key auth over storing passwords in JSON/config files.

**Why:** User originally proposed putting passwords in a JSON file. When offered the trade-off, user picked SSH keys — they're safer (no plaintext secrets on disk) and remove the need for `sshpass`. Decided 2026-05-07.

**How to apply:** When setting up access to a new remote, walk the user through `ssh-keygen` + `ssh-copy-id` rather than asking for a password. If a server (e.g. HPC with mandatory MFA) blocks key auth, surface that explicitly and confirm the fallback with the user before storing any secret.
