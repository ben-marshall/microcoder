

# Specifying IO Ports.

IO port specification is done using a YAML file with the following structure:

```yaml
ports:

  <port name 1>
   range:       [X, Y]
   direction:   <in/out>
   description: >
    What does port 1 do?

  <port name 2>
   range:       [X, Y]
   direction:   <in/out>
   description: >
    What does port 2 do?
```

As can be seen in the YAML snippet above, each port has the following
properties:

## Port Properties

### name         
    
The name of the port used to refer to it in programs. Port names can contain 
any alpha-numeric characters and underscores.

### range        
    
How wide is the port? Specified as a list where the first element is the
highest bit, while the second element is the low bit.

```yaml
- range: [31,0] // Specifies a 32-bit wide port with a range from 31 to 0.
- range: [31,2] // Specifies a 32-bit wide port ranging from 31 to 2.
```

### direction    

Is the port an input or an an output? Bi-directional ports are not supported.

```yaml
- direction: in     // An input port
- direction: out    // An output port
```

If this field is omitted, then the range is assumed to be `[0:0]` which will
create a 1-bit variable.

### description

This field is optional, but allows you to comment on exactly what the port is
for.

## Example Port set

The ports below might describe a very simple "encryption" module, which takes
eight bits at a time, does some encryption on them, and signals when it is
finished.

```yaml
ports:

- data_valid
  - direction: in
  - description: The input <data> port is valid.

- data_in
  - direction: in
  - range:     [7:0]
  - description: The data to be encrypted.

- encrypt_done
  - direction: out
  - description: We have finished encrypted the data. <data_out> is valid.

- data_out
  - direction: out
  - range:     [7:0]
  - description: The encrypted data.
```
