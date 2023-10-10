import argparse
from datetime import datetime, timedelta
from FileActionApi import FileActionApi
import json
from MinuteCodes import MinuteCodes
import os
import re
import time


def datetimeToTicks(datetimeToConvert):
    # Convert datetime object to seconds since the epoch
    datetimeObj = None

    try:
        datetimeObj = datetime.strptime(datetimeToConvert, "%Y-%m-%d~%H_%M_%S")
    except ValueError:
        try:
            datetimeObj = datetime.strptime(datetimeToConvert, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise Exception("Invalid timestamp format!")

    if datetimeObj is not None:
        secondsSinceEpoch = time.mktime(datetimeObj.timetuple())

        # Convert seconds to nanoseconds
        ticks = int(secondsSinceEpoch * 1e9)

        return ticks
    else:
        raise Exception("Invalid timestamp format!")


def determineInputType(input):
    retVal = "unknown"
    # Check if the input is a valid tick value (integer)
    if input.isdigit():
        retVal = "tick"
    # Check if the input is a base26 alpha encoded string
    elif re.match("^[a-z]+$", input) and len(input) == 13:
        retVal = "baseX"
    else:
        # Check if the input is a valid datetime string
        try:
            datetime.strptime(input, "%Y-%m-%d %H:%M:%S")
            retVal = "datetime-s"
        except ValueError:
            try:
                val = datetime.strptime(input, "%Y-%m-%d~%H_%M_%S")
                # print(val)
                retVal = "datetime-a"
            except ValueError:
                pass
    # If it's none of these, return 'unknown'
    return retVal


def convertTicksToDatetime(ticks):
    nanoseconds_per_second = 10 ** 9  # 10^9 nanoseconds in a second
    seconds = ticks / nanoseconds_per_second

    # Convert to datetime object
    epoch = datetime(1970, 1, 1)
    delta = timedelta(seconds=seconds)
    datetime_obj = epoch + delta

    return datetime_obj


def decodeFromBaseX(encoded, alphabet="abcdefghijklmnopqrstuvwxyz"):
    base = len(alphabet)
    decoded = 0
    for i, char in enumerate(reversed(encoded)):
        decoded += alphabet.index(char) * (base ** i)
    return decoded


def encodeToBaseX(num, alphabet="abcdefghijklmnopqrstuvwxyz"):
    base = len(alphabet)
    encoded = ""
    while num > 0:
        remainder = num % base
        encoded = alphabet[remainder] + encoded
        num //= base
    return encoded


def convertBasexToDateTime(baseX):
    ticks = decodeFromBaseX(baseX)
    dateTimeObj = convertTicksToDatetime(ticks)
    return dateTimeObj


def setCwdToScriptAndReturnPath(discardFileExtension=False):
    retVal = os.path.abspath(__file__)
    scriptDir = os.path.dirname(retVal)
    os.chdir(scriptDir)

    if discardFileExtension:
        retVal, _ = os.path.splitext(retVal)
    return retVal


def loadConfig():
    try:
        scriptPath = setCwdToScriptAndReturnPath(discardFileExtension=True)
        configPath = f"{scriptPath}.config.json"

        with open(configPath, "r") as configFile:
            config = json.load(configFile)
            return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found at: {configPath}")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format in configuration file.")


def formatTimestamp(timestampObj):
    timestampType = determineInputType(timestampObj)

    # print(f"Timestamp Type: {timestampType}")

    retVal = None

    if timestampType == "baseX":
        retVal = timestampObj
    elif timestampType == "datetime-s" or timestampType == "datetime-a":
        retVal = encodeToBaseX(datetimeToTicks(timestampObj))
    elif timestampType == "tick":
        retVal = encodeToBaseX(timestampObj)
    elif timestampType == "unknown":
        retVal = encodeToBaseX(time.time_ns())

    return retVal


def parseCommandLineArguments():
    parser = argparse.ArgumentParser(description="Your script description here.")

    # Add arguments
    parser.add_argument(
        "-t",
        "--timestamp",
        required=True,
        type=str,
        help="Required - A timestamp as ticks, base26 alpha encoded, or formatted as 'YYYY-mm-dd~HH_MM_SS'.",
    )
    parser.add_argument(
        "-a",
        "--action",
        required=True,
        type=str,
        help="Required - Single word action label.",
    )
    parser.add_argument(
        "-r",
        "--result",
        required=True,
        type=str,
        help="Required - Describes the result of the action.  Plain text or JSON formatted data structure.",
    )
    parser.add_argument(
        "-c",
        "--contentType",
        required=True,
        type=str,
        help="Required - The type of content generated by the action (eg, video, audio, ioa, compressed, etc).",
    )
    parser.add_argument(
        "-f",
        "--filePath",
        required=True,
        type=str,
        help="Required - Full file path and name.",
    )
    parser.add_argument(
        "-d",
        "--description",
        required=False,
        help="Optional - Plain text or JSON formatted data structure.",
    )

    # Parse arguments
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    config = loadConfig()
    minCodesGen = MinuteCodes()
    storage = FileActionApi(config["baseAddress"], config["port"])

    args = parseCommandLineArguments()

    storageId = formatTimestamp(args.timestamp)

    # print(f"storageId: {storageId}")

    dateTimeObj = convertTicksToDatetime(decodeFromBaseX(storageId))

    # print(f"dateTimeObj: {dateTimeObj}")

    minuteCodes = minCodesGen.getBlockOfMinuteCodes(dateTimeObj, blockCodeCount = 5)

    # print(f"minuteCodes: {minuteCodes}")

    result = storage.storeItem(
        storageId,
        args.action,
        args.result,
        args.contentType,
        minuteCodes,
        args.description,
        args.filePath,
    )
