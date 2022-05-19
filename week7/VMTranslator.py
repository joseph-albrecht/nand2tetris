import sys
import os
import re

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
        split_line= self.lines[self.index].split(" ")
        self.commandType = split_line[0]
        self.arg1        = split_line[1]
        if len(split_line) > 2:
            self.arg2    = split_line[2]

    def hasMoreCommands(self):
        return self.index < len(self.lines)

parser = Parser(sys.argv[1])
