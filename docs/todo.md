
# Todo List

### Features

- [X] Make `current_state` value accessible.
- [X] Call / return ~~using the stack~~ using generic variables.
- [X] Support for include files / packages/ modules.
- [ ] Multiple instantiations of included files.
- [ ] Make it possible to access state (block) encodings directly for better
      call / return support.
- [ ] Inlineable blocks rather than callable blocks.

#### Parsing

- [ ] Proper parsing of instruction statements, rather than simply expecting
      correct Verilog syntax as at the moment.

### Translation

- [X] Detect multiple writes to the same variable in a single state.
- [X] Detect reading from and writing to the same variable in a single state.
- [X] Infrastructure to break up blocks into sequences of atomic operations.
- [ ] Marking of parallelisable statements

### Optimisation

- [X] Infrastructure to coalesce atomised blocks based on tunable parameters.
- [ ] Be able to specify a *cost* for each operator, and coalesce blocks until
      they contain the maximum allowable *cost* per block (per cycle)
- [ ] Detecting and unrolling loops

### Examples

- [ ] Stack example
- [X] Finish the AXI example
- [ ] Mini RISCV registers and instructions. RV32UI Only.
