import re
import subprocess

def _indentListToTable(indentedListAsString):
    lines = indentedListAsString.splitlines()

    rows = []
    rootItem = None

    for line in lines:
        strippedLine = line.strip()

        if strippedLine:
            if line[0].isspace():
                if rootItem is not None:
                    rows.append([rootItem, strippedLine])
            else:
                rootItem = strippedLine
    return rows

def _extractCodecs(v4l2_output):
    lines = v4l2_output.split("\n")
    codecs = []

    codecPattern = r"^\s*\[\d+\]:\s*'([A-Z0-9]+)'\s+\(.*\)$"

    for line in lines:
        match = re.match(codecPattern, line)
        if match:
            codecs.append(match.group(1).strip())
    return codecs

def _getDeviceInfo(devicePath):
    command = ["v4l2-ctl", "-d", devicePath, "--list-formats-ext"]
    try:
        v4l2_output = subprocess.check_output(command, universal_newlines=True)
        return v4l2_output
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        return ""

def _getDeviceCodecs(devicePath):
    deviceInfo = _getDeviceInfo(devicePath)
    codecs = _extractCodecs(deviceInfo)
    return codecs

def _getCodecsForDevicePath(deviceArray):
    fullDeviceInfo = []

    for row in deviceArray:
        devicePath = row[1]

        if ("/video" in devicePath):
            deviceCodecs = _getDeviceCodecs(devicePath)

            for codec in deviceCodecs:
                fullDeviceInfo.append([row[0], row[1], codec])

    return fullDeviceInfo

def getInfo():
    cmd = "v4l2-ctl --list-devices"
    print(cmd)
    try:
        output = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, text=True, shell=True
        )
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output}"
    deviceTable = _indentListToTable(output)
    deviceCodecTable = _getCodecsForDevicePath(deviceTable)

    return deviceCodecTable
