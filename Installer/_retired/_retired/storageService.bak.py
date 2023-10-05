#####################################
##         STORAGE SERVICE         ##
#####################################

# from datetime import datetime
# from fastapi import HTTPException
import inspect
from jdots import jdots
import json
# import numpy as np
import os
import pickle
import time
from types import SimpleNamespace

#  Set the debugger print option
DEBUG_ON = False

# JsonConfigLoader class definition (CamelCase)
class ConfigLoader:
    @staticmethod
    def loadConfig(filename):
        try:
            with open(filename, "r") as file:
                rawJsonData = file.read()
                configObject = json.loads(
                    rawJsonData, object_hook=lambda d: SimpleNamespace(**d)
                )
            return configObject
        except Exception as e:
            debug.log(f"Error loading JSON config: {e}", forceLog=True)
            return None

class debugger:
    @staticmethod
    def log(msg, forceLog=False):
        global DEBUG_ON
        if (DEBUG_ON or forceLog is True):
            lineNum = inspect.currentframe().f_back.f_lineno
            print(f"[{os.path.basename(__file__)}~{lineNum}]: {msg}")

    @staticmethod
    def line(lineChar="-", forceLog=False):
        global DEBUG_ON
        if (DEBUG_ON or forceLog is True):
            print(lineChar * 80)

#  Initialize the debugger printer
debug = debugger()

# Generate the script name without the file extension
scriptName = os.path.splitext(os.path.basename(__file__))[0]

# Define a configuration file name using the script name
configFile = f"{scriptName}.config.json"

# Load the JSON configuration using ConfigLoader
config = ConfigLoader.loadConfig(configFile)

DEBUG_ON = config.DebugOn

if not config:
    e = Exception(f"Failed to load JSON config!\n'{configFile}'")
    debug.log(e, forceLog=True)
    raise e

jDots = jdots()

# Set the index file
indexFilePath = "storeIndex.pkl"

# Various utility classes and methods
class JsonValidator:
    @staticmethod
    def isValidJson(jsonString):
        try:
            json.loads(jsonString)
            return True
        except json.JSONDecodeError:
            return False

class JsonCreator:
    @staticmethod
    def createJsonFromPaths(paths):
        result = {}
        for path in paths:
            keys = path.split(".")
            currentDict = result
            for key in keys:
                if key not in currentDict:
                    currentDict[key] = {}
                currentDict = currentDict[key]
        return result

class JsonUpdater:
    @staticmethod
    def updateJson(jsonObj, updates):
        for path, value in updates.items():
            keys = path.split(".")
            currentDict = jsonObj
            for key in keys[:-1]:
                if key not in currentDict:
                    currentDict[key] = {}
                currentDict = currentDict[key]
            currentDict[keys[-1]] = value

class DateTimeConverter:
    @staticmethod
    def nanosecondsToBaseX(nanoseconds, alphabet="abcdefghijklmnopqrstuvwxyz"):
        # Convert nanoseconds to base26
        timeToBaseX = ""

        xBase = len(alphabet) + 1

        while nanoseconds > 0:
            remainder = nanoseconds % xBase
            timeToBaseX = alphabet[remainder - 1] + timeToBaseX
            nanoseconds //= xBase
        return timeToBaseX

class RecordIndexMerger:
    @staticmethod
    def mergeIndexes(left, right):
        debug.log("Merging RIGHT index INTO LEFT index...")
        if (left is None):
            left = right
        elif (right is None):
            sortedDict = left
        elif (not right):
            sortedDict = left
        else:
            try:
                for key, value in right.items():
                    # debug.log(key, value)
                    # isInLeft = key in left
                    # debug.log(isInLeft)
                    if key in left:
                        for item in value:
                            if item not in left[key]:
                                left[key].append(item)
                    else:
                        left[key] = []
                        for item in value:
                            left[key].append(item)
            except Exception as e:
                debug.log(f"mergeIndexes failure!\n{e}", forceLog=True)

            sortedDict = dict(sorted(left.items()))

        return sortedDict

class IndexSaver:
    @staticmethod
    def pickleIndex(dictionary, filename):
        debug.log(f"Pickling the index: '{filename}'")
        try:
            with open(filename, "wb") as file:
                pickle.dump(dictionary, file, protocol=pickle.HIGHEST_PROTOCOL)
            return True
        except Exception as e:
            debug.log(f"Error pickling index!\n{e}", forceLog=True)
            return False

