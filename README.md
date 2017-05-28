
# uCode

A toy project for turning user-defined assembly-like programs into 
synthesisable verilog code. This verilog code can then be implemented on
an FPGA.

---

## Aims

The aim for this project is to allow people to define a set of their own
assembly-like *micro-instructions* using a very simple syntax. Using these
definitions, they can then write programs which are then transpiled into a
verilog state-machine. It will also be possible to define IO ports which allow
the programs to communicate with the outside world.

A typical flow for using this tool might look like:

1. Define a set of input and output signals that a microcore.
2. Define the amount of readable / writable program state a microcore will
   have access to. These are analogous to the "registers" of a normal CPU.
3. Define the set of instructions that the microcore will be able to
   perform.
4. Write a top-level microcode which will "run" on the core.
5. Generate the synthesisable verilog.

## Progress

As of `v0.1`, one can use the tool to:

- Define arbitrary instructions, with arguments and their own set of
  operations on those arguments.
- Define arbitrary inputs and outputs to the micro-code program, known as 
  *ports*.
- Define global state variables which the instructions can access and modfy.
- Write assembly-like programs, with basic blocks, instructions and
  conditional jumps between those blocks.

Within each block, instructions can read and write the program ports, as well
as the global state variables.

## Documentation

All documentation is found in the [docs/](./docs/) folder of the project.
One can use [mkdocs](http://www.mkdocs.org/) to view them rendered as linked 
HTML pages.


## Examples

There are two examples bundled with the repositiory.

**Counter** - This is a really boring counter which simple counts down
from 10 and then loops. Forever.

```sh
$> make all run EXAMPLE=count
```

**Fibonacci** - This program takes an `n` value, and computes the `n`'th
number in the Fibonacci sequence.

```sh
$> make all run EXAMPLE=fibonacci
```

The output wave files for both examples are written to `work/waves.vcd`. This
can be viewed using a program like
[GTKWave](http://iverilog.wikia.com/wiki/GTKWAVE).

## Todo

- [X] Make it possible to define ports and variables in the same file as
      the rest of the program.
- [ ] Generate documentation for programs automatically.
