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

        if line[0] in ["add", "sub", "and", "or", "neg", "eq", "lt", "gt", "not"]:
            self.commandType = "C_ARITHMETIC"
            self.arg1 = line[0]
        elif line[0] in ["push"]:
            self.commandType = "C_PUSH"
            self.arg1 = line[1]
            self.arg2 = line[2]
        elif line[0] in ["pop"]:
            self.commandType = "C_POP"
            self.arg1 = line[1]
            self.arg2 = line[2]
        elif line[0] == "label":
            self.commandType = "C_LABEL"
            self.arg1        = line[1]
        elif line[0] == "if-goto":
            self.commandType = "C_IF"
            self.arg1        = line[1]
        elif line[0] == "goto":
            self.commandType = "C_GOTO"
            self.arg1        = line[1]
        elif line[0] == "function":
            self.commandType = "C_FUNCTION"
            self.arg1        = line[1]
            self.arg2        = line[2]
        elif line[0] == "return":
            self.commandType = "C_RETURN"
        elif line[0] == "call":
            self.commandType = "C_CALL"
            self.arg1        = line[1]
            self.arg2        = line[2]

    def hasMoreCommands(self):
        return self.index + 1 < len(self.lines)

    def reset(self):
        self.index       = -1
        self.commandType = None
        self.arg1        = None
        self.arg2        = None


