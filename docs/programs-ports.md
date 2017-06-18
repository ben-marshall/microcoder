

# Specifying IO Ports.

IO port specification is done at the top of a program file, before we declare
anything else.

**Grammar:**

```verilog
<port>        := <input_port> 
               | <output_port>

<input_port>  := "input" ["comb"] <port_name>  <port_width>

<output_port> := <reg_out> 
               | <comb_out>

<reg_out>     := "output" ["reg"] <port_name>  <port_width>

<comb_out>    := "output" "comb" <port_name>  <port_width> = <expression>

<port_name>   := (a-zA-Z)[a-zA-Z0-9_]*

<port_width>  := "[" <number> ":" <number> "]"

<number>      := (0-9)+
```

**Examples:**

```verilog
input   count [7:0]

output reg  finished
output comb address     [31:0] = base + offset
```

Ports with no defined width are assumed to be 1-bit wide.

Input ports are always of type `comb` (read as *combinatorial*) while
output ports can be of type `reg` (for register) or `comb`.

## Port Properties

### name         
    
The name of the port used to refer to it in programs. Port names can contain 
any alpha-numeric characters and underscores.

### type

Ports can be declared as registers using `reg` or wires using `comb`.

Register ports are updated only when they are written to by an instruction.

Wire ports are updated continuously whenever a variable in their assignment
expression is changed.

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
input  data_valid         # The input <data> port is valid.
input  data_in      [7:0] # The data to be encrypted.
output comb encrypt_done  = !wait # We have finished encrypting. <data_out> valid.
output reg  data_out     [7:0]
```
