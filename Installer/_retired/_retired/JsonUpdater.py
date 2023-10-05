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

