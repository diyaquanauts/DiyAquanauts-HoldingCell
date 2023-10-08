import json
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

    def send(self, httpVerb, url, payloadObj, headers={}, query_parameters=""):
        # The 'indent' parameter is optional for pretty formatting
        jsonPayload = json.dumps(payloadObj, indent=4)

        if(httpVerb == "GET"):
            responseData = self.get(url, jsonPayload, headers, query_parameters)
        elif(httpVerb == "POST"):
            responseData = self.post(url, jsonPayload, headers, query_parameters)
        else:
            # You ding dong! That ain't nothig we can use!
            responseData = "INVALID HTTP VERB!"

        return responseData

# Example usage:
if __name__ == "__main__":
    #  Prep some objects for use...
    from MinuteCodes import MinuteCodes
    from DateTimeConverter import DateTimeConverter

    #  Prep the rest client...
    client = SimpleRestClient()

    #  Prep some variables for use...
    httpVerb = "POST"
    storeUrl = "http://127.0.0.1:5000/store"
    queryUrl = "http://127.0.0.1:5000/requestForProcess"
    minCodes = MinuteCodes.getCurrentBlockOfCodes()

    #  Create a payload to send and append...
    payloadStore = {
        "storageId": None,
        "action": "store",
        "result": "successful",
        "contentType": "video",
        "minuteCodes": minCodes,
        "description": "fake file that refers to nothing",
        "filePath": f"/home/diyaqua/Videos/{minCodes[0]}.m4v"
    }

    #  Loop and add the same package a few times...
    for i in range(1, 3, 1):
        payloadStore["storageId"] = DateTimeConverter.getBase26TimeStamp()
        responseData = client.send(httpVerb, storeUrl, payloadStore)
        storeId = payloadStore["storageId"]
        print(f"'{storeUrl}' Response: \n{responseData}\n{storeId}")
        print()

    #  Prepare an available records query payload...
    payloadQuery = {
        "criteria": ["store", "ioa"],
        "contentType": "video"
    }

    #  Send the available records query...
    responseData = client.send(httpVerb, queryUrl, payloadQuery)

    #  Show the query response...
    print(f"'{queryUrl}' Response:\n{responseData}")
    print()

    for i in range(1, 121, 1):
        #  Grab the available record storageId...
        storageIdToAdd = responseData["availableRecords"][0]

        #  Prep a storage payload...
        payloadStore["storageId"] = storageIdToAdd
        payloadStore["action"] = "ioa"

        #  Send the store request...
        responseData = client.send(httpVerb, storeUrl, payloadStore)
        storeId = payloadStore["storageId"]
        print(f"'{storeUrl}' Response: \n{responseData}\n{storeId}")
        print()

        #  Send the available records query...
        responseData = client.send(httpVerb, queryUrl, payloadQuery)

        #  Show the query response...
        print(f"'{queryUrl}' Response:\n{responseData}")
        print()

        #  The response data above should be different than
        #  the first time it came back...
