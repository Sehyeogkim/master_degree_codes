---
name: lap-lowonly-hyperemia-54analysis
description: "54_analysis LAP solid ANSYS on ws1 (cases 0-499) — LOW-only even/odd batch, and the resting-vs-hyperemia PSS sensitivity finding"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4c5c939f-6472-457a-bbdc-757c03d64685
  modified: 2026-07-28T13:11:32.342Z
---

54_analysis **LAP** solid ANSYS (fibrous-cap PSS) on **ws1 (cvbml01)**, cases **0-499**, started 2026-07-28. Distinct from [[lap-cp-sim-54analysis]] (that = cvbml02, cases 500-999, LAP→CP sequential). Reuses 65's `pymapdl_simulation_ver5_fibrous.py` class (PCG, FC mat_id=3, ×0.1 scale, surface tags 4/5/6, material.json vessel1/lipid2/fc3/cal8), only paths + concurrency-scope changed. Scripts on ws1 `~/project/54_analysis/`: `pymapdl_sim_LAP_0728.py`, `pymapdl_sim_CP_0728.py`, driver `driver_low.sh`. mesh `LAP_mesh/solid_LAP_{i}.msh` (flat), out `ansys_LAP_0728/case_{i}/FC_case_{i}_{peak,low}.vtk`. param `pre_data/parameter_0728.csv` (row idx=case id), `pre_data/material.json`. CP mesh `CP_mesh/solid_CP_{i}.msh` adds ca(mat8) domain but still extract FC(mat3).

**wall BC = RESTING (non-hyperemia).** `post_data/wall_no_hyperemia/{peak,low}/wall_{ph}_case_{i}.csv` (7-col x,y,z,Tx,Ty,Tz,**Pressure=col7**), produced live on harvey by [[steady3d-nohyperemia-54analysis]]. **ws1 has NO route to harvey** → relay `harvey → local WSL → ws1` every 60s via local `scratchpad/wall_relay.sh` (rsync no --delete, accumulate). /MAP reads col7 pressure.

**KEY SCIENTIFIC FINDING (resting vs hyperemia, 41 cases, mean |traction|=√(Tx²+Ty²+Tz²)=PSS-driving load):**
- **peak (systolic): +1.9%** (0.8–4.7%) → PSS essentially **BC-insensitive / defensible**.
- **low (diastolic): resting +39%** higher than hyperemia (14–82%).
- **ΔPSS driver (peak−low): −22%** (5–42%) → ΔPSS **IS BC-sensitive**.
- Mechanism (confirmed from 1D json Pin/Pout): inlet pressure waveform **identical** (systolic & diastolic Pin same); hyperemia only cuts outlet R (~2.4× sys, ~3.7× dia) → higher flow → big diastolic **distal Pout drop** (case0: resting Pout_dia 114k vs hyper 74k). Systolic ≈ aortic SBP in both. For no_hyp, |traction| ≈ Pressure col7 (213764≈213765).
- **Old paper PSS** `past_results/PSS_result_expB_type2.csv` (May) = **hyperemia + traction-VECTOR method** (`pymapdl_simulation_ver1/ver2.py` INPUT `apply_traction_{bc}.txt`, SFE PRES 3-comp; wall_expB_new is 6-col Tx,Ty,Tz, NO pressure). `ver5_fibrous` = scalar /MAP col4. Current = scalar /MAP col7. scalar≈traction-vector (viscous shear ≪ pressure), so method diff negligible for PSS; real diff is BC state.

**Decision (user):** compute **LOW-only** under resting (`FC_case_{i}_low.vtk`); reuse existing hyperemia peak PSS (≈resting). Corrected ΔPSS ≈ peak_hyper − low_resting.

