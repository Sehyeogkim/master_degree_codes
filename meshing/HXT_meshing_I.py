"""
Solid meshing runner.

Purpose:
- Read geometry from geo_0303/case_xxx
- Generate solid mesh into solid_data/case_xxx

Current case range:
- range(500, 1000)
"""

import multiprocessing
import os
import shutil
import time
from pathlib import Path

import gmsh
import numpy as np
import pandas as pd

import utils.utils_geo_mesh.utils_gmsh as utils


def gmshing_solid(
    lumen_stp_path,
    solid_stp_path,
    lipid_stp_path,
    fc_stp_path,
    save_folder_path,
    nproc=5,
    terminal_display=True,
    mesh_size=0.04,
    lesion_length=1.0,
):
    start_time = time.time()

    gmsh.initialize()
    gmsh.model.add("Stenosis Model")

    if terminal_display:
        gmsh.option.setNumber("General.Terminal", 1)
    else:
        gmsh.option.setNumber("General.Verbosity", 0)

    # STEP1: lipid and fc intersection update
    lipid = gmsh.model.occ.importShapes(str(lipid_stp_path))[0]
    gmsh.model.occ.synchronize()

    fc = gmsh.model.occ.importShapes(str(fc_stp_path))[0]
    gmsh.model.occ.synchronize()

    gmsh.model.occ.intersect([lipid], [fc], removeObject=False, removeTool=True)
    gmsh.model.occ.synchronize()
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()

    # Keeps previous behavior from original script.
    lipid = (3, 3)

    volumes = gmsh.model.getEntities(3)
    if not (lipid and fc in volumes):
        raise RuntimeError("STEP1 failed: lipid/fc volumes not found")

    # STEP2: fc - lumen
    lumen = gmsh.model.occ.importShapes(str(lumen_stp_path))[0]
    gmsh.model.occ.synchronize()

    gmsh.model.occ.cut([fc], [lumen], removeObject=True, removeTool=False)
    gmsh.model.occ.synchronize()
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()

    volumes = gmsh.model.getEntities(3)
    if not (fc and lumen in volumes):
        raise RuntimeError("STEP2 failed: fc/lumen volumes not found")

    # STEP3: solid - (lipid + fc + lumen)
    solid = gmsh.model.occ.importShapes(str(solid_stp_path))[0]
    gmsh.model.occ.synchronize()

    gmsh.model.occ.cut([solid], [lipid, fc, lumen], removeObject=False, removeTool=False)
    gmsh.model.occ.synchronize()
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()

    volumes = set(gmsh.model.getEntities(3))
    solid_candidates = volumes - {lipid, fc, lumen}
    if len(solid_candidates) != 1:
        raise RuntimeError("STEP3 failed: unique solid volume not found")
    solid = solid_candidates.pop()

    # Physical groups (volumes)
    gmsh.model.addPhysicalGroup(3, [solid[1]], tag=1, name="solid")
    gmsh.model.addPhysicalGroup(3, [lipid[1]], tag=2, name="lipid")
    gmsh.model.addPhysicalGroup(3, [fc[1]], tag=3, name="fc")

    lumen_volume_tags = [lumen[1]]
    fc_surfaces = [abs(s[1]) for s in gmsh.model.getBoundary([fc], oriented=False)]
    solid_surfaces = [abs(s[1]) for s in gmsh.model.getBoundary([solid], oriented=False)]
    lipid_surfaces = [abs(s[1]) for s in gmsh.model.getBoundary([lipid], oriented=False)]

    wall_in_fc_tags = utils.find_wall_surfaces(fc_surfaces, lumen_volume_tags)
    wall_in_solid_tags = utils.find_wall_surfaces(solid_surfaces, lumen_volume_tags)
    lipid_in_fc_tags = list(set(lipid_surfaces) & set(fc_surfaces))

    gmsh.model.addPhysicalGroup(2, wall_in_solid_tags, tag=4, name="wall_in_solid")
    gmsh.model.addPhysicalGroup(2, wall_in_fc_tags, tag=5, name="wall_in_fc")
    gmsh.model.addPhysicalGroup(2, lipid_in_fc_tags, tag=7, name="lipid_in_fc")
    gmsh.model.occ.synchronize()

    # Two side surfaces from z-center proximity.
    all_solid_surfaces = gmsh.model.getBoundary([solid], oriented=False)
    surface_centers_z = np.array(
        [gmsh.model.occ.getCenterOfMass(s[0], abs(s[1]))[2] for s in all_solid_surfaces]
    )
    side1_index = int(np.argmin(np.abs(surface_centers_z - (-20.0))))
    side2_index = int(np.argmin(np.abs(surface_centers_z - 80.0)))
    side1_surface = all_solid_surfaces[side1_index]
    side2_surface = all_solid_surfaces[side2_index]

    gmsh.model.addPhysicalGroup(
        2,
        [abs(side1_surface[1]), abs(side2_surface[1])],
        tag=6,
        name="Two_sides",
    )
    gmsh.model.occ.synchronize()

    # Remove lumen volume from final mesh model.
    gmsh.model.occ.remove([lumen])
    gmsh.model.occ.synchronize()

    # Mesh options
    gmsh.option.setNumber("General.NumThreads", nproc)
    gmsh.option.setNumber("Mesh.MaxNumThreads2D", nproc)
    gmsh.option.setNumber("Mesh.MaxNumThreads3D", nproc)

    box_field = gmsh.model.mesh.field.add("Box")
    gmsh.model.mesh.field.setNumber(box_field, "Thickness", 3.0)
    gmsh.model.mesh.field.setNumber(box_field, "VIn", mesh_size)
    gmsh.model.mesh.field.setNumber(box_field, "VOut", 0.2)

    z_lesion = abs(lesion_length) / 2 * 10.0  # cm -> mm
    gmsh.model.mesh.field.setNumber(box_field, "XMin", -10.0)
    gmsh.model.mesh.field.setNumber(box_field, "XMax", 10.0)
    gmsh.model.mesh.field.setNumber(box_field, "YMin", -10.0)
    gmsh.model.mesh.field.setNumber(box_field, "YMax", 10.0)
    gmsh.model.mesh.field.setNumber(box_field, "ZMin", -z_lesion)
    gmsh.model.mesh.field.setNumber(box_field, "ZMax", z_lesion)
    gmsh.model.mesh.field.setAsBackgroundMesh(box_field)
    
    #critical points - Mesh algorithm and options.
    gmsh.option.setNumber("Mesh.ElementOrder", 2)
    gmsh.option.setNumber("Mesh.SecondOrderLinear", 0) #Solution 1 : 1 -> 0
    gmsh.option.setNumber("Mesh.Algorithm", 5)
    gmsh.option.setNumber("Mesh.Algorithm3D", 10)

    gmsh.model.mesh.generate(3)
    utils.check_mesh_quality(0)

    os.makedirs(save_folder_path, exist_ok=True)
    gmsh_save_path = os.path.join(save_folder_path, "solid_type_1_test.msh")
    gmsh.write(gmsh_save_path)
    gmsh.finalize()


    #save as vtu file
    save_vtu = True
    if save_vtu:
        msh_to_vtu(gmsh_save_path)


    utils.get_mesh_info(gmsh_save_path)
    print(f"[Done] mesh saved: {gmsh_save_path}")
    print(f"[Info] gmshing time: {time.time() - start_time:.2f}s")
    return gmsh_save_path


