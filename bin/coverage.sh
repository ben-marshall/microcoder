#!/bin/bash

echo "---------- Coverage Collection Running ----------"

TOOL=./compile.py
ARGS="--opt-coalesce --flowgraph --graphpath work/graph.dot --gendocs --instrdocs work/docs.htm --progdocs work/pd.htm"
BASEPATH=./examples

coverage erase

for EX in `ls ${BASEPATH}`;
do
    coverage run -a ${TOOL} ${BASEPATH}/${EX}/${EX}-program.txt \
        ${ARGS} --output work/out.v
done
