import os, random, math, time, json
import pyvista as pv
import pandas as pd
import utils.utils_geo_mesh.utils_CAD as utils_CAD
import numpy as np
from scipy.spatial import cKDTree
import time
'''
Propgate Lipid first and then Propagate Calcification.
'''

def _one_seed_KDTREE(mesh, 
                    subdomain_cells_indices, 
                    cell_num,
                    seed_point,
                    st_axial_lipid,
                    st_circum_lipid,
                    cell_tag):
    '''
        @Updated 20251027 jeff
        
        One seed KDTREE algorithm.
        
        input:
        mesh: read by meshio, mesh = pv.read_meshio(gmsh_path)
        subdomain_cells_indices: indices of the subdomain cells
        cell_num: number of cells for calcification
        seed_point: point of the seed
        st_axial_lipid: axial weight factor for lipid
        st_circum_lipid: circumferential weight factor for lipid
        cell_tag: tag for calcification
    '''
    calibrated_cells_original_ids = []

    start_time = time.time()

    if cell_num == 0:
        raise ValueError("cell_num is zero. No cells will be calcified.")

    print(f"\nStarting KD-Tree based propagation...")
    # --- Parameters to control propagation shape ---
    # When weight is larger, distance is scaled down in that direction,
    # leading to more propagation in that direction
    # e.g) for more axial propagation,  axial_weight_factor should be larger.
    axial_weight_factor = st_axial_lipid
    circum_weight_factor = st_circum_lipid

    # --- 1. prepare the data: extract the cell centers of the subdomain ---
    subdomain_cell_centers = mesh.cell_centers().points[subdomain_cells_indices]

    # --- 2. transform the coordinates: apply the weight to the coordinates ---
    # to make the general euclidean distance search to be like the weighted distance search,
    # we scale the coordinates by 1/sqrt(weight)
    # Distance^2 ≈ (dx/√w_c)^2 + (dy/√w_c)^2 + (dz/√w_a)^2
    w_axial_sqrt = np.sqrt(axial_weight_factor)
    w_circum_sqrt = np.sqrt(circum_weight_factor)
    
    transformed_centers = np.copy(subdomain_cell_centers)
    transformed_centers[:, 0:2] /= w_circum_sqrt # x, y (circumferential direction)
    transformed_centers[:, 2]   /= w_axial_sqrt   # z (axial direction)

    # --- 3. create the KDTree ---
    # create the KDTree with the transformed cell centers
    kdtree = cKDTree(transformed_centers)

    # --- 4. transform the seed point and query ---
    # transform the seed point with the same weight
    transformed_seed_point = np.copy(seed_point)
    transformed_seed_point[0:2] /= w_circum_sqrt
    transformed_seed_point[2]   /= w_axial_sqrt
    
    # query the cal_num nearest neighbors in the KD-Tree
    distances, indices = kdtree.query(transformed_seed_point, k=cell_num)

    # --- 5. map the result: convert the original cell IDs ---
    valid_indices = indices[np.isfinite(distances)] # filter the valid indices
    calibrated_cells_original_ids = subdomain_cells_indices[valid_indices]

    end_time = time.time()
    print(f"KD-Tree search completed in {end_time - start_time:.4f} seconds.")
    print(f"Selected {len(calibrated_cells_original_ids)} cells.")
    
    # Assign calcification tag (8) to the selected cells
    mesh.cell_data["gmsh:physical"][calibrated_cells_original_ids] = cell_tag # allocate new ca_index = 8
    return calibrated_cells_original_ids

