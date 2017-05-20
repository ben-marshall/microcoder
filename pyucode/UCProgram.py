
"""
Functions and classes for parsing and representing complete programs.
"""

import re
import sys


class UCProgramFlowChange(object):

    def __init__(self, src):
        """
        Create a new program flow change object from source.
        """
        self.src=src

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

class UCProgram(object):
    """
    Represents a set of ProgramBlocks joined together.
    """

    def __init__(self):
        """
        Create a new, empty program.
        """

        self.blocks = []
        self.by_name= {}

    def addProgramBlock(self, block):
        """
        Add a new basic block to the program.
        """
        assert type(block) is UCProgramBlock, "block should be of type UCProgramBlock"
        if not block.name in self.by_name:
            self.blocks.append(block)
            self.by_name[block.name]=block
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
        current_flowchange  = None
                    
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
                    pstate = BLOCK 
                else:
                    pstate = ERROR

            elif(pstate == BLOCK):
                
                if(len(tokens) <= 0):
                    continue
                
                if(tokens[0] == "block"):
                    l_add_current_block(current_name, 
                                        current_sub_block,
                                        current_statements,
                                        current_flowchange)
                    # start parsing the new block.
                    current_name        = tokens[1]
                    current_statements  = []
                    current_sub_block   = 1
                    pstate = BLOCK 

                elif(tokens[0] in ["goto","ifeqz","ifnez"]):
                    current_flowchange = UCProgramFlowChange(line)
                    l_add_current_block(current_name, 
                                        current_sub_block,
                                        current_statements,
                                        current_flowchange)
                    
                    current_statements  = []
                    current_sub_block   += 1
                    pstate = BLOCK 
                else:
                    current_statements.append(line)

            else:
                print("Parse error on line %d" % lno + 1)
                break


if __name__ =="__main__":
    program = UCProgram()

    program.parseSource(sys.argv[1])
    
    for block in program.blocks:
        print("- %s" % block.name)
