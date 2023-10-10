import datetime
from FileActionApi import FileActionApi
import json
import subprocess
import time

"""
#  Sample configuration file...
{
    "processorName": "SampleProcessor",
    "maxProcesses": 5,
    "criteria": "some_criteria",
    "contentType": "application/json",
    "processRunLimit": 60,
    "sleepBetweenChecks": 10,
    "processorCmd": "python generateIoA.py {variable1} {variable2}"
}
"""


class ProcessorService:
    def __init__(self, configPath):
        self.config = self.loadConfig(configPath)
        self.processorName = self.config.processorName
        self.fileAction = FileActionApi(self.config.baseAddress, self.config.port)
        self.runningProcesses = {}
        self.pauseProcessing = False

    def log(self, msg):
        print(msg)

    def loadConfig(self, configPath):
        try:
            with open(configPath, "r") as configFile:
                config = json.load(configFile)
                return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found at: {configPath}")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in configuration file.")

    def maxProcessLimitReached(self):
        # Check if the maximum number of concurrent processes is reached...
        retVal = False
        procCount = len(self.runningProcesses)
        if procCount >= self.config.maxProcesses:
            self.log(
                f"{self.processorName}: Max concurrent processes ({procCount}) reached."
            )
            retVal = True
        return retVal

    def requestItemToProcess(self):
        itemToProcess = self.fileAction.getAvailableItem(
            self.config.criteria, self.config.contentType
        )

        return itemToProcess

    def executeExternalProcess(self, storageId, itemInfo):
        self.log(f"{self.processorName}: Processing '{storageId}'...")

        processThread = storageId, itemInfo

        expiration = datetime.datetime.now() + datetime.timedelta(
            minutes=self.config.processRunLimit
        )

        command = self.config.processorCmd

        processThread = None
        stdErr = None
        stdOut = None

        try:
            # Use subprocess.Popen to start the external process...
            processThread = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            # Capture the process output...
            stdout, stderr = processThread.communicate()

            startResult = ""

            # Check if the process started successfully...
            if processThread.returncode == 0:
                startResult = f"External process started successfully: {command}"
            else:
                startResult = (
                    f"Process returned error exit code: {command}\n\n"
                    + f"{processThread.returncode}\n\n"
                    + f"{stdout.decode('utf-8')}\n\n"
                    + f"{stderr.decode('utf-8')}",
                )
        #  All the badness happened, so...yeah...
        except Exception as e:
            startResult = (
                f"Error while starting external process: {command}\n\n{str(e)}"
            )
        processorInfo = {
            "storageId": storageId,
            "processThread": processThread,
            "stdOut": stdOut,
            "stdErr": stdErr,
            "itemInfo": itemInfo,
            "processStart": datetime.datetime.now(),
            "processExpire": expiration,
            "startResult": startResult,
        }

        self.log(startResult)
        self.runningProcesses[storageId] = processorInfo

    def processComplete(self, process):
        retVal = True

        #  Poll the process to get its current status...
        processStatus = process.poll()

        #  If process.poll() returns nothing, it's still active...
        if processStatus is None:
            retVal = False
        return retVal

    def processExpired(self, process):
        retVal = False
        expiration = process["processExpire"]
        if datetime.datetime.now() > expiration:
            retVal = True
        return retVal

    def checkForCompletedAndExpiredProcesses(self):
        # Remove the completed process from the list of running processes
        for process in self.runningProcesses:
            if self.processComplete(process):
                #  Update the storage db with a successful completion...
                self.log(process)
                del self.runningProcesses[process.storageId]
            elif self.processExpired(process):
                #  Update the storage db with a failed completion...
                self.log(process)
                del self.runningProcesses[process.storageId]

    def processorLoop(self):
        while not self.pauseProcessing:
            #  Check for and clear any processes that may have completed...
            self.checkForCompletedAndExpiredProcesses()

            if not self.maxProcessLimitReached():
                #  Check for available items to process...
                itemToProcess = self.requestItemToProcess()

                #  If we've found one, get the item info, and...
                if itemToProcess["availableRecords"]:
                    storageId = itemToProcess["availableRecords"][0]
                    itemInfo = self.fileAction.getItemInfo(storageId)

                    # Hand the item info over to the external processor...
                    self.executeExternalProcess(itemInfo)

            #  Take a little nap, schnookums...
            time.sleep(self.config.sleepBetweenChecks)
