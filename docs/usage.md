
# Usage

This page explains how to use the tool in terms of invocation, and how it
might fit into a design flow.

---

## What is this for?

- Prototyping sequential control logic.
- Building accelerators for critical code segments which you want to
  offload from a CPU. Because you can define your own instructions and
  semantics, you should be able to replicate most loop kernels without
  much trouble.
- Creating a "run-only" CPU, where the program to be executed is stored
  as part of the actual logic circuit. This makes it *immune* to code
  tampering (since the running software cannot be changed) and means you
  don't need to waste precious memory space with code.
- Experimenting with translating high(ish) level serial code into
  synthesisable digital logic.

**Note:** This tool does *zero* optimisation of the input code. If you are
planning to synthesise a design, then remember that you will be relying on
your synthesis tool to optimise any of the control logic, resource sharing and
register usage.

## Invocation

The main tool is written in Python3 code, using the Jinja2 templating
library, as well as the pyyaml package. Both of these can be installed
via pip.

Run the tool using the following command:

```sh
$> ./counter.py --help

usage: compile.py [-h] [--output OUTPUT] [--gendocs] [--instrdocs INSTRDOCS]
                  instructions program

positional arguments:
  instructions          Instructions definition file
  program               The program to compile.

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT, -O OUTPUT
                        Output path
  --gendocs, -D         Generate documentation
  --instrdocs INSTRDOCS
                        Instruction documentation output file path
$> _
```

The key arguments are `instructions` and `program` which define the source
files containing the instruction definitions and program code / ports
respectively.

The `--gendocs` switch will make the tool emit a simple HTML page which
documents any defined instructions it is aware of. This can be useful for
creating a library of frequently use instructions which you can re-use.

## Where in the flow?

It is expected that the tool is used to create control modules or
accelerators for specific kinds of operation. It will not generate code
as efficient as a human can write, but it will make lowering critical code
into hardware much easier for the sake of prototyping.

Conceptually, a typical flow for using this tool might look like:

1. Define a set of input and output signals that a micro-core.
2. Define the amount of readable / writable program state a micro-core will
   have access to. These are analogous to the "registers" of a normal CPU.
3. Define the set of instructions that the micro-core will be able to
   perform.
4. Write a top-level microcode which will "run" on the core.
5. Generate the synthesisable verilog.
6. Run the verilog in a simulation or synthesis flow of your choice.