def _two_seeds_KDTREE(model, mesh, console = True):
    
    '''
        @Updated 20251024 jeff
        
        Two seeds KDTREE algorithm.

        input:
        mesh: read by meshio ,mesh = pv.read_meshio(gmsh_path)
        model: class instance having (case_index and parameter_csv_path)
            self.case_index = case_index # case id, should be int.
            self.parameter_csv_path = parameter_csv_path

        Lesion region
        - lipid core (tag = 2)
        - Calcification (tag = 8)
        - Fibrous tissue (tag = 10)
    
    Algorithm:
    1. Propagate the lipid core in the subdomain.
       - 1a. randomly select a cell at the interface of the lumen and subdomain.
       - 1b. propagate the lipid core to the nearest cells in the subdomain
            (use Axial and Circumferential weight factor (strength), propagate = vary the cell array tag)

    2. Propagate the calcification in the subdomain.
       - 2a. randomly select a cell in the subodmain(except the lipid core region)
       - 2b. propagate the calcification to the nearest cells in the subdomain
            (use Axial and Circumferential weight factor (strength), propagate = vary the cell array tag)
    
    3. Fill the unfilled region with the fibrous tissue.

    4. Calculate the dependent variables.

        Morphology:
        - Calcification (length, arc angle, boolean(touch lumen or not))
        - Lipid core (length, arc angle)

        Location:
        - Calcification (axial skewness, shoulder skewness)
        - Lipid core (axial skewness, shoulder skewness)
    '''

    #parameters
    fraction_ca = 0.3
    fraction_lipid = 0.4

    st_axial_lipid = 0.8
    st_circum_lipid = 0.2

    st_axial_ca = 0.8
    st_circum_ca = 0.2

    fc_av_th = 0.01 #cm.

    #tag for the subdomain, lipid, and calcification, defined in gmsh.
    subdomain_tag = 2 #subdomain that calcfication will propagate inside.
    lipid_tag = 2
    cal_tag = 8
    fc_tag = 3

    #1. Extract the subdomain mesh(current tag 2 but change it to 3)
    subdomain_mask = (mesh.cell_data["gmsh:physical"] == subdomain_tag) & (mesh.celltypes == 24)
    subdomain_cells_indices  = np.where(subdomain_mask)[0]
    mesh.cell_data["gmsh:physical"][subdomain_cells_indices] = fc_tag # subdomain 2 -> 3
    
    #2. Now set the # of cells for calcification and lipid core from the fraction values.
    lipid_num = round(len(subdomain_cells_indices ) * fraction_lipid)
    cal_num = round(len(subdomain_cells_indices) * fraction_ca)

    #3. get the z_max of the subdomain from the gmsh.
    submesh = mesh.extract_cells(subdomain_cells_indices)
    import random
    skew_axial = random.uniform(0, 1)
    skew_shoulder = random.uniform(-1, 1)

    #inside the subdomain where ca can exist, normalize (z_min, z_max) -> (0, 1)
    z_min = submesh.points[:, 2].min()
    z_max = submesh.points[:, 2].max()
    z_seed = z_min + (z_max - z_min) * skew_axial

    #4. calculate θ_seed from lipid_half_angle(z = z_seed) and the distance from the lumen_centere
    θ_lipid_arc_half = utils_CAD.alpha_theta(model.vessel_model, z_seed) #rad
    θ_seed_half = θ_lipid_arc_half * skew_shoulder # this value can be negative.

    #5. calculate the x, y coordinate of the seed_point
    # distance between the lumen_center and the seed_point 
    # (big assumption seed point is the closests to the lumen_center in the subdomain, divided by d_fc_ca)
    d_lumen_seed = utils_CAD.radius_lumen(model.vessel_model, z_seed) + fc_av_th
    x_seed = d_lumen_seed * math.sin(θ_seed_half)
    y_seed = d_lumen_seed * math.cos(θ_seed_half) + utils_CAD.y_center_lumen(model.vessel_model, z_seed)
    
    if console:
        print(f"x_seed: {x_seed}, y_seed: {y_seed}, z_seed: {z_seed}\n")
    
    #7. Find the tetra element that contains the seed_point.
    seed_point = np.array([x_seed, y_seed, z_seed])
    seed_cell_id = -1
    status = ""

    if submesh.n_cells > 0:
        local_cell_id = submesh.find_containing_cell(seed_point)
        original_ids_in_submesh = submesh.cell_data['vtkOriginalCellIds']
        
        if local_cell_id != -1:
            status = "point is in the subdomain"
            seed_cell_id = original_ids_in_submesh[local_cell_id]
        else:
            status = "closest cell in the subdomain"
            local_closest_cell_id = submesh.find_closest_cell(seed_point)
            seed_cell_id = original_ids_in_submesh[local_closest_cell_id]

    if console:
        print(f"SEED_CELL_ID: {seed_cell_id}")
        print(f"SEED_STATUS: {status}")
    


    ############################################################
    ##### Propagation algorithm starts from the KDTREE #########
    ############################################################
    lipid_cells_original_ids = _one_seed_KDTREE(mesh, 
    subdomain_cells_indices, 
    lipid_num, 
    seed_point, 
    st_axial_lipid, 
    st_circum_lipid, 
    lipid_tag)

    # now we need to select a random cell indices
    leftover_cells_indices = np.setdiff1d(subdomain_cells_indices, lipid_cells_original_ids)
    cal_seed_id = random.choice(leftover_cells_indices)
    cal_seed_point = mesh.cell_centers().points[cal_seed_id]

    cal_cells_original_ids = _one_seed_KDTREE(mesh, 
    leftover_cells_indices, 
    cal_num, 
    cal_seed_point, 
    st_axial_ca, 
    st_circum_ca, 
    cal_tag)

    #save the mesh with tag cal_tag
    # cal_mask = (mesh.cell_data["gmsh:physical"] == cal_tag) & (mesh.celltypes == 24)
    # cal_cells_indices = np.where(cal_mask)[0]
    # cal_mesh = mesh.extract_cells(cal_cells_indices)
    # cal_mesh.save(os.path.join(model.ansys_exec_dir, f"cal_mesh.vtu"))

    # lipid_mask = (mesh.cell_data["gmsh:physical"] == lipid_tag) & (mesh.celltypes == 24)
    # lipid_cells_indices = np.where(lipid_mask)[0]
    # lipid_mesh = mesh.extract_cells(lipid_cells_indices)
    # lipid_mesh.save(os.path.join(model.ansys_exec_dir, f"lipid_mesh.vtu"))


    #####################################################
    ##### 10. Calculate the dependent variables #########
    #####################################################
    
    '''
    dependent variables:
    - ca_length
    - ca_arc
    - lipid_length
    - lipid_arc

    - ca_axial_skewness
    - ca_shoulder_skewness
    - lipid_axial_skewness
    - lipid_shoulder_skewness
    '''

    #10.0 Extract the calcification and lipid cells
    cal_mask = (mesh.cell_data["gmsh:physical"] == cal_tag) & (mesh.celltypes == 24) # Calcification mask
    cal_cells_indices  = np.where(cal_mask)[0]
    
    lipid_mask = (mesh.cell_data["gmsh:physical"] == lipid_tag) & (mesh.celltypes == 24) # Lipid mask
    lipid_cells_indices = np.where(lipid_mask)[0]


    #10.1. Calculate the length of the calcification and lipid cells
    def length(mesh, cells_indices):
        sub_mesh = mesh.extract_cells(cells_indices)
        z_max = sub_mesh.points[:, 2].max()
        z_min = sub_mesh.points[:, 2].min()
        return z_max - z_min
    
    ca_length = length(mesh, cal_cells_indices)
    lipid_length = length(mesh, lipid_cells_indices)
    if console:
        print(f"ca_length: {ca_length}")
        print(f"lipid_length: {lipid_length}")


    #10.2. Maximum cal arc angle
    '''
        change the algorithm 20251010
        
        so, there are calcification cells already defined. we are going to slice the cal_mesh parallel to the xy plane along the z axis.
        z_slice = np.linspace(z_min, z_max, 100)

        and then, calculate the max arc angle on each sliced plane.
        the funcion f(z) will derive the arc angle.

        and then, find the z value with the maximum arc angle, z_max_arc
        and the dependent variable that we are looking for is f(z_max_arc) = ca_arc_max
    '''
    
    def arc_angle(mesh, cells_indices):
        '''
        output the arc angle for the given z plane parallel to the x-y plane
        '''

        sub_mesh = mesh.extract_cells(cells_indices)

        def f(z):
            z_filter = np.abs(sub_mesh.points[:, 2] - z) < 0.01
            filtered_points = sub_mesh.points[z_filter]
            if not len(filtered_points) > 0:
                raise ValueError("No points found within z tolerance for cal arc angle calculation")
            
            lumen_center = np.array([0, utils_CAD.y_center_lumen(model.vessel_model, z), z])
            
            #create vectors from lumen_center to filtered points
            vectors = filtered_points - lumen_center
            vectors_2d = vectors[:, :2]  # z coordinate is removed

            #the angle between the vectors and the y_axis
            angles = np.arctan2(vectors_2d[:, 0], vectors_2d[:, 1])
            arc_angle = np.max(angles) - np.min(angles)
            return arc_angle


        z_max = sub_mesh.points[:, 2].max()
        z_min = sub_mesh.points[:, 2].min()
        z = np.linspace(z_min, z_max, 100)
        arc_angles = np.array([f(z_val) for z_val in z])
        
        # Find the z value with maximum arc angle
        max_arc_idx = np.argmax(arc_angles)
        z_max_arc = z[max_arc_idx]
        arc_angle = arc_angles[max_arc_idx]
        arc_angle_degrees = float(np.degrees(arc_angle).round(4))

        return arc_angle_degrees
    
 
    ca_arc_max_degrees = arc_angle(mesh, cal_cells_indices)
    lipid_arc_max_degrees = arc_angle(mesh, lipid_cells_indices)
    print(f"ca_arc_max_degrees: {ca_arc_max_degrees}")
    print(f"lipid_arc_max_degrees: {lipid_arc_max_degrees}")


    exit()




    ################################################
    ##### 11. Save the dependent variables #########
    ################################################
    json_path = os.path.join(model.ansys_exec_dir, f"dependent_variables.json")
    # Save total_fraction, ca_length, and ca_arc to a JSON file at model.json_path
    
    import json
    result_dict = {
        "total_fraction": round(total_fraction, 4),
        "ca_length": round(ca_length, 4),
        "ca_arc": round(ca_arc_max_degrees, 4)
    }

    with open(json_path, "w") as file:
        json.dump(result_dict, file, indent=4)

    return mesh