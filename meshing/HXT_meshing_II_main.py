import gmsh
from pathlib import Path
from multiprocessing import Process
from HXT_type2_utils import HXT_mesh_II


TIMEOUT_SECONDS = 3600   # per-case mesh budget (presteps + production size/algo sweep + Netgen)

def whole_meshing_process(case_index: int, nproc: int = 20, smooth_mode: str = "taubin"):
    hxt_mesh_II = HXT_mesh_II(case_index = case_index, nproc = nproc)

    # Resume: skip if the quad mesh is already written for this case.
    if hxt_mesh_II.final_solid_msh_path.exists():
        print(f"[skip] case {case_index}: {hxt_mesh_II.final_solid_msh_path.name} already exists")
        return

    # #Step1. Get raw lipid.stl from (lipid - fc)
    HXT_mesh_II.get_lipid_stl(hxt_mesh_II.lipid_path, hxt_mesh_II.fc_path, hxt_mesh_II.lipid_stl_path)

    # #Step2. Create calcification from (lipid - fc_offset)
    HXT_mesh_II.create_cal_mesh(hxt_mesh_II.lipid_path, hxt_mesh_II.fc_offset_path, hxt_mesh_II.raw_cal_msh_path, hxt_mesh_II.nproc)
    hxt_mesh_II.Voronoi_tesselation_KDTREE(hxt_mesh_II.raw_cal_msh_path)

    # #Step3. From sharp vtu -> smoothed stl -> scale stl -> step
    hxt_mesh_II.smooth_vtu_to_stl(hxt_mesh_II.prog_cal_vtu_path, hxt_mesh_II.smooth_cal_stl_path, smooth_mode=smooth_mode)
    is_valid = HXT_mesh_II.does_ca_inside_lipid(hxt_mesh_II.lipid_stl_path, hxt_mesh_II.smooth_cal_stl_path)
    if is_valid:
        print(f"Case {case_index} is valid: The calcification is inside the lipid core")
    else:
        print(f"Case {case_index} is invalid: The calcification is not inside the lipid core")
        return
    HXT_mesh_II.scale_stl(hxt_mesh_II.smooth_cal_stl_path, hxt_mesh_II.scaled_smo_cal_stl_path, scale_factor = 10.0)
    HXT_mesh_II.stl_to_step(hxt_mesh_II.scaled_smo_cal_stl_path, hxt_mesh_II.smooth_cal_step_path, hxt_mesh_II.scripts_dir)

    #Step4. Now Start from beginning we have the Calcification step file now.
    # Production policy (simulation_goal.md): quadratic SecondOrderLinear=True; start 0.05
    # HXT; HXT fail -> Delaunay; >6M -> 0.055; STEP fail -> skip; bad quality -> 0.045 -> 0.04.
    stats = hxt_mesh_II.solid_gmshing_production(
        nproc=hxt_mesh_II.nproc,
        min_quality=0.0,
        max_tet=6_000_000,
        coarsen_size=0.055,
        second_order_linear=True,
        box_vout=0.2,
    )
    print(f"[MESH RESULT] case {case_index}: size={stats['mesh_size']} "
          f"algo={'HXT' if stats.get('algorithm_3d')==10 else 'Delaunay'} "
          f"n_tet={stats['n_tet']:,} nodes={stats['n_nodes']:,} "
          f"min_q={stats['min_quality']:.4f} mean_q={stats['mean_quality']:.4f} "
          f"neg={stats['n_negative']}")

    #Step4 (optional). msh to vtu for the paraview.
    #hxt_mesh_II.msh_to_vtu(hxt_mesh_II.final_solid_msh_path)

    #STep5. Remove the redundant files.
    hxt_mesh_II.remove_redundant_files()
    return


def run_case_with_logging(case_index: int, nproc: int, smooth_mode: str):
    try:
        whole_meshing_process(case_index, nproc, smooth_mode=smooth_mode)
    except Exception as e:
        print(f"Case {case_index} is failed: {e}")
        gmsh.finalize() if gmsh.is_initialized() else None
        with open("failed_cases.txt", "a") as f:
            f.write(f"--------------------------------\n")
            f.write(f"Case {case_index} is failed: {e}\n")


if __name__ == "__main__":

    import sys
    # Usage: python3 HXT_meshing_II_main.py <start> <end> [nproc]
    #   meshes cases [start, end) ; end is EXCLUSIVE.  e.g. 500 1000 20  -> cases 500..999
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    end   = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    nproc = int(sys.argv[3]) if len(sys.argv) > 3 else 20

    for i in range(start, end):
        try:
            print(f"--------------------------------")
            print(f"Case {i} is starting  (mesh, nproc={nproc})")
            print(f"--------------------------------")
            process = Process(target=run_case_with_logging, args=(i, nproc, "laplacian"))
            process.start()
            process.join(timeout=TIMEOUT_SECONDS)

            if process.is_alive():
                print(f"Case {i} timed out after {TIMEOUT_SECONDS} seconds")
                process.terminate()
                process.join()
                with open("failed_cases.txt", "a") as f:
                    f.write(f"--------------------------------\n")
                    f.write(f"Case {i} timed out after {TIMEOUT_SECONDS} seconds\n")
                continue

        except Exception as e:
            print(f"Case {i} is failed: {e}")
            with open("failed_cases.txt", "a") as f:
                f.write(f"--------------------------------\n")
                f.write(f"Case {i} is failed: {e}\n")
            continue
