import math
import numpy as np
import os
from .utils_CAD import *
'''
so far, we made lipid with like a lofted arc shape, and then boolean with the fibrous cap.
but in here we are going to make a booleaned shape of the lipid core right away.
'''

def lipid_arc_shape_step(model, save_folder_path, fc_thickness = 0.01):
    '''
        #Patient parameter
        - lipid_arc_angle(alpha)
        - lipid_length(z_lipid)

        #User defined parameters
        - fillet radius
        - lipid_wall_thickness

        @updated 0722 jeff
        - z_vals is changed to np.linspace(-0.7 * model.z_lipid, 0.7 * model.z_lipid, 10)
        - 10 profiles on each z coordinate.

        @updated 0826 jeff
        - z_lipid_L and z_lipid_R are added.
        - z_lipid_L and z_lipid_R are calculated by the function find_ab.
        - z_lipid_L and z_lipid_R are used to define the z coordinate of the lipid profile.
        - z_lipid_L and z_lipid_R are used to define the z coordinate of the lipid profile.
    '''

    #Autodesk inventor - New part document
    lipid_doc = model.inv.Documents.Add(12290, model.inv.FileManager.GetTemplateFile(12290, 8962))
    lipid_doc.DisplayName = "Lipid"
    lipid_doc.UnitsOfMeasure.LengthUnits = 11268 #11269 -> mm, 11268 -> cm  
    model.part_def = lipid_doc.ComponentDefinition

    model.sketches3d_col = model.part_def.Sketches3D  #set of sketches.
    model.tg = model.inv.TransientGeometry #set of points, lines, circles, etc.

    sections = model.inv.TransientObjects.CreateObjectCollection() #object collection for lofting.
    centerline_sketch = model.sketches3d_col.Add() #sketch3D to contain 2 points.
    centerline_sketch.Name = "points"


    '''
    -Procedure
    Along the z axis, define a point as pt1 at z = -z_lipid.
    And draw 3 profiles at z = -0.5 * z_lipid, 0, 0.5 * z_lipid.
    At last, define a point as pt2 at z = z_lipid.

    And then, do lofting(tangential options are included).
    '''
    
    
    ###updataed 0826 jeff Additional term z_lipid_left and z_lipid_right
    '''
    let us say z_lipid_left = a, z_lipid_right = b
    self.z_lesion > b > z_peak > a > - self.z_lesion, 
    Eq1 : b - a = self.lipid_length
    Eq2 : f(z) = y_center_lumen(model, z) + radius_lumen(model, z),
          f(a) = f(b)

    return a and b.
    '''
    #calculate z_lipid_L and z_lipid_R
    model.z_lipid_L, model.z_lipid_R = find_ab(model) # Function in the utils.CAD


    ###################################################################
    ############  Profiles and 2 points back and forth. ###############
    ###################################################################



    #Define point1 (z = z_lipid_L)
    y1 = y_center_lumen(model, model.z_lipid_L) + radius_lumen(model, model.z_lipid_L) + fc_thickness
    point1 = model.tg.CreatePoint(0, y1, model.z_lipid_L)
    point1_sk = centerline_sketch.SketchPoints3D.Add(point1)
    sections.Add(point1_sk)
    
    #Profiles for the left and right side.
    '''
    @updated 20251121 jeff
    - exclude the profile back and forth of the two points.
    
    z_lipid_L -> z_peak -> z_lipid_R

    z_peak should be embeeded and z_lipid_L and z_lipid_R should be excluded.

    z_lipid_L -> z_peak for instance I would like to have 5 interval points between z_lipid_L and z_peak.
    '''
    n = 3  # points per side (excluding lipid endpoints, including peak once)
    z_L = np.linspace(model.z_lipid_L, model.z_peak, n + 1)[1:]    # drops z_lipid_L
    z_R = np.linspace(model.z_peak, model.z_lipid_R, n + 1)[1:-1]  # drops z_peak dup &
    z_profile = np.concatenate([z_L, z_R])

    xy_plane = model.part_def.WorkPlanes.Item("XY Plane")

    #making profile code.(revised 0417 jeff)
    for z in z_profile:

        #Define a working plane.
        pt = model.tg.CreatePoint(0, 0, z)
        pt_sk = centerline_sketch.SketchPoints3D.Add(pt)
        wp = model.part_def.WorkPlanes.AddByPlaneAndPoint(xy_plane, pt_sk, False)
        wp.Visible = True

        #Draw a profile on the 2D sketch.
        sketch2d = model.part_def.Sketches.Add(wp)
        wp.Visible = False
        sketch2d.Visible = True

        #Parameters for the external arc.
        r_lipid = lipid_ex_y_coordinate(model, z) - y_center_lesion(model,z) # lipid_area radius
        θ = alpha_theta(model, z)
        β = beta(model, θ, z)

        #Let us Draw total 3 arcs and 2 lines.
        x_β, y_β = r_lipid * math.sin(β), r_lipid * math.cos(β) + y_center_lesion(model,z)
        x_θ, y_θ = r_lipid * math.sin(θ), r_lipid * math.cos(θ) + y_center_lesion(model,z)

        #inner arc points
        r_lumen = radius_lumen(model, z)
        r_inner = r_lumen + fc_thickness
        x_in, y_in = r_inner * math.sin(θ), r_inner * math.cos(θ) + y_center_lumen(model,z)
        x_in2, y_in2 = 0, r_inner + y_center_lumen(model,z) # new coordiante for the mid point of the inner arc.
        # Quarter points at ±θ/2 — split inner arc into 4 pieces so fillet hint sits close to the corner.
        θ_half = θ / 2.0
        x_inq, y_inq = r_inner * math.sin(θ_half), r_inner * math.cos(θ_half) + y_center_lumen(model, z)
        


        #Points for 3 arcs and 2 lines.
        center_lesion = model.tg.CreatePoint2d(0, y_center_lesion(model,z))
        start = model.tg.CreatePoint2d(x_β, y_β)  
        intermediate1 = model.tg.CreatePoint2d(x_θ, y_θ)
        intermediate2 = model.tg.CreatePoint2d(-x_θ,y_θ)
        end = model.tg.CreatePoint2d(-x_β, y_β)
        center_lumen = model.tg.CreatePoint2d(0, y_center_lumen(model,z))

        #additional points we need (incl. ±θ/2 quarter points)
        arc_inner_start = model.tg.CreatePoint2d(x_in, y_in)
        arc_inner_end = model.tg.CreatePoint2d(-x_in, y_in)
        arc_inner_mid = model.tg.CreatePoint2d(x_in2, y_in2)
        arc_inner_qR = model.tg.CreatePoint2d(x_inq, y_inq)    # angle  +θ/2 (right quarter)
        arc_inner_qL = model.tg.CreatePoint2d(-x_inq, y_inq)   # angle  -θ/2 (left quarter)

        #DRAW POINTS ON THE SKETCH.
        center_lesion_sk = sketch2d.SketchPoints.Add(center_lesion)
        start_sk = sketch2d.SketchPoints.Add(start)
        intermediate1_sk = sketch2d.SketchPoints.Add(intermediate1)
        intermediate2_sk = sketch2d.SketchPoints.Add(intermediate2)
        end_sk = sketch2d.SketchPoints.Add(end)
        center_lumen_sk = sketch2d.SketchPoints.Add(center_lumen)
        arc_inner_start_sk = sketch2d.SketchPoints.Add(arc_inner_start)
        arc_inner_end_sk = sketch2d.SketchPoints.Add(arc_inner_end)
        arc_inner_mid_sk = sketch2d.SketchPoints.Add(arc_inner_mid)
        arc_inner_qR_sk = sketch2d.SketchPoints.Add(arc_inner_qR)
        arc_inner_qL_sk = sketch2d.SketchPoints.Add(arc_inner_qL)

        #Draw An External Arc and 2 lines.
        line1 = sketch2d.SketchLines.AddByTwoPoints(arc_inner_start_sk, start_sk)
        arc1 = sketch2d.SketchArcs.AddByCenterStartEndPoint(center_lesion_sk, start_sk, intermediate1_sk)
        arc2 = sketch2d.SketchArcs.AddByCenterStartEndPoint(center_lesion_sk, intermediate1_sk, intermediate2_sk)
        arc3 = sketch2d.SketchArcs.AddByCenterStartEndPoint(center_lesion_sk, intermediate2_sk, end_sk)
        line2 = sketch2d.SketchLines.AddByTwoPoints(arc_inner_end_sk, end_sk)
        
        # Draw inner arc as 4 pieces: θ → θ/2 → 0 → -θ/2 → -θ.
        # Only arc_inner1 (right-end) and arc_inner4 (left-end) are filleted against line1/line2.
        arc_inner1 = sketch2d.SketchArcs.AddByCenterStartEndPoint(center_lumen_sk, arc_inner_start_sk, arc_inner_qR_sk)   # R end (near line1)
        arc_inner2 = sketch2d.SketchArcs.AddByCenterStartEndPoint(center_lumen_sk, arc_inner_qR_sk,    arc_inner_mid_sk)  # R mid
        arc_inner3 = sketch2d.SketchArcs.AddByCenterStartEndPoint(center_lumen_sk, arc_inner_mid_sk,   arc_inner_qL_sk)   # L mid
        arc_inner4 = sketch2d.SketchArcs.AddByCenterStartEndPoint(center_lumen_sk, arc_inner_qL_sk,    arc_inner_end_sk)  # L end (near line2)



        ##Safe fillet radius
        safe_ratio = 0.2
        fillet_radius = calculate_safe_fillet_radius(model, z, safe_ratio)


        try:
            sketch2d.SketchArcs.AddByFillet(
                arc1, line1, fillet_radius,
                arc1.EndSketchPoint.Geometry,
                line1.StartSketchPoint.Geometry
            )

        except Exception as e:
            import traceback
            print("Fillet generation failed for the lipid profile:", e)
            traceback.print_exc()


        try:
            sketch2d.SketchArcs.AddByFillet(
                arc3, line2, fillet_radius,
                arc3.StartSketchPoint.Geometry,
                line2.StartSketchPoint.Geometry
            )

        except Exception as e:
            import traceback
            print("Fillet generation failed for the lipid profile:", e)
            traceback.print_exc()




        # inner arc fillet (4-piece split: fillet only the two end sub-arcs).
        # Hint = the FAR end of each filleted entity (same pattern as outer fillet).
        r_inner_sketch = arc_inner1.Radius
        if fillet_radius >= r_inner_sketch:
            print(f"[warn] fillet_radius({fillet_radius:.4f}) >= arc_inner radius({r_inner_sketch:.4f}); skipping inner fillet at z={z:.4f}")
        else:
            # Right corner at arc_inner_start_sk (= arc_inner1.Start = line1.Start).
            # arc_inner1 spans θ → θ/2 so its far end = arc_inner_qR_sk (= arc_inner1.EndSketchPoint).
            try:
                sketch2d.SketchArcs.AddByFillet(
                    arc_inner1, line1, fillet_radius,
                    arc_inner1.EndSketchPoint.Geometry,   # far end: arc_inner_qR
                    line1.EndSketchPoint.Geometry          # far end: start_sk
                )
            except Exception as e:
                import traceback
                print(f"Inner fillet (arc_inner1+line1) failed at z={z:.4f}: {e}")
                traceback.print_exc()

            # Left corner at arc_inner_end_sk (= arc_inner4.End = line2.Start).
            # arc_inner4 spans -θ/2 → -θ so its far end = arc_inner_qL_sk (= arc_inner4.StartSketchPoint).
            try:
                sketch2d.SketchArcs.AddByFillet(
                    arc_inner4, line2, fillet_radius,
                    arc_inner4.StartSketchPoint.Geometry,  # far end: arc_inner_qL
                    line2.EndSketchPoint.Geometry          # far end: end_sk
                )
            except Exception as e:
                import traceback
                print(f"Inner fillet (arc_inner4+line2) failed at z={z:.4f}: {e}")
                traceback.print_exc()

        profile = sketch2d.Profiles.AddForSolid()
        sections.Add(profile)



    #Define Last point2 (z = z_lipid_R)
    y2 = y_center_lumen(model, model.z_lipid_R) + radius_lumen(model, model.z_lipid_R) + fc_thickness
    point2 = model.tg.CreatePoint(0, y2, model.z_lipid_R)
    point2_sk = centerline_sketch.SketchPoints3D.Add(point2)
    sections.Add(point2_sk)


    ##############################################
    ################# Lofting ####################
    ##############################################

    #define lofting OBJECT.
    loftFeatures = model.part_def.Features.LoftFeatures
    loftDef = loftFeatures.CreateLoftDefinition(sections, 20485) #20485-> body, 20484-> surface

    #define planes for the tangential lofting.
    # tangent_plane1 = model.part_def.WorkPlanes.AddByPlaneAndPoint(xy_plane, point1_sk, False)
    # tanget_plane3 = model.part_def.WorkPlanes.AddByPlaneAndPoint(xy_plane, point2_sk, False)
    # tangent_plane1.Visible = True
    # tanget_plane3.Visible = True

    #First and last point conditions.(use 34309 -> sharp point, 34306 -> tangent point, 34310 -> tangent plane)
    loftDef.FirstSectionCondition = 34306
    loftDef.LastSectionCondition = 34306
    loftDef.FirstSectionImpact = 2.0
    loftDef.LastSectionImpact = 2.0
    # loftDef.FirstSectionTangentPlane = tangent_plane1
    # loftDef.LastSectionTangentPlane = tanget_plane3

    #Merge tangent faces option.
    loftDef.MergeTangentFaces = True

    #lofting execute.
    try:
        loft_object = loftFeatures.Add(loftDef) #Lofting execute
        loft_object.Name = "lipid"
    except Exception as e:
        print("Lofting failed with Tangental points:", e)
        try:
            loftDef.FirstSectionCondition = 34309
            loftDef.LastSectionCondition = 34309
            loft_object = loftFeatures.Add(loftDef) #Lofting execute
            loft_object.Name = "lipid"

        except Exception as e:
            import traceback
            print("Lofting failed:", e)
            traceback.print_exc()
            return None



    ##############################################
    ################# Save files #################
    ##############################################
    step_path = os.path.join(save_folder_path, "lipid.stp")
    ipt_path = os.path.join(save_folder_path, "lipid.ipt")

    lipid_doc.SaveAs(ipt_path, True)
    save_as_step(model, lipid_doc, step_path) #save as step from utils.py
    print(f"✅ Completely save file: {step_path}")
    lipid_doc.Close(model.close_CAD)

    return step_path