def msh_to_vtu(msh_path: Path):
    '''
    Convert msh file to vtu file.
    '''
    import meshio
    msh_path = str(msh_path)
    vtu_path = msh_path.replace('.msh', '.vtu')
    mesh = meshio.read(msh_path)
    mesh.points *= 0.1
    
    # VTU format doesn't support cell_sets, so remove them before writing
    # This prevents the IndexError that occurs during automatic conversion
    if mesh.cell_sets:
        mesh.cell_sets = {}
    
    meshio.write(vtu_path, mesh)
    print(f"Msh file saved to: {vtu_path}")
    return

def get_case_param_row(df: pd.DataFrame, case_id: int):
    for col in ["case_id", "case", "case_idx", "id"]:
        if col in df.columns:
            matched = df[df[col] == case_id]
            if not matched.empty:
                return matched.iloc[0]

    if case_id < 0 or case_id >= len(df):
        raise IndexError(
            f"case_id={case_id} is out of bounds for parameter csv with {len(df)} rows, "
            "and no matching case-id column was found."
        )
    return df.iloc[case_id]


def prepare_case_geometry(src_case_dir: Path, dst_case_dir: Path):
    dst_case_dir.mkdir(parents=True, exist_ok=True)

    required = ["lumen.stp", "solid.stp", "lipid.stp", "fc.stp"]
    copied = {}
    for name in required:
        src = src_case_dir / name
        if not src.exists():
            raise FileNotFoundError(f"Missing geometry file: {src}")
        dst = dst_case_dir / name
        shutil.copy2(src, dst)
        copied[name] = dst

    return copied


