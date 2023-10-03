#####################################
##         STORAGE SERVICE         ##
#####################################

import os

# Get the directory where the current script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set the current working directory to the script directory
os.chdir(script_dir)

from fastapi import FastAPI, HTTPException
from storageService import StorageService

# Initialize FastAPI
app = FastAPI()

storage = StorageService()

#######################
#  MAIN REST SERVICE  #
#######################
@app.post("/store")
async def storeItem(itemJson: dict):
    retVal = storage.storeItem(itemJson)
    return retVal

@app.post("/requestForProcess")
async def requestForProcess(itemJson: dict):
    retVal = storage.findAvailableProcessTarget(itemJson)
    return retVal
