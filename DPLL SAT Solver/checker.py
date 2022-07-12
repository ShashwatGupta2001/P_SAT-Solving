# input file
import sys
from pysat.formula import CNF
from pysat.solvers import Minisat22
print(sys.argv[1])

formula = CNF(from_file=sys.argv[1])
#formula = CNF(from_file="uf20-01.cnf")

#output file
file1 = open(sys.argv[2], "r")
#file1 = open("uf20-01.cnf.op", "r")
Lines = file1.readlines()



# checking
if(len(Lines)==1):
  with Minisat22(bootstrap_with=formula.clauses) as l:
    if l.solve() == True:
        print("Not Matching")
    else:
        print("Matched with C++ code")
else:
    a_string=Lines[1]
    file1.close()
    a_list = (a_string[1:-2]).split()
    map_object = map(int, a_list)
    list_of_integers = list(map_object)
    with Minisat22(bootstrap_with=formula.clauses) as l:
        if l.solve(assumptions=list_of_integers) == False:
            print("Not Matching")
        else:
            print("Matched with C++ code")
l.delete()