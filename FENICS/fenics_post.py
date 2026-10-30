"""
Post-processing script to extract displacement and von Mises stress
for cells with a specific cell tag (cell_tag = 3).
"""

import numpy as np
from dolfinx import mesh, fem
from dolfinx.io import XDMFFile, gmshio
from mpi4py import MPI
from pathlib import Path
import warnings

# Try to import h5py, but make it optional
try:
    import h5py
    HAS_H5PY = True
except ImportError:
    HAS_H5PY = False
    if MPI.COMM_WORLD.Get_rank() == 0:
        print("[W] h5py not available. Will try alternative method.")

warnings.filterwarnings("ignore", category=UserWarning)


def extract_by_cell_tag(
    gmsh_path: Path,
    displacement_xdmf: Path,
    stress_xdmf: Path,
    output_dir: Path,
    target_tag: int = 3
):
    """
    Extract displacement and stress data for cells with a specific tag.
    
    Parameters:
    -----------
    gmsh_path : Path
        Path to the GMSH mesh file
    displacement_xdmf : Path
        Path to displacement XDMF file
    stress_xdmf : Path
        Path to von Mises stress XDMF file
    output_dir : Path
        Directory to save filtered output files
    target_tag : int
        Cell tag to extract (default: 3)
    """
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    
    if rank == 0:
        print(f"[I] Starting post-processing for cell_tag = {target_tag}")
        print(f"[I] Reading mesh from: {gmsh_path}")
    
    # 1. Read mesh with cell tags
    domain, cell_tags, facet_tags = gmshio.read_from_msh(
        str(gmsh_path), comm, 0, gdim=3
    )
    
    # Scale mesh coordinates by 0.1 (same as in main script)
    domain.geometry.x[:] *= 0.1
    
    if rank == 0:
        print(f"[I] Mesh loaded: {domain.topology.index_map(3).size_global} cells")
    
    # 2. Find cells with target tag
    tdim = domain.topology.dim
    cell_values = cell_tags.values
    cell_indices = cell_tags.indices
    
    # Find cells with target tag
    mask = (cell_values == target_tag)
    target_cell_local_indices = cell_indices[mask]
    
    if rank == 0:
        n_target_cells = np.sum(mask)
        print(f"[I] Found {n_target_cells} cells with tag = {target_tag}")
    
    # 4. Read displacement and stress from HDF5 files (via XDMF)
    if rank == 0:
        print(f"[I] Reading displacement from: {displacement_xdmf}")
    
    # Read displacement - read directly from HDF5 file
    gdim = domain.geometry.dim
    V_displacement = fem.functionspace(domain, ("Lagrange", 1, (gdim,)))
    u_full = fem.Function(V_displacement)
    
    # Read displacement data from HDF5 file
    h5_path = displacement_xdmf.parent / "displacement.h5"
    all_data = None
    
    if HAS_H5PY:
        # Read on rank 0 and broadcast (simpler approach)
        if rank == 0:
            try:
                with h5py.File(h5_path, "r") as h5f:
                    if "/Function/Displacement/0" in h5f:
                        all_data = h5f["/Function/Displacement/0"][:]
            except Exception as e:
                if rank == 0:
                    print(f"[W] Failed to read from HDF5: {e}")
    
    # Alternative: Try using ADIOS2 if available
    if all_data is None:
        try:
            from dolfinx.io import ADIOS2
            # Try reading with ADIOS2
            if rank == 0:
                print("[I] Attempting to read with ADIOS2...")
            # ADIOS2 reading would go here
        except ImportError:
            pass
    
    # Set function values if we have data
    if all_data is not None:
        if comm.size == 1:
            # Serial: directly assign
            u_full.x.array[:] = all_data.flatten()[:u_full.x.array.size]
        else:
            # Parallel: need to map global to local indices
            if rank == 0:
                flat_data = all_data.flatten()
                u_full.x.array[:] = flat_data[:u_full.x.array.size]
            # Broadcast to other ranks (simplified - may need proper DOF mapping)
            comm.Bcast(u_full.x.array, root=0)
    else:
        if rank == 0:
            print("[E] Could not read displacement data. Please ensure h5py is installed.")
        raise RuntimeError("Failed to read displacement data from HDF5 file")
    
    if rank == 0:
        print(f"[I] Reading stress from: {stress_xdmf}")
    
    # Read stress (DG0 - cell-wise constant) - read directly from HDF5
    V_stress = fem.functionspace(domain, ("DG", 0))
    stress_full = fem.Function(V_stress)
    
    # Read stress data from HDF5 file
    h5_path = stress_xdmf.parent / "EQV_stress.h5"
    all_data = None
    
    if HAS_H5PY:
        # Read on rank 0
        if rank == 0:
            try:
                with h5py.File(h5_path, "r") as h5f:
                    if "/Function/Von_Mises_Stress/0" in h5f:
                        all_data = h5f["/Function/Von_Mises_Stress/0"][:]
            except Exception as e:
                if rank == 0:
                    print(f"[W] Failed to read stress from HDF5: {e}")
    
    # Set stress values if we have data
    if all_data is not None:
        if comm.size == 1:
            stress_full.x.array[:] = all_data.flatten()[:stress_full.x.array.size]
        else:
            # Parallel: map to local cell indices
            if rank == 0:
                flat_data = all_data.flatten()
                stress_full.x.array[:] = flat_data[:stress_full.x.array.size]
            # Broadcast to other ranks
            comm.Bcast(stress_full.x.array, root=0)
    else:
        if rank == 0:
            print("[E] Could not read stress data. Please ensure h5py is installed.")
        raise RuntimeError("Failed to read stress data from HDF5 file")
    
    # 5. Create filtered functions for cells with target tag
    if rank == 0:
        print(f"[I] Creating filtered functions for tag = {target_tag}...")
    
    # Create filtered stress function (set to zero outside selected cells)
    stress_filtered = fem.Function(V_stress)
    stress_filtered.x.array[:] = 0.0  # Initialize to zero
    stress_filtered.x.array[target_cell_local_indices] = stress_full.x.array[target_cell_local_indices]
    stress_filtered.name = "Von_Mises_Stress"
    
    # For displacement, copy all values (nodal data)
    # The visualization will show displacement for all nodes
    u_filtered = fem.Function(V_displacement)
    u_filtered.x.array[:] = u_full.x.array[:]
    u_filtered.name = "Displacement"
    
    # Try to create a proper submesh if possible
    use_submesh = False
    try:
        # Try using create_submesh if available
        from dolfinx.mesh import create_submesh
        
        if rank == 0:
            print(f"[I] Attempting to create submesh from {len(target_cell_local_indices)} cells...")
        
        subdomain, entity_map, vertex_map, geom_map = create_submesh(
            domain, tdim, target_cell_local_indices
        )
        
        # Create function spaces on submesh
        V_sub_displacement = fem.functionspace(subdomain, ("Lagrange", 1, (gdim,)))
        V_sub_stress = fem.functionspace(subdomain, ("DG", 0))
        
        # Interpolate to submesh
        u_sub = fem.Function(V_sub_displacement)
        u_sub.interpolate(u_full)
        u_sub.name = "Displacement"
        
        stress_sub = fem.Function(V_sub_stress)
        stress_sub.interpolate(stress_full)
        stress_sub.name = "Von_Mises_Stress"
        
        use_submesh = True
        if rank == 0:
            print(f"[I] Submesh created successfully with {subdomain.topology.index_map(3).size_global} cells")
            
    except (ImportError, AttributeError, RuntimeError, TypeError) as e:
        # create_submesh not available or failed, use filtered approach
        use_submesh = False
        if rank == 0:
            print(f"[I] Submesh creation not available/failed: {type(e).__name__}")
            print(f"[I] Using filtered functions (stress=0 outside selected cells)")
    
    # 6. Write filtered data to XDMF files
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if use_submesh:
        # Write using submesh
        if rank == 0:
            print(f"[I] Writing filtered displacement to: {output_dir / 'displacement_tag3.xdmf'}")
        
        # Try writing displacement - handle degree mismatch
        try:
            with XDMFFile(comm, output_dir / "displacement_tag3.xdmf", "w") as xdmf:
                xdmf.write_mesh(subdomain)
                xdmf.write_function(u_sub)
        except RuntimeError as e:
            if "degree" in str(e).lower():
                # Mesh geometry degree doesn't match function degree
                # Interpolate to quadratic
                if rank == 0:
                    print(f"[I] Mesh geometry degree mismatch. Interpolating to quadratic...")
                V_sub_out = fem.functionspace(subdomain, ("Lagrange", 2, (gdim,)))
                u_sub_out = fem.Function(V_sub_out)
                u_sub_out.interpolate(u_sub)
                u_sub_out.name = "Displacement"
                with XDMFFile(comm, output_dir / "displacement_tag3.xdmf", "w") as xdmf:
                    xdmf.write_mesh(subdomain)
                    xdmf.write_function(u_sub_out)
            else:
                raise
        
        if rank == 0:
            print(f"[I] Writing filtered stress to: {output_dir / 'EQV_stress_tag3.xdmf'}")
        
        # Stress is DG0, should work fine
        with XDMFFile(comm, output_dir / "EQV_stress_tag3.xdmf", "w") as xdmf:
            xdmf.write_mesh(subdomain)
            xdmf.write_function(stress_sub)
    else:
        # Write filtered functions (stress will be zero outside selected cells)
        if rank == 0:
            print(f"[I] Writing filtered displacement to: {output_dir / 'displacement_tag3.xdmf'}")
        
        with XDMFFile(comm, output_dir / "displacement_tag3.xdmf", "w") as xdmf:
            xdmf.write_mesh(domain)
            xdmf.write_function(u_filtered)
        
        if rank == 0:
            print(f"[I] Writing filtered stress to: {output_dir / 'EQV_stress_tag3.xdmf'}")
        
        with XDMFFile(comm, output_dir / "EQV_stress_tag3.xdmf", "w") as xdmf:
            xdmf.write_mesh(domain)
            xdmf.write_function(stress_filtered)
    
    if rank == 0:
        print(f"[I] Post-processing complete!")
        print(f"[I] Output files saved to: {output_dir}")
        print(f"    - displacement_tag3.xdmf")
        print(f"    - EQV_stress_tag3.xdmf")


if __name__ == "__main__":
    current_dir = Path(__file__).parent
    working_dir = current_dir / "solid_data"
    
    # Input files
    gmsh_path = working_dir / "total_solid_type2.msh"
    displacement_xdmf = working_dir / "xdmf_out" / "displacement.xdmf"
    stress_xdmf = working_dir / "xdmf_out" / "EQV_stress.xdmf"
    
    # Output directory
    output_dir = working_dir / "xdmf_out" / "tag3_extracted"
    
    # Extract data for cell_tag = 3
    extract_by_cell_tag(
        gmsh_path=gmsh_path,
        displacement_xdmf=displacement_xdmf,
        stress_xdmf=stress_xdmf,
        output_dir=output_dir,
        target_tag=3
    )

