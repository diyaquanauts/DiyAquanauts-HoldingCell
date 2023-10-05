import os
import pickle


class IndexOperations:
    def __init__(self, debugger):
        print(debugger)
        self.debug = debugger
        print(self.debug)

    def pickleIndex(self, dictionary, filename):
        # self.debug.log(f"Pickling the index: '{filename}'")
        try:
            with open(filename, "wb") as file:
                pickle.dump(dictionary, file, protocol=pickle.HIGHEST_PROTOCOL)
            return True
        except Exception as e:
            # self.debug.log(f"Error pickling index!\n{e}", forceLog=True)
            return False

    def reloadIndex(self, indexFilePath):
        storeIndex = None
        if os.path.exists(indexFilePath):
            # self.debug.log("Loading the storeIndex...")
            storeIndex = pickle.load(open(indexFilePath, "rb"))
            # debug.log(f"storeIndex after load:\n{storeIndex}")
            # self.debug.line()
        else:
            self.debug.log("No storeIndex found...")

        return storeIndex
