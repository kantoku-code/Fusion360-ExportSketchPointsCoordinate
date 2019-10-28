#FusionAPI_python ExportSketchPointsCoordinate Ver0.0.1
#Author-kantoku
#Description-Export SketchPoints Coordinate to CSVfile

import adsk.core, adsk.fusion, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        des = adsk.fusion.Design.cast(app.activeProduct)
        
        #displayed sketches
        skts = [skt
                for comp in des.allComponents if comp.isSketchFolderLightBulbOn
                for skt in comp.sketches if skt.isVisible]

        #all sketchPoint
        sktPnts = []
        for skt in skts:
            for sktPnt in skt.sketchPoints[1:]:
                sktPnts.append(sktPnt)

        if len(sktPnts) < 1:
            ui.messageBox('There are no points to export')
            return

        #export filepath
        path = Get_Filepath(ui)
        if path is None:
            return
        
        #extension_method
        adsk.fusion.SketchPoint.toRootPosition = GetRootPosition

        #get 3D coordinate values
        posLst = [sktPnt.toRootPosition() for sktPnt in sktPnts]

        #Convert Unit
        convUnit = GetUnitCoefficient(des)
        
        posLst = list([(str(x * convUnit), str(y * convUnit), str(z * convUnit))
                    for (x,y,z) in posLst])

        #save
        ExportFile(path,posLst)

        #finish
        ui.messageBox('Done')
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

#adsk.fusion.SketchPoint extension_method
def GetRootPosition(self):
    skt = adsk.fusion.Sketch.cast(self.parentSketch)
    comp = adsk.fusion.Component.cast(skt.parentComponent)
    root =  comp.parentDesign.rootComponent

    if comp == root:
        pnt3d = self.worldGeometry
    else:
        pnt3d = self.worldGeometry.copy()
        occs = GetParentOccurrenceList(comp)
        mat3ds = [occ.transform for occ in occs]
        for mat3d in mat3ds:
            pnt3d.transformBy(mat3d)

    return [pnt3d.x, pnt3d.y, pnt3d.z]

def GetParentOccurrenceList(comp):
    comp = adsk.fusion.Component.cast(comp)
    des = adsk.fusion.Design.cast(comp.parentDesign)
    root =des.rootComponent

    if root == comp:
        return None

    occs = root.allOccurrencesByComponent(comp)
    if len(occs) < 1:
        return None

    occ = occs[0]
    occ_names = occ.fullPathName.split('+')
    occs = [root.allOccurrences.itemByName(name) 
                for name in occ_names]

    return occs

def Get_Filepath(ui):
    dlg = ui.createFileDialog()
    dlg.title = 'SketchPoints_Export_CSV'
    dlg.isMultiSelectEnabled = False
    dlg.filter = 'CSV(*.csv)'
    if dlg.showSave() != adsk.core.DialogResults.DialogOK :
        return

    return dlg.filename

def GetUnitCoefficient(des):
    unitsMgr = des.unitsManager
    defLenUnit = unitsMgr.defaultLengthUnits

    return unitsMgr.convert(1, unitsMgr.internalUnits, defLenUnit)

def ExportFile(path, lst):
    import csv

    f = open(path, 'w')
    writer = csv.writer(f, lineterminator='\n')
    writer.writerows(lst)
    f.close()