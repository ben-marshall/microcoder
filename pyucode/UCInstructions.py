
"""
Classes and functions for representing instructions.
"""

import re
import sys
import logging as log

from .UCInstructionStatement import UCInstructionStatement

class UCInstructionArgument(object):

    def __init__(self, src=None):
        """
        Create a new instruction argument using a string source.
        """
        
        self.constant = False
        self.variable = False
        self.name     = None
        self.hi       = 0 
        self.lo       = 0 

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
            self.hi = int(bits_split[0])
            self.lo = int(bits_split[1])


class UCInstruction(object):
    """
    Represents a single instruction
    """

    def __init__(self, name, arguments, statements, desc=""):
        """
        Create a new instruction with the supplied name, list of arguments
        and list of statements.
        """
        
        self.name       = name
        self.arguments  = arguments
        self.statements = statements
        self.resolved_args = {}
        self.description = desc


    def is_argument(self, token):
        """
        Checks if the supplied token name is an argument to the instruction.
        """
        return token in self.resolved_args

    def get_argument(self, arg_name):
        """
        Returns an argument to the instruction with the supplied name,
        or None if the instruction has no such named argument.
        """
        for a in self.arguments:
            if(a.name == arg_name):
                return a
        return None


    def synth_statements(self):
        """
        Synthesises the set of instruction statements into something
        we can put into the verilog statemachine. Returns a list of
        the statements as strings.
        """
        tr = []
        for statement in self.statements:
            as_source = "// %s" % statement.src
            
            arg_statement = ""
            tokens = statement.get_tokens()
            eq_seen = False

            for t in tokens:
                if(t == "="):
                    eq_seen = True

                if(self.is_argument(t)):
                    argument_value = self.resolved_args[t]
                    argument_info  = self.get_argument(t)

                    if(argument_info.constant):
                        arg_statement += "%s " % argument_value
                        if(not eq_seen):
                            log.error("Cannot assign to constant argument")
                    elif(argument_info.variable and not eq_seen):
                        arg_statement += "n_%s " % argument_value.name
                    elif(argument_info.variable and eq_seen):
                        arg_statement += "%s " % argument_value.name
                    else:
                        log.error("Argument neither constant or variable: '%s'" %argument_info.name)
                else:
                    arg_statement += "%s " % t
            
            arg_statement += "; %s" % as_source
            tr.append(arg_statement)

        return tr


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


    def getInstruction(self, name):
        """
        Return an instruction with the supplied name or None if it does not
        exist.
        """

        if(name in self.by_name):
            return self.by_name[name]
        else:
            return None

    
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
            lines = [l for l in lines if l != ""]
            lines = [re.sub(" +"," ",l) for l in lines]
    
        IGNORE=1
        ARGS=3
        STATEMENTS=4
        ERROR = 5
        
        pstate = IGNORE
        lno    = 0

        current_comment     = ""
        current_name        = None
        current_args        = []
        current_statements  = []


        for line in lines:
            lno += 1
            tokens = line.split(" ")

            if(line.startswith("//")):
                current_comment += line[2:] + "\n"
                continue

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
                                                 current_statements,
                                                 desc=current_comment)
                    self.addInstruction(instr_to_add)
                    current_name = None
                    current_args = []
                    current_statements = []
                    current_comment = ""
                    pstate = IGNORE 
                else:
                    current_statements.append(UCInstructionStatement(src=line))

            else:
                print("Parse error on line %d" % (lno))
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
