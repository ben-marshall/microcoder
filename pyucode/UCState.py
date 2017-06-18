
"""
Contains classes and functions for loading and representing program state
variables
"""

import logging as log

import yaml

UCTypePortIn    = 0xA0
UCTypePortOut   = 0xA1
UCTypePortNone  = 0xA2 
UCPortTypes     = [UCTypePortIn, UCTypePortOut, UCTypePortNone]

UCPortStrings    = {
    "input"   : UCTypePortIn,
    "output"  : UCTypePortOut
}

UCTypeVarReg    = 0xB0
UCTypeVarConst  = 0xB1
UCTypeVarComb   = 0xB2
UCVarTypes      = [UCTypeVarReg, UCTypeVarConst, UCTypeVarComb]

UCVarStrings    = {
    "reg"   : UCTypeVarReg  ,
    "const" : UCTypeVarConst,
    "comb"  : UCTypeVarComb
}

class UCProgramVariable(object):
    """
    Represents a single program variable within a program.
    """

    def __init__(self, name, 
                       port_type,
                       var_type,
                       bits_hi      = 0, 
                       bits_lo      = 0,
                       description  = ""):
        """
        Create a new UCPort Object
        """
        assert type(name) is str , "A port name must be a string"
        assert type(description) is str , "A port description must be a string"
        assert type(bits_hi) is int
        assert type(bits_lo) is int
        assert bits_hi >= bits_lo, "A port width must be greater than or equal to 1"
        assert port_type in UCPortTypes, "Invalid port type"
        assert var_type  in UCVarTypes, "Invalid var type"

        self.port_type  = port_type
        self.var_type   = var_type
        self.name       = name
        self.width      = 1 + bits_hi - bits_lo
        self.lo         = bits_lo
        self.hi         = bits_hi
        self.description= description.rstrip("\n")
        self.comb_expr  = "0"

        if(self.isRegVar() and self.isInPort()):
            log.error("Input port '%s' cannot be of variable type 'reg'" %
                self.name)

    def __len__(self):
        """
        Returns how many bits wide the variable is.
        """
        return self.width
    
    def isRegVar(self):
        """
        Returns true if the variable is of type UCTypeVarReg
        """
        return self.var_type == UCTypeVarReg

    def isConstVar(self):
        """
        Returns true if the variable is of type UCTypeVarConst
        """
        return self.var_type == UCTypeVarConst

    def isCombVar(self):
        """
        Returns true if the variable is of type UCTypeVarComb
        """
        return self.var_type == UCTypeVarComb

    def isPort(self):
        """
        Returns true if the variable is not of type UCTypePortNone
        """
        return self.port_type != UCTypePortNone

    def isInPort(self):
        """
        Returns true if the variable is of type UCTypePortIn
        """
        return self.port_type == UCTypePortIn

    def isOutPort(self):
        """
        Returns true if the variable is of type UCTypePortOut
        """
        return self.port_type == UCTypePortOut



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
    
    def getVariable(self, name):
        """
        Return the UCProgramVariable with the supplied name or None
        """
        if(name in self.by_name):
            return self.by_name[name]
        else:
            return None
    
    def getPortNames(self):
        """
        Return a list of all variable names which are ports
        """
        return [v.name for v in self.by_index if v.isPort()]

    def getPorts(self):
        """
        Return a list of all variables which are also input or output
        ports.
        """
        return [v for v in self.by_index if v.isPort()]


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
