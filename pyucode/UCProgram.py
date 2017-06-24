
"""
Functions and classes for parsing and representing complete programs.
"""

import re
import os
import sys
import copy
import logging

from .UCInstructions import UCInstructionCollection

from .UCState import UCProgramVariable
from .UCState import UCProgramVariableCollection
from .UCState import UCVarStrings
from .UCState import UCPortStrings
from .UCState import UCTypePortIn  
from .UCState import UCTypePortOut 
from .UCState import UCTypePortNone
from .UCState import UCPortTypes   
from .UCState import UCTypeVarReg  
from .UCState import UCTypeVarConst
from .UCState import UCTypeVarComb 
from .UCState import UCVarTypes    

UCProgramFlowNone   = 0
UCProgramFlowGoto   = 1
UCProgramFlowIfEqz  = 2
UCProgramFlowIfNez  = 3

class UCProgramFlowChange(object):

    def __init__(self, src):
        """
        Create a new program flow change object from source.
        """
        self.log = logging.getLogger(__name__)
        self.src=src
        self.change_type    = UCProgramFlowNone
        self.target         = None
        self.to_variable    = False
        self.conditional    = False
        self.variable       = None
        if(src != None):
            self.parse()

    def parse(self):
        """
        Parse a program flow change from a source line.
        """
        tokens = self.src.split(" ")
        
        if(len(tokens) <= 1):
            self.log.error("Control flow change without target")

        if(tokens[0] == "goto"):
            self.change_type    = UCProgramFlowGoto
            self.target         = tokens[1]

        elif(tokens[0] == "ifeqz"):
            self.change_type    = UCProgramFlowIfEqz
            self.variable       = tokens[1]
            self.target         = tokens[2]
            self.conditional    = True

        elif(tokens[0] == "ifnez"):
            self.change_type    = UCProgramFlowIfNez
            self.variable       = tokens[1]
            self.target         = tokens[2]
            self.conditional    = True



class UCProgramBlock(object):
    """
    Represents a collection of isntruction statements with a control
    flow statement at the end.
    """

    __count__ = 0

    def __init__(self, name, statements, flow_change):
        """
        Create a new program block with the supplied statments and control
        flow change at the end.
        """
        self.id  = UCProgramBlock.__count__
        UCProgramBlock.__count__ = UCProgramBlock.__count__ + 1
        self.log = logging.getLogger(__name__)
        self.name           = name
        self.statements     = statements
        self.flow_change    = flow_change
        self.index          = None
        self.resolved       = False
        self.removable      = False
        self.src_statements = copy.deepcopy(statements)
        self.gets_dereferenced = False

    def is_atomic(self):
        """
        Return True if there are zero or one statements in this program block,
        otherwise return False
        """
        return len(self.statements) <= 1


    def read_write_sets(self):
        """
        Iterates over all instructions in the block, constructing two sets
        representing the variables which are read or written inside the
        block.
        Each set is returned as a list in a tuple of the form 
        `(read set, write set)`. The list contains objects of type
        UCProgramVariable
        """
        assert (self.resolved) , \
            "Blocks must be resolved before read set is constructed."

        read_set    = set([])
        write_set   = set([])

        for statement in self.statements:
            
            rs, ws      = statement.read_write_sets()
            read_set    = read_set.union(rs)
            write_set   = write_set.union(ws)
        
        for fc in self.flow_change:
            if(fc.conditional):
                read_set.add(fc.variable)

        return (read_set, write_set)


    def atomised(self):
        """
        Returns a list of new program blocks, where each block contains
        at most a single statement. The name of the first block is the same
        as this block, and the final block uses the same flow control
        decision logic as this block.
        All newly created blocks use goto statements to the 'next' block.
        """

        tr = []
        namecounter = 0
        
        for statement in self.statements:
            
            # Keep the same block name if this is the first statement,
            # otherwise number it accordingly.
            newblock_name = self.name
            if(not statement is self.statements[0]):
                newblock_name = "%s_%d" % (self.name, namecounter)
            
            # Create a new 'goto' statement for the flowchange if this is a
            # new intermediate block, otherwise re-use the current flow
            # change object.
            newblock_flowchange = None
            if(statement is self.statements[-1]):
                newblock_flowchange = self.flow_change
            else:
                newfc_src = "goto %s_%d" % (self.name, namecounter+1)
                newblock_flowchange = [UCProgramFlowChange(newfc_src)]

            newblock     = UCProgramBlock(newblock_name, 
                                          [statement],
                                          newblock_flowchange)
            tr.append(newblock)
            namecounter += 1

        self.log.info("Atomised block '%s' into %d sub-blocks" % 
            (self.name, len(tr)))

        return tr



