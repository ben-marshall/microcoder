#!/usr/bin/python3

import os
import sys
import argparse
import logging

import pyucode as ucode

class Program(object):

    def __init__(self):
        """
        Create a new program object.
        """
        self.log = logging.getLogger(__name__)


    def configureLogging(self,args):
        """
        Setup all of the logging / info message defaults.
        """
        if(args.verbose):
            self.log.setLevel(logging.INFO)
            logging.basicConfig(level=logging.INFO)
        else:
            self.log.setLevel(logging.WARNING)
            logging.basicConfig(level=logging.WARNING)


    def parseArguments(self):
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
        parser.add_argument("--verbose", "-v", action="store_true",
            help="Be verbose when displaying messages")

        args = parser.parse_args()
        return args

    def main(self):
        """
        Main entry point for the program
        """
        args = self.parseArguments()
        self.configureLogging(args)

        self.log.info("---------- uCode Compiler ----------")
        self.log.info("> Loading sources")

        program = ucode.UCProgram()
        program.parseSource(args.program)
        
        self.log.info("> Resolving objects")

        resolver = ucode.UCResolver()
        resolver.addVariables(program.variables)
        resolver.addInstructions(program.instructions)
        resolver.addProgram(program)
        resolver.enable_coalescing = args.opt_coalesce
        resolver.resolve()
        
        self.log.info("> Rendering template to %s" % args.output)

        renderer = ucode.UCTemplater(resolver)
        renderer.debug_states = args.debug_states
        renderer.renderTo(args.output)
        
        # Generate per-program documentation
        progdocs = ucode.UCProgramDocgen(resolver)

        if(args.gendocs):
            self.log.info("> Rendering instruction documentation to %s" % args.instrdocs)
            dg = ucode.UCInstructionDocGen(resolver.instrs)
            dg.renderTo(args.instrdocs)
            
            self.log.info("> Rendering program documentation to %s" % args.progdocs)
            progdocs.gen_program_docs(args.progdocs)
        
        if(args.flowgraph):
            self.log.info("> Writing flow graph to '%s'" % args.graphpath)
            progdocs.gen_flow_dot_graph(args.graphpath)
        
        self.log.info("> Done")
        return 0


if(__name__ == "__main__"):
    p = Program()
    sys.exit(p.main())

