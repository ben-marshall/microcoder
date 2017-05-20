
# uCode Programs

This page details how uCode programs are specified.

---

uCode programs are composed of user-defined instructions. Each instruction can
be as simple or complex as people like, though this will obviously impact the
complexity of the final state machine.

All instructions can operate on two different sources of data:

- Input and output (IO) ports.
- Program Variables.

Input and output ports allow the uCore to communicate with the outside world.
They are best thought of as general purpose input output (GPIO) ports like
one might find on a typical microcontroller.

Program variables are simply a collection of state variables which programs can
use as scratch space for computation. They are similar to the general purpose
registers (GPRS) of normal instruction set architectures.