class UCProgram(object):
    """
    Represents a set of ProgramBlocks joined together.
    """

    def __init__(self):
        """
        Create a new, empty program.
        """
        self.log = logging.getLogger(__name__)
        self.block_count = 0

        self.blocks     = []
        self.blocks_by_name = {}

        self.variables  = UCProgramVariableCollection()

        # List of parsed instruction files included in this program.
        self.instructions = UCInstructionCollection()

    def get_block_state_name(self,block):
        """
        Given a block, return its state name when being executed.
        """
        return "STATE_%s" % block.name.upper()
    
    def synth_block_statements(self,block, annotate=True):
        """
        Return a synthesised set of statements within the program block.
        """
        tr = []
        for instruction in block.statements:
            if(annotate):
                tr.append("// Instruction: %s" % instruction.name)

            instr_statements = instruction.synth_statements()
            tr += instr_statements

        return tr
    
    def synth_state_encodings(self):
        """
        Return a list of state encoding name and value assignments.
        """
        tr = []

        for block in self.blocks:

            tr.append((self.get_block_state_name(block), block.id))

        return tr


    def synth_flowchanges(self, block):
        """
        Returns a synthesised decision tree of the program flow changes
        at the end of the block.
        """
        has_compare = False
        is_first    = True
        tree = []
        for flow_change in block.flow_change:
            
            target_state = ""
            if flow_change.to_variable :
                target_state = flow_change.target.name
            else:
                target_state = self.get_block_state_name(flow_change.target)

            if(flow_change.conditional):
                has_compare = True
                cmp_type = ""
                if(flow_change.change_type == UCProgramFlowIfEqz):
                    cmp_type = " == 0"
                elif(flow_change.change_type == UCProgramFlowIfNez):
                    cmp_type = " != 0"
                else:
                    self.log.error("Unknown conditional jump type")

                if(is_first):
                    tree.append("if ( %s %s )" % 
                        (flow_change.variable.name, cmp_type))
                    tree.append("    _next_state_ = %s;" % target_state)
                    is_first = False
                else:
                    tree.append("else if ( %s %s )" % 
                        (flow_change.variable.name, cmp_type))
                    tree.append("    _next_state_ = %s;\n" % target_state)

            else:
                pad =""
                if(has_compare):
                    tree.append("else")
                    pad = "    "
                tree.append("%s_next_state_ = %s;" % (pad,target_state))
                break

        return tree
            
    
    def getBlock(self, name):
        """
        Return a block with the supplied name or None if it does not exist.
        """

        if(name in self.blocks_by_name):
            return self.blocks_by_name[name]
        else:
            return None
    
    def getNextBlock(self, name):
        """
        Return the next block in a program given the name of another block
        in the program.
        Returns None if no such block exists, or it has no next block.
        """

        if(name in self.blocks_by_name):
            block_i = self.blocks_by_name[name].index
            return self.blocks[block_i]
        else:
            return None


    def addProgramBlock(self, new_block):
        """
        Add a new basic block to the program.
        """
        assert type(new_block) is UCProgramBlock, "block should be of type UCProgramBlock"

        blocks_to_add = []


        if(new_block.is_atomic()):
            blocks_to_add = [new_block]
        else:
            blocks_to_add = new_block.atomised()

        for block in blocks_to_add:
            if not block.name in self.blocks_by_name:
                block.index = self.block_count
                self.blocks.append(block)
                self.blocks_by_name[block.name]=block
                self.block_count = self.block_count + 1
            else:
                self.log.error("The block with name '%s' has already been declared"% block.name)


    def addProgramVariable(self, lineNo,tokens):
        """
        Add a Program Variable parsed from a program file on the given line.
        """
        if(len(tokens) < 2):
            self.log.error("Line %d: Bad Variable declaration: '%s'\n\t"
                % (" ".join(tokens),lineNo))
        
        name      = "name not found"
        port_type = UCTypePortNone
        var_type  = UCTypeVarReg
        comb_expr = ""
        idx       = 0
        
        if(tokens[idx] in UCPortStrings):
            port_type   =  UCPortStrings[tokens[idx]]
            if port_type == UCTypePortIn:
                var_type = UCTypeVarComb
            idx         += 1

        if(tokens[idx] in UCVarStrings):
            var_type    =  UCVarStrings[tokens[idx]]
            idx         += 1

        name      = tokens[idx]
        idx      += 1

        if(var_type == UCTypeVarComb):
            comb_expr = "".join(tokens).partition("=")[2].partition("#")[0]


        toadd = UCProgramVariable(name, port_type, var_type, description="")
        toadd.const_expr = comb_expr

        if(len(tokens)> idx and tokens[idx][0] != "#"):
            rstr = "".join(tokens[idx:]).partition('#')[0].partition("=")[0]
            hilo = rstr.split(":")
            hi   = int(hilo[0].lstrip(" ["))
            lo   = int(hilo[1].rstrip(" ]\n"))
            toadd.hi = hi
            toadd.lo = lo
            toadd.width = 1 + (hi - lo)

        self.variables.addProgramVariable(toadd)

    

    def handleInclude(self,line_no, line_tokens, current_file):
        """
        Parses a single 'using' statement line
        """
        assert type(line_tokens) == list, "line_tokens should be a list"
        assert (line_tokens[0] == "using"), "First element of line_tokens should be 'using'"

        if ( len(line_tokens) < 3 ):
            self.log.error("Bad 'using' statement on line %d" % line_no)
            self.log.error("Should be of the form 'using [instructions|subprogram] 'filepath'")
        
        base     = os.path.dirname(current_file)
        filepath = "".join(line_tokens[2:]).lstrip("'\"").rstrip("'\"")
        filepath = os.path.join(base,filepath)

        if(line_tokens[1] == "instructions"):
            self.log.info("Parsing instructions file: '%s'" % filepath)
            self.instructions.parse(filepath)

        elif(line_tokens[1] == "subprogram"):
            self.log.info("Parsing subprogram file: '%s'" % filepath)
            self.parseSource(filepath)

        else:
            self.log.error("unknown using directive '%s', should be 'instructions' or 'subprogram'" % line_tokens[1])


    def parseSource(self, filepath):
        """
        Parse a new source file into the program.
        """
        lines = []

        with open(filepath,"r") as fh:
            lines = fh.readlines()
            lines = [l.strip(" \n") for l in lines]
            lines = [l for l in lines if l != "" and not l.startswith("//")]
            lines = [re.sub(" +"," ",l) for l in lines]
    
        BLOCKS_PORTS= 1
        USING  = 2
        BLOCK  = 3
        ERROR  = 0
        
        pstate = USING
        lno    = 0

        current_name        = None
        current_sub_block   = 1
        current_statements  = []
        current_flowchange  = []
                    
        def l_add_current_block(current_name, 
                                current_sub_block,
                                current_statements,
                                current_flowchange):
            # Add the "current" block
            if(current_name != None):
                if(current_sub_block>1):
                    current_name = "%s_%d" % (current_name,
                                              current_sub_block)
                toadd = UCProgramBlock(current_name,
                                       current_statements,
                                       current_flowchange)
                self.log.info("Add block '%s'" % current_name)
                self.addProgramBlock(toadd)


        for line in lines:
            lno += 1
            if(line[0] == "#"):
                continue
            tokens = line.split(" ")
                
            if(pstate == USING):
                
                if(tokens[0] == "using"):
                    self.handleInclude(lno,tokens, filepath)
                elif(tokens[0] in UCVarStrings or
                     tokens[0] in UCPortStrings   ):
                    self.addProgramVariable(lno, tokens)
                    pstate = BLOCKS_PORTS
                else:
                    self.log.error("0")
                    pstate = ERROR

            elif(pstate == BLOCKS_PORTS):
                
                if(tokens[0] == "block"):
                    # start parsing the new block.
                    current_name        = tokens[1]
                    current_statements  = []
                    current_sub_block   = 1
                    current_flowchange  = []
                    pstate = BLOCK 

                elif(tokens[0] in UCVarStrings or
                     tokens[0] in UCPortStrings   ):
                    self.addProgramVariable(lno, tokens)

                else:
                    self.log.error("1")
                    pstate = ERROR

            elif(pstate == BLOCK):
                
                if(len(tokens) <= 0):
                    continue
                
                if(tokens[0] == "block"):
                    if(current_name != None  and
                       (current_flowchange != None or
                        current_statements != [])):
                        l_add_current_block(current_name, 
                                            current_sub_block,
                                            current_statements,
                                            current_flowchange)
                    # start parsing the new block.
                    current_name        = tokens[1]
                    current_statements  = []
                    current_sub_block   = 1
                    current_flowchange  = []
                    pstate = BLOCK 

                elif(tokens[0] in ["goto", "ifeqz", "ifnez"]):
                    current_flowchange.append(UCProgramFlowChange(line))
                elif(tokens[0] == "port"):
                    self.log.error("Line %d: Cannot put port declarations inside blocks." % lno)
                elif(tokens[0] == "state"):
                    self.log.error("Line %d: Cannot put state delcarations inside blocks." % lno)
                else:
                    current_statements.append(line)

            else:
                self.log.error("Parse error on line %d: %s" % (lno + 1, line))
                break

        if(current_name != None and
           (current_flowchange != None or
            current_statements != [])):
            l_add_current_block(current_name, 
                                current_sub_block,
                                current_statements,
                                current_flowchange)


if __name__ =="__main__":
    program = UCProgram()

    program.parseSource(sys.argv[1])
    
    for block in program.blocks:
        self.log.info("- %s" % block.name)
