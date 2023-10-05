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

