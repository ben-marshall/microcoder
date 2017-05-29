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
    parser.add_argument("instructions",help="Instructions definition file")
    parser.add_argument("program",help="The program to compile.")
    parser.add_argument("--output","-O",help="Output path", default="out.v")
    parser.add_argument("--gendocs","-D", help="Generate documentation",
        action="store_true")
    parser.add_argument("--instrdocs", 
                        help="Instruction documentation output file path",
                        default = "doc-instrs.html")

    args = parser.parse_args()
    return args

def main():
    """
    Main entry point for the program
    """
    args = parseArguments()

    print("---------- uCode Compiler ----------")
    print("> Loading sources")
    
    instrs  = ucode.UCInstructionCollection()
    instrs.parse(args.instructions)

    program = ucode.UCProgram()
    program.parseSource(args.program)
    
    print("> Resolving objects")

    resolver = ucode.UCResolver()
    resolver.addPorts(program.ports)
    resolver.addVariables(program.variables)
    resolver.addInstructions(instrs)
    resolver.addProgram(program)

    resolver.resolve()
    
    print("> Rendering template to %s" % args.output)

    renderer = ucode.UCTemplater(resolver)
    renderer.renderTo(args.output)

    if(args.gendocs):
        print("> Rendering instruction documentation to %s" % args.instrdocs)
        dg = ucode.UCInstructionDocGen(resolver.instrs)
        dg.renderTo(args.instrdocs)

    
    print("> Done")

if(__name__ == "__main__"):
    main()
