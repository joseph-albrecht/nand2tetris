import sys
import os
import re

def hasIndex(array, index):
    return index < len(array)

class Parser():
    def __init__(self, relative_path):
        self.lines       = []
        self.path        = os.path.abspath(relative_path)
        self.name        = os.path.splitext(os.path.basename(self.path))[0] 
        self.index       = -1
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
        self.arg2        = line[2] if hasIndex(line, 2) else None

    def hasMoreCommands(self):
        return self.index < len(self.lines) - 1


class CodeWriter():
    def __init__(self, parser):
        self.parser = parser

    def write(self):
        with open(self.parser.name + ".asm" ,'w') as file:
            file.write("")

code_writer = CodeWriter(Parser(sys.argv[1]))
code_writer.write()
