
SRC_PORTS    = examples/count-ports.yaml
SRC_STATE    = examples/count-state.yaml
SRC_INSTRS   = examples/count-instrs.txt
SRC_PROGRAM  = examples/count-program.txt

VERILOG_SRC  = work/count.v
SIM_FILE     = work/count.sim

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
