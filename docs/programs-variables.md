
## Specifying Program Variables

Like the IO ports, program state is declared at the top of the program
file, before we specify any program behaviour.

**Grammar:**

```verilog
<program_variable> :=  <const_var>
                    |  <reg_var>
                    |  <comb_var>

<const_var>        := "const" <var_name> [<var_width>] "=" <expression>

<reg_var>          := "reg" <var_name> [<var_width>]

<comb_var>         := "comb" <var_name> [<var_width>] "=" <expression>

<var_name>         := (a-zA-Z)[a-zA-Z0-9_]*

<var_width>        := "[" <number> ":" <number> "]"

<number>           := (0-9)+
```

**Examples:**

```verilog
const low_halfword   = 32'h0000FFFF
reg  program_counter [31:0]
comb status_bits     [5:0] = {overflow, 3'b000, error}
reg overflow
```

As with ports, omitting the explicit range declaration (as with the `overflow`
signal above) will make it a 1-bit variable.

##  Program Variable Properties

### name         
    
The name of the variable used to refer to it in programs. Variable names can
contain any alpha-numeric characters and underscores.

### range        
    
How wide is the variable? Specified as a list where the first element is the
highest bit, while the second element is the low bit.

### type

Variables can be declared as registers using `reg`, constants using
`const` or wires using `comb`.

Register variables are updated only when they are written to by an instruction.

Wire ports are updated continuously whenever a variable in their assignment
expression is changed.

Constant ports are assigned to on declaration and take only one value.
