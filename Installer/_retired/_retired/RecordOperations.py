import json


class RecordOperations:
    @staticmethod
    def storeJsonRecord(jsonRecord, storeId):
        global debug
        # Save the JSON structure as a file with the storeId as the filename
        debug.log("Setting the JSON filename...")
        storeFilename = f"{storeId}.json"
        debug.log(f"Saving the JSON file: '{storeFilename}'")
        with open(storeFilename, "w") as jsonFile:
            json.dump(jsonRecord, jsonFile, indent=4)
