import json
from types import SimpleNamespace

class ConfigLoader:
    def __init__(self, debug):
        self.debug = debug

    def loadConfig(filename):
        try:
            with open(filename, "r") as file:
                rawJsonData = file.read()
                configObject = json.loads(
                    rawJsonData, object_hook=lambda d: SimpleNamespace(**d)
                )
            return configObject
        except Exception as e:
            self.debug.log(f"Error loading JSON config: {e}", forceLog=True)
            return None

