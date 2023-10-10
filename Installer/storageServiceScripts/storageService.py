#####################################
# #        STORAGE SERVICE        # #
#####################################

from ConfigLoader import ConfigLoader
from debugger import debugger
from FileActionsStorage import FileActionsStorage
import json
from JsonValidator import JsonValidator
import os


class StorageService:
    def __init__(self):
        self._initConfig()
        self.FileActionsStorage = FileActionsStorage(self.Config.FileActionDatabasePath)

    def _initConfig(self):
        #  Set the debugger print option
        self.DEBUG_ON = True

        # Generate the script name without the file extension
        self.ScriptName = os.path.splitext(os.path.basename(__file__))[0]

        # Define a configuration file name using the script name
        configFile = f"{self.ScriptName}.config.json"

        # Load the JSON configuration using ConfigLoader
        self.Config = ConfigLoader.loadConfig(configFile)

        #  Initialize the debugger printer
        self.Debug = debugger(self.DEBUG_ON)

        #  Check to make sure the Config didn't blow up...
        if not self.Config:
            e = Exception(f"Failed to load JSON config!\n'{configFile}'")
            self.Debug.log(e, forceLog=True)
            raise e

        #  Reset the DEBUG_ON setting to whatever is in the config...
        self.DEBUG_ON = self.Config.DebugOn

        #  Reinitialize the debugger printer...
        self.Debug = debugger(self.DEBUG_ON)

    def _validateJson(self, itemJson: dict):
        if not JsonValidator.isValidJson(json.dumps(itemJson)):
            httpEx = Exception(status_code=400, detail="Invalid JSON structure")
            self.Debug.log(httpEx, forceLog=True)
            raise httpEx

    def storeItem(self, itemJson: dict):
        try:
            # Validate JSON integrity
            print(itemJson)
            self._validateJson(itemJson)
            retVal = self.FileActionsStorage.addFileActionFromJson(itemJson)
        except Exception as e:
            # Handle any other errors here and return as a JSON response
            retVal = {"error": str(e)}
        return retVal

    def findAvailableProcessTarget(self, itemJson: dict):
        retVal = self.FileActionsStorage.getIncompleteRecordSetsFromJson(itemJson)

        return {"availableRecords": retVal}

    def getFileActionsByStorageId(self, itemJson: dict):
        retVal = self.FileActionsStorage.getByStorageIdValueFromJson(itemJson)

        return retVal


if __name__ == "__main__":
    from MinuteCodes import MinuteCodes
    from DateTimeConverter import DateTimeConverter

    StorageService = StorageService()

    payload = {
        "storageId": None,
        "action": "store",
        "result": "successful",
        "contentType": "video",
        "minuteCodes": [],
        "description": "fake file that refers to nothing",
        "filePath": "",
    }

    for i in range(1, 24, 1):
        minCodes = MinuteCodes.getCurrentBlockOfCodes()
        payload["action"] = "store"
        payload["storageId"] = DateTimeConverter.getBase26TimeStamp()
        payload["minuteCodes"] = minCodes
        payload["filePath"] = f"/home/diyaqua/Videos/{minCodes[0]}.m4v"
        result = StorageService.storeItem(payload)
        if i % 3 == 0:
            payload["action"] = "ioa"
            StorageService.storeItem(payload)
        if i % 100 == 0:
            print(f"Record count: {i}")

    payload = {"criteria": ["store", "ioa"], "contentType": "video"}

    results = StorageService.findAvailableProcessTarget(payload)

    print(results)
