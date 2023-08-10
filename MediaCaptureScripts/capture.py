#!/usr/bin/python3
import os
import subprocess
import sys
from pathlib import Path

# !pip install shortuuid
import shortuuid

# !pip install psutil
import psutil

# import time

import json
from types import SimpleNamespace

# from libcamera import controls
from datetime import datetime
from pathlib import Path

import logging

#########################################################
#  PREPARE SOME LOGGING AND OTHER REQUIRE VARIABLES...
#  
#  Force the CWD to the local path of the script...
#
scriptFullPath = Path(__file__)
localDir = str(scriptFullPath.parent)
print(localDir)
logFilePath = localDir + "/logs" + sys.argv[1].upper() + ".log"

######################################################
#  PREP LOGGER...
#
def prepareLogger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

    #  stdout_handler = logging.StreamHandler(sys.stdout)
    #  stdout_handler.setLevel(logging.DEBUG)
    #  stdout_handler.setFormatter(formatter)

    global logFilePath  
    file_handler = logging.FileHandler(logFilePath)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    #  logger.addHandler(stdout_handler)

    return logger

################################
#  Log a message...
#
def log(msg):
    logger.debug(msg)
    print(msg)

#  Get the logger set and append the opening message...
logger = prepareLogger()
log("LOG ACTIVATED!")
log("Log file path set to: " + logFilePath)

######################################################
#  LOAD CONFIG DATA...
#
log("*****************************************************")
log("***       AUDIO/VIDEO CAPTURE CONFIGURATION       ***")
log("*****************************************************")
log("   ")

log("Current directory: " + os.getcwd())
log("Setting current directory: " + localDir)
os.chdir(localDir) 

modelNameFilePath = "/proc/device-tree/model"

#  Check to make sure the model file exists...
if os.path.isfile(modelNameFilePath) is not True:
    log("Unable to find model file at path!")
    log("   ---> Model filepath: '" + modelNameFilePath + "'")
    sys.exit("      ***   Please check to see if this is Raspian based OS!   ***")

#  Grab the machine model...
f = open(modelNameFilePath, mode="rt")
modelName = f.read()
f.close()
modelName = modelName.rstrip("\x00")

log("Detected machine model: '" + modelName + "'...")

#  Determine if this is an audio or video capture...
captureLabel = "UNKNOWN!"

log("    ")
log("Startup argument: " + sys.argv[1])
log("    ")

if sys.argv[1] == "-a":
    captureLabel = "Audio"
elif sys.argv[1] == "-v":
    captureLabel = "Video"

log("   ")
log("                   =====")
log("Executing in ->>>  " + captureLabel.upper() + "  <<<- mode...")
log("                   =====")
log("   ")

#  Concat the JSON config file name...
configFileName = "capture" + captureLabel + "." + modelName + ".json"

if os.path.isfile(configFileName) is not True:
    log("Unable to find JSON configuration file!")
    log("   ---> JSON config filepath: '" + configFileName + "'")
    errMsg = "***   Please check to see if this system has been fully configured!   ***"
    sys.exit(errMsg)
log("Using '" + configFileName + "' as configuration source...")

#  Read in config data from JSON file and display...
f = open(configFileName, mode="rt")
rawData = json.load(f)
f.close()
rawJsonData = json.dumps(rawData, indent=4)

log("   ")
log(rawJsonData)
log("   ")

# Parse JSON into an object with attributes corresponding to dict keys.
configObject = json.loads(rawJsonData, object_hook=lambda d: SimpleNamespace(**d))

######################################################
#  *** THE ALL IMPORTANT SETTINGS ***
#  Capture related variables we need to set...
#
if (captureLabel == "Audio"):
    preferredRecorder = configObject.PreferredRecorder
    devicePath = configObject.DevicePath
    recordingQuality = configObject.RecordingQuality
    recordingClipLengthInMinutes = configObject.RecordingClipLengthInMinutes
    preferLargestAvailableMount = configObject.PreferLargestAvailableMount
    ffmpegInputFormat = configObject.FFmpegInputFormat
    outputExtension = configObject.OutputExtension

elif (captureLabel == "Video"):
    preferredRecorder = configObject.PreferredRecorder  # "ffmpeg"
    screenWidth = configObject.ScreenWidth  # 1280
    screenHeight = configObject.ScreenHeight  # 720
    devicePath = configObject.DevicePath  # "/dev/video0"
    recordingPath = configObject.RecordingPath
    recordingClipLengthInMinutes = configObject.RecordingClipLengthInMinutes  # 5
    preferLargestAvailableMount = configObject.PreferLargestAvailableMount  # True
    ffmpegInputFormat = configObject.FFmpegInputFormat  # " -input_format mjpeg"
    outputExtension = configObject.OutputExtension  # Determines the output file type

