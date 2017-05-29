
"""
A simple documentation generator for microprograms.
"""

import os
import sys

from jinja2 import Environment
from jinja2 import FileSystemLoader

from .UCInstructions import UCInstruction
from .UCInstructions import UCInstructionCollection

class UCInstructionDocGen(object):
    """
    Takes a set of instructions and generates a small HTML documentation page
    for them.
    """

    def __init__(self, instructions ):
        """
        Create a new template renderer.
        """
        self.instrs = instructions 

    def renderTo(self, output_path):
        """
        Render the ucore to the supplied output path.
        """
        
        env      = Environment(loader=FileSystemLoader("./templates/"))
        template = env.get_template("instr-docs.html")

        with open(output_path,"w") as fh:
            fh.write(
                template.render(
                    pagetitle="Instruction Documentation",
                    instrs   = self.instrs
                )
            )