class RecordOperations:
    @staticmethod
    def storeJsonRecord(jsonRecord, storeId):
        # Save the JSON structure as a file with the storeId as the filename
        debug.log("Setting the JSON filename...")
        storeFilename = f"{storeId}.json"
        debug.log(f"Saving the JSON file: '{storeFilename}'")
        with open(storeFilename, "w") as jsonFile:
            json.dump(jsonRecord, jsonFile, indent=4)

class StorageService:
    @staticmethod
    def storeItem(itemJson: dict):
        try:
            # Validate JSON integrity
            if not JsonValidator.isValidJson(json.dumps(itemJson)):
                httpEx = HTTPException(status_code=400, detail="Invalid JSON structure")
                debug.log(httpEx, forceLog=True)
                raise httpEx

            # Get the current date and time in base26 format
            timeStampNs = time.time_ns()
            storeId = DateTimeConverter.nanosecondsToBaseX(timeStampNs)

            debug.log(f"timeStampNs: {timeStampNs}")
            debug.log(f"storeId: {storeId}")

            # Convert JSON to dot notation
            global jDots
            jsonDots = jDots.flatten(itemJson, returnAsDictionary=False)
            jsonIndex = {item: [storeId] for item in jsonDots}

            debug.log(f"jsonIndex:\n{jsonIndex}")
            debug.line()
            debug.log("Creating JSON record...")

            # Create the JSON record with new values

            actions = {}
            actions["indexed"] = True
            actions["stored"] = True

            jsonRecord = {
                "storeId": storeId,
                "actionStamps": [{"indexed": timeStampNs}, {"stored": timeStampNs}],
                "actions": actions,
                "index": jsonDots,
                "body": itemJson,
            }

            debug.log(f"JSON record:\n{jsonRecord}")
            debug.line()

            # Create the action index...
            actionIndex = jDots.flatten(actions, returnAsDictionary=False)
            actionIndex = {item: [storeId] for item in actionIndex}
            metadataIndex = jDots.flatten(itemJson["metadata"], returnAsDictionary=False)
            metadataIndex = {item: [storeId] for item in metadataIndex}

            # Prep an empty dictionary
            storeIndex = {}

            # Check if the file exists and load it if it does...
            # debug.log("Checking on storeIndex file existence...")
            if os.path.exists(indexFilePath):
                debug.log("Loading the storeIndex...")
                storeIndex = pickle.load(open(indexFilePath, "rb"))
                debug.log(f"storeIndex after load:\n{storeIndex}")
                debug.line()
            else:
                debug.log("No storeIndex found...")

            # Merge the JSON structure with the updates
            # storeIndex = RecordIndexMerger.mergeIndexes(storeIndex, jsonIndex)
            storeIndex = RecordIndexMerger.mergeIndexes(storeIndex, actionIndex)
            storeIndex = RecordIndexMerger.mergeIndexes(storeIndex, metadataIndex)
            debug.log(f"storeIndex after merge:\n{storeIndex}")
            debug.line()

            #  Save the JSON record in a file...
            jsonRecordFilePath = RecordOperations.storeJsonRecord(jsonRecord, storeId)

            # Save the storeIndex as a file
            if IndexSaver.pickleIndex(storeIndex, indexFilePath):
                debug.log(f"Index pickled as '{storeIndex}'...")
            else:
                debug.log(f"Failed to save index at '{storeIndex}'!!")

            # If everything is successful, return a response
            debug.log("SUCCESS!!!")
            retVal = {"status": "stored", "StoreId": storeId}

        except Exception as e:
            # Handle any other errors here and return as a JSON response
            retVal = {"error": str(e)}

        return retVal

if __name__ == "__main__":
    from MinuteCodes import MinuteCodes

    payload = {
      "metadata" : { "content": "video" },
      "minuteCodes": [],
      "description": "fake file that refers to nothing",
      "filePath": ""
    }

    for i in range(1, 100, 1):
        minCodes = MinuteCodes.getCurrentBlockOfCodes()
        payload["minuteCodes"] = minCodes
        payload["filePath"] = f"/home/diyaqua/Videos/{minCodes[0]}.m4v"
        result = StorageService.storeItem(payload)
        print(result)
