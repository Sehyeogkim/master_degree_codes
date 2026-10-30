---
name: mesh-independence-workflow
description: End-to-end pipeline for the coronary mesh-independence study (mesh gen → transfer → svFSI steady fluid → convergence graphs)
metadata: 
  node_type: memory
  type: project
  originSessionId: 33e5ae63-e425-452d-807e-1e223f480745
---

Goal: run a steady fluid simulation on the ideal-coronary lumen at several mesh sizes and check
whether inlet/outlet flow & pressure converge within 500 steps (mesh-independence study). Spec/goal
lives at `1_Ideal_coronary/goal.md`. Mesh sizes used: 0.05, 0.02, 0.015, 0.01 (elem counts
199k / 811k / 1.24M / 3.17M).

Pipeline (per mesh size):
1. **Mesh gen on cvbml02** (`ssh ws2`): `lumen_simmetrix.py` (MESH_SIZES list) → Simmetrix
   `mesh_generator` → `63_mesh_independent_test/1_Ideal_coronary/mesh/<size>/lumen/mesh-complete/`
   ({mesh-complete.mesh.vtu, mesh-complete.exterior.vtp, walls_combined.vtp, mesh-surfaces/{inlet,outlet,wall}.vtp}).
   Verify inlet/outlet/wall by point-centroid: inlet z=-2.0, outlet z=+8.0, wall between — stable across sizes.
2. **Transfer cvbml02→harvey**, flattening the `lumen/mesh-complete/` wrapper:
   `ssh ws2 'tar -C .../mesh/<size>/lumen/mesh-complete -cf - .' | ssh harvey 'tar -C .../mesh/<size> -xf -'`
   (pipes through local; ws2↔harvey direct SSH not assumed). Target on harvey:
   `71_mesh_indepedent_test_snap_shot/1_ideal_coronary/mesh/<size>/` (flat: vtu + mesh-surfaces/).
3. **Convert meshes to binary** — see [[svfsi-mesh-and-bc-gotchas]] (required before svFSI).
4. **Per-size svFSI input**: copy `fluid.inp` → `fluid_<size>.inp`, set `Save results in folder:
   ./mesh/<size>/fluid_steady`, mesh paths `./mesh/<size>/...`. Copy `fluid.sh` → `fluid_<size>.sh`
   (job name, `-o fluid_<size>.o%j`, explicit `--partition=` + `--nodelist=`, run `fluid_<size>.inp`).
   Run from project root so `./mesh/<size>/...` resolves.
5. **Submit one-by-one** via Slurm `sbatch`; chain with `--dependency=afterany:<prev>` to serialize.
   Check nodes first with `pestat` — see [[compute-servers-and-simmetrix-license]].
6. **Convergence graphs**: read `mesh/<size>/fluid_steady/B_NS_Velocity_flux.txt` &
   `B_NS_Pressure_average.txt`, plot inlet/outlet flow & pressure vs timestep. Steady = curves
   plateau (0.05 plateaued by ~step 30). If diverged (NaN / |v|>1e6) write `mesh/<size>/not_converged.txt`.

Plot/inspect helper scripts kept in session scratchpad: `plot_conv.py`, `to_binary.py`, `inspect_vtu.py`,
`check_surfaces.py`, `count_mesh.py`. Python with vtk+numpy+matplotlib: `/home/jeff/miniconda3/bin/python3`
on both ws2 and harvey (system python3 lacks them).
