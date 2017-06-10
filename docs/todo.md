
# Todo List

### Parsing

- [ ] Proper parsing of instruction statements, rather than simply expecting
      correct Verilog syntax as at the moment.

### Translation

- [X] Detect multiple writes to the same variable in a single state.
- [X] Detect reading from and writing to the same variable in a single state.
- [X] Infrastructure to break up blocks into sequences of atomic operations.

### Optimisation

- [ ] Infrastructure to coalesce atomised blocks based on tunable parameters.
- [ ] Be able to specify a *cost* for each operator, and coalesce blocks until
      they contain the maximum allowable *cost* per block (per cycle)
