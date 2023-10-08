import pickle


class IndexSaver:
    @staticmethod
    def pickleIndex(dictionary, filename):
        global debug
        debug.log(f"Pickling the index: '{filename}'")
        try:
            with open(filename, "wb") as file:
                pickle.dump(dictionary, file, protocol=pickle.HIGHEST_PROTOCOL)
            return True
        except Exception as e:
            debug.log(f"Error pickling index!\n{e}", forceLog=True)
            return False
