# import ExternalScriptManager

import ast
from audioInput import audioInput
import fileCopy
import getpass
import getVideoInputs
from HostnameChanger import HostnameChanger
import installer
import inspect
import jsonUpdater
import os
from stringer import stringer
import sudoifyUser
import sys
import sysInfoEx
import time
from userChooser import userChooser
from WorkflowSelector import WorkflowSelector

###############
#   GLOBALS   #
###############

stringEx = stringer()
sysModel = sysInfoEx.getSystemModel()

###############


class MasterInstaller:
    def __init__(self):
        self.setCwdToInstaller()


    def methodName(self):
        return inspect.currentframe().f_back.f_code.co_name


    def stringBox(
        self, stringToBox, borderChar="*", padding=8, delayInMilliseconds=50
    ):
        paddingSpace = " " * padding
        stringToBox = stringEx.camelToCapCase(stringToBox)
        bufferLine = f"{borderChar * 3}  {' ' * len(stringToBox)}  {borderChar * 3}"
        marquee = f"{borderChar * 3}  {stringToBox}  {borderChar * 3}"
        borderLine = borderChar * len(marquee)
        box = (
            f"{paddingSpace}{borderLine}\n"
            + f"{paddingSpace}{bufferLine}\n"
            + f"{paddingSpace}{marquee}\n"
            + f"{paddingSpace}{bufferLine}\n"
            + f"{paddingSpace}{borderLine}"
        )

        print("")
        for line in box.split("\n"):
            print(line.rstrip())  # Remove trailing newline
            self.delayMS(delayInMilliseconds)
        print("")


    def delayMS(self, milliseconds):
        startTime = time.perf_counter()
        while (time.perf_counter() - startTime) * 1000 < milliseconds:
            pass


    def slowPrint(self, msg, delayInMilliseconds=25):
        for char in msg:
            sys.stdout.write(char)
            sys.stdout.flush()
            self.delayMS(delayInMilliseconds)


    def displayWelcome(self, asciiArtFile, delayInMilliseconds=25):
        os.system("clear")

        with open(asciiArtFile, "r") as file:
            lines = file.readlines()
        for line in lines:
            print(line.rstrip())  # Remove trailing newline
            self.delayMS(delayInMilliseconds)
        print("\n\n")
        self.slowPrint("                   <~~~~>  Press ENTER key to continue  <~~~~>")
        getpass.getpass(prompt="")
        os.system("clear")


    def setCwdToInstaller(self):
        scriptPath = os.path.abspath(__file__)
        scriptDir = os.path.dirname(scriptPath)
        os.chdir(scriptDir)


    def installDependencies(self):
        self.stringBox(self.methodName())
        installer.aptUpdate()
        installer.installPackage("ffmpeg")
        installer.installPackage("python3-pip")


    def installOptionals(self):
        self.stringBox(self.methodName())
        installer.aptUpdate()

        if (input("   --- Full system upgrade? [Y/n]: ") == "Y"):
            installer.aptUpgrade()

        if (input("   --- Install Cockpit system managment software? [Y/n]: ") == "Y"):
            installer.installPackage("cockpit")

        if (input("   --- Install RaspAP wi-fi access point software? [Y/n]: ") == "Y"):
                installer.execRawCmd("curl -sL https://install.raspap.com | bash -s -- --assume-yes")

        if (input("   --- Install Tailscale virtual networking? [Y/n]: ") == "Y"):
            installer.execRawCmd("curl -fsSL https://tailscale.com/install.sh | sh")


    def installPythonPackages(self):
        self.stringBox(self.methodName())
        installer.installPipPackages("shortuuid")
        installer.installPipPackages("psutil")
        installer.installPipPackages("flask")


    def installCaptureScripts(self):
        self.stringBox(self.methodName())
        fileCopy.copyFiles("./captureScripts", "/home/diyaqua")


    def setHostname(self):
        changer = HostnameChanger()
        changer.userQueryHostnameChange()


    def setupAudioConfigFiles(self):
        self.stringBox(self.methodName())
        audioIn = audioInput()
        audioList = audioIn.listHardware()
        audioChoice = userChooser.showChoices(audioList)

        print("   ")
        print(f"   --->  Audio input selected: {audioChoice}")
        print("   ")

        audioHardwareSetting = stringEx.getLeft(audioChoice, "[").strip()

        global sysModel

        print("Updating audio hardware settting in capture config file...")
        jsonUpdater.updateJson(
            f"/home/diyaqua/captureAudio.{sysModel}.json",
            {"DevicePath": audioHardwareSetting},
        )


    def setupVideoConfigFiles(self):
        self.stringBox(self.methodName())
        videoList = getVideoInputs.getInfo()

        print("")
        print("")
        print("      <><><><><><><><><><><><><><><><><><><><><>")
        print("      WARNING!!  WARNING!!  WARNING!!  WARNING!!")
        print("      <><><><><><><><><><><><><><><><><><><><><>")
        print("")
        self.slowPrint("         Choosing an available H264 option is\n")
        self.slowPrint("                     * *_VERY_**             \n")
        self.slowPrint("                 strongly recommended!       \n")
        print("")
        print("      <><><><><><><><><><><><><><><><><><><><><>")
        print("      WARNING!!  WARNING!!  WARNING!!  WARNING!!")
        print("      <><><><><><><><><><><><><><><><><><><><><>")
        print("")

        videoChoice = userChooser.showChoices(videoList)

        print("   ")
        print(f"   --->  Video input selected: {videoChoice}")
        print("   ")

        print(videoChoice)

        videoDeviceArray = ast.literal_eval(str(videoChoice))

        global sysModel

        print("Updating audio hardware settting in capture config file...")

        jsonUpdater.updateJson(
            f"/home/diyaqua/captureVideo.{sysModel}.json",
            {"DevicePath": videoDeviceArray[1]},
        )

        jsonUpdater.updateJson(
            f"/home/diyaqua/captureVideo.{sysModel}.json",
            {"OutputExtension": videoDeviceArray[2].lower()},
        )

        jsonUpdater.updateJson(
            f"/home/diyaqua/captureVideo.{sysModel}.json",
            {"FFmpegInputFormat": f" -input_format {videoDeviceArray[2].lower()}"},
        )


    def setSudoPrivileges(self):
        self.stringBox(self.methodName())
        sudoifyUser.addUserToSudoGroup("diyaqua")
        sudoifyUser.grantSudoPrivilegesWithoutPassword("diyaqua")


    def installSystemdServices(self):
        self.stringBox(self.methodName())

        installer.execRawFromTemplate(
            "serviceInstallTemplate.tmpl",
            {"$SERVICE_NAME$": "Audio"},
            exitOnFailure=False
        )
        installer.execRawFromTemplate(
            "serviceInstallTemplate.tmpl",
            {"$SERVICE_NAME$": "Video"},
            exitOnFailure=False
        )


    def mountDrives(self):
        """
        (1) Edit fstab file to include mount entries
        (2) Alternatively, use mount commands to mount drives
        (3) Verify drives are mounted successfully
        """
        self.stringBox(self.methodName())
        self.editFstabFileForMountEntries()
        self.useMountCommandsToMountDrives()
        self.verifySuccessfulMounting()


    def reboot(self):
        print("~ " * 30)
        print()
        self.stringBox("  **  Buoy Installation Complete!!  **  ")

        reboot = input("Install script successful. Reboot? [Y/n]: ")

        if reboot == "Y":
            installer.execRawCmd("sudo reboot")
        else:
            print("Install complete.")
            self.stringBox("Don't forget to reboot soon!")


