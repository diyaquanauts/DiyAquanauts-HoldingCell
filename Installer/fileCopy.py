import argparse
import os
import shutil


def copyFiles(sourceDir, targetDir):

    try:
        for filename in os.listdir(sourceDir):
            sourceFile = os.path.join(sourceDir, filename)
            print(f"Copying '{sourceFile}' to '{targetDir}'...")
            if os.path.isfile(sourceDir):
                shutil.copy(source_file, targetDir)

        print("File copy complete.")
    except Exception as e:
        print(f"An error occurred: {e}")
