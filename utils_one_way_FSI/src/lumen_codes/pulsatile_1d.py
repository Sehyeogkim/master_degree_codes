'''
This is a script for the pulsatile 1D simulation.

3 convert tree.dat -> output_tree.dat(Syntehtic solver)

0. make a pulsatile 1D folder.
1. Move the tree.dat, slab.txt, FlowHist.dat to the pulsatile 1D folder.
1a make outlet_information.dat file just writen as 1 50 0.
2. Make a slopes.dat file. (regression_abc.py)
    (requires inp file had used on the Q_ramped 3D simulation)
4. Now run the Reduced order model.py -> get a,b,c written output_tree.dat

5. prepare bc_types.dat file.(P_in, Coronary Bc, P_myo)
- generate P_in.dat along with the hemodynamic parameters.
- generate Coronary Bc.dat along with the hemodynamic parameters.
- generate P_myo.dat from the Elastance.dat and the hemodynamic parameters.
- Combine them into bc_types.dat file.

6. run 1D simulation.

7. Post processing -> 1D post.py


#updated 20260327 jeff
'''


import os
import utils.utils_lumen.paths as utils_paths
import utils.utils_lumen.regression as utils_reg
import utils.utils_lumen.ROM as utils_ROM
from utils.utils_lumen.heart_model_in import generate_coronary_pressure_decay_ratio, generate_coronary_pressure, generate_coronary_pressure_cos
from pathlib import Path

import numpy as np
import subprocess

