---
name: Harvey HPC cluster facts
description: Connection and scheduler info for the harvey HPC cluster
type: project
originSessionId: 09397dbb-5629-47d6-b63a-015b28e41479
---
Harvey HPC cluster:
- Hostname: `harvey.kaist.ac.kr` (KAIST university cluster)
- Scheduler: **Slurm** (inferred from a `slurm_smp_11161_392.out` file the user was editing on 2026-05-07)
- User accesses it via Cursor IDE Remote-SSH as well as direct ssh

**Why:** Spotted in win-status output — user had a Slurm output file open in Cursor with `[SSH: harvey.kaist.ac.kr]` in the title.

**How to apply:** When polling harvey, use Slurm commands: `squeue -u <user>`, `sacct`, `sinfo`. Job output files follow pattern `slurm_smp_<jobid>_<idx>.out`. Confirm with user before assuming this is current — info inferred, not directly stated.
