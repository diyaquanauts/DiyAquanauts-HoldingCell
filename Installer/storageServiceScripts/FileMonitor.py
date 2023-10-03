import os
import time

class FileMonitor:
    def __init__(self, filePath):
        self.filePath = filePath
        self.lastSize = self.getFileSize()
        self.lastMtime = self.getFileMtime()

    def getFileSize(self):
        return os.path.getsize(self.filePath)

    def getFileMtime(self):
        return os.path.getmtime(self.filePath)

    def hasChanged(self):
        currentSize = self.getFileSize()
        currentMtime = self.getFileMtime()

        # Check if either size or modification timestamp has changed
        if currentSize != self.lastSize or currentMtime != self.lastMtime:
            self.lastSize = currentSize
            self.lastMtime = currentMtime
            return True

        return False

if __name__ == "__main__":
    # Example usage
    filePath = "example.txt"
    monitor = FileMonitor(filePath)

    while True:
        if monitor.hasChanged():
            print("File has changed since last inspection.")
        time.sleep(1)  # Adjust the polling interval as needed
