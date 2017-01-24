'''
Created on 16 July 2016

Author: BenjiA (Requested by Ross)

About:
Creates a workplane (construction plane) aligned to a poly face

Use:
Select a poly face and run the code
'''

import pymel.core as pm;
import maya.api.OpenMaya as om;

def GetSel():
    #Get the selected thing and only return it if its a poly face
    sel = pm.selected();
    if len(sel) < 1:
        return None;
    else:
        if pm.nodeType(sel) == 'mesh':            
            return sel[0];

def CreateWorkplaneFromPoly(sel = GetSel()):
    if sel is None:
        raise RuntimeError('Select a polygonal face and then run the tool')
        return;
    else:
        #Get the center of the selected face
        pt = sel.__apimfn__().center(om.MSpace.kWorld);
        selCentre = pm.datatypes.Point(pt);        
        #Create the construction plane at that point
        constPlane = pm.plane(n='ConstructionPlane', p=selCentre, s=10);
        #Create a normal constraint to align the construction plane to the face
        normCons = pm.normalConstraint(sel, constPlane, aim=(0, 0, 1));
        pm.delete(normCons);
        #Make the plane live so that geo will snap to it
        pm.makeLive(constPlane);
        
CreateWorkplaneFromPoly();