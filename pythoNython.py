#!/usr/bin/env python
from sys import argv

def main(mainfile):
    pass

if __name__ == "__main__":
    if len(argv) > 1:
        with open(argv[1]) as f:
            mainfile = f.readlines()
        main(mainfile)
    else:
        print("PythoNython test 1\n"
              "Usage: PythoNython.py file.py")