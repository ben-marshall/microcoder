
# uCore Architecture

This page describes the architecture of a micro-core.

---

## Overview

At a high level, a micro-core is simply a finite state machine. Each state
represents the execution of a single basic block within a program, and
transitions between states represent jumps of control flow between basic
blocks within the program.

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

- All instructions will be implemented as sequential statements in the
  appropriate states of the FSM where they are used.

## Program blocks

- Each program block is implemented as a series of sequential states, with a
  single instruction executing per block [^1]
  These statements are the expansion of all instructions within a basic block.
- At the end of the block, the *next* block is computed based on the control
  flow statements at the end of the block.
- Blocks with no explicit control flow statement will cause the program to
  return to the `main` start block.

---

[^1] This will change in future if optimisation is allowed.
