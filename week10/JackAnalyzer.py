import sys
import os
import re

class JackTokenizer():
    def __init__(self, path):
        self.path = path
        self.name = os.path.splitext(os.path.basename(self.path))[0]
        self.text = self.fileText()
        self.cursor = 0
        self.token = None
        self.keywords = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"]
        self.symbols = ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"]
        self.whitespace = [" ", "\t", "\n", "\r"]
        self.quote = "\""

    def fileText(self):
        with open(self.path) as f:
            return "".join([line for line in f.read()
                            if not re.match(r"//.*", line)])

    def advanceCursor(self, cursor):
        if cursor > len(self.text):
            return None, None
        token     = None
        in_string = False
        in_block_comment = False
        in_line_comment  = False
        while cursor < len(self.text) and self.text[cursor] in self.whitespace:
            cursor += 1
        tokenized = False
        while cursor < len(self.text) and \
              (self.text[cursor] not in self.whitespace or \
               in_string or \
               in_line_comment or \
               in_block_comment):
            c = self.text[cursor]
            if token and token + c == "//":
                in_line_comment = True
                cursor += 1
                token = ""
                continue
            elif in_line_comment and c != "\n":
                cursor += 1
                continue
            elif in_line_comment and c == "\n":
                cursor += 1
                in_line_comment = False
                if token and token != "":
                    return token, cursor
                else:
                    token, cursor = self.advanceCursor(cursor)
                    return token, cursor 
            elif token and token + c == "/*":
                in_block_comment = True
            elif in_block_comment and (token + c)[-2:] == "*/":
                cursor += 1
                token, cursor = self.advanceCursor(cursor)
                return token, cursor
            elif in_block_comment:
                cursor += 1
                continue
            elif token and c in self.symbols:
                break
            elif token in self.symbols:
                return token, cursor
            elif c in self.symbols:
                tokenized = True
            elif c == self.quote and in_string:
                tokenized = True
            elif c == self.quote:
                in_string = True
            elif token and not token.isdigit() and c.isdigit():
                return token, cursor
            token = token + c if token else c
            cursor += 1
        return token, cursor

    def advance(self):
        self.token, self.cursor = self.advanceCursor(self.cursor)

    def hasMoreTokens(self):
        token, _ = self.advanceCursor(self.cursor)
        return token is not None

    def tokenType(self):
        if self.token in self.keywords:
            return "keyword"
        elif self.token in self.symbols:
            return "symbol"
        elif self.token.isdigit():
            return "integerConstant"
        elif re.match(r"^\".*\"$", self.token):
            return "stringConstant"
        elif re.match(r"^[^ \t\n]+$", self.token) or re.match(r"^\..*", self.token):
            return "identifier"
        else:
            print(f"unknown token: {self.token}")

    def keyword(self):
        return self.token

    def symbol(self):
        symbol_to_xml = {"<": "&lt;",
                         ">": "&gt;",
                         "\"": "&quot;",
                         "&": "&amp;"}
        if self.token in symbol_to_xml:
            return symbol_to_xml[self.token]
        else:
            return self.token

    def identifier(self):
        return self.token

    def intVal(self):
        return self.token

    def stringVal(self):
        return self.token[1:-1]

compilation_target = sys.argv[1]

if os.path.isfile(compilation_target):
    files = [sys.argv[1]]
    folder  = os.path.dirname(os.path.abspath(sys.argv[1]))
else:
    folder  = os.path.abspath(sys.argv[1])
    files = [os.path.join(folder, f)
             for f in os.listdir(compilation_target)
             if re.match(r".*\.jack$", f)]

for file in files:
    tokenizer = JackTokenizer(file)
    with open(f"{folder}/{tokenizer.name}T.xml", "w") as f:
        f.write("<tokens>\n")
        while tokenizer.hasMoreTokens():
            tokenizer.advance()
            val = ""
            if tokenizer.tokenType() == "integerConstant":
                val = tokenizer.intVal()
            elif tokenizer.tokenType() == "stringConstant":
                val = tokenizer.stringVal()
            elif tokenizer.tokenType() == "symbol":
                val = tokenizer.symbol()
            elif tokenizer.tokenType() == "keyword":
                val = tokenizer.keyword()
            elif tokenizer.tokenType() == "identifier":
                val = tokenizer.identifier()
            f.write(f"<{tokenizer.tokenType()}> {val} </{tokenizer.tokenType()}>\n")
        f.write("</tokens>\n")