**Run design — 2 cases at once via parity split, nproc 20 each:**
`python pymapdl_sim_LAP_0728.py <start> 500 20 --step 2 --port <p> --suffix <S>`; driver `driver_low.sh <LABEL> <pyargs>` re-loops (resumable, skip if low vtk exists; skip no-mesh; wait if low csv absent) with 120s gap.
- even: `driver_low.sh LAP_even pymapdl_sim_LAP_0728.py 0 500 20 --step 2 --port 50052 --suffix E`
- odd:  `driver_low.sh LAP_odd  pymapdl_sim_LAP_0728.py 1 500 20 --step 2 --port 50072 --suffix O`
`--suffix` → launch jobname `-j LAP{E,O}_{i}_low` at EVERY ANSYS rank level (bash/mpirun/ansysdis251/ansys.e) → **scoped kill `pkill -9 -f '-j LAP{E,O}_'` is unique per process** (never cross-kills the sibling, the Workbench GUI `runwb2`, or the gmsh meshing jobs). Distinct ports avoid gRPC 50052 collision (both defaulting to 50052 was why concurrent LAP+CP earlier failed with "Connection refused"). **pkill self-match gotcha**: a pattern that appears in the ssh shell's own cmdline kills the shell (exit 255 / silent) — use bracket trick `'[p]ymapdl_sim_LAP'`, `'[-]j LAP'`, or kill by PID. `pgrep -c -f PAT` over ssh also self-counts (+1).

**Per-case timing (case 4, ~1.65M elem, PCG tol 1e-5/1e-6):** msh→cdb ~16s, launch ~7s, /MAP prep ~25-30s, **solve ~110-114s (dominant)**, FC extract (`_save_fc_results_rst` Python FC-only element-avg) ~40-76s. **/MAP is NOT the bottleneck — solve+extract dominate.** Optimizations tested: removing PLGEOM/PLMAP plots = −5.7s, bit-identical results (kept). tol 1e-5 vs 1e-6 negligible (reverted to 1e-6 for consistency with existing done vtk). **SFE-direct (`pymapdl_simulation_ver2.py` + `utils_bc.Apply_Traction`) is SLOWER not faster** (57s prep: 62k SFE-text lines via mapdl.input + Python conn loop) AND gave 100× wrong stress on our type1 mesh (its KEYOPT(7,2,1)+ESYS-local setup mis-applies scalar PRES) — do NOT use. Note: Apply_Traction applies `||traction||` as scalar normal PRES (LKEY1), same physics as /MAP col7.

**FAILURE cleanup:** production `except:` now calls `wipe_out_useless_data` (was missing → failed/interrupted cases hoarded GBs). wipe = WHITELIST (keeps .vtk/.msh/.json/_0.err, removes .rst/.db/.cdb/.DSP/.full/BeforeMapping.db). Killing an ANSYS mid-solve auto-frees its open-but-unlinked out-of-core temp (.DSP/.full) — case 77 released 130GB on pkill. My-restart-interrupted cases (vtk written, wipe not reached) leave scratch → periodic safe sweep: for case dirs not currently-solving & newest file >3min old, rm non-whitelist.

**DISK/CPU are the real constraints (2026-07-28):** ws1 = AMD Threadripper PRO 5995WX = **64 PHYSICAL cores / 128 logical (SMT)** — FEA gets ~1.2× not 2× from SMT, so effective ~64 cores. Shared 3.6T `/` is **95-99% full**; top users: **jan 1.5T**, jeff 620G, chan 310G. **chan runs ~76 tetgen/python procs = ~76 cores** → my ANSYS starved (contended). One pathological case (77) wrote **130GB** solver scratch → nearly filled disk. Mitigations applied: (1) freed 87G by `pigz`-compressing `65_final_0723` (134G→47G tar.gz, verified, original removed → `65_final_0723.tar.gz`); (2) dropped to **1-way** (`driver_low.sh LAP_solo ... --step 1 --port 50052 --suffix S`) so peak scratch ≤130GB fits free space. Only `pigz`/`zstd`/`xz` live in `/home/jeff/miniconda3/bin/` (not /usr/bin). **When chan finishes** (background monitor watches, alerts when chan cores <8): go in-core solve (`BCSOPTION,,INCORE`, 440G RAM free — kills the 130GB disk blowup) + 2-way/4-way. ws1↔harvey no route; local WSL relays wall csv 60s.
