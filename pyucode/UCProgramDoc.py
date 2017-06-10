
"""
Functions and classes for creating documentation on a resolved
program.
"""

from jinja2 import Environment
from jinja2 import FileSystemLoader

from .UCResolver import UCResolver

class UCProgramDocgen(object):
    """
    A top level class which analyses a program and can export various
    pieces of information about each element of the program. This
    includes control flow diagrams, read/write sets and code highlighting.
    """

    def __init__(self, resolved_program):
        """
        Create a new class using an existing and pre-resolved program
        """
        assert type(resolved_program) == UCResolver
        
        self.prog = resolved_program


    def gen_flow_dot_graph(self, filepath):
        """
        Creates a graphviz representation of the program flow which can
        be fed into the `dot` program.
        """
        
        env      = Environment(loader=FileSystemLoader("./templates/"))
        template = env.get_template("dot-graph.dot")

        with open(filepath,"w") as fh:
            fh.write(
                template.render(
                    program   = self.prog.program,
                )
            )

    def gen_program_docs(self, filepath):
        """
        Generates a small HTML page documenting the program.
        """
        
        env      = Environment(loader=FileSystemLoader("./templates/"))
        template = env.get_template("prog-docs.html")

        with open(filepath,"w") as fh:
            fh.write(
                template.render(
                    program   = self.prog.program,
                    pagetitle = "Program Documentation"
                )
            )

