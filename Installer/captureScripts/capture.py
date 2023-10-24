#!/usr/bin/python3
from datetime import datetime
import json
import logging
from multiprocessing import Process
import os
from pathlib import Path
import psutil
import shlex
import shortuuid
import subprocess
import sys
import time
from types import SimpleNamespace

#########################################################
#  PREPARE SOME LOGGING AND OTHER REQUIRE VARIABLES...
#
#  Force the CWD to the local path of the script...
#
scriptFullPath = Path(__file__)
localDir = str(scriptFullPath.parent)

# Just in case this is a windows based environment, search
# for the ':' character within the first five characters
index = localDir.find(":", 0, 5)

# If ':' is found, return everything after it
if index != -1:
    localDir = localDir[index + 1 :]

print(localDir)

sysArgv = "-v"

if len(sys.argv) > 1:
    sysArgv = sys.argv[1]

logFilePath = localDir + f"/logs{sysArgv.upper()}.log"
stopFile = os.path.join(localDir, "capture.stop")

######################################################
#  PREP LOGGER...
#
def prepareLogger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

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


########################################################
#  Get the logger set and append the opening message...
logger = prepareLogger()
log("LOG ACTIVATED!")
log("Log file path set to: " + logFilePath)

#######################################
#  Remove any 'capture.stop' file...
#
if os.path.exists(stopFile):
    log("Found a 'capture.stop' flag file.  Removing...")
    os.remove(stopFile)

######################################################
#  LOAD CONFIG DATA...
#
log("**********************************************")
log("***       DATA CAPTURE CONFIGURATION       ***")
log("**********************************************")
log("   ")

log("Current directory: " + os.getcwd())
log("Setting current directory: " + localDir)
os.chdir(localDir)

modelNameFilePath = "/proc/device-tree/model"

#  Check to make sure the model file exists...
if os.path.isfile(modelNameFilePath) is not True:
    log("Unable to find model file at path!")
    log("   ---> Model filepath: '" + modelNameFilePath + "'")
    # sys.exit("      ***   Please check to see if this is Raspian based OS!   ***")
    log(
        "      ***   "
        + "This does not appear to be a Raspian based OS "
        + "and may not function as expected!"
        + "   ***"
    )
else:
    #  Grab the machine model...
    f = open(modelNameFilePath, mode="rt")
    modelName = f.read()
    f.close()
    modelName = modelName.rstrip("\x00")

    log("Detected machine model: '" + modelName + "'...")

#  Determine if this is an audio or video capture...
captureLabel = "UNKNOWN!"

log("    ")
log("Startup argument: " + sysArgv)
log("    ")

if sysArgv == "-a":
    captureLabel = "Audio"
elif sysArgv == "-v":
    captureLabel = "Video"
elif sysArgv == "-vm":
    captureLabel = "Voltage"

log("   ")
log("                   =====")
log("Executing in ->>>  " + captureLabel.upper() + "  <<<- mode...")
log("                   =====")
log("   ")

#  Concat the JSON config file name...
# configFileName = "capture" + captureLabel + "." + modelName + ".json"
configFileName = f"capture{captureLabel}.json"

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
cfg = json.loads(rawJsonData, object_hook=lambda d: SimpleNamespace(**d))

################################################
#  Capture related variables we need to set...

#  --->>> *The IS_TEST_MODE variable should *NORMALLY* be set to False...*
IS_TEST_MODE = cfg.IsTestMode

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
    cfg.RecordingClipLengthInMinutes = 0.2
    testClipMax = 2
#  Set the clip length and commandline timeout
#  based on the outcome of the previous lines...
recordingClipInSeconds = cfg.RecordingClipLengthInMinutes * 60
recordingClipInMilliseconds = recordingClipInSeconds * 1000
cmdCallTimeout = recordingClipInMilliseconds + (10 * 1000)

