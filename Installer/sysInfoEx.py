import os
import sys

def getSystemModel():
    modelNameFilePath = "/proc/device-tree/model"

    # Check to make sure the model file exists...
    if os.path.isfile(modelNameFilePath) is not True:
        print("Unable to find model file at path!")
        print("   ---> Model filepath: '" + modelNameFilePath + "'")
        sys.exit("      ***   Please check to see if this is a Debian based OS!   ***")

    # Grab the machine model...
    f = open(modelNameFilePath, mode="rt")
    modelName = f.read()
    f.close()
    modelName = modelName.rstrip("\x00")

    print("Detected machine model: '" + modelName + "'...")

    return modelName
