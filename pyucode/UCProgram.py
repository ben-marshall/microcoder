
"""
Functions and classes for parsing and representing complete programs.
"""

import re
import sys
import logging as log

UCProgramFlowNone   = 0
UCProgramFlowGoto   = 1
UCProgramFlowIfEqz  = 2
UCProgramFlowIfNez  = 3

class UCProgramFlowChange(object):

    def __init__(self, src):
        """
        Create a new program flow change object from source.
        """
        self.src=src
        self.change_type    = UCProgramFlowNone
        self.target         = None
        self.conditional    = False
        self.variable       = None
        self.parse()

    def parse(self):
        """
        Parse a program flow change from a source line.
        """
        tokens = self.src.split(" ")
        
        if(len(tokens) <= 1):
            log.error("Control flow change without target")

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
    Represents a block of code defined by the user.
    """

    def __init__(self, name, statements, flow_change):
        """
        Create a new program block with the supplied statments and control
        flow change at the end.
        """
        self.name = name
        self.statements = statements
        self.flow_change = flow_change
        self.index = None


class UCProgram(object):
    """
    Represents a set of ProgramBlocks joined together.
    """

    def __init__(self):
        """
        Create a new, empty program.
        """
        self.block_count = 0

        self.blocks = []
        self.by_name= {}
    
    def getBlock(self, name):
        """
        Return a block with the supplied name or None if it does not exist.
        """

        if(name in self.by_name):
            return self.by_name[name]
        else:
            return None
    
    def getNextBlock(self, name):
        """
        Return the next block in a program given the name of another block
        in the program.
        Returns None if no such block exists, or it has no next block.
        """

        if(name in self.by_name):
            block_i = self.by_name[name].index
            return self.blocks[block_i]
        else:
            return None


    def addProgramBlock(self, block):
        """
        Add a new basic block to the program.
        """
        assert type(block) is UCProgramBlock, "block should be of type UCProgramBlock"
        if not block.name in self.by_name:
            block.index = self.block_count
            self.blocks.append(block)
            self.by_name[block.name]=block
            self.block_count = self.block_count + 1
        else:
            log.error("The block with name '%s' has already been declared"% block.name)


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
    
        IGNORE = 1
        BLOCK  = 2
        ERROR  = 0
        
        pstate = IGNORE
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
                print("Add block '%s'" % current_name)
                self.addProgramBlock(toadd)


        for line in lines:
            lno += 1
            tokens = line.split(" ")

            if(pstate == IGNORE):

                if(tokens[0] == "block"):
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
                else:
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
                else:
                    current_statements.append(line)

            else:
                print("Parse error on line %d" % lno + 1)
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
        print("- %s" % block.name)
