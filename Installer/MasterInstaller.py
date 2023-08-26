# import ExternalScriptManager

import ast
from audioInput import audioInput
import fileCopy
import getpass
import getVideoInputs
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
        installer.installPackage("cockpit")
        installer.installPackage("ffmpeg")
        installer.installPackage("python3-pip")


    def installPythonPackages(self):
        self.stringBox(self.methodName())
        installer.installPipPackages("shortuuid")
        installer.installPipPackages("psutil")


    def installCaptureScripts(self):
        self.stringBox(self.methodName())
        fileCopy.copyFiles("./captureScripts", "/home/diyaqua")


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

        reboot = input("Install script successful. Reboot? (Y/n): ")

        if reboot == "Y":
            installer.execRawCmd("sudo reboot")
        else:
            print("Install complete.")
            self.stringBox("Don't forget to reboot soon!")


if __name__ == "__main__":
    installMaster = MasterInstaller()
    installMaster.displayWelcome("buoy-ascii.art", 50)
    installMaster.installDependencies()
    installMaster.installPythonPackages()
    installMaster.installCaptureScripts()
    installMaster.setupAudioConfigFiles()
    installMaster.setupVideoConfigFiles()
    installMaster.setSudoPrivileges()
    installMaster.installSystemdServices()
    installMaster.reboot()
