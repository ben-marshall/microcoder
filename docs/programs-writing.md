
# Writing Programs

Programs are written as series of "basic blocks" which can be jumped between
using built-in control flow operations.


## Program blocks

All program execution starts at the `main` block. Ports and state variables
must all be declared before the first block.

Blocks consist of a `block <name>` statement, followed by one or more
instructions. One instruction per line.

```

<instruction / subprogram  includes>

<port declarations>

<variable declarations>

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

The `goto` operation will immediately and unconditionally move control flow of
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

using instructions "my-instructions.txt"

port output port_1 [5:0]

state var1 [5:0]

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


## Special Variables and Call / Return

There are two ways to implement call/return behaviour in programs. The first
is via the `_current_state` special variable, the second is via the
state de-reference operator: `*`.

### The `_current_state_` variable

1. Declare a state variable at least 12-bits wide to be your *return address*
pointer.
2. Declare a 1-bit state variable to indicate a call or return is taking place.
3. Write your *function* such that when it is finished, it jumps to the value
inside your *return address* variable using a `goto` or `if*` statement.
Upon returning it must set the `called` bit to zero.
4. Any code which wants to call this function can now simply set the *called*
bit, set the *return address* variable to `_current_state_` and then jump
to the function.

The caller function **must** jump to the callee if and only if the *called*
bit is set. If the called bit is not set, this means we have returned to the
caller state from the callee, and can continue to the next state.


### State Dereference Operator

It is possible to access the actual encoding of a block state by prefixing
its name with a `*`. This is substituded in the final program with the
encoded value of that state.

In order to use this in an instruction argument, the arugment must be of type
`constant`.

For example, if we want to call a function `callee` from a function `caller`
and then return to the `loop` block:

```
reg return_value [11:0]

block loop
    blah
    foo
    bar
    goto    caller

block caller
    set     return_value    *callee
    goto    callee

block callee
    blar
    boo
    far
    goto    return_value

```

This method is usually simpler to use than the `_current_state` variable.
