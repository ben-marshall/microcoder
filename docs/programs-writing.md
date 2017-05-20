
# Writing Programs

Programs are written as series of "basic blocks" which can be jumped between
using built-in control flow operations.


## Program blocks

All programs start at the `main` block.

Blocks consist of a `block <name>` statement, followed by one or more
instructions. One instruction per line.

```
block main

    instr 0
    instr 1
    instr 2
    instr 3
    instr 4

```


## Program control flow

There are three kinds of control flow operations supplied:

- `goto <block>`

The `goto` operation will immediatly and unconditionally move control flow of
the program to the start of the named block.

- `ifeqz <variable> <block>`

The `ifeqz` operation will jump to the named block if and only if the variable
it is supplied with is zero.

- `ifnez <variable> <block>`

The `ifnez` operation will jump to the named block if and only if the variable
it is supplied with is not zero.

A block with no control flow statement at the end of it will simply continue
to the next defined block. If no subsequent block is found, then behaviour is
undefined.


```
block main

    set  var1    10

block loop
    set     port_1  var1
    sub     var1    1
    
    ifeqz   var1    finish

    goto    loop

block finish
    goto finish
```

The example program above decrements a counter from 10 to 0 and then "quits"
by entering an infinite loop.

