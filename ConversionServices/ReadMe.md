So this is a farily simple set of stuff...

The first bit called "conversionQueueService.py" does the following:
   *  Accepts a REST request to /queueConvert a JSON request body:
         { 
           "FilePath": "[path to file]" 
         }
   *  Takes the given data and dumps it into a QueueFile (JSON formatted) and associated directory that contains relevant information
   *  Accepts a REST request to lock the next available QueueFile item and hand the info over to the requestor for processing
   *  Accepts a REST request to update the status of the given QueueFile item and updates the relevant information

The second bit called "conversionService.py" does the hard parts:
   *  Requests a QueueFile from the QueueService for processing
   *  Runs FFMPEG (or whatever appropriate file convertor is needed) based on the QueueFile info
   *  Determines if the conversion was successful and deletes the file if it was
   *  Sends a status update request on the QueueFile in question
   *  Moves to the next big thing...
