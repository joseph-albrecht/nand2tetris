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
                pass
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

    def peek(self):
        token, _ = self.advanceCursor(self.cursor)
        return token

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
        if not self.tokenType() == "keyword":
            print(f"{self.name} {self.token} is not a keyword!")
        return self.token

    def symbol(self):
        if not self.tokenType() == "symbol":
            print(f"{self.name} {self.token} is not a symbol!")
        symbol_to_xml = {"<": "&lt;",
                         ">": "&gt;",
                         "\"": "&quot;",
                         "&": "&amp;"}
        if self.token in symbol_to_xml:
            return symbol_to_xml[self.token]
        else:
            return self.token

    def identifier(self):
        if not self.tokenType() == "identifier":
            print(f"{self.name} {self.token} is not a identifier!")
        return self.token

    def intVal(self):
        if not self.tokenType() == "integerConstant":
            print(f"{self.name} {self.token} is not an integerConstant!")
        return self.token

    def stringVal(self):
        if not self.tokenType() == "stringConstant":
            print(f"{self.name} {self.token} is not a stringConstant!")
        return self.token[1:-1]


class CompilationEngine():
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.stack = []

    def compile(self):
        jack_path = self.tokenizer.path
        vm_path   = f"{os.path.splitext(jack_path)[0]}T.xml"
        with open(f"{vm_path}", "w") as out:
            self.out = out
            self.compileClass()

    def tokenOut(self):
        jack_path = self.tokenizer.path
        vm_path   = f"{os.path.splitext(jack_path)[0]}T.xml"
        with open(f"{vm_path}", "w") as f:
            f.write("<tokens>\n")
            while self.tokenizer.hasMoreTokens():
                self.tokenizer.advance()
                val = ""
                if self.tokenizer.tokenType() == "integerConstant":
                    val = self.tokenizer.intVal()
                elif self.tokenizer.tokenType() == "stringConstant":
                    val = self.tokenizer.stringVal()
                elif self.tokenizer.tokenType() == "symbol":
                    val = self.tokenizer.symbol()
                elif self.tokenizer.tokenType() == "keyword":
                    val = self.tokenizer.keyword()
                elif self.tokenizer.tokenType() == "identifier":
                    val = self.tokenizer.identifier()
                f.write(f"<{self.tokenizer.tokenType()}> {val} </{self.tokenizer.tokenType()}>\n")
            f.write("</tokens>\n")

    def writeLine(self, line):
        self.out.write(f"{line}\n")
        self.stackTrace()
        print(f"{line}\n")

    def compileKeyword(self, val=None):
        if val and \
           ((type(val) == str and val != self.tokenizer.token) or \
            (type(val) == list and self.tokenizer.token not in val)):
            print(f"{self.tokenizer.name} {self.stack} {self.tokenizer.token} is not {val}")
            exit()
        # if self.tokenizer.tokenType() == "keyword":
        self.writeLine(f"<keyword> {self.tokenizer.keyword()} </keyword>")
        self.tokenizer.advance()
        return True
        # return False

    def compileIdentifier(self, val=None):
        if val and val != self.tokenizer.token:
            print(f"{self.tokenizer.name} {self.stack} {self.tokenizer.token} is not {val}")
            exit()
        # if self.tokenizer.tokenType() == "identifier":
        self.writeLine(f"<identifier> {self.tokenizer.identifier()} </identifier>")
        self.tokenizer.advance()
        return True
        # return False

    def compileSymbol(self, val=None):
        if val and \
           ((type(val) == str and val != self.tokenizer.token) or \
            (type(val) == list and self.tokenizer.token not in val)):
            print(f"{self.tokenizer.name} {self.stack} {self.tokenizer.token} is not {val}")
            exit()
        # if self.tokenizer.tokenType() == "symbol":
        self.writeLine(f"<symbol> {self.tokenizer.symbol()} </symbol>")
        self.tokenizer.advance()
        return True
        # return False

    def compileIntegerConstant(self):
        self.writeLine(f"<integerCostant> {self.tokenizer.intVal()} </integerConstant>")
        self.tokenizer.advance()

    def compileStringConstant(self):
        self.writeLine(f"<stringCostant> {self.tokenizer.stringVal()} </stringConstant>")
        self.tokenizer.advance()
        
    def compileStar(self, function):
        found = function()
        while found:
            found = function()
        return True

    def compileList(self, function):
        self.enter("list")
        found = function()
        while found:
            if self.tokenizer.token == ",":
                self.compileSymbol(",")
                found = function()
            else:
                break

        self.exit("list")
        return True

    def compileClass(self):
        self.enter("class")
        self.writeLine("<class>")
        # class declaration
        self.tokenizer.advance()
        self.compileKeyword("class")
        self.compileIdentifier()
        self.compileSymbol("{")
        # class variable declarations
        self.compileStar(self.compileClassVarDec)
        # class method declarations
        self.compileStar(self.compileSubroutine)
        # close class declaration
        self.compileSymbol("}")
        self.writeLine("</class>")
        self.exit("class")
        return True

    def compileClassVarDec(self):
        self.enter("classVarDec")
        if self.tokenizer.token in ["static", "field"]: # found a class variable!
            self.writeLine("<classVarDec>")
            self.compileKeyword(["static", "field"])
            self.compileKeyword()
            self.compileIdentifier()
            while self.tokenizer.token == ",":
                self.compileSymbol(",")
                self.compileIdentifier()
            self.compileSymbol(";")
            self.writeLine("</classVarDec>")
            self.exit()
            return True
        self.exit("classVarDec")
        return False

    def compileConstructor(self):
        self.enter("constructor")
        self.writeLine("<subroutineDec>")
        self.compileKeyword("constructor")
        self.compileIdentifier()
        self.compileIdentifier("new")
        self.compileSymbol("(")
        self.compileList(self.compileParameter)
        self.compileSymbol(")")
        self.compileSubroutineBody()
        self.writeLine("</subroutineDec>")
        self.exit("constructor")

        return True

    def compileFunction(self):
        self.enter("function")
        self.writeLine("<subroutineDec>")
        self.compileKeyword("function")
        if self.tokenizer.token == "void":
            self.compileKeyword("void")
        else:
            self.compileIdentifier()
        self.compileIdentifier()
        self.compileSymbol("(")
        self.compileList(self.compileParameter)
        self.compileSymbol(")")
        self.compileSubroutineBody()
        self.writeLine("</subroutineDec>")
        self.exit("function")
        return True

    def compileMethod(self):
        self.enter("method")
        self.writeLine("<subroutineDec>")
        self.compileKeyword("method")
        if self.tokenizer.token == "void":
            self.compileKeyword("void")
        else:
            self.compileIdentifier()
        self.compileIdentifier()
        self.compileSymbol("(")
        self.compileList(self.compileParameter)
        self.compileSymbol(")")
        self.compileSubroutineBody()
        self.writeLine("</subroutineDec>")
        self.exit("method")
        return True
    
    def compileSubroutine(self):
        results = False
        if self.tokenizer.token == "constructor":
            results = self.compileConstructor()
        elif self.tokenizer.token == "method":
            results = self.compileMethod()
        elif self.tokenizer.token == "function":
            results = self.compileFunction()
        return results

    def compileParameter(self):
        self.enter("parameter")
        if self.tokenizer.token in ["int", "char", "boolean"]:
            self.compileKeyword(["int", "char", "boolean"])
            self.compileIdentifier()
            self.exit("parameter")
            return True
        self.exit("parameter")
        return False

    def compileSubroutineBody(self):
        self.enter("subroutineBody")
        self.writeLine("<subroutineBody>")
        self.compileSymbol("{")
        self.compileStar(self.compileVarDec)
        self.compileStar(self.compileStatement)
        self.compileSymbol("}")
        self.writeLine("</subroutineBody>")
        self.exit("subroutineBody")
        return True

    def compileVarDec(self):
        self.enter("varDec")
        if self.tokenizer.token == "var": # found variable
            self.writeLine("<varDec>")
            self.compileKeyword("var")
            if self.tokenizer.token in ["int", "char", "boolean"]:
                self.compileKeyword(["int", "char", "boolean"])
            else:
                self.compileIdentifier()
            self.compileIdentifier()
            while self.tokenizer.token == ",":
                self.compileSymbol(",")
                self.compileIdentifier()
            self.compileSymbol(";")
            self.writeLine("</varDec>")
            self.exit("varDec")
            return True
        self.exit("varDec")
        return False

    def compileStatement(self):
        statements_to_functions = {"let":    self.compileLet,
                                   "if":     self.compileIf,
                                   "while":  self.compileWhile,
                                   "do":     self.compileDo,
                                   "return": self.compileReturn}
        if self.tokenizer.token in statements_to_functions:
            return statements_to_functions[self.tokenizer.token]()
        return False

    def compileLet(self):
        self.enter("let")
        self.compileKeyword("let")
        self.compileExpression(with_equals=False)
        self.compileSymbol("=")
        self.compileExpression(with_equals=False)
        self.compileSymbol(";");
        self.exit("let")
        return True

    def compileIf(self):
        self.enter("if")
        self.compileKeyword("if")
        self.compileSymbol("(")
        self.compileExpression()
        self.compileSymbol(")")
        self.compileSymbol("{");
        self.compileStar(self.compileStatement)
        self.compileSymbol("}")
        if self.tokenizer.token == "else":
            self.compileKeyword("else")
            self.compileSymbol("{");
            self.compileStar(self.compileStatement)
            self.compileSymbol("}")
        self.exit("if")
        return True

    def compileWhile(self):
        self.enter("while")
        self.compileKeyword()
        self.compileSymbol()
        self.compileExpression()
        self.compileSymbol()
        self.compileSymbol()
        self.compileStar(self.compileStatement)
        self.compileSymbol()
        self.exit("while")
        return True

    def compileDo(self):
        self.enter("do")
        self.compileKeyword("do")
        self.compileSubroutineCall()
        self.compileSymbol(";")
        self.exit("do")
        return True

    def compileSubroutineCall(self):
        self.enter("subroutineCall")
        # check if identifer.function() or just function()
        self.compileIdentifier()
        if self.tokenizer.token == ".":
            self.compileSymbol(".")
            self.compileIdentifier()
        #expression list
        self.compileSymbol("(")
        self.compileList(self.compileExpression)
        self.compileSymbol(")")
        self.exit("subroutineCall")
        return True

    def compileReturn(self):
        self.enter("return")
        self.writeLine("<return>")
        self.compileKeyword("return")
        self.compileExpression()
        self.compileSymbol(";")
        self.writeLine("</return>")
        self.exit("return")
        return True

    def compileExpression(self, with_equals=True):
        self.enter("expression")
        found = self.compileTerm()
        ops = ["+", "-", "*", "/", "&", "|", "<", ">"] + (["="] if with_equals else [])
        print(ops)
        while self.tokenizer.token in ops:
            self.compileSymbol(ops)
            found = self.compileTerm()
        self.exit("expression")
        return True

    def compileTerm(self):
        self.enter("term")
        # integerConstant
        if self.tokenizer.tokenType() == "integerConstant":
            self.compileIntegerConstant()
        # stringConstant
        elif self.tokenizer.tokenType() == "stringConstant":
            self.compileStringConstant()
        # keywordConstant
        elif self.tokenizer.token in ["true", "false", "null", "this"]:
            self.compileKeyword()
        # '-'|'~' term
        elif self.tokenizer.token in ["-", "~"]:
            self.compileSymbol()
            self.compileTerm()
        # '(' expression ')'
        elif self.tokenizer.token == "(":
            self.compileSymbol("(")
            self.compileExpression()
            self.compileSymbol(")")
        # subroutineCall
        elif self.tokenizer.tokenType() == "identifier" and self.tokenizer.peek() in [".", "("]:
            self.compileSubroutineCall()
        elif self.tokenizer.tokenType() == "identifier" and self.tokenizer.peek() == "[":
            self.compileIdentifier()
            self.compileSymbol("[")
            self.compileExpression(with_equals=False)
            self.compileSymbol("]")
        elif self.tokenizer.tokenType() == "identifier":
            self.compileIdentifier()
        self.exit("term")

    def enter(self, name):
        self.stack.append(name)

    def exit(self, name=None):
        if name and name != self.stack[-1]:
            print(f"stack out of alignment!")
        self.stack.pop()

    def stackTrace(self):
        print(f"file: {self.tokenizer.name} stack: {self.stack}")
    


class JackAnalyzer():
    def __init__(self, target):
        if os.path.isfile(target):
            self.folder = os.path.dirname(os.path.abspath(target))
            self.files  = [os.path.abspath(target)]
        else:
            self.folder = os.path.abspath(target)
            self.files  = [os.path.join(self.folder, f)
                           for f in os.listdir(target)
                           if re.match(r".*\.jack$", f)]

    def compile(self):
        for file in self.files:
            compiler = CompilationEngine(JackTokenizer(file))
            compiler.compile()

analyzer = JackAnalyzer(sys.argv[1])
analyzer.compile()