class Pulsatile_1D():
    
    def __init__(self, parent):
        '''
        parent: lumen_simulation class instnaace(which is the highest level class)
        '''

        self.exe_dir = Path(parent.pul_1d_dir) # folder dir
        
        # the data will be calculated
        self.mean_pressure = 0 # mmHg.

        #Nomralized pre - data file path
        self.P_myo_norm_path = parent.scripts_dir / "P_myo_norm.dat"
        self.P_in_norm_path = parent.scripts_dir / "P_in_norm.dat"
        
        #will be created file path.
        self.P_in_data_path = self.exe_dir / "P_in.dat"
        self.P_myo_data_path = self.exe_dir / "P_myo.dat"
        self.bc_save_path = self.exe_dir / "bc_types.dat"

        #these files will be created.
        self.outlet_info_path = self.exe_dir / "outlet_information.dat"
        self.abc_tree_path = None
        self.converted_tree_path = None

        #default values will be changed in the lumen_main.py
        self.SBP = 120 * 1333.22 # mmHg
        self.DBP = 80 * 1333.22 # mmHg
        self.HR = 60 # bpm
        self.P_ratio = 1.05
        self.n_steps = 500
        self.t_size = 0.01
        self.decay_ratio = 0.1 # 0.1 ~ 0.5

        #all the 1d simulation result will be saved in this directory
        self.save_dir = self.exe_dir / "result"
        os.makedirs(self.save_dir, exist_ok=True)

    @staticmethod
    def create_outlet_information_file(outlet_info_path):
        '''
        Make a outlet_information.dat file.
        '''
        with open(outlet_info_path, "w") as f:
            f.write("1 49 0")
        return

    @staticmethod
    def Reduced_order_modeling(tree_path, slab_path, flowhist_path, ramped_inp_path, outlet_info_path, save_dir):
        '''
        Run the Reduced order modeling -> create self.abc_tree_path
        '''
        slab_p_path, variable_path, slopes_path = utils_reg.regression(slab_path, flowhist_path, ramped_inp_path, save_dir)
        abc_tree_path = utils_ROM.ROM_main(tree_path, outlet_info_path, slab_p_path, variable_path, slopes_path, save_dir)
        return abc_tree_path
    
    def create_P_in_dat(self):
        '''
        1. create P_in.dat from the SBP, DBP, HR and normalized P_in_norm.dat and P_myo_norm.dat
        2. calculate the mean pressure from the P_in.dat -> save self.mean_pressure
        '''
        t, P = generate_coronary_pressure_cos(SBP=self.SBP, 
                                              DBP=self.DBP, 
                                              HR=self.HR, 
                                              decay_ratio=self.decay_ratio,
                                              save_path=self.P_in_data_path,
                                              plot=True,
                                              t_peak_ratio=0.2, 
                                              num_points=1001)

        # Mean pressure = (1/T) * integral(P(t)dt) from 0 to T
        # Using trapezoidal rule: integral ≈ sum of trapezoid areas
        T = t[-1] - t[0]  # Total time period
        if T > 0:
            # Trapezoidal rule: sum of (P[i] + P[i+1]) * (t[i+1] - t[i]) / 2
            integral = 0.0
            for i in range(len(t) - 1):
                dt = t[i+1] - t[i]
                integral += (P[i] + P[i+1]) * dt / 2.0
            mean_pressure = integral / T
        else:
            mean_pressure = P[0]  # If single point, use that value 

        return mean_pressure
    

    def scale_P_myo_dat(self, myo_scale_factor):
        '''
        read the data from the P_myo_norm_path and scale it up

        P_myo = P_myo_norm * myo_scale_factor * SBP
        
        Parameters:
        - myo_scale_factor: scaling factor (e.g., 1.05 for LCA, 0.3 for RCA)
        '''
        
        # Read normalized data
        with open(self.P_myo_norm_path, 'r') as f:
            lines = f.readlines()
        
        # First line contains the number of data points
        num_points = int(lines[0].strip())
        
        # Read t, P pairs and scale the pressure
        scaled_data = []
        for i in range(1, num_points + 1):
            parts = lines[i].strip().split()
            t = float(parts[0])
            P_norm = float(parts[1])
            
            # Scale up: P_myo = P_myo_norm * myo_scale_factor * SBP
            P_myo = P_norm * myo_scale_factor * self.SBP
            scaled_data.append([t, P_myo])
        
        # Save scaled data to P_myo_data_path (format: t P pairs, no header)
        with open(self.P_myo_data_path, 'w') as f:
            for t, P_myo in scaled_data:
                f.write(f"{t:.6f} {P_myo:.6f}\n")
        
        print(f"Scaled myocardial pressure data saved to {self.P_myo_data_path} ({num_points} points)")
        
        return


    def create_bc_types(self, C_total =0.36):
        '''
            mean_pressure: mean pressure in Pa
            is_LCA: True -> LCA, False -> RCA
    
            This code is to set the bc_tyes.dat file for the 1D ROM simulation.
            bc_types.dat sturcture:
            1. P_inlet time series data -> should varry along the hemodynamic parameters.
            2. coronary BC data
            3. P_myo time series data
        
            1. read the P_in.dat
            2. open new .dat file and write 0 DirichletPressure 1001 1 0
            3. write the time series data to the file in a row.
            4. write 49 NeumannCoronary 1001 4 12
            5. write the calculated parameters
            6. write the P_myo time series data

            -> create self.bc_save_path

            Reference for the Q = 0.363cc/s:
            Sharif, D., Sharif-Rasslan, A., Shahla, C., & Abinader, E. G. (2010). 
            Detection of severe left anterior descending coronary artery stenosis by transthoracic evaluation 
            of resting coronary flow velocity dynamics. Heart International, 5(2), e10. https://doi.org/10.4081/hi.2010.e10
        '''

        # Calculate resistances and capacitances, revised 2026/03/27 jeff fix the R total plz.
        # R_total = float(P_mean / Q_mean)
        Q_mean = 0.363 # cc/s (reference plz)
        R_total = float(93 * 1333.22 / (Q_mean * 3.5)) # 3.5 for the adenosine protocol.
        R_a, R_a_micro, R_v = 0.32 * R_total, 0.52 * R_total, 0.16 * R_total
        C_a, C_im = 0.11 * C_total, 0.89 * C_total
        R_venous = R_v_micro = R_v / 2

        # Load P_in.dat and P_myo.dat
        P_in_data = np.loadtxt(self.P_in_data_path, delimiter=' ', dtype=float)
        P_myo_data = np.loadtxt(self.P_myo_data_path, delimiter=' ', dtype=float)
        assert len(P_in_data) == len(P_myo_data), "P_in_data and P_myo_data must have the same length"

        # Open new boundary condition file
        with open(self.bc_save_path, 'w') as f:
            
            # Write inlet boundary condition (point 0)
            f.write("0 DirichletPressure 1001 1 0\n") # 1001 -> # of points, 1 -> dimension
            
            # Write P_in time series data
            for i in range(len(P_in_data)):
                f.write(f"{P_in_data[i,0]:.6f} {P_in_data[i,1]:.6f}\n")
            
            # Write outlet boundary condition (point 49)
            f.write("49 NeumannCoronary 1001 4 12\n")
            
            # Write the 12 coupled parameters
            f.write(f"arterial_resistance {R_a:.6f}\n")
            f.write(f"arterial_compliance {C_a:.4f}E-5\n")
            f.write(f"arterial_microcirculation_resistance {R_a_micro:.6f}\n")
            f.write(f"myocardial_compliance {C_im:.4f}E-5\n")
            f.write(f"venous_microcirculation_resistance {R_v_micro:.6f}\n")
            f.write(f"venous_resistance {R_venous:.6f}\n")
            f.write(f"venous_compliance 1.00E-5\n")
            f.write(f"venous_pressure 0\n") # 20000 -> 0
            f.write(f"total_compliance 0\n")
            f.write(f"arterial_resistance_ratio 0\n")
            f.write(f"venous_resistance_ratio 0\n")
            f.write(f"total_resistance 0\n")
            
            # Write P_myo time series data
            for i in range(len(P_myo_data)):
                f.write(f"{P_myo_data[i,0]:.6f} {P_myo_data[i,1]:.6f}\n")
        
        return

        
 