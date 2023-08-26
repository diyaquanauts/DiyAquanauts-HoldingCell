import re

class stringer:
    def __init__(self):
        pass

    def camelToCapCase(self, camelString, joinChar=" "):
        # Replace underscores with spaces and split into words
        words = re.findall(r'[A-Za-z][a-z]*', camelString.replace('_', ' '))

        # Capitalize each word and join with spaces
        capitalized = [word.capitalize() for word in words]
        return joinChar.join(capitalized)

    def _strip(self, source, stripWhitespace):
        retVal = source

        if (stripWhitespace==True):
            retVal = retVal.strip()

        return retVal

    def getLeft(self, source, pattern, stripWhitespace=True):
        retVal = None

        if pattern in source:
            retVal = self._strip(source.split(pattern, 1)[0], stripWhitespace)

        return retVal

    def getRight(self, source, pattern, stripWhitespace=True):
        retVal = None

        if pattern in source:
            retVal = self._strip(source.split(pattern, 1)[1], stripWhitespace)

        return retVal

    def getLeftFromLast(self, source, pattern, stripWhitespace=True):
        retVal = None

        if pattern in source:
            retVal = self._strip(source.rsplit(pattern, 1)[0], stripWhitespace)

        return retVal

    def getRightFromLast(self, source, pattern, stripWhitespace=True):
        retVal = None

        if pattern in source:
            retVal = self._strip(source.rsplit(pattern, 1)[1], stripWhitespace)

        return None

    def getBetween(self, source, patternStart, patternEnd, stripWhitespace=True):
        retVal = None

        start = source.find(patternStart)

        if start != -1:
            end = source.find(patternEnd, start + len(patternStart))
            if end != -1:
                retVal = self._strip(source[start + len(patternStart):end], stripWhitespace)

        return retVal

if __name__ == "__main__":
    stringUtil = stringer()
    '''
    card 1: Device [USB PnP Sound Device], device 0: USB Audio [USB Audio]
    card 2: Camera [Arducam USB Camera], device 0: USB Audio [USB Audio]
    '''

    source = "card 1: Device [USB PnP Sound Device], device 0: USB Audio [USB Audio]"
    patternStart = "["
    patternEnd = "]"

    print("getLeft:", stringUtil.getLeft(source, patternStart))
    print("getRight:", stringUtil.getRight(source, patternEnd))
    print("getLeftFromLast:", stringUtil.getLeftFromLast(source, patternStart))
    print("getRightFromLast:", stringUtil.getRightFromLast(source, patternEnd))
    print("getBetween:", stringUtil.getBetween(source, patternStart, patternEnd))

    deviceInfo = stringUtil.getBetween(source, "card", ":")
    subChannel = stringUtil.getBetween(source, "device", ":")
    deviceName = stringUtil.getBetween(source, "[", "]")

    print(deviceInfo)
    print(subChannel)
    print(deviceName)

    print(f"plughw:{deviceInfo},{subChannel} [{deviceName}]")
