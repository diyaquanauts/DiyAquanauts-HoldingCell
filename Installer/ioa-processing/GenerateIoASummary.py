from FileActionApi import FileActionApi
import json
import os
from SimpleObjectCounter2 import IoAGenerator
import sys


def loadJsonConfig(filePath):
    try:
        with open(filePath, "r") as configFile:
            configData = json.load(configFile)
        return configData
    except FileNotFoundError:
        print(f"Error: File {filePath} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON in {filePath}.")
        return None


def parseCommandLineArguments(sysArgV):
    args = {}
    for i in range(1, len(sysArgV), 2):
        if sysArgV[i].startswith("--"):
            args[sysArgV[i].lstrip("--")] = sysArgV[i + 1]
    return args


def setCurrentWorkingDirectory():
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(scriptDir)


def getScriptName():
    scriptNameWithExtension = os.path.basename(__file__)
    scriptName, _ = os.path.splitext(scriptNameWithExtension)
    return scriptName


def isDebugMode():
    return sys.gettrace() is not None


# Usage
if __name__ == "__main__":
    setCurrentWorkingDirectory()

    configFilename = f"{getScriptName()}.config.json"
    config = loadJsonConfig(configFilename)
    storage = FileActionApi(config["hostUrl"], config["hostPort"])

    sysArgV = sys.argv

    if isDebugMode():
        sysArgV = [
            "",
            "--storageId",
            "abbdssdfa",
            "--inputVideoPath",
            "f:/temp/DiyAquanauts-HoldingCell/Installer/ioa-processing/30s-sample-footage-2023-09-01-131920_002.mp4",
            "--frameInterval",
            "3",
            "--outputVideoPath",
            "f:/temp/deleteMe.mp4",
            "--ioaOutputPath",
            "f:/temp/deleteMe.ioa.json",
        ]

    print(" ".join(sysArgV))

    #  --storageId abbdssdfa --inputVideoPath f:/temp/DiyAquanauts-HoldingCell/Installer/ioa-processing/30s-sample-footage-2023-09-01-131920_002.mp4 --frameInterval 3 --outputVideoPath f:/temp/deleteMe.mp4 --ioaOutputPath f:/temp/deleteMe.ioa.json
    args = parseCommandLineArguments(sysArgV)

    # Get named cmdline args...
    storageId = args.get("storageId", None)
    inputVideoPath = args.get("inputVideoPath", None)
    frameInterval = args.get("frameInterval", None)
    outputVideoPath = args.get("outputVideoPath", None)
    fps = args.get("fps", None)
    ioaOutputPath = args.get("ioaOutputPath", None)

    result = None

    if fps is None:
        result = IoAGenerator.generateIndexOfActivity(
            inputVideoPath, int(frameInterval), outputVideoPath, ioaOutputPath
        )
    else:
        result = IoAGenerator.generateIndexOfActivity(
            inputVideoPath, int(frameInterval), outputVideoPath, ioaOutputPath, int(fps)
        )

    print(result)
