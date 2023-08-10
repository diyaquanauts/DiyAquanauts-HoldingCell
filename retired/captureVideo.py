#!/usr/bin/python3
import os
import subprocess
import sys

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


######################################################
#  LOAD CONFIG DATA...
#
print("***********************************************")
print("***       VIDEO CAPTURE CONFIGURATION       ***")
print("***********************************************")
print("   ")

modelNameFilePath = "/proc/device-tree/model"

#  Check to make sure the model file exists...
if(os.path.isfile(modelNameFilePath) != True):
    print("Unable to find model file at path!")
    print("   ---> Model filepath: '" + modelNameFilePath + "'")
    sys.exit("      ***   Please check to see if this is Raspian based OS!   ***")

#  Grab the machine model...
f = open(modelNameFilePath, mode="rt")
modelName = f.read()
f.close()
modelName = modelName.rstrip('\x00')

print("Detected machine model: '" + modelName + "'...")

#  Concat the JSON config file name...
configFileName = "captureVideo." + modelName + ".json"

if(os.path.isfile(configFileName) != True):
    print("Unable to find JSON configuration file!")
    print("   ---> JSON config filepath: '" + configFileName + "'")
    sys.exit("      ***   Please check to see if this system has been fully configured!   ***")

print("Using '" + configFileName + "' as configuration source...")

#  Read in config data from JSON file and display...
f = open(configFileName, mode="rt")
rawData = json.load(f)
f.close()
rawJsonData = json.dumps(rawData, indent=4)

print("   ")
print(rawJsonData)
print("   ")

# Parse JSON into an object with attributes corresponding to dict keys.
configObject = json.loads(rawJsonData, object_hook=lambda d: SimpleNamespace(**d))

######################################################
#  *** THE ALL IMPORTANT SETTINGS ***
#  Variables we need to set...
preferredRecorder = configObject.PreferredRecorder  # "ffmpeg"
screenWidth = configObject.ScreenWidth  # 1280
screenHeight = configObject.ScreenHeight  # 720
devicePath = configObject.DevicePath  # "/dev/video0"
recordingClipLengthInMinutes = configObject.RecordingClipLengthInMinutes  # 5
preferLargestAvailableMount = configObject.PreferLargestAvailableMount  # True
ffmpegInputFormat = configObject.FFmpegInputFormat  # " -input_format mjpeg"
outputExtension = configObject.OutputExtension  # Determines the output file type

#  --->>> *The IS_TEST_MODE variable should *NORMALLY* be set to False...*
IS_TEST_MODE = configObject.IsTestMode

#  Variables that get set in the course of things...
mountpointPrefix = ""
targetOutputDirectory = ""
videoBinaryDirectory = ""
videoCmd = ""
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
libcameraCmdCallTimeout = recordingClipInMilliseconds + (10 * 1000)

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
            if testMountpointFreeSpace > bestMountpointFreeSpace:
                bestMountpoint = str(p.mountpoint)
                bestMountpointFreeSpace = testMountpointFreeSpace
                freespaceInMb = bestMountpointFreeSpace / 1048576
        print("  ")
        print(
            "Largest available mount free space is '"
            + bestMountpoint
            + "' with "
            + str(freespaceInMb)
            + "mb."
        )
        print("  ")
        global mountpointPrefix
        mountpointPrefix = bestMountpoint


