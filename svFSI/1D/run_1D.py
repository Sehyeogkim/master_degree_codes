'''
This script is used to run the 1D Pulsatile Tree solver RCR simulation.
'''
import subprocess, os

#run the 1D simulation
n_steps = 1000
t_size = 0.01
pul_1d_solver_path = "/home/jeff/repo/SyntheticTreeGenerator/build/apps/PulsatileTreeSolver/pulsatile_tree_solver"
tree_path = "treedata.dat"
bc_types_path = "bc_types_heart.dat"
output_dir = "1D_result_heart"
os.makedirs(output_dir, exist_ok=True)

output_file = os.path.join(output_dir, "result.json")

argv = [
    pul_1d_solver_path,
    "--input_tree_file", tree_path,
    "--input_bc_file", bc_types_path,
    "--input_elastance_file", "Elastance.dat",
    "--output_tree_file", output_file,
    "--prescribe_resistances", "1",
    "--output_frequency", "1",
    "--time_step_size", str(t_size),
    "--number_of_iterations", "10",
    "--number_of_time_steps", str(n_steps)
]
subprocess.run(argv, check=True)