#  --->>> *The IS_TEST_MODE variable should *NORMALLY* be set to False...*
IS_TEST_MODE = configObject.IsTestMode

#  Variables that get set in the course of things...
mountpointPrefix = ""
targetOutputDirectory = ""
cmdBinaryDirectory = ""
captureCmd = ""
#  This is UUID that will be prefixed to every file name to
#  differentiate which session each file belongs to...
uniqueSessionId = shortuuid.uuid()

#  If this is test mode, then we're going to do some overrides...
if IS_TEST_MODE:
    recordingClipLengthInMinutes = 1
    testClipMax = 2
#  Set the clip length and commandline timeout
#  based on the outcome of the previous lines...
recordingClipInSeconds = recordingClipLengthInMinutes * 60
recordingClipInMilliseconds = recordingClipInSeconds * 1000
cmdCallTimeout = recordingClipInMilliseconds + (10 * 1000)

###############################################################################
#  Checks to see if there is a mount point preference for available drive space
#  and sets clip drop points according to that preference...
def CheckMountPoint():
    #  If 'preferLargestAvailableMount' is set to True,
    #  the we need to determine the root directory to use
    #  for dumping the clips into...
    if preferLargestAvailableMount:
        partitions = psutil.disk_partitions()
        bestMountpointFreeSpace = 0
        bestMountpoint = ""
        for p in partitions:
            testMountpointFreeSpace = psutil.disk_usage(p.mountpoint).free
            gb = round(testMountpointFreeSpace/(1024 * 1024 * 1024), 2)
            log("Found mountpoint: " + str(p.mountpoint) + " -- {} GB".format(gb))
            if testMountpointFreeSpace > bestMountpointFreeSpace:
                bestMountpoint = str(p.mountpoint)
                bestMountpointFreeSpace = testMountpointFreeSpace
                bestFreespace = round(bestMountpointFreeSpace/(1024 * 1024 * 1024), 2)
        log("  ")
        log(
            "Largest available mount free space is '"
            + bestMountpoint
            + "' with "
            + str(bestFreespace)
            + " GB..."
        )
        log("  ")
        global mountpointPrefix
        mountpointPrefix = bestMountpoint


##############################################################################
#  Determines what type of system we're running on and what preferences should
#  be set in relation to that fact...
def SetSystemPrefs():
    #  Determine the appropriate paths and arguments for capture...

    #  TODO: Abstract this away into a separate class that
    #        reads in the appropriate data from a config file...
    global captureCmd
    global targetOutputDirectory
    global screenWidth
    global screenHeight
    global captureLabel

    #  Set the directory to dump the capture files into...
    targetPath = mountpointPrefix + "/" + localDir  + "/" + captureLabel
    targetOutputDirectory = os.path.expandvars(targetPath)
    targetOutputDirectory = os.path.normpath(targetOutputDirectory)

    #  Make sure the directory exicmdResults...
    Path(targetOutputDirectory).mkdir(parents=True, exist_ok=True)
    log("  ")
    log("Output directory set to '" + targetOutputDirectory + "'...")
    log("  ")
    log("Preferred recording method: '" + preferredRecorder + "'...")

    #  Start making some decisions based on the settings data from above...
    if captureLabel == "Audio":
        if preferredRecorder == "arecord" or preferredRecorder == "default":
            captureCmd = (
                "arecord -D "
                + devicePath  # arecord -D plughw:0,0 -f cd -d 10 -V stereo test.wav
                + " -f "
                + recordingQuality  # audio recording quality
                + " -d "
                + str(recordingClipInSeconds)  # Length of clip...
            )
        elif preferredRecorder == "ffmpeg":
            #  Need to incorporate this form of the command:
            #
            #     ffmpeg -f pulse
            #            -sample_rate 48000
            #            -i alsa_input.
            #            usb-C-Media_Electronics_Inc.
            #            _USB_PnP_Sound_Device-00.
            #            mono-fallback
            #            -c copy
            #            -ac 2
            #            -t 60 [OUTPUT FILEPATH]
            #
            #  This bit below is TOTALLY fake.
            #  It's just there as a placeholder
            #  till we figure out the correct cmd format...
            captureCmd = (
                "ffmpeg " + devicePath + " -c copy -t " + str(recordingClipInSeconds)
            )
    elif captureLabel == "Video":
        if preferredRecorder == "libcamera" or preferredRecorder == "default":
            captureCmd = (
                "libcamera-vid -t "
                + str(recordingClipInMilliseconds)  # Length of clip...
                + " --width "
                + str(screenWidth)  # Screen X dimensions
                + " --height "
                + str(screenHeight)  # Screen Y dimensions...
                + " --nopreview "  # Do not show a preview...
                + " --autofocus-mode continuous"  # Set the autofocus mode...
                + " -o "  # The output filePath will be appended here...
            )
        elif preferredRecorder == "ffmpeg":
            captureCmd = (
                "ffmpeg -f v4l2"
                + ffmpegInputFormat
                + " -video_size "
                + str(screenWidth)
                + "x"
                + str(screenHeight)
                + " -i "
                + devicePath
                + " -c copy -t "
                + str(recordingClipInSeconds)
            )


