'''
Created on 29 Jul 2016
 
@author: BenjiA
 
About:
This tool rotates a UV shell so that it is oriented 90 degrees orthogonal to the edge that you select
If you want to align a shell to the vector between two UVs, just select the two UVs and run the tool
 
Use:
Select an edge, or two UVs and run the tool
 
Special thanks:
Thanks to Owen Burgess for supplying his script 'findUvShells()' which I modified in order to make this tool work, 
available here: mayastation.typepad.com/maya-station/2011/03/how-many-shells-in-a-uv-set-.hmtl
 
'''
 
import maya.OpenMaya as om;
import pymel.core as pm;
 
degrees = None;
 
def GetSel():
    #Get the selected edge
    sel = pm.selected();
    if not sel:
        raise RuntimeError('Select an edge or a face, and run the tool again');
    else:
        selType = pm.nodeType(sel);
        #make sure its an edge by converting it to an edge
        selEdge = pm.polyListComponentConversion(te=1);
        return selEdge[0];
 
def GetVectors():
    global degrees;
    sel = GetSel();
    #convert the edge selection to uvs
    selUVs = pm.polyListComponentConversion(tuv=1);
    #flatten the uv selection so that adjacent UV IDs become separate list entries
    selUVs = pm.ls(selUVs, fl=1);
    if len(selUVs) < 2:
        raise RuntimeError('Select a face or an edge with more connected UV point');
    else:
        print 'selUvs is' + str(selUVs);
        #get the two UV points individually
        UV0 = pm.polyEditUV(selUVs[0], query=1, u=1, v=1);
        UV1 = pm.polyEditUV(selUVs[-1], query=1, u=1, v=1);
        #work out the vector that represents the edge between the UV points
        edgeVect = pm.datatypes.Vector((UV0[0] - UV1[0]), (UV0[1] - UV1[1]));
        #normalize it
        edgeVect = edgeVect.normal();
        #get the vector orthogonal to the edge vector
        orthVect = pm.datatypes.Vector(-edgeVect[1], edgeVect[0]);
        #normalize it
        orthVect = orthVect.normal();
        #calculate the arctangent of the orthogonal vector
        atan = pm.datatypes.atan2(orthVect[1], orthVect[0]);
        #convert the arctangent to degrees
        degrees = pm.datatypes.degrees(atan);
        pm.select(sel);
        findUVShellFromID(getSelectedUVIDs());
 
#you have to select UVs for this method to work
def getSelectedUVIDs():
    #store the inital edge selection so that we can access it later
    initEdge = cmds.ls(sl=1);
    #convert the selection to uvs
    uvs = pm.polyListComponentConversion(tuv=1);
    pm.select(uvs);
    #get the selection and set up an iterator
    list = om.MSelectionList();
    om.MGlobal.getActiveSelectionList(list);
    listIter = om.MItSelectionList(list);
    #arrays for DAG paths and compnents
    paths = om.MDagPathArray();
    comps = om.MObjectArray();
    uvIDs = [];
     
    for i in range(list.length()):
        path = om.MDagPath();
        comp = om.MObject();
        stat = list.getDagPath(i, path, comp);
        #room for an if python exception here, instead of MStatus
        paths.append(path);
        comps.append(comp);
    #man i really have no idea what this does but it doesn't work if you remove it
    for i in range(paths.length()):
        if comps[i]:
            compFn = om.MFnSingleIndexedComponent(comps[i]);
            if compFn.componentType() == om.MFn.kMeshMapComponent:
                uvIDs = om.MIntArray();
                compFn.getElements(uvIDs);
    pm.polyListComponentConversion(te=1);    
    pm.select(initEdge); 
    return uvIDs;
        
def findUVShellFromID(_IDs, uvSet='map1'):
  #get the selection and set up an iterator again
  selList = om.MSelectionList()
  om.MGlobal.getActiveSelectionList(selList)
  selListIter = om.MItSelectionList(selList, om.MFn.kMeshEdgeComponent)  
  uvShellArray = om.MIntArray() 
  IDShells = [];
   
  #step through the objects on our selection list
  while not selListIter.isDone():
    pathToShape = om.MDagPath();
    selListIter.getDagPath(pathToShape);
    meshNode = pathToShape.fullPathName();
    #continue only if the given UV set exists on the shape
    uvSets = cmds.polyUVSet(meshNode, query=True, allUVSets=True)
     
    if (uvSet in uvSets):
      shapeFn = om.MFnMesh(pathToShape);  
      shells = om.MScriptUtil();
      shells.createFromInt(0);
      shellsPtr = shells.asUintPtr();  
      shapeFn.getUvShellsIds(uvShellArray, shellsPtr, uvSet);
       
      for i in range(len(_IDs)):
           IDShells.append(uvShellArray[_IDs[i]]);
            
    #uvShellArray.clear();
    selListIter.next();
  return selectShellByIndex(IDShells[0], uvShellArray, meshNode);
  #return IDShells;
   
def selectShellByIndex(_shellIndex, _uvShellArray, _meshNode):
    #using the shell ID, select all the UVs with that shell ID
    UVIDList = [];
    for i in range(_uvShellArray.length()):
        if _uvShellArray[i] == _shellIndex:
            UVIDList.append(i);
    pm.select(cl=1);
    #make it select the uvs one by one in the for loop 
    for i in range(len(UVIDList)):
        selUVs = pm.select(_meshNode+'.map['+str(UVIDList[i])+']', add=1);
    pm.polyEditUV(a=-degrees);
    pm.select(cl=1);
    for i in range(len(UVIDList)):
        selUVs = pm.select(_meshNode+'.map['+str(UVIDList[i])+']', add=1);
    pivCentre = pm.getAttr(_meshNode+'.uvPivot')
    faces = pm.polyListComponentConversion(tf=1);
    pm.select(faces);
    pm.polyEditUV(u=-pivCentre[0]+0.5,v=-pivCentre[1]+0.5);
    pm.setAttr(_meshNode+'.uvPivot', [0.5, 0.5]);
     
GetVectors();