
## Specifying Program Variables

Like the IO ports, program state is declared at the top of the program
file, before we specify any program behaviour.

**Grammar:**

```verilog
state <variable_1> [<hi>:<lo>]
state <variable_2>
```

**Examples:**

```verilog
state program_counter [31:0]
state status_bits     [5:0]
state overflow
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
