#####################################
##         STORAGE SERVICE         ##
#####################################

from datetime import datetime
from fastapi import FastAPI, HTTPException
import json
import numpy as np
import os
import pickle
import time
from types import SimpleNamespace

DEBUG_ON = True

class debugger:
    @staticmethod
    def log(msg):
        global DEBUG_ON
        if (DEBUG_ON):
            print(msg)

    @staticmethod
    def line(lineChar="-"):
        global DEBUG_ON
        if (DEBUG_ON):
            print(lineChar * 40)

debug = debugger()

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
            debug.log(f"Error loading JSON config: {e}")
            return None


# Generate the script name without the file extension
scriptName = os.path.splitext(os.path.basename(__file__))[0]

# Define a configuration file name using the script name
configFile = f"{scriptName}.config.json"

# Load the JSON configuration using ConfigLoader
config = ConfigLoader.loadConfig(configFile)
if not config:
    raise Exception("Failed to load JSON config")

# Initialize FastAPI
app = FastAPI()

# Various utility classes and methods
class JsonValidator:
    @staticmethod
    def isValidJson(jsonString):
        try:
            json.loads(jsonString)
            return True
        except json.JSONDecodeError:
            return False



class JsonConvertor:
    @staticmethod
    def jsonToDotNotation(jsonObj, parentKey="", separator="."):
        result = {}
        for key, value in jsonObj.items():
            newKey = f"{parentKey}{separator}{key}" if parentKey else key
            if isinstance(value, dict):
                result.update(JsonConvertor.jsonToDotNotation(value, newKey, separator))
            else:
                result[newKey] = value
        return result


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
            timeToBaseX = alphabet[remainder] + timeToBaseX
            nanoseconds //= xBase
        return timeToBaseX


"""
# Example usage:
from datetime import datetime

dt = datetime.now()
base26_result = DateTimeConverter.nanosecondsToBaseX(dt)
debug.log(base26_result)
"""


class IndexMerger:
    @staticmethod
    def mergeDictionaries(left, right):
        if (left is None):
            left = right
        elif (right is None):
            sortedDict = left
        else:
            for key, value in right.items():
                if key not in left:
                    left[key] = value
                else:
                    for item in value:
                        if item not in left[key]:
                            left[key].append(item)

            sortedDict = dict(sorted(left.items()))

        return sortedDict


class DictionarySaver:
    @staticmethod
    def saveDictAsFile(dictionary, filename):
        try:
            with open(filename, "wb") as file:
                pickle.dump(dictionary, file, protocol=pickle.HIGHEST_PROTOCOL)
            return True
        except Exception as e:
            debug.log(f"Error saving dictionary to file: {e}")
            return False


app = FastAPI()

indexFile = "storeIndex.pkl"


@app.post("/store")
async def storeItem(itemJson: dict):
    try:
        # Validate JSON integrity
        if not JsonValidator.isValidJson(json.dumps(itemJson)):
            raise HTTPException(status_code=400, detail="Invalid JSON structure")

        # Get the current date and time in base26 format
        timeStampNs = time.time_ns()
        storeId = DateTimeConverter.nanosecondsToBaseX(timeStampNs)

        debug.log(f"timeStampNs: {timeStampNs}")
        debug.log(f"storeId: {storeId}")

        # Convert JSON to dot notation
        dotJson = JsonConvertor.jsonToDotNotation(itemJson)

        debug.log(f"dotJson:\n{dotJson}")
        debug.line()
        debug.log("Creating JSON paths...")
        # Create JSON structure from predefined paths
        jsonPaths = ["storeId", "actions", "index", "body"]
        jsonStructure = JsonCreator.createJsonFromPaths(jsonPaths)

        debug.log("Setting JSON structure...")
        # Update the JSON structure with new values
        updates = {
            "storeId": storeId,
            "actions": [{"stored": timeStampNs}],
            "index": dotJson,
            "body": itemJson,
        }

        debug.log(f"update structure:\n{updates}")
        debug.line()

        debug.log("Updating JSON structure...")
        indexedJson = JsonUpdater.updateJson(jsonStructure, updates)

        debug.log(f"indexedJson:\n{indexedJson}")
        debug.line()

        debug.log("Checking on storeIndex file existence...")
        # Check if the file exists
        if not os.path.exists(indexFile):
            debug.log("Creating empty storeIndex!!!")
            # Create an empty dictionary
            storeIndex = {}
            DictionarySaver.saveDictAsFile(storeIndex, indexFile)

        debug.log("Loading the storeIndex...")
        # Load the existing storeIndex from a file
        storeIndex = pickle.load(open(indexFile, "rb"))

        debug.log(f"storeIndex after load:\n{storeIndex}")
        debug.line()

        debug.log("Merging the storeIndex and the indexedJson...")
        # Merge the JSON structure with the updates
        storeIndex = IndexMerger.mergeDictionaries(storeIndex, indexedJson)

        debug.log(f"storeIndex after merge:\n{storeIndex}")
        debug.line()

        debug.log("Setting the JSON filename...")
        # Save the JSON structure as a file with the storeId as the filename
        storeFilename = f"{storeId}.json"

        debug.log("Saving the JSON file...")
        with open(storeFilename, "w") as jsonFile:
            json.dump(indexedJson, jsonFile)

        debug.log("Saving the storeIndex file...")
        # Save the storeIndex as a file
        if DictionarySaver.saveDictAsFile(storeIndex, indexFile):
            debug.log(f"Dictionary saved as {storeFilename}")
        else:
            debug.log("Failed to save dictionary")

        debug.log("SUCCESS!!!")
        # If everything is successful, return a response
        retVal = {"status": "stored", "StoreId": storeId}

    except Exception as e:
        # Handle any other errors here and return as a JSON response
        retVal = {"error": str(e)}

        return retVal
