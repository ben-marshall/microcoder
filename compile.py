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
    parser.add_argument("program",help="The program to compile.")
    parser.add_argument("--output","-O",help="Output path", default="out.v")
    parser.add_argument("--gendocs","-D", help="Generate documentation",
        action="store_true")
    parser.add_argument("--instrdocs", 
                        help="Instruction documentation output file path",
                        default = "doc-instrs.html")
    parser.add_argument("--progdocs", 
                        help="Program documentation output file path",
                        default = "doc-program.html")
    parser.add_argument("--debug-states", help="Display the current state each\
    simulation cycle.",action="store_true")
    parser.add_argument("--flowgraph", help="Emit a graph of program control\
    flow changes.",action="store_true")
    parser.add_argument("--graphpath", help="Path of file created when \
    --flowgraph is set.",default="flow.dot")
    parser.add_argument("--opt-coalesce",
        help="Enable coalecsing of blocks to improve performance.",
        action="store_true")

    args = parser.parse_args()
    return args

def main():
    """
    Main entry point for the program
    """
    args = parseArguments()

    print("---------- uCode Compiler ----------")
    print("> Loading sources")

    program = ucode.UCProgram()
    program.parseSource(args.program)
    
    print("> Resolving objects")

    resolver = ucode.UCResolver()
    resolver.addVariables(program.variables)
    resolver.addInstructions(program.instructions)
    resolver.addProgram(program)
    resolver.enable_coalescing = args.opt_coalesce
    resolver.resolve()
    
    print("> Rendering template to %s" % args.output)

    renderer = ucode.UCTemplater(resolver)
    renderer.debug_states = args.debug_states
    renderer.renderTo(args.output)
    
    # Generate per-program documentation
    progdocs = ucode.UCProgramDocgen(resolver)

    if(args.gendocs):
        print("> Rendering instruction documentation to %s" % args.instrdocs)
        dg = ucode.UCInstructionDocGen(resolver.instrs)
        dg.renderTo(args.instrdocs)
        
        print("> Rendering program documentation to %s" % args.progdocs)
        progdocs.gen_program_docs(args.progdocs)
    
    if(args.flowgraph):
        print("> Writing flow graph to '%s'" % args.graphpath)
        progdocs.gen_flow_dot_graph(args.graphpath)
    
    print("> Done")

if(__name__ == "__main__"):
    main()
