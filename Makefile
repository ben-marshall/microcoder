
SRC_PORTS    = examples/ports.yaml
SRC_STATE    = examples/state.yaml
SRC_INSTRS   = examples/instructions.txt
SRC_PROGRAM  = examples/program.txt

VERILOG_SRC  = work/out.v
SIM_FILE     = work/out.sim

CC = ./compile.py
VCC= iverilog
VVP= vvp

all: $(SIM_FILE) $(VERILOG_SRC)

dirs:
	mkdir -p ./work

#
# Target to build verilog source files from the spec files for a program.
#
%.v : ${SRC_PORTS} ${SRC_STATE} ${SRC_INSTRS} ${SRC_PROGRAM} dirs
	${CC} ${SRC_PORTS} ${SRC_STATE} ${SRC_INSTRS} ${SRC_PROGRAM} \
        --output $@

#
# Target to convert verilog files into icarus verilog simulation exes
#
%.sim : %.v
	${VCC} -o $@  $< work/tb_out.v


run : $(SIM_FILE) $(VERILOG_SRC)
	$(VVP) $(SIM_FILE)
