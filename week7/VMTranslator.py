import sys
import os
import re

def list(list):
    def get(self, index, default=None):
        if index < len(self):
            self[index]
        else:
            return default
def get_default(array, index, default):
    if index < len(array):
        return array[index]
    else:
        return default

class Parser():
    def __init__(self, relative_path):
        self.lines       = []
        self.path        = os.path.abspath(relative_path)
        self.name        = os.path.basename(self.path)
        self.index       = -1
        self.parsing     = False
        self.commandType = 0
        self.arg1        = None
        self.arg2        = None
        self.parseInput()

    def parseInput(self):
        with open(self.path) as f:
            self.lines = [line for line in f.read().splitlines()
                          if line and not re.match(r"//", line)]

    def advance(self):
        self.index += 1
        line = self.lines[self.index].split(" ")
        self.commandType = line[0]
        self.arg1        = line[1]
        self.arg2        = line[2] if 2 < len(line) else None

    def hasMoreCommands(self):
        return self.index < len(self.lines)

parser = Parser(sys.argv[1])
parser.advance()
