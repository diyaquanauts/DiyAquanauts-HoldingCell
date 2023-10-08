import inspect
import os

class debugger:
    def __init__(self, DEBUG_ON):
        self.DEBUG_ON = DEBUG_ON

    def log(self, msg, forceLog=False):
        if (self.DEBUG_ON or forceLog is True):
            lineNum = inspect.currentframe().f_back.f_lineno
            print(f"[{os.path.basename(__file__)}~{lineNum}]: {msg}")

    def line(self, lineChar="-", forceLog=False):
        if (self.DEBUG_ON or forceLog is True):
            print(lineChar * 80)

