import sys
import os
import re

class Parser():
    def __init__(self, relative_path):
        self.lines       = []
        self.path        = os.path.abspath(relative_path)
        self.name        = os.path.splitext(os.path.basename(self.path))[0] 
        self.index       = -1
        self.commandType = None
        self.arg1        = None
        self.arg2        = None
        self.parseInput()
        self.reset()
        self.commands = {"push": "C_PUSH",
                         "add":  "C_ARITHMETIC"}

    def parseInput(self):
        with open(self.path) as f:
            self.lines = [line for line in f.read().splitlines()
                          if line
                          and not re.match(r"//", line)
                          and not re.match(r"^[ \t]*$", line)]

    def advance(self):
        self.index += 1
        line = self.lines[self.index].split(" ")
        self.commandType = None
        self.arg1 = None
        self.arg2 = None
        if line[0] in ["add"]:
            self.commandType = "C_ARITHMETIC"
            self.arg1 = line[0]
        elif line[0] in ["push"]:
            self.commandType = "C_PUSH"
            self.arg1 = line[1]
            self.arg2 = line[2]

    def hasMoreCommands(self):
        return self.index + 1 < len(self.lines)

    def reset(self):
        self.index       = -1
        self.commandType = None
        self.arg1        = None
        self.arg2        = None


class CodeWriter():
    def __init__(self, parser):
        self.parser = parser

    def writeLines(self, file, lines):
        for line in lines:
            file.write(line)
            file.write(os.linesep)

    def advancePointer(self, f, pointer):
        locations = {"stack": 0}
        self.writeLines(f, [f"////advance {pointer} pointer",
                            f"@{locations[pointer]}",
                            f"M=M+1"])

    def decrementPointer(self, f, pointer):
        locations = {"stack": 0}
        self.writeLines(f, [f"////advance {pointer} pointer",
                            f"@{locations[pointer]}",
                            f"M=M-1"])

    def loadAFromStack(self, f):
        self.decrementPointer(f, "stack")
        self.writeLines(f, [f"////load from stack to A register",
                            f"@0",
                            f"A=M",
                            f"A=M"])

    def loadDFromStack(self, f):
        self.decrementPointer(f, "stack")
        self.writeLines(f, [f"////load from stack to D register",
                            f"@0",
                            f"A=M",
                            f"D=M"])

    def resultToStack(self, f):
        self.writeLines(f, [f"////result to stack",
                            f"@0",
                            f"A=M",
                            f"M=D"])
        self.advancePointer(f, "stack")

    def writeArithmetic(self, f, op):
        op_to_asm = {"add": "D=D+A"}
        f.write(f"//{self.parser.arg1}\n")
        self.loadDFromStack(f)
        self.loadAFromStack(f)
        self.writeLines(f, [op_to_asm[op]])
        self.resultToStack(f)

    def writePush(self, f, stack, address):
        f.write(f"//push {self.parser.arg1} {self.parser.arg2}\n")
        self.writeLines(f, [f"@{self.parser.arg2}",
                                       f"D=A",
                                       f"@0",
                                       f"A=M",
                                       f"M=D",])
        self.advancePointer(f, "stack")

    def write(self):
        with open(f"{self.parser.name}.asm", 'w') as f:
            while self.parser.hasMoreCommands():
                self.parser.advance()
                if self.parser.commandType == "C_ARITHMETIC":
                    self.writeArithmetic(f, self.parser.arg1)
                elif self.parser.commandType == "C_PUSH":
                    self.writePush(f, self.parser.arg1, self.parser.arg2)
                elif self.parser.commandType == "C_POP":
                    continue
                elif self.parser.commandType == "C_LABEL":
                    continue
                elif self.parser.commandType == "C_GOTO":
                    continue
                elif self.parser.commandType == "C_IF":
                    continue
                elif self.parser.commandType == "C_FUNCTION":
                    continue
                elif self.parser.commandType == "C_RETURN":
                    continue
                elif self.parser.commandType == "C_CALL":
                    continue
                else:
                    print(f"{self.parser.commandType} is not a valid command")
                    break

code_writer = CodeWriter(Parser(sys.argv[1]))
code_writer.write()
