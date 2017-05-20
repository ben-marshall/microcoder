
"""
Contains classes and functions for loading and representing program state
variables
"""

import logging as log

import yaml

UCPortInput = 0
UCPortOutput= 1

class UCProgramVariable(object):
    """
    Represents a single program variable within a program.
    """

    def __init__(self, name, 
                       bits_hi      = 0, 
                       bits_lo      = 0, 
                       description  = None):
        """
        Create a new UCPort Object
        """
        assert type(name) is str , "A port name must be a string"
        assert type(description) is str , "A port description must be a string"
        assert type(bits_hi) is int
        assert type(bits_lo) is int
        assert bits_hi >= bits_lo, "A port width must be greater than or equal to 1"

        self.name       = name
        self.width      = 1 + bits_hi - bits_lo
        self.lo         = bits_lo
        self.hi         = bits_hi
        self.description= description


class UCProgramVariableCollection (object):
    """
    Represents a collection of program variables
    """

    def __init__(self):
        """
        Create a new empty collection of ports.
        """

        self.by_index = []
        self.by_name  = {}


    def addProgramVariable(self, variable):
        """
        Add a new program variable to the collection
        """
        
        assert type(variable) is UCProgramVariable, "variable should be of type UCProgramVariable"

        if not variable.name in self.by_name:
            self.by_name[variable.name] = variable
            self.by_index.append(variable)
        else:
            log.error("The variable with name '%s' has already been declared"
                % port.name)


def parseProgramVariablesYAML(yaml_path):
    """
    Given a string to a yaml file, return a UCProgramVariableCollection object
    describing the variables it contains.
    """

    tr = UCProgramVariableCollection()
    
    with open(yaml_path,"r") as fh:
        contents = yaml.load(fh)

        variables = contents["program_state"]

        for variable_name in variables:
            variable                = variables[variable_name]
            variable_hi             = 0
            variable_lo             = 0
            variable_description    = ""

            if ("range" in variable):
                variable_hi = variable["range"][0]
                variable_lo = variable["range"][1]
            if("description" in variable):
                variable_description = variable["description"]

            toadd = UCProgramVariable(variable_name, bits_hi = variable_hi,
                                      bits_lo = variable_lo,
                                      description = variable_description)
            tr.addProgramVariable(toadd)

