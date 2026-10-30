---
name: compute-servers-and-simmetrix-license
description: "Compute servers (ws1/ws2/harvey SSH aliases, roles), Simmetrix license facts, Slurm/pestat usage"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 33e5ae63-e425-452d-807e-1e223f480745
---

SSH aliases (in `~/.ssh/config`, key `~/.ssh/id_ed25519`; use `ssh <alias> "<cmd>"` one-shot, no
interactive sessions). Also documented in `.claude/commands/ssh.md`:
- `ws1` = cvbml01.kaist.ac.kr — also the **Simmetrix RLM license server** (port 2800).
- `ws2` = cvbml02.kaist.ac.kr — **meshing** workstation (Simmetrix `mesh_generator`).
- `harvey` = harvey.kaist.ac.kr:10022 — **Slurm cluster** for svFSI simulations.

Simmetrix on ws2:
- binary `/opt/cvbml/repos/SyntheticTreeGenerator/build/apps/MeshGenerator/mesh_generator`
- license `/opt/cvbml/repos/SyntheticTreeGenerator/apps/MeshGenerator/floating.lic`
  (set env `SimModSuite_licenseFile`). License is a **single concurrent seat** — two meshings at once
  fail with `All licenses in use (-22)`. (`/opt/cvbml` does NOT exist on the local box — must run on ws2.)
  License file shows expiry `8-jun-2026` but checkout still worked on 2026-06-24; expiry text isn't a hard cutoff there.

harvey Slurm:
- Check nodes with **`pestat`** before submitting; `sinfo`/`squeue` for partitions/queue.
- Partitions overlap nodes: `defaults` = harvey02–07; `harvey02` = harvey02–04; `harvey05` = harvey05–07;
  `harvey01` = harvey01 (only 72 cores). Compute nodes harvey02–07 have 96 cores; harvey05/06 have 386GB RAM.
- User wants sbatch scripts to **explicitly list both** `#SBATCH --partition=<p>` and `#SBATCH --nodelist=<n>`.
- svFSI jobs: 1 node, 96 MPI tasks (`-N 1 -n 96 --ntasks-per-node=96`), `mpirun -np $SLURM_NTASKS svFSI fluid.inp`.
- Serialize jobs with `sbatch --dependency=afterany:<jobid>`.

See [[mesh-independence-workflow]] and [[slurm-parallelism-preference]].
