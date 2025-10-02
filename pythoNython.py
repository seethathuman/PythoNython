#!/usr/bin/env python
import sys

def main(mainfile):
    pass

if __name__ == "__main__":
    if sys.argv:
        with open(sys.argv[0]) as f:
            mainfile = f.readlines()
        main(mainfile)
    else:
        print("PythoNython 1.0")