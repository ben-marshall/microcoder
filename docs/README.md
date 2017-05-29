
# uCode

[![Documentation Status](https://readthedocs.org/projects/microcoder/badge/?version=latest)](http://microcoder.readthedocs.io/README/)

A toy project for turning user-defined assembly-like programs into 
synthesisable verilog code. This verilog code can then be implemented on
an FPGA.

More information on what this tool might be used for is found 
[here](usage.md). There is also a **walkthrough example** [
here](example-dma.md).

---

## Aims

The aim for this project is to allow people to define a set of their own
assembly-like *micro-instructions* using a very simple syntax. Using these
definitions, they can then write programs which are then transpiled into a
verilog state-machine. These programs then communicate with the outside world
using custom IO ports.

## Progress

Currently, one can use the tool to:

- Define arbitrary instructions, with arguments and their own set of
  operations on those arguments.
- Define arbitrary inputs and outputs to the micro-code program, known as 
  *ports*.
- Define global state variables which the instructions can access and modify.
- Write assembly-like programs, with basic blocks, instructions and
  conditional jumps between those blocks.

Within each block, instructions can read and write the program ports, as well
as the global state variables.

## Documentation

All documentation is found in the [docs/](./docs/) folder of the project.
These same files are also hosted on 
[microcoder.readthedocs.io](http://microcoder.readthedocs.io/README/).

## Examples

There are some simple examples bundled with the repository:

**Counter** - This is a really boring counter which simply counts down
from 10 and then loops. Forever.

```sh
$> make all run EXAMPLE=count
```

**Fibonacci** - This program takes an `n` value, and computes the `n`'th
number in the Fibonacci sequence.

```sh
$> make all run EXAMPLE=fibonacci
```

**DMA** - An example of a DMA memcopy co-processor which coppies multiple
words from one memory base address to another.

```sh
$> make all run EXAMPLE=dma
```

The output wave files for both examples are written to `work/waves.vcd`. This
can be viewed using a program like
[GTKWave](http://iverilog.wikia.com/wiki/GTKWAVE).
