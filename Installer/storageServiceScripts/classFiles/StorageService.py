from ConfigLoader import ConfigLoader
from debugger import debugger
from JsonValidator import JsonValidator
from JsonCreator import JsonCreator
from JsonUpdater import JsonUpdater
from DateTimeConverter import DateTimeConverter
from RecordIndexMerger import RecordIndexMerger
from IndexSaver import IndexSaver
from RecordOperations import RecordOperations
from StorageService import StorageService

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


