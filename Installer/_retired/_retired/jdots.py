import json


class jdots:
    def __init__(self):
        self.delimiter = ":"

    def _flattenDictionary(self, jsonAsDict, root="", accumulator=None):
        prefix = ""

        #  Check to see if there's a root prefix we should be using...
        if len(root) > 0:
            prefix = "{}.".format(root)

        #  Check to see what kind of object got passed into the
        #  function and handle as appropriate...
        if isinstance(jsonAsDict, dict):

            #  Add the magic sauce for dictionaries...
            for k in jsonAsDict.keys():
                accumulator = self._flattenDictionary(
                    jsonAsDict[k], prefix + str(k), accumulator
                )

        elif isinstance(jsonAsDict, list):

            #  Add the magic sauce for lists...
            for i, k in enumerate(jsonAsDict):
                accumulator = self._flattenDictionary(
                    k, prefix + "[" + str(i) + "].", accumulator
                )
        else:

            #  Make sure we're not pumping through a line
            #  that just starts with a plain dot...
            prefix = prefix.rstrip(".")

            #  Check to see if we're dealing with a plain string here...
            if isinstance(jsonAsDict, str):
                jsonAsDict = '"{}"'.format(jsonAsDict)

            #  If we're dealing with Boolean, it needs to be handled
            #  a big differently since converting directly to a string
            #  won't turn out very well...
            elif isinstance(jsonAsDict, bool):
                jsonAsDict = "{}".format(str(jsonAsDict).lower())

            #  Dump the whole flattened schmear into a string...
            # flatDot = "{" + '"{}": {}'.format(prefix, jsonAsDict) + "},"
            flatDot = f"{prefix}{self.delimiter}{jsonAsDict}"

            #  Make sure we didn't inadvertenly wind up with any
            #  double-dot situations...
            flatDot = flatDot.replace("..", ".")

            #  If the accumulator doesn't have anything in yet,
            #  we need to set to a valid zero-length string...
            if accumulator is None:
                accumulator = ""

            #  Append the value of the flatDot to the accumulator...
            accumulator = accumulator + "\n" + flatDot

        #  Return the accumulator.  Since this is a recursive function,
        #  this accumulator value will potentially be appended to the
        #  callers accumulator.  In this way, the contents of the file
        #  are built up one call at a time...
        return accumulator

    def _flattenString(self, jsonAsString, root=""):
        #  Convert the string to a dictionary object...
        tmpJson = json.loads(jsonAsString)

        #  Now flatten the JSON as normal...
        dotted = self._flattenDictionary(tmpJson, root)

        return dotted

    def flatten(
        self, jsonStringOrDict, rootPath="", returnAsDictionary=False, delimiter=":"
    ):
        retVal = ""
        dotJson = ""
        self.delimiter = delimiter

        #  Check to see if this is a dictionary or plain string
        #  JSON object and handle it appropriately...
        if isinstance(jsonStringOrDict, dict):
            dotJson = self._flattenDictionary(jsonStringOrDict, rootPath)
        elif isinstance(jsonStringOrDict, str):
            dotJson = self._flattenString(jsonStringOrDict, rootPath)

        #  Now clean up any potential weirdness that the
        #  conversion process may have caused...
        while dotJson.startswith(" ") or dotJson.endswith(" ") or dotJson.endswith(","):
            dotJson = dotJson.strip(" ")
            dotJson = dotJson.rstrip(",")

        #  Get ready to throw things into either a dictionary or a list...
        retVal = None

        #  Split the dotJson clump into lines and get rid of empties...
        lines = [line for line in dotJson.splitlines() if line.strip()]

        if returnAsDictionary:
        #  Fill the dictionary...
            for line in lines:
                keyVal = line.split(self.delimiter)
                retVal[keyVal[0]] = keyVal[1]
        else:
            retVal = lines

        #  Get the heck outta Dodge...
        return retVal
