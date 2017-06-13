
EXAMPLE = count

SRC_PROGRAM  = examples/${EXAMPLE}/${EXAMPLE}-program.txt

VERILOG_SRC  = work/${EXAMPLE}.v
SIM_FILE     = work/${EXAMPLE}.sim

CC = ./compile.py
VCC= iverilog
VVP= vvp

CC_FLAGS=

GRAPH = work/graph.svg

ifdef OPT
    CC_FLAGS += --opt-coalesce
endif

ifdef DOT
    CC_FLAGS += --flowgraph --graphpath work/graph.dot
endif

ifdef DEBUG
    CC_FLAGS += --debug-states
endif

.PHONY: docs

all: $(SIM_FILE) $(VERILOG_SRC) 
ifdef DOT
	$(MAKE) $(GRAPH)
endif

dirs:
	mkdir -p ./work

#
# Target to build verilog source files from the spec files for a program.
#
%.v : ${SRC_PROGRAM} dirs
	${CC} ${SRC_PROGRAM} \
        --output $@ \
        --gendocs --instrdocs work/doc-instrs.html \
        --progdocs work/doc-program.html \
        $(CC_FLAGS)

everything:
	$(MAKE) EXAMPLE=count
	$(MAKE) EXAMPLE=call
	$(MAKE) EXAMPLE=axi
	$(MAKE) EXAMPLE=memctrl
	$(MAKE) EXAMPLE=dma
	$(MAKE) EXAMPLE=fibonacci

#
# Target to convert verilog files into icarus verilog simulation exes
#
%.sim : %.v
	${VCC} -o $@  $< work/tb_${EXAMPLE}.v


run : $(SIM_FILE) $(VERILOG_SRC)
	$(VVP) $(SIM_FILE)

docs:
	mkdocs serve

%.svg : %.dot
ifdef DOT
	dot -O -Tsvg $<
endif
