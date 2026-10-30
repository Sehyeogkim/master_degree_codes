import math
import numpy as np
import os
from .utils_CAD import *


def lipid_sub_step(model, save_folder_path):
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
    y1 = y_center_lumen(model, model.z_lipid_L) + radius_lumen(model, model.z_lipid_L)
    point1 = model.tg.CreatePoint(0, y1, model.z_lipid_L)
    point1_sk = centerline_sketch.SketchPoints3D.Add(point1)
    sections.Add(point1_sk)
    
    #Profiles for the left and right side.
    '''
    @updated 20251121 jeff
    - exclude the profile back and forth of the two points.
    '''
    z_profile_L = np.linspace(model.z_lipid_L, model.z_peak, 4, endpoint=False)[2:] #Modfied
    z_profile_R = np.linspace(model.z_peak, model.z_lipid_R, 3, endpoint=False)[:-1] #Modfied
    z_profile = np.concatenate([z_profile_L, z_profile_R])
    

    xy_plane = model.part_def.WorkPlanes.Item("XY Plane")
    

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


        #Points for 3 arcs and 2 lines.
        center_lesion = model.tg.CreatePoint2d(0, y_center_lesion(model,z))
        start = model.tg.CreatePoint2d(x_β, y_β)  
        intermediate1 = model.tg.CreatePoint2d(x_θ, y_θ)
        intermediate2 = model.tg.CreatePoint2d(-x_θ,y_θ)
        end = model.tg.CreatePoint2d(-x_β, y_β)
        center_lumen = model.tg.CreatePoint2d(0, y_center_lumen(model,z))

        
        #DRAW POINTS ON THE SKETCH.
        center_lesion_sk = sketch2d.SketchPoints.Add(center_lesion)
        start_sk = sketch2d.SketchPoints.Add(start)
        intermediate1_sk = sketch2d.SketchPoints.Add(intermediate1)
        intermediate2_sk = sketch2d.SketchPoints.Add(intermediate2)
        end_sk = sketch2d.SketchPoints.Add(end)
        center_lumen_sk = sketch2d.SketchPoints.Add(center_lumen)


        #Draw An External Arc and 2 lines.
        line1 = sketch2d.SketchLines.AddByTwoPoints(center_lumen_sk, start_sk)
        arc1 = sketch2d.SketchArcs.AddByCenterStartEndPoint(center_lesion_sk, start_sk, intermediate1_sk)
        arc2 = sketch2d.SketchArcs.AddByCenterStartEndPoint(center_lesion_sk, intermediate1_sk, intermediate2_sk)
        arc3 = sketch2d.SketchArcs.AddByCenterStartEndPoint(center_lesion_sk, intermediate2_sk, end_sk)
        line2 = sketch2d.SketchLines.AddByTwoPoints(center_lumen_sk, end_sk)


        #Safe fillet radius
        safe_ratio = 0.5
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
    

        profile = sketch2d.Profiles.AddForSolid()
        sections.Add(profile)



    #Define Last point2 (z = z_lipid_R)
    y2 = y_center_lumen(model, model.z_lipid_R) + radius_lumen(model, model.z_lipid_R)
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


    ###NEW code in here
    '''
    1(done). lipid lofting is done.
    2. derive fc.ipt file on the current same working dir as lipid.ipt
    3. and then, combine (boolean lipid - fc)
    4. fillet the edges -> 0.01cm plz.
    '''

    # ----- Step 2: derive fc.ipt -----
    fc_ipt_path = os.path.join(save_folder_path, "fc.ipt")
    derived_comps = model.part_def.ReferenceComponents.DerivedPartComponents
    derived_def   = derived_comps.CreateUniformScaleDef(fc_ipt_path)
    derived_comps.Add(derived_def)
    print(f"[OK] Derived fc.ipt: {fc_ipt_path}")

    # ----- Step 3: boolean cut (lipid - fc) -----
    trans_objs = model.inv.TransientObjects
    lipid_body = model.part_def.SurfaceBodies.Item(1)   # lipid (target)
    fc_body    = model.part_def.SurfaceBodies.Item(2)   # fc (tool)

    # Snapshot original lipid face InternalNames (used later to identify boundary edges)
    original_face_keys = set()
    for face in lipid_body.Faces:
        original_face_keys.add(face.InternalName)

    tool_bodies = trans_objs.CreateObjectCollection()
    tool_bodies.Add(fc_body)

    combine_features = model.part_def.Features.CombineFeatures
    combine_features.Add(lipid_body, tool_bodies, 20482)   # 20482 = cut
    print("[OK] Boolean cut: lipid - fc")

    # ----- Step 4: identify boundary edges & apply 0.01 cm fillet -----
    combined_body = model.part_def.SurfaceBodies.Item(1)

    # Iterate body.Edges directly (each edge appears once; no dedup needed).
    # An edge is on the boolean boundary iff exactly one of its two adjacent
    # faces was present BEFORE the cut (i.e., InternalName in original_face_keys).
    # NOTE: FilletFeatures requires an EdgeCollection (not ObjectCollection).
    fillet_edges = trans_objs.CreateEdgeCollection()
    for edge in combined_body.Edges:
        adj_originals = sum(1 for f in edge.Faces if f.InternalName in original_face_keys)
        if adj_originals == 1:
            fillet_edges.Add(edge)

    print(f"[OK] Identified {fillet_edges.Count} fillet-target edges")

    if fillet_edges.Count > 0:
        fillet_features = model.part_def.Features.FilletFeatures
        try:
            # AddSimple(EdgeCollection, Radius) — direct, simplest path.
            fillet_features.AddSimple(fillet_edges, 0.01)
            print("[OK] Edge fillet 0.01 cm applied via AddSimple")
        except Exception as e:
            # Fallback: definition-based API (kEdgeFilletType = 1).
            try:
                fillet_def = fillet_features.CreateFilletDefinition(1)
                edge_set   = fillet_def.EdgeSetDefinitions.AddConstantRadiusEdgeSet(0.01)
                edge_set.EdgeCollection = fillet_edges
                fillet_features.Add(fillet_def)
                print("[OK] Edge fillet via FilletDefinition")
            except Exception as e2:
                import traceback
                print(f"[WARN] Edge fillet failed: AddSimple={e}; Definition={e2}")
                traceback.print_exc()



    ##############################################
    ################# Save files #################
    ##############################################
    step_path = os.path.join(save_folder_path, "lipid.stp")
    ipt_path = os.path.join(save_folder_path, "lipid.ipt")

    lipid_doc.SaveAs(ipt_path, True)

    # Option 2: Document.SaveAs directly (bypasses ApplicationAddIns translator path).
    # The translator add-in path (translator.SaveCopyAs) hangs on fillet blend surfaces;
    # Document.SaveAs to .stp uses Inventor's built-in export route which often differs.
    lipid_doc.SaveAs(step_path, True)

    print(f"[OK] Completely save file: {step_path}")
    lipid_doc.Close(model.close_CAD)

    return step_path