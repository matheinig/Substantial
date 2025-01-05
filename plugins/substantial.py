from PySide6 import QtWidgets 
from substance_painter import ui
from substance_painter import project
from substance_painter import event
from substance_painter import textureset
from substance_painter import js
import os
 
isNewProject = False
def onNewProject(e):
    # Can't actually do anything just yet as the project hasn't really been processed by painter yet
    global isNewProject
    isNewProject = True
    return
def onProjectReady(e):
    global isNewProject
    if isNewProject: 
        onNewProjectReady()
    else:
        onOldProjectReady()
    isNewProject = False
    return

def onNewProjectReady():
    # Find the highpoly file
    lowpolyFile = project.last_imported_mesh_path()
    highpolyFile = lowpolyFile.replace("_low.fbx", "_high.fbx")
    
    # Change some improtant settings to something I like more (inlcuding the highpoly file)
    for texset in textureset.all_texture_sets():
        # is it me or there are still no baker settings in the python bindings?
        # do we really have to go through javascript???
        leEpicJsCommand = """
        var bp = alg.baking.textureSetBakingParameters("{0}")
        bp.materialParameters.detailParameters.Antialiasing = "Supersampling 4x"
        bp.materialParameters.detailParameters.Match = "By Mesh Name"
        bp.definitions["Ambient_occlusion"].parameters.Ignore_Backface = "By Mesh Name"
        bp.definitions["Bent_normals"].parameters.Ignore_Backface = "By Mesh Name"
        bp.materialParameters.detailParameters.High_Definition_Meshes = ["{1}"]
        alg.baking.setTextureSetBakingParameters("{0}", bp)
        alg.log.warn(bp)
        """.format(texset.name(), highpolyFile)
        js.evaluate(leEpicJsCommand)
        print("[Substantial] Initialised the project settings")

    return
def onOldProjectReady():
    # TODO: maybe convert the high poly mesh path to a local path so that the project can easily be shared (or do it at save time?)
    return


def start_plugin(): 
    # Connect our callbacks to painter
    connections = {
        event.ProjectCreated: onNewProject,
        event.ProjectEditionEntered: onProjectReady
    }
    for evt, callback in connections.items(): 
        event.DISPATCHER.connect(evt, callback) 
 
def close_plugin(): 
    return
if __name__ == "__main__": 
    start_plugin() 

# class substance_painter.event.
# ProjectCreated