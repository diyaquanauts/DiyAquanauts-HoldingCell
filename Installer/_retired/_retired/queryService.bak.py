###################################
##         QUERY SERVICE         ##
###################################

# from datetime import datetime
# from fastapi import HTTPException
from FileMonitor import FileMonitor
import IndexSearch
import inspect
from jdots import jdots
import json

# import numpy as np
import os
import pickle
import re
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
        if DEBUG_ON or forceLog is True:
            lineNum = inspect.currentframe().f_back.f_lineno
            print(f"[{os.path.basename(__file__)}~{lineNum}]: {msg}")

    @staticmethod
    def line(lineChar="-", forceLog=False):
        global DEBUG_ON
        if DEBUG_ON or forceLog is True:
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


class IndexOperations:
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

    @staticmethod
    def reloadIndex(indexFilePath):
        storeIndex = None
        if os.path.exists(indexFilePath):
            debug.log("Loading the storeIndex...")
            storeIndex = pickle.load(open(indexFilePath, "rb"))
            #debug.log(f"storeIndex after load:\n{storeIndex}")
            debug.line()
        else:
            debug.log("No storeIndex found...")

        return storeIndex

class RecordOperations:
    @staticmethod
    def storeJsonRecord(jsonRecord, storeId):
        # Save the JSON structure as a file with the storeId as the filename
        debug.log("Setting the JSON filename...")
        storeFilename = f"{storeId}.json"
        debug.log(f"Saving the JSON file: '{storeFilename}'")
        with open(storeFilename, "w") as jsonFile:
            json.dump(jsonRecord, jsonFile, indent=4)

class QueryService:
    def __init__(self):
        global indexFilePath
        self.fileMon = FileMonitor(config.IndexFile)
        self.storeIndex = IndexOperations.reloadIndex(config.IndexFile)

    def refreshIndex(self):
        if self.fileMon.hasChanged():
            self.storeIndex = IndexOperations.reloadIndex(config.IndexFile)

    def findMatches(self, source, targets):
        matches = []
        for source_index, source_string in enumerate(source):
            for target_index, target in enumerate(targets):
                if isinstance(target, str) and source_string.lower() == target.lower():
                    matches.append((source_index, target_index))
                elif isinstance(target, str) and re.search(
                    target, source_string, re.IGNORECASE
                ):
                    matches.append((source_index, target_index))
        return matches

    def queryRecords(self, itemJson: dict):
        try:
            # Validate JSON integrity
            if not JsonValidator.isValidJson(json.dumps(itemJson)):
                httpEx = HTTPException(status_code=400, detail="Invalid JSON structure")
                debug.log(httpEx, forceLog=True)
                raise httpEx
            self.refreshIndex()

            # Get the current date and time in base26 format
            timeStampNs = time.time_ns()
            queryId = DateTimeConverter.nanosecondsToBaseX(timeStampNs)

            debug.log(f"timeStampNs: {timeStampNs}")
            debug.log(f"queryId: {queryId}")

            retVal = IndexSearch.find(itemJson, self.storeIndex)

        except Exception as e:
            # Handle any other errors here and return as a JSON response
            retVal = {"error": str(e)}

        return retVal


if __name__ == "__main__":
    payload = {
        "MatchPatterns": [
            "(content:*video*)",
            "(Actions.Stored=true)",
            "(Actions.IndexOfActivity=true)|(Actions.IndexOfActivityError=true)",
        ],
        "FilterType": "subtractionSet",
        "RecordSetSize": 1
    }

    query = QueryService()

    result = query.queryRecords(payload)

    print(result)
