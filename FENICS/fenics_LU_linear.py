import json
from typing import Dict, Any
import numpy as np
import ufl
from dolfinx import mesh, fem, default_scalar_type
from dolfinx.fem import Function, locate_dofs_topological, functionspace
from dolfinx.fem.petsc import LinearProblem
from dolfinx.io import XDMFFile, gmshio
from mpi4py import MPI
from scipy.spatial import cKDTree
import warnings
from pathlib import Path
import pandas as pd

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning, module="ufl")



def main(gmsh_path: Path, materials_path: Path, csv_path: Path, save_dir: Path):

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    print("[rank", comm.rank, "] size =", comm.size) if rank == 0 else None

    import time
    start = time.time()
    
    # 1. read gmsh -> domain, cell_tags, facet_Tags
    domain, cell_tags, facet_tags = gmshio.read_from_msh(str(gmsh_path), comm, 0, gdim=3)
    

    # Scale mesh coordinates by 0.1
    domain.geometry.x[:] *= 0.1
    if rank == 0:
        print(f"[I] Mesh loading completed in {time.time() - start:.2f} s")
    
    
    start = time.time()
    # ---------------- Material fields (DG0) ----------------
    V0 = functionspace(domain, ("DG", 0))
    E_fun = Function(V0)
    nu_fun = Function(V0)
    #rho_fun = Function(V0)

    # Load material map from JSON
    with open(materials_path, "r") as f:
        mat_map: Dict[str, Dict[str, Any]] = json.load(f)

    cell_indices = cell_tags.indices
    cell_values = cell_tags.values
    n_cells = len(cell_values)
    
    E_vals = np.zeros(n_cells, dtype=np.float64)
    nu_vals = np.zeros(n_cells, dtype=np.float64)

    for i, tag in enumerate(cell_values):
        key = str(int(tag))
        props = mat_map.get(key)
        E_vals[i] = float(props["E"])
        nu_vals[i] = float(props["v"])

    E_fun.x.array[cell_indices] = E_vals
    nu_fun.x.array[cell_indices] = nu_vals
    

    print(f"complete material fields {time.time() - start:.2f} s") if rank == 0 else None
    start = time.time()


    # ---------------- Spaces, BCs, and traction ----------------
    # Vector function space for displacement
    gdim = domain.geometry.dim
    V = fem.functionspace(domain, ("Lagrange", 1, (gdim,)))
    u = ufl.TrialFunction(V)
    v = ufl.TestFunction(V)

    # Boundary conditions(unit: cm) (should be checked. by max and min z cooridnate on every points.)
    def side1(x):
        return np.isclose(x[2], -2.0)
    def side2(x):
        return np.isclose(x[2], 8.0)


    fdim = domain.topology.dim - 1
    boundary_facets1 = mesh.locate_entities_boundary(domain, fdim, side1)
    boundary_facets2 = mesh.locate_entities_boundary(domain, fdim, side2)
    boundary_facets = np.concatenate([boundary_facets1, boundary_facets2])
    u_D = np.array([0.0, 0.0, 0.0], dtype = default_scalar_type)
    dofs = locate_dofs_topological(V, fdim, boundary_facets)
    bcs = [fem.dirichletbc(u_D, dofs, V)]


    ####################################################
    ########### Apply Total traction ####################
    ####################################################
    '''
    1. read the csv file.
    2. Make a interpolate function w/ KDTREE.
    3. Interpolate the traction data to the boundary facets.
    '''

    traction_df = pd.read_csv(csv_path)
    csv_points = traction_df[['x', 'y', 'z']].values
    csv_Tx = traction_df['Tx'].values
    csv_Ty = traction_df['Ty'].values
    csv_Tz = traction_df['Tz'].values

    # Build KDTree once (reusable)
    kdtree = cKDTree(csv_points)

    def interpolate_traction(x):
        '''
        closest point interpolation.
        '''
        # x has shape (gdim, npoints); transpose for (npoints, 3)
        points = x.T  # shape: (npoints, 3)
        distances, indices = kdtree.query(points, k=1)
        Tx = csv_Tx[indices]
        Ty = csv_Ty[indices]
        Tz = csv_Tz[indices]
        return np.vstack([Tx, Ty, Tz])

    if rank == 0:
        print("[I] Creating traction using expression approach...")
    
    # Expression approach: Python function is directly interpolated
    # interpolate() is called at evaluation points
    # This is similar to the Expression approach: evaluate only when needed
    traction_coeff = fem.Function(V)
    traction_coeff.interpolate(interpolate_traction)
    traction_coeff.name = "Traction"
    
    if rank == 0:
        print("[I] Traction using expression approach created successfully")

    # ---------------- Define weak form ----------------
    if rank == 0:
        print("\n[I] Defining weak form...")
    
    # Strain tensor (symmetric gradient)
    def epsilon(u):
        return ufl.sym(ufl.grad(u))
    
    # Stress tensor (Cauchy stress for linear elasticity)
    def sigma(u):
        lmbda = E_fun * nu_fun / ((1 + nu_fun) * (1 - 2 * nu_fun))
        mu = E_fun / (2 * (1 + nu_fun))
        return lmbda * ufl.tr(epsilon(u)) * ufl.Identity(len(u)) + 2 * mu * epsilon(u)
    
    # Bilinear form (stiffness)
    a = ufl.inner(sigma(u), epsilon(v)) * ufl.dx
    
    # Linear form (traction on facets 4 and 5) - Expression 사용
    ds = ufl.Measure("ds", domain=domain, subdomain_data=facet_tags)
    # Expression을 직접 사용: assembly 시점에 boundary integration points에서 평가됨
    L = ufl.inner(traction_coeff, v) * ds(4) + ufl.inner(traction_coeff, v) * ds(5)


    if rank == 0:
        print("[I] Weak form defined")
        print("    - Bilinear form: inner(sigma(u), epsilon(v)) * dx")
        print("    - Linear form: inner(traction, v) * ds(4) + inner(traction, v) * ds(5)")
        print(f"complete weak form setup {time.time() - start:.2f} s")

    #start solver part.
    start = time.time()
    
    # Option 4A: ILU preconditioner (most robust for near-incompressible materials)
    # Poisson ratio 0.45 is close to 0.5 (incompressible), making the system ill-conditioned
    # Solve using PCG (Preconditioned Conjugate Gradient) - fast for symmetric problems
    opts = {
        "ksp_type": "cg",                 # Conjugate Gradient (for symmetric positive definite)
        "ksp_rtol": 1e-8,                 # Relative tolerance
        "ksp_atol": 1e-10,                # Absolute tolerance
        "ksp_max_it": 1000,               # Maximum iterations
        "pc_type": "hypre",               # Hypre preconditioner
        "pc_hypre_type": "boomeramg",     # BoomerAMG (Algebraic Multigrid)
        "ksp_monitor_true_residual": None,  # Print true residual norm per iteration
        "ksp_converged_reason": None,     # Print convergence reason
        "mat_type": "aij",                # Sparse AIJ format
    }
    problem = LinearProblem(a, L, bcs=bcs, petsc_options=opts)
    print("\n\nstart solving...\n\n") if rank == 0 else None
    u_sol = problem.solve()

    if rank == 0:
        print(f"complete solving {time.time() - start:.2f} s")
        print(f"[I] Max displacement magnitude: {np.max(np.linalg.norm(u_sol.x.array.reshape(-1, 3), axis=1)):.6f}")


    # Set function name for displacement
    u_sol.name = "Displacement"
    
    # Write displacement to XDMF
    # For linear elements, try writing directly first
    # If mesh geometry degree doesn't match, interpolate to match
    try:
        with XDMFFile(comm, Path(save_dir) / "displacement.xdmf", "w") as xout:
            xout.write_mesh(domain)
            xout.write_function(u_sol)
    except RuntimeError as e:
        if "degree" in str(e).lower():
            # Mesh geometry degree doesn't match function degree
            # Interpolate to quadratic (typical for curved meshes from GMSH)
            if rank == 0:
                print(f"[I] Mesh geometry degree mismatch detected. Interpolating to quadratic...")
            V_out = fem.functionspace(domain, ("Lagrange", 2, (gdim,)))
            u_out = fem.Function(V_out)
            u_out.interpolate(u_sol)
            u_out.name = "Displacement"
            with XDMFFile(comm, Path(save_dir) / "displacement.xdmf", "w") as xout:
                xout.write_mesh(domain)
                xout.write_function(u_out)
        else:
            raise

    if rank == 0:
        print(f"Results written to {save_dir}/")
        print(f"Displacement.xdmf: Total displacement field")

    
    # --- Save von Mises stress as XDMF ---
    # For linear elements, stress (gradient of displacement) is constant per cell
    # Project von Mises stress to a DG0 (cellwise constant) function space
    if rank == 0:
        print("\n[I] Computing von Mises stress...")
    
    Vsig = fem.functionspace(domain, ("DG", 0)) # define new Function space. 0: means a value on each cell.
    
    def von_mises(u):
        s = sigma(u) - 1. / 3 * ufl.tr(sigma(u)) * ufl.Identity(len(u))
        von_Mises = ufl.sqrt(3. / 2 * ufl.inner(s, s))
        return von_Mises
    
    # For linear elements, use projection to DG0
    # This is more appropriate than interpolation for cell-wise constant fields
    # Since stress from linear displacement is constant per cell, projection is exact
    
    # Create test and trial functions for projection
    v_sig = ufl.TestFunction(Vsig)
    u_sig = ufl.TrialFunction(Vsig)
    
    # Projection: solve (u_sig, v_sig) * dx = (von_mises(u_sol), v_sig) * dx
    a_proj = ufl.inner(u_sig, v_sig) * ufl.dx
    L_proj = ufl.inner(von_mises(u_sol), v_sig) * ufl.dx
    
    # Solve projection problem
    problem_proj = LinearProblem(a_proj, L_proj, petsc_options={"ksp_type": "preonly", "pc_type": "jacobi"})
    stresses = problem_proj.solve()
    stresses.name = "Von_Mises_Stress"  # Set function name

    # Write to XDMF
    with XDMFFile(comm, Path(save_dir) / "EQV_stress.xdmf", "w") as xdmf:
        xdmf.write_mesh(domain)
        xdmf.write_function(stresses)

    if rank == 0:
        print(f"Von Mises stress saved to {save_dir}/EQV_stress.xdmf")


if __name__ == "__main__":
    current_dir = Path(__file__).parent
    working_dir = current_dir / "solid_data"
    
    #Input files.
    gmsh_path = working_dir / "total_solid_type2.msh"
    materials_path = working_dir / "material.json"
    csv_path = working_dir / "wall_peak_1.csv"

    #output dir
    save_dir = working_dir / "xdmf_out"
    save_dir.mkdir(parents=True, exist_ok=True)

    main(gmsh_path, materials_path, csv_path, save_dir)
