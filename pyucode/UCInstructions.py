
"""
Classes and functions for representing instructions.
"""

import re
import sys

class UCInstructionArgument(object):

    def __init__(self, src=None):
        """
        Create a new instruction argument using a string source.
        """
        
        self.constant = False
        self.variable = False
        self.name     = None
        self.bits_hi  = None
        self.bits_lo  = None

        if src != None:
            self.parse(src)

    def parse(self, src):
        """
        Parse the string representation of the argument
        """
        self.src=src
        tokens = src.split()
        if(tokens[1] == "variable"):
            self.variable = True
        elif(tokens[1] == "constant"):
            self.constant = True

        if(len(tokens) == 3):
            self.name = tokens[2]
        else:
            self.name = tokens[-1]
            bits = src.split("[")[1].split("]")[0]
            bits_split = bits.split(":")
            self.bits_hi = int(bits_split[0])
            self.bits_lo = int(bits_split[1])


class UCInstructionStatement(object):

    def __init__(self, src=None):
        """
        Create a new instruction behaviour statement using a string source.
        """

        if src != None:
            self.parse(src)

    def parse(self, src):
        """
        Parse the string representation of the statement 
        """
        self.src = src


class UCInstruction(object):
    """
    Represents a single instruction
    """

    def __init__(self, name, arguments, statements):
        """
        Create a new instruction with the supplied name, list of arguments
        and list of statements.
        """
        
        self.name       = name
        self.arguments  = arguments
        self.statements = statements



class UCInstructionCollection(object):
    """
    Represents a collection of instructions
    """

    def __init__(self):
        """
        Create a new empty instruction collection.
        """
        self.by_name = {}
        self.by_index = []

    
    def addInstruction(self, instr):
        """
        Add a new instruction to the collection
        """
        
        assert type(instr) is UCInstruction, "instruction should be of type UCInstruction"

        if not instr.name in self.by_name:
            self.by_name[instr.name] = instr
            self.by_index.append(instr)
        else:
            log.error("The instruction with name '%s' has already been declared"% instr.name)


    def parse(self, filepath):
        """
        Given a filepath, parse all of the instructions inside it.
        """
        lines = []

        with open(filepath,"r") as fh:
            lines = fh.readlines()
            lines = [l.strip(" \n") for l in lines]
            lines = [l for l in lines if l != "" and not l.startswith("//")]
            lines = [re.sub(" +"," ",l) for l in lines]
    
        IGNORE=1
        ARGS=3
        STATEMENTS=4
        ERROR = 5
        
        pstate = IGNORE
        lno    = 0

        current_name        = None
        current_args        = []
        current_statements  = []


        for line in lines:
            lno += 1
            tokens = line.split(" ")

            if   ( pstate == IGNORE     ):

                if(tokens[0] == "define"):
                    current_name = tokens[1]
                    pstate = ARGS
                else:
                    pstate = ERROR

            elif ( pstate == ARGS       ):

                if(tokens[0] == "argument"):
                    current_args.append(UCInstructionArgument(src=line))
                    pstate = ARGS

                elif(tokens[0] == "begin"):
                    pstate = STATEMENTS
                else:
                    pstate = ERROR

            elif ( pstate == STATEMENTS ):
                if(tokens[0] == "end"):
                    instr_to_add = UCInstruction(current_name,
                                                 current_args,
                                                 current_statements)
                    self.addInstruction(instr_to_add)
                    current_name = None
                    current_args = []
                    current_statements = []
                    pstate = IGNORE 
                else:
                    current_statements.append(UCInstructionStatement(src=line))

            else:
                print("Parse error on line %d" % lno + 1)
                break


if __name__ =="__main__":
    instrs = UCInstructionCollection()

    instrs.parse(sys.argv[1])

    for instr in instrs.by_index:
        print("Name: %s" % instr.name)

        for arg in instr.arguments:
            print("    > %s" % arg.name)
        
        for statement in instr.statements:
            print("    - %s" % statement.src)
        print(" ")
