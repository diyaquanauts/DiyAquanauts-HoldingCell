from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import json

class Gupload:
    def __init__(self, configFilePath):
        # Load configuration from the JSON file
        with open(configFilePath, 'r') as configFile:
            config = json.load(configFile)

        if config.get('useApiKey', False):
            # Authenticate using API key
            self.drive = GoogleDrive(config.get('apiKey'))
        else:
            # Authenticate using Google Drive API credentials from a configuration file
            gauth = GoogleAuth()
            gauth.LocalWebserverAuth()  # Authenticates using a local webserver
            self.drive = GoogleDrive(gauth)

            # Load credentials from the configuration file
            gauth.LoadCredentialsFile(config.get('credentialsPath'))

        # Initialize target folder ID
        self.targetFolderId = None

    def setTargetFolder(self, folderName):
        # Set the target folder for uploads
        self.targetFolderName = folderName
        self.targetFolderId = self.getOrCreateFolderId(folderName)

    def getOrCreateFolderId(self, folderName):
        # Check if the folder already exists, if not, create it
        folderList = self.drive.ListFile({'q': f"mimeType='application/vnd.google-apps.folder' and title='{folderName}'"}).GetList()
        if folderList:
            return folderList[0]['id']
        else:
            # Folder doesn't exist, create it
            folder = self.drive.CreateFile({'title': folderName, 'mimeType': 'application/vnd.google-apps.folder'})
            folder.Upload()
            return folder['id']

    def listFiles(self):
        # List all files and directories within the root level of the target folder
        fileList = self.drive.ListFile({'q': f"'{self.targetFolderId}' in parents and trashed=false"}).GetList()
        return fileList

    def uploadFile(self, localFilePath):
        # Upload a single file to the specified folder
        file = self.drive.CreateFile({'parents': [{'id': self.targetFolderId}]})
        file.UploadFile(localFilePath)

    def uploadMultipleFiles(self, filePaths):
        # Upload multiple files sequentially
        for filePath in filePaths:
            self.uploadFile(filePath)

# Example usage:
configFilePath = 'config.Gupload.json'
upload = Gupload(configFilePath)
upload.setTargetFolder('dataDrop')
filesToUpload = ['file1.txt', 'file2.txt', 'file3.txt']
upload.uploadMultipleFiles(filesToUpload)
fileList = upload.listFiles()
for file in fileList:
    print(file['title'])
