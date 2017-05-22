
"""
Classes and functions for resolving the various components of a program into
proper objects.
"""

import copy
import logging as log

from .UCPorts import UCPort
from .UCPorts import UCPortCollection

from .UCState import UCProgramVariable
from .UCState import UCProgramVariableCollection

from .UCInstructions import UCInstruction
from .UCInstructions import UCInstructionCollection

from .UCProgram import UCProgramBlock
from .UCProgram import UCProgram

class UCResolver(object):
    """
    Takes all of the components of a ucore (program, ports, state and 
    instructions) and resolves them to make sure that the naming is
    consistent.
    """

    def __init__(self):
        """
        Create a new resolver with initially no objects
        """
        self.variables  = UCProgramVariableCollection()
        self.ports      = UCPortCollection()
        self.instrs     = UCInstructionCollection()
        self.program    = UCProgram()

    def addVariables(self, variables):
        for v in variables.by_index:
            self.variables.addProgramVariable(v)
    
    def addPorts(self, ports_to_add):
        for p in ports_to_add.by_index:
            self.ports.addPort(p)
    
    def addInstructions(self, instrs):
        for i in instrs.by_index:
            self.instrs.addInstruction(i)

    def addProgram(self, program):
        for b in program.blocks:
            self.program.addProgramBlock(b)

    def getVariableOrPort(self, var_or_port_name):
        """
        Searches the list of variables, then the list of ports for one
        matching the supplied name.
        Returns None if no matching object is found.
        """
        tr = self.variables.getVariable(var_or_port_name)
        if(tr != None):
            return tr
        tr = self.ports.getPort(var_or_port_name)
        if(tr != None):
            return tr
        return None

    
    def resolveInstructionArguments(self, instr, statement):
        """
        Given an instance of UCInstruction and the statement where it is
        used, resolve all of its arguments.
        """
        assert type(instr) == UCInstruction, "instr should be UCInstruction"
        assert type(statement) == str, "statement should be of type str"
        
        tokens  = statement.split()
        args    = tokens [1:]
        memonic = tokens [0]

        resolved_args = {}

        assert memonic == instr.name, "memonic %s != instr.name %s" % (
                                            memonic, instr.name)
        
        for argument, val in zip(instr.arguments, args):
            
            var = self.getVariableOrPort(val)

            if(argument.constant):
                resolved_args[argument.name] = val

            elif(argument.variable):
                
                if(var == None):
                    log.error("Variable '%s' referenced by instruction '%s'\
 and used for argument '%s' has not been declared" %
                        (val, instr.name, argument.name))
                else:
                    resolved_args[argument.name] = var

            else:
                log.error("Argument %s of instruction %s is neither a variable\
                or constant type. Is it properly defined?" % 
                    (argument.name, instr.name))

        tr               = copy.deepcopy(instr)
        tr.resolved_args = resolved_args
        return tr


    def resolveInstructions(self):
        """
        Makes sure all instructions used in the program are also defined.
        """

        for block in self.program.blocks:
            print("Block: %s" % block.name)

            for i in range(0,len(block.statements)):
                
                statement_type = type(block.statements[i])

                if(statement_type == str):
                    
                    tokens      = block.statements[i].split()
                    
                    mnemonic    = tokens[0]
                    instr       = self.instrs.getInstruction(mnemonic)

                    if(instr == None):
                        log.error("Instruction '%s' in block '%s' not defined."
                            % (mnemonic, block.name))
                    else:
                        resolved = self.resolveInstructionArguments(
                                                    instr, block.statements[i])

                        block.statements[i] = resolved

                else:
                    print("Unexpected statement type: %s" % statement_type)


    def resolve(self):
        """
        Call this function once all of the various program sources have been
        added. Resolve all objects and report any errors.
        - All instructions used in a program must be defined.
        - Instructions must have the correct number of arguments.
        - All variable arguments used in an instruction must be defined as
          either a program variable or a port.
        - All constant arguments used in an instruction must indeed be
          constants.
        - All blocks referenced within a program must be defined.
        - Variable widths must be consistant.
        """
        
        self.resolveInstructions()
