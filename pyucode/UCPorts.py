
"""
Contains classes and functions for loading and representing ucore port
connections
"""

import logging as log

import yaml

UCPortInput = 0
UCPortOutput= 1

class UCPort (object):
    """
    Represents a single port on a ucore
    """

    def __init__(self, name, 
                       bits_hi      = 0, 
                       bits_lo      = 0, 
                       direction    = UCPortInput,
                       description  = None):
        """
        Create a new UCPort Object
        """
        assert type(name) is str , "A port name must be a string"
        assert type(description) is str , "A port description must be a string"
        assert type(bits_hi) is int
        assert type(bits_lo) is int
        assert bits_hi >= bits_lo, "A port width must be greater than or equal to 1"
        assert direction==UCPortInput or direction==UCPortOutput, "Port direction must be valid value"

        self.name       = name
        self.width      = 1 + bits_hi - bits_lo
        self.lo         = bits_lo
        self.hi         = bits_hi
        self.direction  = direction
        self.description= description


class UCPortCollection (object):
    """
    Represents a collection of ports on a ucore.
    """

    def __init__(self):
        """
        Create a new empty collection of ports.
        """

        self.by_index = []
        self.by_name  = {}


    def addPort(self, port):
        """
        Add a new port to the collection
        """
        
        assert type(port) is UCPort, "port should be of type UCPort"

        if not port.name in self.by_name:
            self.by_name[port.name] = port
            self.by_index.append(port)
        else:
            log.error("The port with name '%s' has already been declared"% port.name)


def parsePortsYAML(yaml_path):
    """
    Given a string to a yaml file, return a UCPortCollection object
    describing the ports it contains.
    """

    tr = UCPortCollection()
    
    with open(yaml_path,"r") as fh:
        contents = yaml.load(fh)

        ports = contents["ports"]

        for port_name in ports:
            port                = ports[port_name]
            port_hi             = 0
            port_lo             = 0
            port_description    = ""
            port_direction      = UCPortInput

            if ("range" in port):
                port_hi = port["range"][0]
                port_lo = port["range"][1]
            if("description" in port):
                port_description = port["description"]
            if("direction" in port):
                if(port["direction"] == "in"):
                    port_direction = UCPortInput
                elif(port["direction"] == "out"):
                    port_direction = UCPortOutput
                else:
                    log.error("Port %s has invalid port direction: '%s'"
                        %(port_name, port["direction"]))

            toadd = UCPort(port_name, bits_hi = port_hi,
                                      bits_lo = port_lo,
                                      direction = port_direction,
                                      description = port_description)
            tr.addPort(toadd)
    return tr