class CodeWriter():
    def __init__(self, path):
        self.path        = path
        self.parser      = None
        self.currentLine = 0
        self.symbol_count = 1

    def makeSymbol(self):
        symbol = str(self.symbol_count)
        self.symbol_count += 1
        return symbol

    def writeLines(self, file, lines):
        for line in lines:
            if not re.match(r"^//", line):
                file.write(f"//{self.currentLine}" + os.linesep)

            file.write(line)
            file.write(os.linesep)
            if not re.match(r"^//", line):
                self.currentLine += 1

    def advancePointer(self, f, pointer):
        locations = {"stack": 0}
        self.writeLines(f, [f"////advance {pointer} pointer",
                            f"@{locations[pointer]}",
                            f"M=M+1"])

    def decrementPointer(self, f, pointer):
        locations = {"stack": 0}
        self.writeLines(f, [f"////decrement {pointer} pointer",
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
        f.write(f"//arithmetic: {self.parser.arg1}\n")
        self.loadDFromStack(f)
        if op not in ["neg", "not"]:
            self.loadAFromStack(f)
        if_true = "if_true" + self.makeSymbol()
        if_false = "if_false" + self.makeSymbol()
        op_to_asm = {"add": ["D=D+A"],
                     "sub": ["D=A-D"],
                     "and": ["D=D&A"],
                     "or":  ["D=D|A"],
                     "neg": ["D=-D"],
                     "not": ["D=!D"],
                     "eq":  ["D=A-D",
                             f"@{if_true}",
                             f"D;JEQ",
                             f"D=0",
                             f"@{if_false}",
                             f"0;JMP",
                             f"({if_true})",
                             f"D=-1",
                             f"({if_false})"],
                     "lt":  ["D=A-D",
                             f"@{if_true}",
                             f"D;JLT",
                             f"D=0",
                             f"@{if_false}",
                             f"0;JMP",
                             f"({if_true})",
                             f"D=-1",
                             f"({if_false})"],
                     "gt":  ["D=A-D",
                             f"@{if_true}",
                             f"D;JGT",
                             f"D=0",
                             f"@{if_false}",
                             f"0;JMP",
                             f"({if_true})",
                             f"D=-1",
                             f"({if_false})"]}
        self.writeLines(f, op_to_asm[op])
        self.resultToStack(f)

    def writePush(self, f, pointer, offset):
        pointer_to_address = {"stack": 0,
                              "local": 1,
                              "argument": 2,
                              "this": 3,
                              "that": 4,
                              "temp": 5,
                              "static": -1,
                              "constant": -1,
                              "pointer": -1}
        f.write(f"//push {pointer} {offset}\n")
        address = pointer_to_address[pointer]
        if pointer == "constant":
            self.writeLines(f, [f"@{offset}",
                                f"D=A"])
        elif pointer == "pointer":
            self.writeLines(f, [f"@{3+int(offset)}",
                                f"D=M"])
        elif pointer == "static":
            self.writeLines(f, [f"@{self.parser.name+offset}",
                                f"D=M"])
        elif pointer == "temp":
            self.writeLines(f, [f"@{offset}",
                                f"D=A",
                                f"@{address}",
                                f"A=D+A",
                                f"D=M"])
        else:
            self.writeLines(f, [f"@{offset}",
                                f"D=A",
                                f"@{address}",
                                f"A=M",
                                f"A=D+A",
                                f"D=M"])
        self.writeLines(f, [f"@0",
                            f"A=M",
                            f"M=D",])
        self.advancePointer(f, "stack")

    def writePop(self, f, pointer, offset):
        pointer_to_address = {"stack": 0,
                              "local": 1,
                              "argument": 2,
                              "this": 3,
                              "that": 4,
                              "temp": 5,
                              "static": -1,
                              "pointer": -1,
                              "constant": -1}
        f.write(f"//pop {self.parser.arg1} {self.parser.arg2}\n")
        address = pointer_to_address[pointer]
        if pointer == "pointer":
            self.writeLines(f, [f"@{3+int(offset)}",
                                f"D=A",
                                f"@13",
                                f"M=D"])
        elif pointer == "static":
            self.writeLines(f, [f"@{self.parser.name+offset}",
                                f"D=A",
                                f"@13",
                                f"M=D"])
        elif pointer == "temp":
            self.writeLines(f, [f"@{offset}",
                                f"D=A",
                                f"@{address}",
                                f"D=D+A",
                                f"@13",
                                f"M=D"])
        else:
            self.writeLines(f, [f"@{offset}",
                                f"D=A",
                                f"@{address}",
                                f"A=M",
                                f"D=D+A",
                                f"@13",
                                f"M=D"])
        self.decrementPointer(f, "stack")
        self.writeLines(f, [f"@0",
                            f"A=M",
                            f"D=M",])
        self.writeLines(f, [f"@13",
                            f"A=M",
                            f"M=D",])

    def writeLabel(self, f, label):
        self.writeLines(f, [f"//write label {label}",
                            f"({label})"])

    def writeIf(self, f, label):
        self.loadDFromStack(f)
        self.writeLines(f, [f"//goto label {label}",
                            f"@{label}",
                            f"D;JNE"])

    def writeGoto(self, f, label):
        self.writeLines(f, [f"//goto label {label}",
                            f"@{label}",
                            f"0;JMP"])

    def writeFunction(self, f, label, args):
        self.writeLines(f, ["//make function",
                            f"({label})",
                            f"@0",
                            f"D=M",
                            f"@1",
                            f"M=D"])
        for i in range(int(args)):
            self.advancePointer(f, "stack")
            
    def writeReturn(self, f):
        self.writeLines(f, ["//write return code"])
        self.loadDFromStack(f)
        self.writeLines(f, [f"@13", # save return value
                            f"M=D",
                            f"@2",
                            f"D=M",
                            f"@14",
                            f"M=D",
                            f"@1",   #move SP to LCL
                            f"D=M",
                            f"@0",
                            f"M=D"])
        # reset that
        self.loadDFromStack(f)
        self.writeLines(f, [f"@4",
                            f"M=D"])
        #reset this
        self.loadDFromStack(f)
        self.writeLines(f, [f"@3",
                            f"M=D"])
        #reset arg
        self.loadDFromStack(f)
        self.writeLines(f, [f"@2",
                            f"M=D"])
        #reset lcl
        self.loadDFromStack(f)
        self.writeLines(f, [f"@1",
                            f"M=D"])

        #save return address
        self.loadDFromStack(f)
        self.writeLines(f, [f"//save return address",
                            f"@15",
                            f"M=D"])

        #move SP to argument section
        self.writeLines(f, [f"@14",
                            f"D=M",
                            f"@0",
                            f"M=D"])

        #push return value to stack
        self.writeLines(f, [f"//push return value to stack",
                            f"@13",
                            f"D=M",
                            f"@0",
                            f"A=M",
                            f"M=D"])

        self.advancePointer(f, "stack")

        #goto return address
        self.writeLines(f, [f"@15",
                            f"A=M",
                            f"0;JMP"])

    def writePointerToStack(self, f, pointer):
        pointer_to_address = {"stack": 0,
                              "local": 1,
                              "argument": 2,
                              "this": 3,
                              "that": 4,
                              "temp": 5,
                              "static": -1,
                              "pointer": -1,
                              "constant": -1}
        self.writeLines(f, [f"@{pointer_to_address[pointer]}",
                            f"D=M"])
        self.writeDtoStack(f)

    def writeDtoStack(self, f):
        self.writeLines(f, [f"@0",
                            f"A=M",
                            f"M=D"])
        self.advancePointer(f, "stack")
        
    def writeChangePointer(self, f, pointer, val):
        self.writeLines(f, [f"// write {pointer}"])
        pointer_to_address = {"stack": 0,
                              "local": 1,
                              "argument": 2,
                              "this": 3,
                              "that": 4,
                              "temp": 5,
                              "static": -1,
                              "pointer": -1,
                              "constant": -1}
        self.writeLines(f, [f"@{val}",
                            f"D=A",
                            f"@{pointer_to_address[pointer]}",
                            f"M=D"])
        
        
    def writeCall(self, f, function, args):
        symbol = "return" + self.makeSymbol()
        self.writeLines(f, [f"// call {function}"])
        self.writeLines(f, ["@0",
                            "D=M",
                            "@13",
                            "M=D"])
        self.writeLines(f, [f"@{symbol}",
                            f"D=A"])
        self.writeDtoStack(f)
        self.writePointerToStack(f, "local")
        self.writePointerToStack(f, "argument")
        self.writePointerToStack(f, "this")
        self.writePointerToStack(f, "that")
        self.writeLines(f, [f"@{args}",
                            f"D=A",
                            f"@13",
                            f"A=M",
                            f"D=A-D",
                            f"@2",
                            f"M=D"])
        self.writeGoto(f, function)
        self.writeLines(f, [f"({symbol})"])
        self.writeLines(f, ["// return from {function}"])

    def write(self):
        name = os.path.splitext(self.path)[0]
        if os.path.isfile(self.path):
            files = [self.path]
            outfile = f"{name}.asm"
        else:
            files = [os.path.join(name, file) for file in os.listdir(self.path) if re.match(r".*vm$", file)]
            outfile = f"{name}/{name}.asm"


        with open(outfile, 'w') as f:
            ## remove at the end!!
            if len(files) > 1:
                self.writeLines(f, [f"@256",
                                    f"D=A",
                                    f"@0",
                                    f"M=D"])
                self.writeCall(f, "Sys.init", 0)
            for file in files:
                self.parser = Parser(file)
                while self.parser.hasMoreCommands():
                    self.parser.advance()
                    if self.parser.commandType == "C_ARITHMETIC":
                        self.writeArithmetic(f, self.parser.arg1)
                    elif self.parser.commandType == "C_PUSH":
                        self.writePush(f, self.parser.arg1, self.parser.arg2)
                    elif self.parser.commandType == "C_POP":
                        self.writePop(f, self.parser.arg1, self.parser.arg2)
                    elif self.parser.commandType == "C_LABEL":
                        self.writeLabel(f, self.parser.arg1)
                    elif self.parser.commandType == "C_IF":
                        self.writeIf(f, self.parser.arg1)
                    elif self.parser.commandType == "C_GOTO":
                        self.writeGoto(f, self.parser.arg1)
                    elif self.parser.commandType == "C_FUNCTION":
                        self.writeFunction(f, self.parser.arg1, self.parser.arg2)
                    elif self.parser.commandType == "C_RETURN":
                        self.writeReturn(f)
                    elif self.parser.commandType == "C_CALL":
                        self.writeCall(f, self.parser.arg1, self.parser.arg2)
                    else:
                        print(f"{self.parser.commandType} is not a valid command")
                        break

code_writer = CodeWriter(sys.argv[1])
code_writer.write()

