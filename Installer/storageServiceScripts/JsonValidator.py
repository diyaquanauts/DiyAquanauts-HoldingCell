import json


class JsonValidator:
    @staticmethod
    def isValidJson(jsonString):
        try:
            json.loads(jsonString)
            return True
        except json.JSONDecodeError:
            return False
