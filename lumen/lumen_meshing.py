"""
Minimal lumen meshing runner.

Purpose:
- Iterate cases under geo_0303/case_xxx
- Run fluid domain meshing for each case
- Generate per-case tree.dat and xyzts.dat

Outputs per case:
- fluid_data/case_xxx/meshing/mesh-complete/...
- fluid_data/case_xxx/tree.dat
- fluid_data/case_xxx/xyzts.dat
"""

import json
import shutil
from pathlib import Path

from lumen_codes.cad_meshing import VesselCADModel, LumenMeshing
import utils.utils_lumen.runner as runner


class LumenMeshingCase:
    def __init__(
        self,
        case_id: int,
        exec_dir: Path,
        parameter_csv_path: Path,
        config_path: Path,
    ):
        self.case_id = case_id
        self.exec_dir = Path(exec_dir)
        self.parameter_csv_path = Path(parameter_csv_path)

        with open(config_path, "r") as f:
            self.config = json.load(f)

        self.meshing_dir = self.exec_dir / "meshing"
        self.mesh_complete_dir = self.meshing_dir / "mesh-complete"
        self.tree_path = self.exec_dir / "tree.dat"
        self.xyzt_path = self.exec_dir / "xyzts.dat"

        self.meshing_dir.mkdir(parents=True, exist_ok=True)

    def run(self, stp_path: Path, grid_size: float = 0.015, number_of_boundary_layers: int = 3):
        stp_src = Path(stp_path)
        if not stp_src.exists():
            raise FileNotFoundError(f"Input STP not found: {stp_src}")

        # Keep all meshing artifacts inside fluid_data/case_xxx/meshing
        stp_dst = self.meshing_dir / stp_src.name
        shutil.copy2(stp_src, stp_dst)

        vtk_path = LumenMeshing._stp_to_vtk(str(stp_dst))
        vtp_path = LumenMeshing._vtk_to_vtp(vtk_path)

        runner.run_simmetrix_license(license_path=self.config["simmetrix"]["license"])
        runner.run_simmetrix_meshing(
            vtp_path=vtp_path,
            exe_dir=self.meshing_dir,
            simmetrix_path=self.config["simmetrix"]["meshing"],
            grid_size=grid_size,
            boundary_layer_thickness=0.005,
            number_of_boundary_layers=number_of_boundary_layers,
        )

        LumenMeshing._assemble_mesh_tree(self.meshing_dir)

        cad = VesselCADModel.CAD_instance_from_idx(self.case_id, self.parameter_csv_path)
        cad.tree_xyzts_generator(
            tree_path=self.tree_path,
            xyzt_path=self.xyzt_path,
            num_points=50,
        )


def main():
    current_dir = Path(__file__).resolve().parent
    pre_data_dir = current_dir / "pre_data"
    geo_dir = current_dir / "geo_0303"
    fluid_root_dir = current_dir / "fluid_data_failed"

    parameter_csv_path = pre_data_dir / "parameter.csv"
    config_path = pre_data_dir / "solver_path.json"

    if not geo_dir.exists():
        raise FileNotFoundError(f"geo input directory not found: {geo_dir}")
    if not parameter_csv_path.exists():
        raise FileNotFoundError(f"parameter csv not found: {parameter_csv_path}")
    if not config_path.exists():
        raise FileNotFoundError(f"solver config not found: {config_path}")

    fluid_root_dir.mkdir(parents=True, exist_ok=True)

    failed_cases = []

    new_cases = [208, 209, 210, 211, 212, 213, 214, 215, 216, 217,
                 218, 219, 220, 221, 222, 223, 224, 225, 226, 227,
                 228, 229, 230, 231, 232, 233, 234, 235, 236, 237,
                 238, 239, 240, 241, 242, 243, 244, 245, 246, 247,
                 248, 202, 206, 438]
    for case_id in new_cases:
        case_dir = geo_dir / f"case_{case_id}"
        if not case_dir.exists():
            print(f"[Skip] case_{case_id}: case directory not found")
            failed_cases.append(case_id)
            continue

        stp_path = case_dir / "lumen.stp"

        if not stp_path.exists():
            print(f"[Skip] case_{case_id}: lumen.stp not found")
            failed_cases.append(case_id)
            continue

        out_dir = fluid_root_dir / case_dir.name
        runner_case = LumenMeshingCase(
            case_id=case_id,
            exec_dir=out_dir,
            parameter_csv_path=parameter_csv_path,
            config_path=config_path,
        )

        try:
            runner_case.run(stp_path=stp_path)
            print(f"[Done] {case_dir.name}: meshing + tree.dat + xyzts.dat")
        except Exception as e:
            print(f"[Fail] {case_dir.name}: {e}")
            failed_cases.append(case_id)

    with open(current_dir / "lumen_failed_meshing.txt", "w") as f:
        f.write(str(failed_cases))


if __name__ == "__main__":
    main()
