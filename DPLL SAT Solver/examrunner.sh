#!/bin/bash

g++ solver.cpp -o solver

start_time=`date +%s`

./solver emailtestcases/m2.cnf

end_time=`date +%s`

echo execution time was `expr $end_time - $start_time` s.