###############################################################################
#  Checks to see if there is a mount point preference for available drive space
#  and sets clip drop points according to that preference...
def CheckMountPoint():
    #  If 'cfg.PreferLargestAvailableMount' is set to True,
    #  the we need to determine the root directory to use
    #  for dumping the clips into...
    if cfg.PreferLargestAvailableMount:
        partitions = psutil.disk_partitions()
        bestMountpointFreeSpace = 0
        bestMountpoint = ""
        for p in partitions:
            testMountpointFreeSpace = psutil.disk_usage(p.mountpoint).free
            gb = round(testMountpointFreeSpace / (1024 * 1024 * 1024), 2)
            log("Found mountpoint: " + str(p.mountpoint) + " -- {} GB".format(gb))
            if testMountpointFreeSpace > bestMountpointFreeSpace:
                bestMountpoint = str(p.mountpoint)
                bestMountpointFreeSpace = testMountpointFreeSpace
                bestFreespace = round(bestMountpointFreeSpace / (1024 * 1024 * 1024), 2)
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
    # global cfg.ScreenWidth
    # global cfg.ScreenHeight
    global captureLabel

    #  Set the directory to dump the capture files into...
    targetPath = mountpointPrefix + "/" + localDir + "/" + captureLabel
    targetOutputDirectory = os.path.expandvars(targetPath)
    targetOutputDirectory = os.path.normpath(targetOutputDirectory)

    #  Make sure the directory exicmdResults...
    Path(targetOutputDirectory).mkdir(parents=True, exist_ok=True)
    log("  ")
    log("Output directory set to '" + targetOutputDirectory + "'...")
    log("  ")
    log("Preferred recording method: '" + cfg.PreferredRecorder + "'...")

    #  Start making some decisions based on the settings data from above...
    if captureLabel == "Audio":
        if cfg.PreferredRecorder == "arecord" or cfg.PreferredRecorder == "default":
            captureCmd = (
                "arecord -D "
                + cfg.DevicePath  # arecord -D plughw:0,0 -f cd -d 10 -V stereo test.wav
                + " -f "
                + cfg.RecordingQuality  # audio recording quality
                + " -d "
                + str(recordingClipInSeconds)  # Length of clip...
            )
        elif cfg.PreferredRecorder == "ffmpeg":
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
                "ffmpeg "
                + cfg.DevicePath
                + " -c copy -t "
                + str(recordingClipInSeconds)
            )
    elif captureLabel == "Video":
        if cfg.PreferredRecorder == "libcamera" or cfg.PreferredRecorder == "default":
            captureCmd = (
                "libcamera-vid -t "
                + str(recordingClipInMilliseconds)  # Length of clip...
                + " --width "
                + str(cfg.ScreenWidth)  # Screen X dimensions
                + " --height "
                + str(cfg.ScreenHeight)  # Screen Y dimensions...
                + " --nopreview "  # Do not show a preview...
                + " --autofocus-mode continuous"  # Set the autofocus mode...
                + " -o "  # The output filePath will be appended here...
            )
        elif cfg.PreferredRecorder == "ffmpeg":
            captureCmd = (
                f"ffmpeg {cfg.FFmpegInputFormatSource} {cfg.FFmpegInputFormat} "
                + f"-video_size {cfg.ScreenWidth}x{cfg.ScreenHeight} "
                + f"-i {cfg.DevicePath} "
                + f"-c copy -t {recordingClipInSeconds}"
            )
    elif captureLabel == "Voltage":
        captureCmd = (
            f"{cfg.PreferredRecorder} {cfg.DevicePath} "
            + f"-t {recordingClipInSeconds * 1000} "
            + "-o "
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
    log("   ")
    log("You are executing this script in test mode!")
    log("                             ------\\/------")
    log(
        "It will not record more than -->>  {}  <<-- clips before quitting!!!".format(
            str(testClipMax)
        )
    )
    log("                             ----^^^^^^----   ")
    log("   ")
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


def CheckForStopCapture():
    global stopFile
    return os.path.exists(stopFile)


def StoreCapture(storageScriptPath, storageId, captureLabel, filePath):
    cmdLine = (
        f"python " +
        f"{storageScriptPath} "
        + f"-t {storageId} "
        + f"-a store -r + -c {captureLabel} "
        + f"-f {filePath}"
    )

    cmdLine = cmdLine.replace("\\", "/")

    log(f"Calling storage process: {cmdLine}")

    # Parse the command string into a list of arguments
    args = shlex.split(cmdLine)

    try:
        # Start the subprocess without waiting for it to complete
        process = subprocess.Popen(args)
        log(f"ProcessId: {process.pid}")
    except Exception as e:
        log(f"ERROR!]\n\n{e}")

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
    storageId = time.time_ns()

    #  Construct the full file path and name...
    filePath = (
        targetOutputDirectory
        + "/"
        + uniqueSessionId
        + "_"
        + timeStamp
        + "."
        + cfg.OutputExtension
    )

    #  Index the clip count...
    clipCount = clipCount + 1

    clipLine = f"--  CLIP # {clipCount}  --"

    print("-" * len(clipLine))
    print(clipLine)
    print("-" * len(clipLine))

    try:
        CaptureViaCmdLine(filePath)
        StoreCapture(cfg.StorageScriptPath, storageId, captureLabel, filePath)

    finally:
        #  Check for IS_TEST_MODE again...
        if IS_TEST_MODE:
            if clipCount >= testClipMax:
                DisplayPostTestWarning()
                keepRecording = False
        #  We also need a way to break out
        #  if a RESTish stop call is made...
        # time.sleep(2)
        if CheckForStopCapture() is True:
            log("Found a 'capture.stop' flag file!")
            log("Stopping all recording now!")
            log("   ")
            log("   ")
            log("-" * 80)
            log(
                "-" * 6
                + "  "
                + "THE CAPTURE.STOP FILE WILL BE DELETED UPON THE NEXT CAPTURE START!"
                + "  "
                + "-" * 6
            )
            log("-" * 80)
# ffmpeg -f dshow -i video="Lenovo EasyCamera" output.h264
