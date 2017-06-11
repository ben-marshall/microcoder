
"""
Classes and functions for resolving the various components of a program into
proper objects.
"""

import sys
import copy
import logging as log

from .UCPorts import UCPort
from .UCPorts import UCPortCollection

from .UCState import UCProgramVariable
from .UCState import UCProgramVariableCollection

from .UCInstructions import UCInstruction
from .UCInstructions import UCInstructionCollection

from .UCProgram import UCProgramFlowChange
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
        self.enable_coalescing = False

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
        tr.resolved      = True
        return tr


    def resolveInstructions(self):
        """
        Makes sure all instructions used in the program are also defined.
        """
        prev_block = None

        for block in self.program.blocks:
            print("Block: %s" % block.name)

            # Check each statement (instruction) in the block.
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

            if(len(block.flow_change) == 0):
                log.error("The block '%s' has no defined target block to \
                jump to afterwards. This can lead to unpredictable \
                behaviour."%block.name)

            # Check that the jump (if any) at the end of the block goes
            # to the right place.
            for flow_change in block.flow_change:
                if(flow_change.conditional):
                    varname = flow_change.variable
                    v       = self.getVariableOrPort(varname)

                    if(v != None):
                        flow_change.variable = v
                    else:
                        log.error("Cannot find conditional variable '%s' used\
 at the end of block '%s'" % (varname, block.name))

                jump_target = flow_change.target
                if(type(jump_target) == str):

                    if(jump_target in self.program.blocks_by_name):
                        
                        tgt_block = self.program.getBlock(jump_target)
                        flow_change.target = tgt_block
                    elif(jump_target in self.variables.by_name):
                        tgt_var   = self.variables.getVariable(jump_target)
                        flow_change.target      = tgt_var
                        flow_change.to_variable = True

                    else:
                        log.error("Jump target '%s' at the end of block '%s'\
 does not exist." % (jump_target, block.name))

            block.resolved = True

    def check_reads_and_writes(self):
        """
        Looks over the program blocks and notifies when we write to a
        variable more than once in a single block.
        TODO - implement this!
        """
        for block in self.program.blocks:

            reads, writes = block.read_write_sets()


    def incoming_blocks(self,block):
        """
        Given an instance of a block, return a list of blocks which might
        jump into it.
        """
        tr = []
        for b in self.program.blocks:
            for flowchange in b.flow_change:
                if flowchange.target== block:
                    tr.append(b)
        return tr

    def outgoing_blocks (self,block):
        """
        Given an instance of a block, return a list of blocks which
        it could jump to.
        """
        tr = []
        for flowchange in block.flow_change:
            tr.append(flowchange.target)
        return tr

    def remove_unreachable_blocks(self):
        """
        Removes all unreachable blocks from the program
        """
        newlist = []
        for block in self.program.blocks:
            
            inset   = self.incoming_blocks(block)
            outset  = self.outgoing_blocks(block)

            if(len(inset) + len(outset) == 0 or block.removable):
                print("Removing un-reachable block: '%s'" % block.name)
            else:
                newlist.append(block)
        self.program.blocks = newlist


    def coalesce_blocks(self, parent, child):
        """
        Merge two blocks together.
        """

        print("O: Merging block %s into %s" % (child.name,parent.name))

        parent.statements += child.statements
        parent.flow_change = child.flow_change

        for block in self.program.blocks:
            for fc in block.flow_change:
                if(fc.target == child):
                    fc.target = parent

        return parent


    def coalesce_program(self):
        """
        Modifys the program by coalescing blocks which appear in sequence
        and which are orthogonal into a single block.
        """

        changes = 0

        for i in range(0,len(self.program.blocks)):
            block = self.program.blocks[i]

            print("C: %s" % block.name)

            inset   = self.incoming_blocks(block)
            outset  = self.outgoing_blocks(block)
            
            if(len(inset) + len(outset) == 0):
                block.removable = True
                continue
            
            # Reads and writes for the parent block.
            reads,writes = block.read_write_sets()

            if(len(outset) == 1):
                candidate = outset[0]
                cin      = self.incoming_blocks(candidate)
                cout     = self.outgoing_blocks(candidate)

                # Reads and writes for the candidate merge block
                crd, cwr = candidate.read_write_sets()

                # If multiple things target this block, we cannot merge it
                # safely.
                if(len(cin) > 1): continue

                # Avoid read after write hazards.
                if(not crd.isdisjoint(writes)): continue
                if(not cwr.isdisjoint(writes)): continue
                
                self.program.blocks[i] = self.coalesce_blocks(block,candidate)
                candidate.removable = True
                changes += 1
                break

        if(changes > 0):
            self.remove_unreachable_blocks()
            changes = self.coalesce_program()

        return changes


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
        self.check_reads_and_writes()
        if(self.enable_coalescing):
            print(">> Pre-coalesce state count: %d" % len(self.program.blocks))
            self.coalesce_program()
            self.remove_unreachable_blocks()
            print(">> Post-coalesce state count %d" % len(self.program.blocks))
