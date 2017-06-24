
"""
Classes and functions for resolving the various components of a program into
proper objects.
"""

import sys
import copy
import logging

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
        self.log = logging.getLogger(__name__)
        self.variables  = UCProgramVariableCollection()
        self.instrs     = UCInstructionCollection()
        self.program    = UCProgram()
        self.enable_coalescing = False

    def addVariables(self, variables):
        for v in variables.by_index:
            self.variables.addProgramVariable(v)
    
    def addInstructions(self, instrs):
        for i in instrs.by_index:
            self.instrs.addInstruction(i)

    def addProgram(self, program):
        for b in program.blocks:
            self.program.addProgramBlock(b)

    def getVariable(self, var_name):
        """
        Searches the list of variables for one matching the supplied name.
        Returns None if no matching object is found.
        """
        tr = self.variables.getVariable(var_name)
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

            if(argument.constant):
                
                if(val[0] == "*"):
                    if (val[1:] in self.program.blocks_by_name):
                        # We are de-referencing a block / state encoding.
                        block = self.program.blocks_by_name[val[1:]]
                        resolved_args[argument.name] = \
                            self.program.get_block_state_name(block)
                        block.gets_dereferenced = True
                    else:
                        # Bad reference to a block name.
                        self.log.error(
                            "Could not find de-referenced block '*%s'" % (
                            val[1:]))
                else:
                    resolved_args[argument.name] = val

            elif(argument.variable):
            
                var = self.getVariable(val)
                
                if(var == None):
                    self.log.error("Variable '%s' referenced by '%s'\
 and used for argument '%s' has not been declared" %
                        (val, instr.name, argument.name))
                else:
                    resolved_args[argument.name] = var

            else:
                self.log.error("Argument %s of instruction %s is neither a variable\
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
            self.log.info("Block: %s" % block.name)

            # Check each statement (instruction) in the block.
            for i in range(0,len(block.statements)):
                
                statement_type = type(block.statements[i])

                if(statement_type == str):
                    
                    tokens      = block.statements[i].split()
                    
                    mnemonic    = tokens[0]
                    instr       = self.instrs.getInstruction(mnemonic)

                    if(instr == None):
                        self.log.error("Instruction '%s' in block '%s' not defined."
                            % (mnemonic, block.name))
                    else:
                        resolved = self.resolveInstructionArguments(
                                                instr, block.statements[i])

                        block.statements[i] = resolved

                else:
                    self.log.info("Unexpected statement type: %s" % statement_type)

            if(len(block.flow_change) == 0):
                self.log.error("The block '%s' has no defined target block to \
                jump to afterwards. This can lead to unpredictable \
                behaviour."%block.name)

            # Check that the jump (if any) at the end of the block goes
            # to the right place.
            for flow_change in block.flow_change:
                if(flow_change.conditional):
                    varname = flow_change.variable
                    v       = self.getVariable(varname)

                    if(v != None):
                        flow_change.variable = v
                    else:
                        self.log.error("Cannot find conditional variable '%s' used\
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
                        self.log.error("Jump target '%s' at the end of block '%s'\
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
        assert type(block) == UCProgramBlock, "Type should be UCProgramBlock\
 but instead is '%s'" % type(block)
        tr = []
        for flowchange in block.flow_change:
            if(type(flowchange.target) == UCProgramBlock):
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
                self.log.info("Removing un-reachable block: '%s'" % block.name)
            else:
                newlist.append(block)
        self.program.blocks = newlist


    def coalesce_blocks(self, parent, child):
        """
        Merge two blocks together.
        """

        self.log.debug("O: Merging block %s into %s" % (child.name,parent.name))

        parent.statements += child.statements
        parent.flow_change = child.flow_change
        parent.src_statements += child.src_statements

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

            self.log.debug("C: %s" % block.name)

            inset   = self.incoming_blocks(block)
            outset  = self.outgoing_blocks(block)
            
            if(len(inset) + len(outset) == 0):
                block.removable = True and not candidate.gets_dereferenced
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
                candidate.removable = True and not candidate.gets_dereferenced
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
          a program variable.
        - All constant arguments used in an instruction must indeed be
          constants.
        - All blocks referenced within a program must be defined.
        - Variable widths must be consistant.
        """
        
        self.resolveInstructions()
        self.check_reads_and_writes()
        if(self.enable_coalescing):
            self.log.info(">> Pre-coalesce state count: %d" % len(self.program.blocks))
            self.coalesce_program()
            self.remove_unreachable_blocks()
            self.log.info(">> Post-coalesce state count %d" % len(self.program.blocks))
