'''
Subfunctions for the Boundary conditions:

-Pressure and traction on the wall_inner surface.

'''

import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
import time

def Interpolate_wall_data(wall_csv_path, node_ids, node_coords):
    '''
    Interpolate the wall data (Only Total traction) according to the node_ids and node_coords.

    INPUT:
    - wall_csv_path: the path of the wall data.
    - node_ids: the node IDS of the wall (SURF154 nodes)
    - node_coords: the coordinates of the wall.

    OUTPUT:
    - interpolated_data: only node_id and traction data.(x,y,z)
    '''
    start_time = time.time()
    df = pd.read_csv(wall_csv_path)

    wall_points = df[['x', 'y', 'z']].values
    traction = df[['Tx', 'Ty', 'Tz']].values

    tree = cKDTree(wall_points)
    distances, nearest_indices = tree.query(node_coords, k=3)

    power = 2
    with np.errstate(divide='ignore'):
        weights = 1.0 / (distances ** power)
    weights[np.isinf(weights)] = 1e12
    norm_weights = weights / np.sum(weights, axis=1, keepdims=True)

    new_tractions = np.sum(norm_weights[..., None] * traction[nearest_indices], axis=1)

    interpolated_data = pd.DataFrame({
        "node_ID": node_ids,
        "Tx": new_tractions[:, 0],
        "Ty": new_tractions[:, 1],
        "Tz": new_tractions[:, 2],
    })

    end_time = time.time()
    print(f"Interpolated wall data created in memory: {end_time - start_time:.2f} seconds  ")
    return interpolated_data
