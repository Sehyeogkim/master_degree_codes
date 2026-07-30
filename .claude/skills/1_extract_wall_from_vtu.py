#!/usr/bin/env python
"""
Extract wall surface from VTU files using ROM wall VTP as mask.

Uses KDTree coordinate-based matching to find corresponding points.

Steps:
1. Copy the wall.vtp geometry as mask
2. Use KDTree to find nearest points on VTU from all wall.vtp points
3. Copy the mapped Pressure point array to the mask vtp file
4. Save as (vtu_filename)_wall.vtp
"""

import vtk
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk
import numpy as np
from scipy.spatial import cKDTree
import os
import glob
from pathlib import Path


def read_wall_mask(mask_path):
    """Read wall mask VTP file to get geometry"""
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(mask_path)
    reader.Update()
    return reader.GetOutput()


def read_vtu(vtu_path):
    """Read VTU file"""
    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(vtu_path)
    reader.Update()
    return reader.GetOutput()


def get_points_as_numpy(vtk_data):
    """Extract points from VTK data as numpy array"""
    n_points = vtk_data.GetNumberOfPoints()
    points = np.zeros((n_points, 3))
    for i in range(n_points):
        points[i] = vtk_data.GetPoint(i)
    return points


def extract_wall_from_vtu_kdtree(vtu, wall_mask):
    """
    Extract wall surface from VTU using KDTree coordinate-based matching.
    
    Args:
        vtu: VTK unstructured grid (source data)
        wall_mask: VTK polydata (geometry mask, all point arrays will be removed)
    
    Returns:
        VTK polydata with wall geometry and pressure data from VTU
    """
    # Get points from VTU and wall mask
    vtu_points = get_points_as_numpy(vtu)
    wall_points = get_points_as_numpy(wall_mask)
    
    print(f"  Building KDTree with {len(vtu_points)} VTU points...")
    
    # Build KDTree from VTU points
    tree = cKDTree(vtu_points)
    
    # Find nearest VTU point for each wall point
    print(f"  Finding nearest points for {len(wall_points)} wall points...")
    distances, indices = tree.query(wall_points, k=1)
    
    # Check matching quality
    max_dist = distances.max()
    mean_dist = distances.mean()
    print(f"  Matching distances: max={max_dist:.6f}, mean={mean_dist:.6f}")
    
    # Get pressure from VTU
    vtu_pressure = vtu.GetPointData().GetArray('Pressure')
    if vtu_pressure is None:
        raise ValueError("VTU does not have Pressure array!")
    
    vtu_pressure_np = vtk_to_numpy(vtu_pressure)
    
    # Map pressure to wall points using KDTree indices
    wall_pressure = vtu_pressure_np[indices]
    
    # Create output polydata (copy geometry from mask)
    wall_output = vtk.vtkPolyData()
    
    # Copy points from wall mask (keep original geometry)
    wall_output.SetPoints(wall_mask.GetPoints())
    
    # Copy cells from wall mask
    wall_output.SetPolys(wall_mask.GetPolys())
    
    # Clear all existing point data arrays (remove pre-existing Pressure, etc.)
    # We only add the new Pressure from VTU
    
    # Add Pressure array (only this one, no old data)
    pressure_vtk = numpy_to_vtk(wall_pressure, deep=True)
    pressure_vtk.SetName('Pressure')
    wall_output.GetPointData().AddArray(pressure_vtk)
    
    return wall_output


def process_all_vtu_files(vtu_dir, mask_path, output_dir):
    """Process all VTU files in directory"""
    
    # Read wall mask
    print(f"Reading wall mask: {mask_path}")
    wall_mask = read_wall_mask(mask_path)
    print(f"  Wall mask points: {wall_mask.GetNumberOfPoints()}")
    print(f"  Wall mask cells: {wall_mask.GetNumberOfCells()}")
    
    # Find all VTU files
    vtu_files = sorted(glob.glob(os.path.join(vtu_dir, '*.vtu')))
    print(f"\nFound {len(vtu_files)} VTU files")
    
    for vtu_path in vtu_files:
        vtu_name = os.path.basename(vtu_path)
        print(f"\nProcessing: {vtu_name}")
        
        # Read VTU
        vtu = read_vtu(vtu_path)
        print(f"  VTU points: {vtu.GetNumberOfPoints()}")
        
        # Extract wall using KDTree
        wall_vtp = extract_wall_from_vtu_kdtree(vtu, wall_mask)
        
        # Get pressure stats
        pressure = wall_vtp.GetPointData().GetArray('Pressure')
        p_np = vtk_to_numpy(pressure)
        print(f"  Wall pressure range: {p_np.min():.2f} ~ {p_np.max():.2f}")
        
        # Save output
        output_name = vtu_name.replace('.vtu', '_wall.vtp')
        output_path = os.path.join(output_dir, output_name)
        
        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName(output_path)
        writer.SetInputData(wall_vtp)
        writer.Write()
        
        print(f"  Saved: {output_path}")
    
    print("\n✓ All files processed!")


if __name__ == "__main__":

    base_dir = Path.cwd()
    vtu_dir = os.path.join(base_dir, 'full_FSI_solid')
    mask_path = os.path.join(base_dir, 'ROM_wall_vtp', 'pt0_wall.vtp')
    output_dir = os.path.join(base_dir, 'full_FSI_wall')
    
    # Create output directory if not exists
    os.makedirs(output_dir, exist_ok=True)
    
    process_all_vtu_files(vtu_dir, mask_path, output_dir)