def main():

    current_dir = Path(__file__).resolve().parent
    geo_dir = current_dir / "geo_0303_500"
    solid_root_dir = current_dir / "solid_data"
    parameter_csv_path = current_dir / "pre_data" / "parameterB_new.csv"
    error_log_path = current_dir / "gmsh_errors_solid.txt"

    if not geo_dir.exists():
        raise FileNotFoundError(f"geo input directory not found: {geo_dir}")
    if not parameter_csv_path.exists():
        raise FileNotFoundError(f"parameter csv not found: {parameter_csv_path}")
    
    df = pd.read_csv(parameter_csv_path)
    solid_root_dir.mkdir(parents=True, exist_ok=True)

    timeout_seconds = 180 # 3 mins
    mesh_size = 0.05
    nproc = 30

    non_meshed = []

    for case_id in range(500, 501):
        case_name = f"case_{case_id}"
        src_case_dir = geo_dir / case_name
        dst_case_dir = solid_root_dir / case_name

        if not src_case_dir.exists():
            msg = f"[Skip] {case_name}: source directory missing"
            print(msg)
            non_meshed.append(case_id)
            with open(error_log_path, "a") as f:
                f.write(msg + "\n")
            continue

        # msh_path = dst_case_dir / "solid_type_1.msh"
        # if msh_path.exists():
        #     print(f"[Skip] {case_name}: mesh already exists")
        #     continue

        try:
            copied = prepare_case_geometry(src_case_dir, dst_case_dir)
            row = get_case_param_row(df, case_id)
            lesion_length = float(row["lesion_length"])

            print(f"\n[Run] {case_name}")
            start = time.time()

            mesh_process = multiprocessing.Process(
                target=gmshing_solid,
                args=(
                    copied["lumen.stp"],
                    copied["solid.stp"],
                    copied["lipid.stp"],
                    copied["fc.stp"],
                    dst_case_dir,
                    nproc,
                    True,
                    mesh_size,
                    lesion_length,
                ),
            )

            mesh_process.start()
            mesh_process.join(timeout=timeout_seconds)

            if mesh_process.is_alive():
                mesh_process.terminate()
                mesh_process.join()
                raise TimeoutError(f"Meshing timeout > {timeout_seconds}s")

            if mesh_process.exitcode != 0:
                raise RuntimeError(f"Meshing process failed with exit code {mesh_process.exitcode}")

            print(f"[Done] {case_name}: {time.time() - start:.2f}s")

        except Exception as e:
            non_meshed.append(case_id)
            err = f"Case {case_id}: {type(e).__name__} - {e}"
            print(f"[Fail] {err}")
            with open(error_log_path, "a") as f:
                f.write(err + "\n")

    print(f"\nNon-meshed cases: {non_meshed}")
    print(f"Total non-meshed cases: {len(non_meshed)}")


if __name__ == "__main__":
    main()
