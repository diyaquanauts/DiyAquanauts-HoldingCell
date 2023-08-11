import flask
from flask import request  # , jsonify
# import inspect
import json
import logging
import os
from types import SimpleNamespace
from pathlib import Path
import shortuuid
# import sys
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
logFilePath = os.path.normpath(logFilePath)
cfg = object

######################################################
#  PREP LOGGER...
#
def prepareLogger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

    #  stdout_handler = logging.StreamHandler(sys.stdout)
    #  stdout_handler.setLevel(logging.DEBUG)
    #  stdout_handler.setFormatter(formatter)

    global logFilePath  
    file_handler = logging.FileHandler(logFilePath)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    #  logger.addHandler(stdout_handler)

    return logger

################################
#  Log a message...
#
def log(msg):
    logger.debug(msg)
    print(msg)

##################################################
#  Initialize the Logger...
#
#  Get the logger set and append the opening message...
logger = prepareLogger()
log("LOG ACTIVATED!")
log("Log file path set to: " + logFilePath)

#####################################
#  Initialize the Flask stuff...
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
    if not jsonBody:  # or "FilePath" not in jsonBody:
        retVal = False
    return retVal


###################################
#  Load the config file into
#  an intelligible object...
#
def loadConfig():
    f = open("conversionQueueService.config.json")
    rawData = json.load(f)
    f.close()

    cfg = convertJsonToObject(rawData)

    rawJsonCfg = json.dumps(cfg.__dict__, indent=4)

    log("Configuration data:")
    log(rawJsonCfg)

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

    newQueueObj = {
        "TimeStamp": "{}".format(timeStamp),
        "FilePath": filePath,
        "State": "queued",
        "Id": shortuuid.uuid(),
        "Message": "n/a",
    }

    rawJson = json.dumps(newQueueObj, indent=4)

    global cfg

    targetFilePath = cfg.QueueDirectory + "/" + str(timeStamp) + ".json"
    targetFilePath = os.path.normpath(targetFilePath)

    dumpJsonToFile(targetFilePath, rawJson)
    
    log("New file queue item: " + str(targetFilePath))
    return rawJson


#######################
#  API routing...
#
@app.route("/queueItem", methods=["GET", "POST"])
def queueItem():
    retVal = ""
    if request.method == "POST" or request.method == "GET":
        if not validJsonBody(request.json):
            retVal = (
                "Error: Improperly formatted JSON body or missing required key field..."
            )
        else:
            retVal = queueConversionRequest(request.json)
        
        log(retVal)
        return retVal


@app.route("/requestQueueItem", methods=["GET", "POST"])
def requestQueueItem():
    retVal = ""
    if request.method == "POST" or request.method == "GET":
        filePath = ""
        if not validJsonBody(request.json):
            retVal = (
                "Error: Improperly formatted JSON body or missing required key field..."
            )
        else:
            filePath = request.json.get("FilePath")
            retVal = queueConversionRequest(filePath)
        
        log(retVal)
        return retVal


#######################################
#  The guts of stuff, I suppose...
#
cfg = loadConfig()
