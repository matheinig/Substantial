from PySide6 import QtWidgets 
from substance_painter import ui
from substance_painter import project
from substance_painter import event
from substance_painter import textureset
from substance_painter import js
from substance_painter import logging
from substance_painter import baking
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
        bp = baking.BakingParameters.from_texture_set(texset)
        common_params = bp.common()
        ao_params = bp.baker(baking.MeshMapUsage.AO)
        bn_params = bp.baker(baking.MeshMapUsage.BentNormals)
        id_params = bp.baker(baking.MeshMapUsage.ID)
        baking.BakingParameters.set({
            common_params['HipolyMesh'] : "file:///"+highpolyFile,
            common_params['FilterMethod'] : common_params['FilterMethod'].enum_value('By Mesh Name'),
            common_params['SubSampling'] : common_params['SubSampling'].enum_value('Supersampling 4x'),
            ao_params['IgnoreBackfaceSecondary'] : ao_params['IgnoreBackfaceSecondary'].enum_value('By Mesh Name'),
            bn_params['IgnoreBackfaceSecondary'] : bn_params['IgnoreBackfaceSecondary'].enum_value('By Mesh Name')
        })

    logging.log(logging.INFO, "Substantial", "Initialised the project settings")

    return

def checkAndUpdatePath(originalPath):
    result = originalPath
    searchPath = originalPath.strip("file:///")
    if not os.path.exists(searchPath): 
        logging.log(logging.WARNING, "Substantial", "File "+ searchPath + " not found. ")
        filename = os.path.basename(searchPath.replace('\\', '/'))
        projectFolder = os.path.dirname(project.file_path())
        potentialPath = projectFolder + "/" + filename
        # Replace the file with the new one if it exists on the machine
        if os.path.exists(potentialPath):
            logging.log(logging.WARNING, "Substantial", "\t -> Replaced with "+potentialPath)
            result = potentialPath
    return "file:///"+result

def onOldProjectReady():
    for texset in textureset.all_texture_sets():
        bp = baking.BakingParameters.from_texture_set(texset)
        common_params = bp.common()

        # Check if any file is missing and update their path if they are found next to the project file
        highPolyFilesStr = str(common_params['HipolyMesh'].value())
        if len(highPolyFilesStr)>0:
            highPolyFilesList = highPolyFilesStr.split("|")
            newHighPolyFilesList = []
            for hp in highPolyFilesList:
                path = hp.strip("file:///")
                newHighPolyFilesList.append(checkAndUpdatePath(path))

            highPolyFilesStr = '|'.join(newHighPolyFilesList)
            baking.BakingParameters.set({common_params['HipolyMesh']: highPolyFilesStr})
            highPolyFilesStr = str(common_params['HipolyMesh'].value())

        # Same with cage files
        cageFileStr = str(common_params['CageMesh'].value())
        if len(cageFileStr)>0:
            cageFileStr = checkAndUpdatePath(cageFileStr)
            baking.BakingParameters.set({common_params['CageMesh']: cageFileStr})
    return

def onProjectSaved(e):

    return


def start_plugin(): 
    # Connect our callbacks to painter
    connections = {
        event.ProjectCreated: onNewProject,
        event.ProjectEditionEntered: onProjectReady,
        event.ProjectAboutToSave: onProjectSaved
    }
    for evt, callback in connections.items(): 
        event.DISPATCHER.connect(evt, callback) 
 
def close_plugin(): 
    return
if __name__ == "__main__": 
    start_plugin() 