if __name__ == "__main__":
    installMaster = MasterInstaller()

    installMaster.displayWelcome("buoy-ascii.art", 50)

    workflow = [
        [True, "Install the required dependencies for the Buoy System", "installMaster.installDependencies()"],
        [True, "Install required Python libraries for the Buoy System", "installMaster.installPythonPackages()"],
        [False, "Install optional applications (useful but not required)", "installMaster.installOptionals()"],
        [True, "Install video, audio, and sensor capture scripts", "installMaster.installCaptureScripts()"],
        [True, "Configure the Audio settings based on current hardware", "installMaster.setupAudioConfigFiles()"],
        [True, "Configure the Video settings based on current hardware", "installMaster.setupVideoConfigFiles()"],
        [True, "Install the auto-start services for capture script", "installMaster.installSystemdServices()"],
        [True, "Set the Hostname of the machine", "installMaster.setHostname()"],
        [True, "Reboot to complete all changes", "installMaster.reboot()"]
        ]

    selector = WorkflowSelector(workflow)

    workflow = selector.selectWorkflow("If you have not run the installer script before, it is\n\n    ***>  HIGHLY RECOMMENDED  <***\n\nthat you leave all the values above at their defaults...")

    for step in workflow:
        if (step[0] == True):
            code = step[2]
            try:
                exec(code)
            except Exception as e:
                print("Uh-oh!  Please contact Buoy Support with the following information!\n\n" + code, e)
                break



