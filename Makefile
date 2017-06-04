
EXAMPLE = count

SRC_INSTRS   = examples/${EXAMPLE}/${EXAMPLE}-instrs.txt
SRC_PROGRAM  = examples/${EXAMPLE}/${EXAMPLE}-program.txt

VERILOG_SRC  = work/${EXAMPLE}.v
SIM_FILE     = work/${EXAMPLE}.sim

CC = ./compile.py
VCC= iverilog
VVP= vvp

CC_FLAGS=

ifdef DEBUG
    CC_FLAGS = --debug-states
endif

all: $(SIM_FILE) $(VERILOG_SRC)

dirs:
	mkdir -p ./work

#
# Target to build verilog source files from the spec files for a program.
#
%.v : ${SRC_INSTRS} ${SRC_PROGRAM} dirs
	${CC} ${SRC_INSTRS} ${SRC_PROGRAM} \
        --output $@ \
        --gendocs --instrdocs work/doc-instrs.html \
        $(CC_FLAGS)

#
# Target to convert verilog files into icarus verilog simulation exes
#
%.sim : %.v
	${VCC} -o $@  $< work/tb_${EXAMPLE}.v


run : $(SIM_FILE) $(VERILOG_SRC)
	$(VVP) $(SIM_FILE)
