import datetime

class MinuteCodes:
    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base = len(characters)

    @staticmethod
    def _encodeDateChunk(value):
        encoded_value = ""
        while value > 0:
            value, remainder = divmod(value, MinuteCodes.base)
            encoded_value = MinuteCodes.characters[remainder] + encoded_value
        return encoded_value

    @staticmethod
    def _getMinuteCodeFromDateChunks(dateChunks):
        encodedDateChunks = [MinuteCodes._encodeDateChunk(comp) for comp in dateChunks]
        minuteCode = "".join(encodedDateChunks)
        return minuteCode

    @staticmethod
    def _dateTimeToYmdhm(dateTime):
        year = dateTime.year
        month = dateTime.month
        day = dateTime.day
        hour = dateTime.hour
        minute = dateTime.minute

        return [year, month, day, hour, minute]

    @staticmethod
    def generateNextMinuteCodes(minuteCode, count=1):
        yearLen = monthLen = dayLen = hourLen = minuteLen = len(MinuteCodes.characters)

        nextCodes = []
        for _ in range(count):
            yearIndex = minuteCode[:yearLen]

            monthIndex = minuteCode[yearLen : yearLen + monthLen]

            dayIndex = minuteCode[yearLen + monthLen : yearLen + monthLen + dayLen]

            hourIndex = minuteCode[
                yearLen + monthLen + dayLen : yearLen + monthLen + dayLen + hourLen
            ]

            minuteIndex = minuteCode[
                yearLen
                + monthLen
                + dayLen
                + hourLen : yearLen
                + monthLen
                + dayLen
                + hourLen
                + minuteLen
            ]

            nextMinute = (int(minuteIndex, MinuteCodes.base) + 1) % MinuteCodes.base

            nextHour = (
                int(hourIndex, MinuteCodes.base) + (1 if nextMinute == 0 else 0)
            ) % MinuteCodes.base

            nextDay = (
                int(dayIndex, MinuteCodes.base)
                + (1 if nextHour == 0 and nextMinute == 0 else 0)
            ) % MinuteCodes.base

            nextMonth = (
                int(monthIndex, MinuteCodes.base)
                + (1 if nextDay == 0 and nextHour == 0 and nextMinute == 0 else 0)
            ) % MinuteCodes.base

            nextYear = (
                int(yearIndex, MinuteCodes.base)
                + (
                    1
                    if nextMonth == 0
                    and nextDay == 0
                    and nextHour == 0
                    and nextMinute == 0
                    else 0
                )
            ) % MinuteCodes.base

            nextMinuteCode = MinuteCodes._getMinuteCodeFromDateChunks(
                [nextYear, nextMonth, nextDay, nextHour, nextMinute]
            )

            nextCodes.append(nextMinuteCode)

            minuteCode = nextMinuteCode

        return nextCodes

    @staticmethod
    def _isDateTimeFormattedString(dateTime):
        retVal = False

        try:
            if isinstance(dateTime, str):
                if (
                    len(dateTime) == 16
                    and dateTime[4] == "\\"
                    and dateTime[7] == "\\"
                    and dateTime[10] == "."
                    and dateTime[13] == "."
                ):
                    if datetime.datetime.strptime(dateTime, "%Y\\%m\\%d.%H.%M"):
                        retVal = True
        except ValueError:
            retVal = False
        return retVal

    @staticmethod
    def _isYmdhmArray(dateTimeObj):
        retVal = False

        if (
            isinstance(dateTimeObj, (list, tuple))
            and len(dateTimeObj) == 5
            and all(isinstance(item, int) for item in dateTimeObj)
        ):
            retVal = True
        return retVal

    @staticmethod
    def getMinuteCode(dateTimeObj):
        if MinuteCodes._isDateTimeFormattedString(dateTimeObj):
            dateTimeObj = MinuteCodes._dateTimeStringToDateTime(dateTimeObj)
        if isinstance(dateTimeObj, datetime.datetime):
            dateTimeObj = MinuteCodes._dateTimeToYmdhm(dateTimeObj)
        if MinuteCodes._isYmdhmArray(dateTimeObj):
            retVal = MinuteCodes._getMinuteCodeFromDateChunks(dateTimeObj)
        else:
            retVal = "Unknown data format!"
        return retVal

    @staticmethod
    def getCurrentBlockOfCodes(blockCodeCount=5):
        ymdhm = MinuteCodes._datetimeToArray(datetime.datetime.now())

        retVal = MinuteCodes.getBlockOfMinuteCodes(ymdhm, blockCodeCount)

        return retVal

    @staticmethod
    def getBlockOfMinuteCodes(dateTimeObj, blockCodeCount=5):
        retVal = []

        if MinuteCodes._isYmdhmArray(dateTimeObj):
            ymdhm = dateTimeObj
        else:
            ymdhm = MinuteCodes._datetimeToArray(dateTimeObj)

        for i in range(1, blockCodeCount + 1):
            minuteCode = MinuteCodes.getMinuteCode(ymdhm)

            retVal.append(minuteCode)

            ymdhm[-1] += 1

        return retVal

    @staticmethod
    def _decodeChunk(encoded_value):
        decodedDateChunk = 0
        for char in encoded_value:
            decodedDateChunk = (
                decodedDateChunk * MinuteCodes.base + MinuteCodes.characters.index(char)
            )
        return decodedDateChunk

    @staticmethod
    def _datetimeToArray(dateObject):
        # Extract year, month, day, hour, and minute components from the datetime object
        year = dateObject.year
        month = dateObject.month
        day = dateObject.day
        hour = dateObject.hour
        minute = dateObject.minute

        # Return the components as an array
        return [year, month, day, hour, minute]

    @staticmethod
    def _timestampToArray(timestamp):
        # Convert the timestamp to a datetime object
        dateObject = datetime.datetime.fromtimestamp(timestamp)

        return MinuteCodes._datetimeToArray(dateObject)

    @staticmethod
    def printCurrentBlockOfMinuteCodes():
        for minuteCode in MinuteCodes.getCurrentBlockOfCodes():
            print(minuteCode)
