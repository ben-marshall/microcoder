

# Specifying IO Ports.

IO port specification is done at the top of a program file, before we declare
anything else.

**Grammar:**

```verilog
port <input|output> <port-name> [<hi>:<lo>]
```

**Examples:**

```verilog
port input count [7:0]
port output finished
```

Ports with no defined width are assumed to be 1-bit wide.

## Port Properties

### name         
    
The name of the port used to refer to it in programs. Port names can contain 
any alpha-numeric characters and underscores.

### range        
    
How wide is the port? Specified as a list where the first element is the
highest bit, while the second element is the low bit.

### direction    

Is the port an input or an an output? Bi-directional ports are not supported.

## Example Port set

The ports below might describe a very simple "encryption" module, which takes
eight bits at a time, does some encryption on them, and signals when it is
finished.

```verilog
port input  data_valid         # The input <data> port is valid.
port input  data_in      [7:0] # The data to be encrypted.
port output encrypt_done       # We have finished encrypting. <data_out> valid.
port output data_out     [7:0]
```
