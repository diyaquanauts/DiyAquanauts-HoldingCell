from DateTimeConverter import DateTimeConverter
import json
from MinuteCodes import MinuteCodes
import requests

class SimpleRestClient:
    def __init__(self):
        self.session = requests.Session()

    def _send_request(self, url, payload, headers={}, queryParameters="", method="GET"):
        params = queryParameters  # Incorporate query parameters
        if method == "GET":
            response = self.session.get(url, headers=headers, data=payload, params=params)
        elif method == "POST":
            response = self.session.post(url, headers=headers, data=payload, params=params)
        else:
            raise ValueError("Unsupported HTTP method")
        return response.json()

    def get(self, url, payload, headers={}, queryParameters=""):
        return self._send_request(url, payload, headers, queryParameters, method="GET")

    def post(self, url, payload, headers={}, queryParameters=""):
        return self._send_request(url, payload, headers, queryParameters, method="POST")

    def send(self, httpVerb, url, payloadObj, headers={}, queryParameters=""):
        requestStruct = {
            "httpVerb": httpVerb,
            "headers": headers,
            "url": url,
            "queryParameters": queryParameters,
            "payload": payloadObj
        }

        print("-----------------")
        print(json.dumps(requestStruct, indent=4))
        print("-----------------")

        # The 'indent' parameter is optional for pretty formatting
        jsonPayload = json.dumps(payloadObj, indent=4)

        if(httpVerb == "GET"):
            responseData = self.get(url, jsonPayload, headers, queryParameters)
        elif(httpVerb == "POST"):
            responseData = self.post(url, jsonPayload, headers, queryParameters)
        else:
            # You ding dong! That ain't nothig we can use!
            responseData = "INVALID HTTP VERB!"

        return responseData

class FileActionApi:
    def __init__(self, baseAddress, port):
        #  Prep some objects for use...
        self.client = SimpleRestClient()

        #  Prep some variables for use...
        self.httpVerb = "POST"
        self.headers = { "Content-Type": "application/json" }

        self.storeUrl = f"http://{baseAddress}:{port}/store"
        self.queryUrl = f"http://{baseAddress}:{port}/requestForProcess"
        self.infoUrl = f"http://{baseAddress}:{port}/getFileActions"

    def storeItem(self, storageId, action, result, contentType, minuteCodes, description, filePath):
        print("Sending store item request...")

        #  Create a storage payload template...
        payloadStore = {
            "storageId": storageId,
            "action": action,
            "result": result,
            "contentType": contentType,
            "minuteCodes": minuteCodes,
            "description": description,
            "filePath": filePath
        }

        responseData = self.client.send(self.httpVerb, self.storeUrl, payloadStore, self.headers)
        print("  -- Response...")
        print(json.dumps(responseData, indent=4))
        print()

        return responseData

    def getItemInfo(self, storageId):
        # Prep an info retrieval request payload...
        infoPayload = { "storageId": storageId }
        print("Sending get item info request...")
        responseData = self.client.send(self.httpVerb, self.infoUrl, infoPayload, self.headers)
        print("  -- Response...")
        print(json.dumps(responseData, indent=4))
        print()

        return responseData

    def getAvailableItem(self, criteria, contentType):
        #  Prepare an available records query payload...
        payloadQuery = {
            "criteria": criteria,
            "contentType": contentType
        }

        print("Sending available item request...")
        #  Send the available records query...
        responseData = self.client.send(self.httpVerb, self.queryUrl, payloadQuery, self.headers)
        print("  -- Response...")
        print(json.dumps(responseData, indent=4))

        return responseData

def _shortTest():
    storeApi = FileActionApi("192.168.8.155","5000")

    minCodes = MinuteCodes.getCurrentBlockOfCodes()
    
    storageId = DateTimeConverter.getBase26TimeStamp()

    results = storeApi.storeItem(storageId, "stored", "successful", "video", minCodes, "Test file - ignore", "/home/diyaqua/Videos/fake.mp4")

    results = storeApi.getItemInfo(storageId)

    results = storeApi.getAvailableItem(["stored", "ioa"], "video")

    storageId = results["availableRecords"][0]

    results = storeApi.storeItem(storageId, "ioa", "successful", "video", minCodes, "Test IoA record - ignore", "/home/diyaqua/Videos/fake.mp4.ioa")

if __name__ == "__main__":
    _shortTest()
