import os
import platform
from datetime import datetime
import keyboard
import shortuuid

####
####  Setup some universally used variables...
####

#  --->>> *The IS_TEST_MODE variable should *NORMALLY* be set to False...*
IS_TEST_MODE = False
testClipMax = 2

#  This is UUID that will be prefixed to every file name to 
#  differentiate which session each file belongs to...
uniqueSessionId = shortuuid.uuid()

#  Settings for determining how to actually generate a video clip...
targetOutputDirectory = ""
videoCmd = ""
preferredRecorder = "default"
videoBinaryDirectory = ""
recordingClipLengthInMinutes = 3
recordingClipInMilliseconds = recordingClipLengthInMinutes * 60 * 1000

#  Flags used by the script's internal logic to determine if
#  clip recording should continue or be gracefully exited...
keepRecording = True
clipCount = 0

#  Determine what base OS we're running on...
sysType = platform.system()

#  Based on the base OS info found above, determine the
#  appropriate paths and arguments to record video...

#  TODO: Abstract this away into a separate class that
#        reads in the appropriate data from a config file...
#  ALSO: Go back and find my 'Python psuedo-switch' structure
#        and refactor this code into that pattern...

#  IF THIS IS A LINUX OR MAC BASED SYSTEM...
if sysType == "Linux" or sysType == "Mac":
    targetOutputDirectory = "/"
    if preferredRecorder == "libcamera" or preferredRecorder == "default":
        videoCmd = (
            "libcamera-vid -t "
            + str(recordingClipInMilliseconds)
            + " --width 1920 --height 1080 --autofocus-mode continuous --nopreview -o "
        )
    elif preferredRecorder == "ffmpeg":
        #  Need to fix the time/video length portion of the cmd line...
        videoCmd = "ffmpeg -f pulse -ac 2 -i default -f v4l2 -i /dev/video0 -t 00:01:00 -vcodec libx264 record.h264"
#  OTHERWISE, IF THIS A WINDOWS BASED SYSTEM...
elif sysType == "Windows":
    targetOutputDirectory = "c:\\temp\\"
    if preferredRecorder == "ffmpeg" or preferredRecorder == "default":
        videoBinaryDirectory = (
            "C:\\Users\\kmlan\\Downloads\\ffmpeg-6.0-essentials_build\\bin\\"
        )
        #  Need to fix the time/video length portion of the cmd line...
        videoCmd = 'ffmpeg -f dshow -s 320x240 -r 30 -vcodec mjpeg -i video="Lenovo EasyCamera" -t 00:01:00'

#  Message displayed in the event IS_TEST_MODE is left set to True...
def DisplayTestWarning():
    print("*******************************")
    print("*******************************")
    print("WARNING!!  WARNING!!  WARNING!!")
    print("*******************************")
    print("*******************************")
    print("   ")
    print("You are executing this script in test mode!")
    print(
        "It will not record more than " + str(testClipMax) + " clips before quitting!!!"
    )
    print("   ")
    print("*******************************")
    print("*******************************")
    print("WARNING!!  WARNING!!  WARNING!!")
    print("*******************************")
    print("*******************************")

####################################
#####
#####  THE MAIN EVENT, KIDDIES!
#####
####################################

while keepRecording:
    #  If we're in test mode, warn the user...
    if IS_TEST_MODE:
        DisplayTestWarning()
    #  Grab a file timestamp...
    timeStamp = datetime.now().strftime("%Y-%m-%d~%H_%M_%S")
    #  Construct the full file path and name...
    filePath = uniqueSessionId + "_" + timeStamp + ".h264"
    #  Construct the video clip recording command line...
    fullCmd = videoBinaryDirectory + videoCmd + " " + filePath
    #  Display the fullCmd for debugging assistance...
    if IS_TEST_MODE:
        print("   ")
        print(fullCmd)
        print("   ")
    #  Index the clip count...
    clipCount = clipCount + 1
    #  Here's where the actual command line gets executed...
    os.system(fullCmd)
    #  Check for IS_TEST_MODE again...
    if IS_TEST_MODE:
        if clipCount >= testClipMax:
            print("   ")
            print("WARNING!  WARNING!  WARNING!")
            print("   ")
            print("THIS SCRIPT IS CURRENTLY IN TEST MODE!")
            print("   ")
            print("STOPPING RECORDING NOW!")
            print("   ")
            keepRecording = False
    #  Apparently, this bit requires root mode?  Kinda weird...
    # if keyboard.read_key() == "x":
    #    keepRecording = false
    #  We also need a way to break out
    #  if a RESTish stop call is made...
