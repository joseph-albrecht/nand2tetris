#!/usr/bin/env python3
import sys
import os

def run_test(file):
    parser_command = "python3 " + os.path.abspath("./VMTranslator.py")
    test_paths = {"basic":   "./MemoryAccess/BasicTest/",
                  "pointer": "./MemoryAccess/PointerTest/",
                  "static":  "./MemoryAccess/StaticTest/",
                  "simple":  "./StackArithmetic/SimpleAdd/",
                  "stack":   "./StackArithmetic/StackTest/"}
    emulator = "/Users/joey/Documents/nand2tetris/tools/CPUEmulator.sh"
    if file not in test_paths:
        print(f"this is not a test: {file}")
        return
    os.system(f"./run-test.sh '{parser_command}' {emulator} {test_paths[file]}"),

files = sys.argv[1:]

if len(files) > 0:
    for file in files:
        run_test(file)
else:
    for file in ["basic", "pointer", "static", "simple", "static"]:
        run_test(file)
