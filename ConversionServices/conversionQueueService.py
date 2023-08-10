import flask
from flask import request, jsonify
import inspect
import json
import logging
import os
from types import SimpleNamespace
from pathlib import Path
import shortuuid
import sys
import time

#########################################################
#  PREPARE SOME LOGGING AND OTHER REQUIRE VARIABLES...
#  
#  Force the CWD to the local path of the script...
#
scriptFullPath = Path(__file__)
localDir = str(scriptFullPath.parent)
filename = os.path.basename(scriptFullPath)
print(localDir)
logFilePath = localDir + "/logs-" + filename + ".log"
cfg = object


#####################################
#  Init the Flask stuff...
#
app = flask.Flask(__name__)
app.config["DEBUG"] = True


#######################################################################
#  Converts a raw JSON blarp into a regular intelligible object...
#
def convertJsonToObject(rawJson):
    rawJsonData = json.dumps(rawJson, indent=4)

    # Parse JSON into an object with attributes corresponding to dict keys.
    newObj = json.loads(rawJsonData, object_hook=lambda d: SimpleNamespace(**d))

    return newObj


#####################################################################
#  Check to see if the the incoming Json body object is valid...
#
def validJsonBody(jsonBody):
    retVal = True
    if not jsonBody or not 'FilePath' in jsonBody:
        retVal = False
    return retVal


###################################
#  Load the config file into 
#  an intelligible object...
#
def loadConfig():
    f = open('conversionQueueService.config.json')
    rawData = json.load(f)
    f.close()
    #rawJsonData = json.dumps(rawData, indent=4)

    # Parse JSON into an object with attributes corresponding to dict keys.
    #cfg = json.loads(rawJsonData, object_hook=lambda d: SimpleNamespace(**d))

    cfg = convertJsonToObject(rawData)
    
    return cfg


#######################################
#  Dump a JSON blarp to a file...
#
def dumpJsonToFile(filePath, rawJson):
    # Writing to sample.json
    with open(filePath, "w") as outfile:
        outfile.write(rawJson)


#################################################
#  Queue a conversion request item...
#  
def queueConversionRequest(filePath):
    timeStamp = time.time_ns()

    newQueueObj ={ 
        "TimeStamp": "{}".format(timeStamp), 
        "FilePath": filePath, 
        "State": "queued",
        "Id": shortuuid.uuid(),
        "Message": "n/a"
    } 

    rawJson = json.dumps(newQueueObj, indent=4)

    global cfg

    targetFilePath = cfg.QueueDirectory + "/" + str(timeStamp) + ".json"
    targetFilePath = os.path.normpath(targetFilePath)

    dumpJsonToFile(targetFilePath, rawJson)

    return rawJson 


#######################
#  API routing...
#
@app.route('/queueConvert', methods=['POST'])
def queueConvert():
    if request.method == 'POST':
        filePath  = ""
        if not validJsonBody(request.json):
            retval = "Error: Improperly formatted JSON body or missing required key field..."
        else:
            filePath = request.json.get('FilePath')
            retVal = queueConversionRequest(filePath)

        return retVal 

#######################################
#  The guts of stuff, I suppose...
#
cfg = loadConfig()

app.run()