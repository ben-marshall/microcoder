
# uCore Architecture

This page describes the architecture of a microcore.

---

## Overview

At a high level, a microcore is simply a finite state machine. Each state
represents the execution of a single instruction within a program, and
transitions between states represent the progression of execution through
the program.

Execution will always start in the `main` state and continue from there.

## Ports

- Each port will be input or output (as appropriate) *wires*. Any ports which
  must store state will have registers with the same name (but with a `_reg`
  suffix created).
- Two auxiliary ports will be created: `clk` and `aresetn`.

## Program Variables

- All program variables will be registers, with an accompanying `n_*` signal
  denoting the next value.
- When instructions *read* a variable, they will read the *current* value in
  the register.
- When instructions *write* a variable, they set the *next* `n_*` value of
  the variable.
- Progression from one state to another will propagate the *next* value into
  the register, such that it becomes the current value.

## Instructions

- All instructions will be implemented as functions which execute *in zero
  time*. This makes them much easier to implement and re-use with different
  arguments. A side effect of this is to mandate that all `n_*` signals for
  program variables are of type `reg`.

## Program blocks

- Each program block is implemented as a series of sequential states, each one
  with a single instruction function call. Progression to the next state in a
  block is un-conditional until the final instruction of the block.
- At the end of the block, the *next* block is computed based on the control
  flow statements at the end of the block.
- Blocks with no explicit control flow statement simply carry on to the next
  block in the program sequence.


