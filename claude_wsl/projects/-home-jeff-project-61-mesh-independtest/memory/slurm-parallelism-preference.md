---
name: slurm-parallelism-preference
description: How many Slurm jobs to run concurrently for the mesh-independence sweep
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 33e5ae63-e425-452d-807e-1e223f480745
---

User initially said run the mesh sizes "one by one" (strictly sequential), then relaxed it: **if nodes
are available, up to 2 Slurm jobs may run in parallel** ("next case at most 2").

**Why:** the finer meshes take a long time (0.01 ≈ 3.17M elements, ~hours), and harvey usually has
several idle nodes — capping at 2 concurrent cuts wall-clock without hogging the cluster.

**How to apply:** schedule the sweep so at most 2 svFSI jobs run at once, each on its own node
(distinct `--nodelist`). Use `--dependency=afterany:<jobid>` to gate the 3rd/4th so concurrency never
exceeds 2. Check `pestat` for idle nodes first. See [[compute-servers-and-simmetrix-license]].
