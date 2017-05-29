
# Example Program: DMA

This page walks through how to re-create the DMA example found in
the `examples/dma/` folder of the project.

---

## Introduction

DMA stands for *Direct Memory Access*. It is an umbrella term for basically
taking long memory copying / moving / managment operations away from the CPU
and giving them to a dedicated piece of hardware. Meanwhile, the CPU can do
something more useful.

This example creates a tiny, simplified DMA module which can be programmed to
copy `N` words of data from a *source* address to a *destination* address.

In Python-esq code, such an operation looks like this:

```python
def memcpy (source_address, destination_address, count):
    
    down_counter = count

    while (down_counter > 0):
        
        temp = memory [ source_address ]

        memory [ destination_address ] = temp

        source_address      = source_address        + 4
        destination_address = destination_address   + 4

        down_counter = down_counter - 1

    return
```


## Ports

First we define the ports our DMA module will use. From the pseudo code above
we know we will need atleast the following:

- A source address *input*.
- A destination address *input*.
- A *number of words to move* count *input*.
- An *output* to say, I've finished!
- An *input* to say, *you can start copying things now*.

But, we also need to access memory! For the sake of this example, we will
assume an idealised *SRAM-like* interface with address, data and control
lines on a single channel.

So here are the ports we will use!

```
#
# Control ports our 'CPU' can use to program the DMA module
#

port input  ctrl_valid
port output ctrl_en
port input  ctrl_src_addr_base   [31:0]
port input  ctrl_dst_addr_base   [31:0]
port input  ctrl_count           [7:0]
port output ctrl_finished

#
# The memory interface used by the port.
#

port output data_addr            [31:0]
port output data_wdata           [31:0]
port input  data_rdata           [31:0]
port output data_valid
port output data_w_en
port input  data_en
```

## Variables

We will also need some scratch variables so we can increment the
address pointers, and decrement the counter. We'll also need somewhere to
temporarily store the read data before writing it out again.

```
state   counter                  [7:0]
state   temp_data                [31:0]
state   dst_addr                 [31:0]
state   src_addr                 [31:0]
```

## Instructions

Now we need to work out what kind of operations we actually need to perform.
The fewer instructions we define and use, the smaller our module will be.

Obviously we will need to be able to increment and decrement, as well as
copy data. We could also define a couple of big *memory* instructions which
handle lots of the memory interface protocol for us:

```
// Set a variable to a constant value
define set
    argument variable var
    argument constant val
begin
    var = val
end

// Copy one variable into another
define copy
    argument variable dest
    argument variable source
begin
    dest = source
end


// Add two variables together and put the result in another variable.
define add_vars
    argument variable result
    argument variable a
    argument variable b
begin
    result = a + b
end

// Increment a variable by a constant value
define inc
    argument variable var
    argument constant increment
begin
    var = var + increment
end

// decrement a variable by a constant value
define dec
    argument variable var
    argument constant increment
begin
    var = var - increment
end


// Read an address (stored in a variable) into another variable.
define mem_rd
    argument variable address
    argument variable destination
begin
    data_w_en   = 0
    data_valid  = 1 && !data_en
    data_addr   = address
    destination = data_rdata
end

// write an address (stored in a variable) into another variable.
define mem_wr
    argument variable address
    argument variable data
begin
    data_w_en   = 0
    data_valid  = 1 && !data_en
    data_addr   = address
    data_wdata  = data
end
```

## Writing the program

To recap, we have defined how our DMA module will interract with the
outside world with the *ports*, what internal state it will need, and the
operations we will need to perform.

Now we can write the program. Below is a very heavily commented version of
what is in the `examples` folder of the project.

```

#
# Program main block - execution starts here.
#
#   First, make sure we reset all of our outputs to a known value.
#
block main
    
    # Reset all out the outputs.
    set     ctrl_en         0
    set     ctrl_finished   0
    set     data_addr       32'b0
    set     data_wdata      32'b0
    set     data_valid      0
    set     data_w_en       0
    
    # Execution will automatically continue into the next block.

#
# Loop inside this block waiting for the valid signals to go on the control
# port. When this happens, the CPU has told us that there is valid data on
# the ctrl_* ports.
#
block   wait_for_command
    
    # Stay here until we get the right command.
    ifeqz   ctrl_valid  wait_for_command
    ifnez   ctrl_valid  store_inputs

#
# Now we have a valid command, store the data in our state variables and tell
# the CPU it can leave us be until we are finished.
#
block   store_inputs
    
    copy    counter         ctrl_count
    copy    src_addr        ctrl_src_addr_base
    copy    dst_addr        ctrl_dst_addr_base
    set     ctrl_en         1

    goto    dma_loop

#
# Outer loop of the dma operation.
#
block dma_loop
    set     ctrl_en         0

#
# Perform the read operation using our 'mem_rd' instruction, and waiting in
# this block until the memory acknowledges our request.
#
block do_read
    mem_rd  src_addr        temp_data
    ifeqz   data_en         do_read
    ifnez   data_en         do_write

#
# Write back the stored data to the destination address, again waiting in case
# the memory needs to stall.
#
block do_write
    mem_wr  dst_addr        temp_data
    ifeqz   data_en         do_write
    ifnez   data_en         update_count

#
# Increment our counters and check if we are finished. If yes, continue and
# if not then go back to the dma_loop block.
#
block update_count
    dec     counter         1
    inc     src_addr        4
    inc     dst_addr        4
    set     data_valid      0
    ifeqz   counter         finished
    ifnez   counter         dma_loop

#
# Signal to the CPU our operation is complete and head back to the main block
# to wait for another command.
#
block finished
    set     ctrl_finished   1
    goto    main
```

## Building

All that is left to do now is compile the program. You can do this really
easily by running:

```sh
$> make run EXAMPLE=dma
```

This will build the example program and simulate it. You can examine the
`Makefile` to see the exact command sequence used.

Congratulations on building your DMA co-processor!
