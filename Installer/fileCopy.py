import argparse
import os
import shutil


def copyFiles(sourceDir, targetDir):

    try:
        for filename in os.listdir(sourceDir):
            sourceFile = os.path.join(sourceDir, filename)
            targetFile = os.path.join(targetDir, filename)
            #if os.path.isfile(sourceDir) == False:
            print(f"Copying '{sourceFile}' to '{targetFile}'...")
            shutil.copy(sourceFile, targetFile)

        print("File copy complete.")
    except Exception as e:
        print(f"An error occurred: {e}")
