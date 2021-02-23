#!/usr/bin/env python3

#IMPORTANT REGISTERS
# SP         RAM[0]
# LCL        RAM[1]
# ARG        RAM[2]
# THIS       RAM[3]
# THAT       RAM[4]
# TEMP       RAM[5-12]
# GP         RAM[13-15]

#all static variables j in file xxx should be translated to xxx.j

#this program should be calleable as VMTranslator.py source.vm

from enum import Enum
import sys
import os

register_addresses = {"SP"   : 0,
                      "LCL"  : 1,
                      "ARG"  : 2,
                      "THIS" : 3,
                      "THAT" : 4,
                      "TEMP" : (5,12),
                      "GP"   : (13,15),}

class CommandType(Enum):
    ARITHMETIC =  1
    PUSH       =  2
    POP        =  3
    LABEL      =  4
    GOTO       =  5
    IF         =  6
    FUNCTION   =  7
    RETURN     =  8
    CALL       =  9

class Parser:

    def __init__(self, file_path):
        self.file_handle = open(file_path, "rt")


    def hasMoreCommands(self):
        return False

    def commandType(self):
        return CommandType.ARITHMETIC

    def arg1(self):
        return ""

    def arg2(self):
        return 0

    def close(self):
        self.file_handle.close()

class CodeWriter:
    def __init__(self, file_path):
        self.file_handle = open(file_path, "wt")

    def setFileName(self, filename):
        file_path = file_path

    def writeArithmetic(self, command):
        return

    def writePushPop(self, command, segment, index):
        return

    def close(self):
        self.file_handle.close()

input_file_path = sys.argv[1]
output_file_path = os.path.splitext(input_file_path)[0] + ".asm"

vm_parser = Parser(input_file_path)
asm_writer = CodeWriter(output_file_path)

while vm_parser.hasMoreCommands():
    command = vm_parser.commandType()
    arg1 = vm_parser.arg1()
    arg2 = vm_parser.arg2()

    if command == CommandType.ARITHMETIC:
        asm_writer.writeArithmetic(command)

    elif command == CommandType.PUSH:
        asm_writer.writePushPop(command, arg1, arg2)

    else:
        print(f"{command} is not a command")

vm_parser.close()
asm_writer.close()
