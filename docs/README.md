
# uCode

A toy project for generating state machines by defining small microcoded
operations.

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
