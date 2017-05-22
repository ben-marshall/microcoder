
## Specifying Program Variables

Like the IO ports, program state is specified using YAML data:

```yaml
program_state:

  <variable_1>:
    range: [X, Y]
    description: >
        What is variable_1 used for?

  <variable_2>:
    description: >
        What is variable_1 used for?
```

##  Program Variable Properties

### name         
    
The name of the variable used to refer to it in programs. Variable names can
contain any alpha-numeric characters and underscores.

### range        
    
How wide is the variable? Specified as a list where the first element is the
highest bit, while the second element is the low bit.

```yaml
- range: [31,0] // Specifies a 32-bit wide variable with a range from 31 to 0.
- range: [31,2] // Specifies a 32-bit wide variable ranging from 31 to 2.
```

If this field is omitted, then the range is assumed to be `[0:0]` which will
create a 1-bit variable.

### description

This field is optional, but allows you to comment on exactly what the variable
is used for or what it represents.
