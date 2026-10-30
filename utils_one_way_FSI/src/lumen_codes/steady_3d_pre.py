import os
import shutil
import utils.utils_lumen.paths as utils_paths
from utils.utils_lumen.extract_wall_csv import extract_wall_data
'''
# Total 4 stages
    - prepare ( make 3 folders and copy mesh,svpre, inp file, create flow file ,  )
    - run svpre solver
    - run svsolver nproc / 3 each. at the same time (parallel process.)
    - post procesing(extract the wall_peak.csv, wall_low.csv, wall_av.csv)
'''

class Steady_3d():
    
    def __init__(self, parent):
        '''
        parent: lumen_simulation class instance(which is the highest level class)
        '''
        self.st_3d_dir = parent.st_3d_dir # folder dir
        self.mesh_complete_dir = parent.mesh_complete_dir #mesh dir
        self._1d_rst_json = parent._1d_rst_json # 1d result json path.

        #define the parent path
        self.parent_svpre_dir = os.path.join(parent.scripts_dir, "model.svpre")
        self.parent_inp_dir = os.path.join(parent.scripts_dir, "solver.inp")

        #Generate 3 folders and 1d json file path
        self.peak_dir = os.path.join(self.st_3d_dir, "peak")
        self.low_dir = os.path.join(self.st_3d_dir, "low")
        self.av_dir = os.path.join(self.st_3d_dir, "av")

        #define the wall csv path (will be saved as the final result wall csv path)
        self.wall_peak_csv = os.path.join(parent.wall_folder, "wall_peak.csv")
        self.wall_low_csv = os.path.join(parent.wall_folder, "wall_low.csv")
        self.wall_av_csv = os.path.join(parent.wall_folder, "wall_av.csv")
        
        #define the parameters
        self.num_timesteps = 250
        self.time_step_size = 0.0005
        self.file_name = "rst"
        self.nproc = 10
   
    def create_three_folders(self):
        '''
        create 3 folders.
        '''
        os.makedirs(self.peak_dir, exist_ok=True)
        os.makedirs(self.low_dir, exist_ok=True)
        os.makedirs(self.av_dir, exist_ok=True)

    def copy_mesh(self):
        '''
        copy mesh_dir folder into peak_dir, low_dir, av_dir (preserve original folder name)
        '''
        peak_mesh = os.path.join(self.peak_dir, "mesh-complete")
        low_mesh = os.path.join(self.low_dir, "mesh-complete")
        av_mesh = os.path.join(self.av_dir, "mesh-complete")
        shutil.copytree(self.mesh_complete_dir, peak_mesh, dirs_exist_ok=True)
        shutil.copytree(self.mesh_complete_dir, low_mesh, dirs_exist_ok=True)
        shutil.copytree(self.mesh_complete_dir, av_mesh, dirs_exist_ok=True)

    def create_flowfile(self):
        '''
        create flowfile in the three folders from the 1d json file.
        '''
        peak_flow_dir = os.path.join(self.peak_dir, "inflow.flow")
        low_flow_dir = os.path.join(self.low_dir, "inflow.flow")
        av_flow_dir = os.path.join(self.av_dir, "inflow.flow")

        #read Q_peak, Q_av, Q_low from the 1d json file.
        import json
        with open(self._1d_rst_json, "r") as f:
            data = json.load(f)
            Q_peak = data["systolic"]["Q"]
            Q_low = data["diastolic"]["Q"]
            Q_av = data["mean"]["Q"]

        utils_paths.create_flow_file(peak_flow_dir, Q_peak)
        utils_paths.create_flow_file(low_flow_dir, Q_low)
        utils_paths.create_flow_file(av_flow_dir, Q_av)

    def prepare_svpre(self):
        #copy svpre file to peak_dir, low_dir, av_dir
        peak_svpre_dir = os.path.join(self.peak_dir, "model.svpre")
        low_svpre_dir = os.path.join(self.low_dir, "model.svpre")
        av_svpre_dir = os.path.join(self.av_dir, "model.svpre")
        shutil.copyfile(self.parent_svpre_dir, peak_svpre_dir)
        shutil.copyfile(self.parent_svpre_dir, low_svpre_dir)
        shutil.copyfile(self.parent_svpre_dir, av_svpre_dir)

    def prepare_inp(self):
        
        '''
            #Fixe this parameters for the 3d simulation.
            Number of Timesteps: step_number
            Time Step Size: 0.0005
            Number of Timesteps between Restarts: 10
        '''

        peak_svsolver_dir = os.path.join(self.peak_dir, "solver.inp")
        low_svsolver_dir = os.path.join(self.low_dir, "solver.inp")
        av_svsolver_dir = os.path.join(self.av_dir, "solver.inp")
        shutil.copyfile(self.parent_inp_dir, peak_svsolver_dir)
        shutil.copyfile(self.parent_inp_dir, low_svsolver_dir)
        shutil.copyfile(self.parent_inp_dir, av_svsolver_dir)

        #Open json file(got from 1D simulation) -> get R_peak, R_low, R_av
        import json
        with open(self._1d_rst_json, "r") as f:
            data = json.load(f)
            R_peak = data["systolic"]["R"]
            R_low = data["diastolic"]["R"]
            R_av = data["mean"]["R"]

        #Modify the resistance values on the inp file.
        chages_peak = {"Resistance Values:": R_peak, "Number of Timesteps:": self.num_timesteps, "Time Step Size:": self.time_step_size}
        chages_low = {"Resistance Values:": R_low, "Number of Timesteps:": self.num_timesteps, "Time Step Size:": self.time_step_size}
        chages_av = {"Resistance Values:": R_av, "Number of Timesteps:": self.num_timesteps, "Time Step Size:": self.time_step_size}
        utils_paths.revise_inp_file(peak_svsolver_dir, chages_peak)
        utils_paths.revise_inp_file(low_svsolver_dir, chages_low)
        utils_paths.revise_inp_file(av_svsolver_dir, chages_av)

    def save_wall_csv(self, exe_dir: str, wall_csv_path: str):
        
        # ex) vtp_path = "peak/rst_00250.vtp" (file_name = rst)
        vtp_path = os.path.join(exe_dir, f"{self.file_name}_{self.num_timesteps:05d}.vtp")
        extract_wall_data(vtp_path, wall_csv_path)
        return