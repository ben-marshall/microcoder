#!/usr/bin/python3

import os
import sys
import argparse
import logging as log

import pyucode as ucode

def parseArguments():
    """
    parse all command line arguments to the program.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ports",help="Description file for the ports")
    parser.add_argument("state",help="Description file for program state")
    parser.add_argument("instructions",help="Instructions definition file")
    parser.add_argument("program",help="The program to compile.")

    args = parser.parse_args()
    return args

def main():
    """
    Main entry point for the program
    """
    args = parseArguments()

    print("---------- uCode Compiler ----------")
    
    ports   = ucode.parsePortsYAML(args.ports)
    state   = ucode.parseProgramVariablesYAML(args.state)
    
    instrs  = ucode.UCInstructionCollection()
    instrs.parse(args.instructions)

    program = ucode.UCProgram()
    program.parseSource(args.program)

if(__name__ == "__main__"):
    main()
