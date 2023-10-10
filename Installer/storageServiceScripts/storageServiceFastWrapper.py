#####################################
# #        STORAGE WRAPPER        # #
#####################################

import inspect
import os
from flask import Flask, jsonify, request
from storageService import StorageService

# Get the directory where the current script is located
scriptDir = os.path.dirname(os.path.abspath(__file__))

# Set the current working directory to the script directory
os.chdir(scriptDir)

# Initialize Flask
app = Flask(__name__)

storage = StorageService()

#######################
#  MAIN REST SERVICE  #
#######################

def getCallingFuctionName():
    # Get the current frame
    currentFrame = inspect.currentframe()

    # Go back two frames (or as many frames as specified)
    for _ in range(2):
        currentFrame = currentFrame.f_back

    # Use the stack frame to get the name of the calling function
    callerFuncName = currentFrame.f_code.co_name
    return callerFuncName

def handleWebCall(request):
    callerName = getCallingFuctionName()
    print(callerName)
    retVal = None
    try:
        itemJson = request.json
        if not itemJson:
            retVal = {"Error": 400, "Exception": "JSON data is required"}
        else:
            if callerName == "storeItem":
                retVal = storage.storeItem(itemJson)
            elif callerName == "requestForProcess":
                retVal = storage.findAvailableProcessTarget(itemJson)
            elif callerName == "getFileActions":
                retVal = storage.getFileActionsByStorageId(itemJson)
    except Exception as e:
        retVal = {"Error": 500, "Exception": str(e)}
    return retVal

@app.route("/store", methods=["POST"])
def storeItem():
    retVal = handleWebCall(request)
    return retVal

@app.route("/requestForProcess", methods=["POST"])
def requestForProcess():
    retVal = handleWebCall(request)
    return retVal

@app.route("/getFileActions", methods=["POST"])
def getFileActions():
    retVal = handleWebCall(request)
    return retVal

if __name__ == "__main__":
    app.run()