###############################################################################
#  Message (initial) displayed in the event IS_TEST_MODE is left set to True...
def DisplayTestWarning():
    log("*******************************")
    log("*******************************")
    log("WARNING!!  WARNING!!  WARNING!!")
    log("*******************************")
    log("*******************************")
    log("   ")
    log("You are executing this script in test mode!")
    log(
        "It will not record more than >>"
        + str(testClipMax)
        + "<< clips before quitting!!!"
    )
    log("   ")
    log("*******************************")
    log("*******************************")
    log("WARNING!!  WARNING!!  WARNING!!")
    log("*******************************")
    log("*******************************")


############################################################################
#  Message (exit) displayed in the event IS_TEST_MODE is left set to True...
def DisplayPostTestWarning():
    log("   ")
    log("WARNING!  WARNING!  WARNING!")
    log("   ")
    log("THIS SCRIPT IS CURRENTLY IN TEST MODE!")
    log("   ")
    log("STOPPING RECORDING NOW!")
    log("   ")


#####################################################
#  Displays any error or unexpected command result...
def ReportCmdHiccup(commandResults=None, exceptionObj=None):
    log("----------------------------------------------")
    if exceptionObj is not None:
        log(f"UNEXPECTED ERROR ECOUNTERED {exceptionObj=}, {type(exceptionObj)=}")
    else:
        log("UNEXPECTED COMMAND LINE RESULT")
    if commandResults is not None:
        log("----------------------------------------------")
        log("   ")
        log("----- STANDARD OUT -----")
        log(commandResults.stdout)
        log("   ")
        log("----- STANDARD ERR -----")
        log(commandResults.stderr)
        log("   ")
        log("----- RETURN CODE -----")
        log(commandResults.returncode)
        log("   ")
        log("----- CALLING ARGS -----")
        log(commandResults.args)


################################################################
#  Captures clips via the preferred command line method...
def CaptureViaCmdLine(filePath):
    #  Construct the clip recording command line...
    fullCmd = cmdBinaryDirectory + captureCmd + " " + filePath
    log("   ")
    log(fullCmd)
    log("   ")

    try:
        #  Here's where the actual command line gets executed...
        cmdResults = subprocess.run(
            fullCmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True,
            timeout=cmdCallTimeout,
        )
        if cmdResults.returncode != 0:
            ReportCmdHiccup(commandResults=cmdResults)
    except Exception as err:
        ReportCmdHiccup(exceptionObj=err)


####################################
#
#  THE MAIN EVENT, KIDDIES!
#
####################################
CheckMountPoint()

SetSystemPrefs()

#  Flags used by the script's internal logic to determine if
#  clip recording should continue or be gracefully exited...
keepRecording = True
clipCount = 0

while keepRecording:
    #  If we're in test mode, warn the user...
    if IS_TEST_MODE:
        DisplayTestWarning()
    #  Grab a file timestamp...
    timeStamp = datetime.now().strftime("%Y-%m-%d~%H_%M_%S")

    #  Construct the full file path and name...
    filePath = (
        targetOutputDirectory
        + "/"
        + uniqueSessionId
        + "_"
        + timeStamp
        + "."
        + outputExtension
    )

    #  Index the clip count...
    clipCount = clipCount + 1

    try:
        CaptureViaCmdLine(filePath)
    finally:
        #  Check for IS_TEST_MODE again...
        if IS_TEST_MODE:
            if clipCount >= testClipMax:
                DisplayPostTestWarning()
                keepRecording = False
        #  We also need a way to break out
        #  if a RESTish stop call is made...
        # time.sleep(2)
