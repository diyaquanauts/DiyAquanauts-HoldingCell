class debugger:
    @staticmethod
    def log(msg, forceLog=False):
        global DEBUG_ON
        if DEBUG_ON or forceLog is True:
            lineNum = inspect.currentframe().f_back.f_lineno
            print(f"[{os.path.basename(__file__)}~{lineNum}]: {msg}")

    @staticmethod
    def line(lineChar="-", forceLog=False):
        global DEBUG_ON
        if DEBUG_ON or forceLog is True:
            print(lineChar * 80)


#  Initialize the debugger printer
debug = debugger()

# Generate the script name without the file extension
scriptName = os.path.splitext(os.path.basename(__file__))[0]

# Define a configuration file name using the script name
configFile = f"{scriptName}.config.json"

# Load the JSON configuration using ConfigLoader
config = ConfigLoader.loadConfig(configFile)

DEBUG_ON = config.DebugOn

if not config:
    e = Exception(f"Failed to load JSON config!\n'{configFile}'")
    debug.log(e, forceLog=True)
    raise e

jDots = jdots()

# Set the index file
indexFilePath = "storeIndex.pkl"

# Various utility classes and methods
