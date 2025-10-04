#!/usr/bin/env python
from sys import argv

class NythonInt:
    """Nython Integer class"""
    def __init__(self, value):
        self.value = value
    def __add__(self, other):
        return self.value + other
    def __str__(self):
        return str(self.value)

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

def print_n(args, kwargs):
    """print(*objects, sep=' ', end='\n', file=None, flush=False)
    Print objects to the text stream file, separated by sep and followed by end.
    sep, end, file, and flush, if present, must be given as keyword arguments. Python-print"""
    sep = kwargs.get("sep", " ")
    end = kwargs.get("end", "\n")
    if kwargs.has_key("flush", "file"):
        raise_exception(NythonUniplemented("print() currently does not support flush and file kwargs"))
    args.append(end)
    text = sep.join(str(args))
    print(text)

# =============GLOBALS============= #
linecount = 0
tokencount = 0
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
    print(f("Stack trace:","; ".join(map(str, stack))).replace("\n", "\\n"))
    print(f("Token trace: ", ", ".join(map(str, tokens))).replace("\n", "\\n"))
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
    operations = ["+", "-", "*", "/", "^", "|", "&", ":"]
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
                if char == "\n": # after indent is newline, skip empty line
                    continue
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

        elif char in operations:
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

def evaluate(tokens, objects, layer, take_elif):
    global linecount
    global tokencount
    global stack
    current_tk = 0

    token = tokens[current_tk]

    if token == "if" or token == "elif":
        if token == "elif":
            if not take_elif:
                return None
        line = []
        while token != ":":
            current_tk += 1
            token = tokens[current_tk]

            line.append(token)
            result = evaluate(line, objects, layer, take_elif)
            if result:
                stack.append(-1)
                layer[0] += 1
                take_elif[0] = 0
            else:
                take_elif[0] = 1
        return None
    if token.isdigit():
        return int(token)
    raise_exception(NythonUniplemented(f("token ", token, " unimplemented")))
    return None

def main(tokens):
    global linecount
    global stack
    global tokencount
    linecount = 0
    tokens.append("\n") # file end terminator
    line = []
    objects = [[]]
    layer = [0]     # quick alternative to pointer
    indent = 0
    take_elif = [0]
    while tokencount < len(tokens):
        token = tokens[tokencount]
        if token == " ":
            indent += 1
        elif token == "\n":
            # start executing this line
            if indent != layer[0]: # we need to skip this line part of a conditional, or an indent has ended
                if indent > layer[0]: # indent is more than what we should be executing, is a false conditional
                    tokencount += 1
                    continue
                else: # a function, conditional or loop has ended
                    return_token = stack.pop()
                    if return_token != -1: # not a conditional
                        tokencount = return_token
                        continue
            evaluate(line, objects, layer, take_elif)
            linecount += 1
            indent = 0
            line = []
        else:
            line.append(token)
        tokencount += 1


if __name__ == "__main__":
    if len(argv) > 1:
        with open(argv[1]) as _:
            mainfile = _.read().replace("\r", "")
        main(tokenize(mainfile))
        exit(0)
    else:
        print("PythoNython test 1\n"
              "Usage: python PythoNython.py file.py")
