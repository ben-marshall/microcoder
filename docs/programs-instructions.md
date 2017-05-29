
# Specifying Program Instructions

Instructions are specified by defining their name, parameters and a function
they perform on those parameters.

```

// Add a constant value b to program variable a
define add_constant 
    argument variable a
    argument constant b
begin
    a = a + b
end

// add variables a and b, store the result in a
define add_variable
    argument variable a
    argument constant b
begin
    a = a + b
end

// apply a mask to variable a and store the result in a
define mask
    argument variable a
    argument constant mask
begin
    a = a & b
end

// set a bit of variable a
define set_bit
    argument variable a
    argument constant bit
begin
    a = a | (1 << bit)
end

// Perform a fused multiply add operation and store the result in d
define fmadd
    argument variable a
    argument variable b
    argument variable c
    argument variable d
begin
    d = (a * b) + c
end

// Split two 32 bit variables into 4 16 bit variables and add them together.
// Store the result in a different variable.
define add_double_16
    argument variable [31:0] a
    argument variable [31:0] b
    argument variable [31:0] c
begin
    c [15: 0] = a [15: 0] + b [15: 0]
    c [31:16] = a [31:16] + b [31:16]
end
```
