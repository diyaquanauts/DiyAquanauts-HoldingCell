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


