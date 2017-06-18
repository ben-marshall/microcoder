
"""
Classes and functions for rendering the template.
"""

import os
import sys

from jinja2 import Environment
from jinja2 import FileSystemLoader

from .UCResolver import UCResolver

class UCTemplater(object):
    """
    Takes a resolved program and renders it into a template.
    """

    def __init__(self, resolved_program):
        """
        Create a new template renderer.
        """
        self.prog = resolved_program
        self.debug_states = False

    def renderTo(self, output_path):
        """
        Render the ucore to the supplied output path.
        """
        
        env      = Environment(loader=FileSystemLoader("./templates/"))
        template = env.get_template("ucore-template.v")

        with open(output_path,"w") as fh:
            fh.write(
                template.render(
                    core_name = "main",
                    variables = self.prog.variables,
                    instrs    = self.prog.instrs,
                    program   = self.prog.program,
                    debug_states = self.debug_states
                )
            )

