#!/bin/bash

g++ solver.cpp -o solver

mkdir -p testcases_op

ls -1 testcases | while read LINE
do 
    ./solver testcases/$LINE > testcases_op/$LINE.op 
    python3 checker.py testcases/$LINE testcases_op/$LINE.op
done