##############################################################################
#  Determines what type of system we're running on and what preferences should
#  be set in relation to that fact...
def SetSystemPrefs():
    #  Determine the appropriate paths and arguments to record video...

    #  TODO: Abstract this away into a separate class that
    #        reads in the appropriate data from a config file...
    global videoCmd
    global targetOutputDirectory

    #  Set the directory to dump the video files into...
    targetPath = mountpointPrefix + "$HOME/Videos"
    targetOutputDirectory = os.path.expandvars(targetPath)

    #  Make sure the directory exicmdResults...
    Path(targetOutputDirectory).mkdir(parents=True, exist_ok=True)
    print("  ")
    print("Output directory set to '" + targetOutputDirectory + "'...")
    print("  ")
    print("Preferred recording method: '" + preferredRecorder + "'...")

    #  Start making some decisions based on the settings data from above...
    if preferredRecorder == "libcamera" or preferredRecorder == "default":
        videoCmd = (
            "libcamera-vid -t "
            + str(recordingClipInMilliseconds)  # Length of clip...
            + " --width " + str(screenWidth)  # Screen X dimensions
            + " --height " + str(screenHeight)  # Screen Y dimensions...
            + " --nopreview "  # Do not show a preview...
            + " --autofocus-mode continuous"  # Set the autofocus mode...
            + " -o "  # The output filePath will be appended here...
        )
    elif preferredRecorder == "ffmpeg":
        videoCmd = (
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


"""
    #
    #  This whole section needs to be reworked to handle systems
    #  that don't have libcamera-vid installed or cannot have
    #  libcamera-vid installed...
    #
    elif preferredRecorder == "picamera2":
        # !pip install Picamera2
        from picamera2 import Picamera2
        from picamera2.encoders import H264Encoder, Quality
"""

###############################################################################
#  Message (initial) displayed in the event IS_TEST_MODE is left set to True...
def DisplayTestWarning():
    print("*******************************")
    print("*******************************")
    print("WARNING!!  WARNING!!  WARNING!!")
    print("*******************************")
    print("*******************************")
    print("   ")
    print("You are executing this script in test mode!")
    print(
        "It will not record more than >>"
        + str(testClipMax)
        + "<< clips before quitting!!!"
    )
    print("   ")
    print("*******************************")
    print("*******************************")
    print("WARNING!!  WARNING!!  WARNING!!")
    print("*******************************")
    print("*******************************")


############################################################################
#  Message (exit) displayed in the event IS_TEST_MODE is left set to True...
def DisplayPostTestWarning():
    print("   ")
    print("WARNING!  WARNING!  WARNING!")
    print("   ")
    print("THIS SCRIPT IS CURRENTLY IN TEST MODE!")
    print("   ")
    print("STOPPING RECORDING NOW!")
    print("   ")


#####################################################
#  Displays any error or unexpected command result...
def ReportCmdHiccup(commandResults=None, exceptionObj=None):
    print("----------------------------------------------")
    if exceptionObj is not None:
        print(f"UNEXPECTED ERROR ECOUNTERED {exceptionObj=}, {type(exceptionObj)=}")
    else:
        print("UNEXPECTED COMMAND LINE RESULT")
    if commandResults is not None:
        print("----------------------------------------------")
        print("   ")
        print("----- STANDARD OUT -----")
        print(commandResults.stdout)
        print("   ")
        print("----- STANDARD ERR -----")
        print(commandResults.stderr)
        print("   ")
        print("----- RETURN CODE -----")
        print(commandResults.returncode)
        print("   ")
        print("----- CALLING ARGS -----")
        print(commandResults.args)


################################################################
#  Captures video clips via the preferred command line method...
def CaptureViaCmdLine(filePath):
    #  Construct the video clip recording command line...
    fullCmd = videoBinaryDirectory + videoCmd + " " + filePath
    print("   ")
    print(fullCmd)
    print("   ")

    try:
        #  Here's where the actual command line gets executed...
        cmdResults = subprocess.run(
            fullCmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True,
            timeout=libcameraCmdCallTimeout,
        )
        if cmdResults.returncode != 0:
            ReportCmdHiccup(commandResults=cmdResults)
    except Exception as err:
        ReportCmdHiccup(exceptionObj=err)


"""
#
#  Need to rework this for systems that don't or can't have
#  libcamera-vid installed on them...
#
##########################################################
#  Captures video clips via th Picamera2 Python library...
def CaptureViaPicamera2(filePath):
    #  Declare the camera object...
    picam2 = Picamera2()

    #  Set the video and control configuration info...
    #  picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
    video_config = picam2.create_video_configuration(
        main={"size": (screenWidth, screenHeight)}
    )
    #  video_config.controls.FrameRate = 25.0
    picam2.configure(video_config)

    #  Prepare an encoder to record with...
    encoder = H264Encoder(qp=30)

    #  Set the value for the length of recording time...
    clipLengthInMinutes = recordingClipLengthInMinutes * 60

    # picam2.start_recording(
    #    encoder, filePath, duration=clipLengthInMinutes, quality=Quality.HIGH
    # )

    print("Output file: " + filePath)
    picam2.start_recording(encoder, filePath, quality=Quality.HIGH)

    #
    #  Don't think we need these following bits as it seems
    #  like it should just auto-stop after reaching the
    #  duration limit.  At least I hope that's the case...
    #
    time.sleep(clipLengthInMinutes)
    picam2.stop_recording()
"""


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
        """
        #
        #  Need to rework for non-Picamera2 compatible systems...
        #
        #  Determine what methodology to use to record the clip...
        if preferredRecorder == "picamera2":
            CaptureViaPicamera2(filePath)
        else:
            CaptureViaCmdLine(filePath)
        """
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
