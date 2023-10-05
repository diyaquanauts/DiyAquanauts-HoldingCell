###################################
##         QUERY SERVICE         ##
###################################

from FileMonitor import FileMonitor
import IndexSearch
import json
import os
import re
import time

from ConfigLoader import ConfigLoader
from debugger import debugger
from JsonValidator import JsonValidator
from DateTimeConverter import DateTimeConverter
from IndexOperations import IndexOperations

#  Set the default debugger print option
DEBUG_ON = False

# Generate the script name without the file extension
scriptName = os.path.splitext(os.path.basename(__file__))[0]

# Define a configuration file name using the script name
configFile = f"{scriptName}.config.json"

# Load the JSON configuration using ConfigLoader
config = ConfigLoader.loadConfig(configFile)

DEBUG_ON = config.DebugOn

#  Initialize the debugger printer
debug = debugger(DEBUG_ON)

if not config:
    e = Exception(f"Failed to load JSON config!\n'{configFile}'")
    debug.log(e, forceLog=True)
    raise e

# jDots = jdots()

# Set the index file
indexFilePath = config.IndexFile

IndexOperations = IndexOperations(config)


class QueryService:
    def __init__(self):
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
        global debug
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
