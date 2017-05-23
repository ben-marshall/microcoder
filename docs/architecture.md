
# uCore Architecture

This page describes the architecture of a microcore.

---

## Overview

At a high level, a microcore is simply a finite state machine. Each state
represents the execution of a single instruction within a program, and
transitions between states represent the progression of execution through
the program.

Execution will always start in the `main` state and continue from there.
