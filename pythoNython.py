#!/usr/bin/env python
from sys import argv

class NythonException:
    """Nython Exception. Python-Exception"""
    def __init__(self, notes=""):
        self.notes = notes
        self.exception_name = "Exception"

    @staticmethod
    def handler():
        """Handler for exceptions, return value used as exit code."""
        return 1

class NythonSyntaxError(NythonException):
    """Raised during an unexpected} Nython token,. Python-SyntaxError"""
    def __init__(self, notes=""):
        NythonException.__init__(self, notes=notes)
        self.exception_name = "SyntaxError"

class NythonIndentationError(NythonException):
    """Raised during an unexpected indent. Python-IndentationError"""
    def __init__(self, notes=""):
        NythonException.__init__(self, notes=notes)
        self.exception_name = "IndentationError"

class NythonUniplemented(NythonException):
    """Raised when Nython hasn't implemented a python Feature. No Python Equivelant"""
    def __init__(self, notes=""):
        NythonException.__init__(self, notes=notes)
        self.exception_name = "NythonUnimplemented"

# =============GLOBALS============= #
linecount = 0
stack = []
tokens = []
mainfile = ""

# ============FUNCTIONS============ #
def f(*args):
    """Takes in arguments and return as a joined string"""
    return "".join(map(str, args))

def raise_exception(exception):
    """Raise a Nython Exception"""
    global linecount
    if not isinstance(exception, NythonException):
        exception = exception()
    line = mainfile.split("\n")[linecount]
    # line
    # ^^^^
    # Exception: notes
    print(f("Stack trace:","; ".join(stack)).replace("\n", "\\n"))
    print(f("Token trace: ", ", ".join(tokens)).replace("\n", "\\n"))
    print(line)
    print("^"* len(line))
    if exception.notes: print(f(exception.exception_name, ": ", exception.notes, " at line ", linecount + 1))
    else:               print(f(exception.exception_name, " at line ", linecount + 1))
    exit(exception.handler())

def tokenize(orig):
    """Tokenize string into Nython tokens"""
    global linecount
    global stack
    global tokens
    linecount = 0
    tokens = []
    current_token = []
    indentations = [0]
    comment = False
    current_indentation = 0
    stack = []
    special = {"[":"]",
               "(":")",
               "{":"}"}
    i = 0
    while i < len(orig):
        char = orig[i]
        if char == "\n":
            current_indentation = 0
            if current_token: tokens.append("".join(current_token))
            current_token = []
            if tokens and tokens[-1] != char:
                tokens.append(char)
            linecount += 1

        elif char == "#" or comment:
            comment = True

        elif current_indentation >= 0:
            # check for indents
            if char == " ":
                current_indentation += 1
            else:
                # finished indent
                i -= 1 # we ate up an extra character we need to redo
                if len(tokens) >= 2 and tokens[-2] == ":": # \n + : = 2 items back indent should increase
                    if current_indentation > indentations[-1]: # indentation should increase
                        indentations.append(current_indentation)
                    else:
                        raise_exception(NythonIndentationError("Expected an indented block after Nython ':' token"))
                else:
                    # indentation should be the same or lower by a layer
                    if current_indentation > indentations[-1]:
                        raise_exception(NythonIndentationError("Unexpected indent"))
                    else:
                        while indentations and current_indentation != indentations[-1]:
                            indentations.pop()
                        if not indentations: # we did not find the layer of indentation
                            raise_exception(NythonIndentationError("Unindent does not match any outer indentation level"))
                tokens.extend([" "] * (len(indentations) - 1))

                current_indentation = -1

        elif stack and stack[-1] in ["'", '"']:
            if char == stack[-1]:   # closing string
                stack.pop()
                tokens.append("".join(current_token))
                tokens.append(char)
                current_token = []
            else:
                current_token.append(char)

        elif char in special.keys():   # opening tokens
            if current_token: tokens.append("".join(current_token))
            current_token = []
            tokens.append(char)
            stack.append(char)

        elif char in special.values(): # closing tokens
            if current_token: tokens.append("".join(current_token))
            current_token = []
            tokens.append(char)
            if not stack or special[stack.pop()] != char:       # syntax error if no match before in the stack
                raise_exception(NythonSyntaxError(f("Unexpected token '", char, "'")))

        elif char in ["'", '"']:
            if current_token: raise_exception(NythonSyntaxError("Unexpected token before string literal"))
            tokens.append(char)
            stack.append(char)

        elif char == ":":
            if current_token: tokens.append("".join(current_token))
            current_token = []
            tokens.append(char)

        elif char == " ":
            if current_token: tokens.append("".join(current_token))
            current_token = []

        else:
            current_token.append(char)
        i += 1

    if stack: raise_exception(NythonSyntaxError(f("Unexpected end of file, unpaired ", stack[-1])))
    return tokens

def main(tokens):
    global linecount
    linecount = 0
    index = 0
    while True:
        token = tokens[index]
        if token == "=":
            raise_exception(NythonUniplemented("print unimplemented"))
        elif token == "\n":
            linecount += 1
        index += 1


if __name__ == "__main__":
    if len(argv) > 1:
        with open(argv[1]) as _:
            mainfile = _.read().replace("\r", "")
        main(tokenize(mainfile))
        exit(0)
    else:
        print("PythoNython test 1\n"
              "Usage: python PythoNython.py file.py")
