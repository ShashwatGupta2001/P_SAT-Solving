import pandas as pd
import numpy as np
from pysat.formula import CNF
from pysat.solvers import Minisat22
import random
from timeit import default_timer as timer

k= int(input("Enter value of k:\n"))  # sqrt(no. of col in csv file )
n=k**2 # no. of rows and columns

start=timer()

# base n+1 encoding in with the order of parameters only
# i.e. s_vijd = v*n^3 + i * n^2 + j*n + d // encoding 
def encode(n, sudoku, row, column, digit, sign):
  return (sign*(sudoku * ((n+1)*(n+1)*(n+1)) + row * ((n+1)*(n+1)) + column * ((n+1)) + digit)) //1

# base n+1 decoding in with the order of parameters only
# i.e. s_vijd = v*n^3 + i * n^2 + j*n + d // encoding 
def decode(n, code):
  
  sign=1 if (code>0) else -1
  code=code*sign

  digit=code%(n+1)
  code=(code)//(n+1)
    
  column=code%(n+1)
  code=(code)//(n+1)
  
  row=code%(n+1) 
  code=(code)//(n+1)
   
  sudoku=code%(n+1)
  code=(code)//(n+1)
   
  return (n, sudoku, row, column, digit, sign)

#Encoding Problem:
formula = CNF()

# 1.1 every cell has atmost 1 entry
for u in range (0,2):
  for i in range(1,n+1):
    for j in range(1,n+1):
      for d1 in range(1,n):
        for d2 in range(d1+1,n+1):
          formula.extend([[encode(n,u,i,j,d1,-1), encode(n,u,i,j,d2,-1)]]) # encoding NAND operation for this

# 1.2 every cell has atleast 1 entry
for u in range (0,2):
  for i in range(1,n+1):
    for j in range(1,n+1):
      formula.extend([[encode(n,u,i,j,d,1) for d in range(1,n+1)]])
          
# 2. every number appears atleast once in each column
for u in range (0,2):
  for j in range(1,n+1):
    for d in range(1,n+1):
      formula.append([encode(n,u,i,j,d,1) for i in range(1,n+1)]) # clause consisting of all rows

# 3. every number appears atleast once in each row
for u in range (0,2):
  for i in range(1,n+1):
    for d in range(1,n+1):
      formula.append([encode(n,u,i,j,d,1) for j in range(1,n+1)]) # clause consisting of all columns

# 4. every number appears atleast once in each grid 
# every sudoku can be viewed as a grid of kxk within each grid of kxk
for u in range (0,2):
  for g_out in range(1,n+1):
    for d in range(1,n+1):
      formula.append([encode(n,u,( ((g_out -1)//k)*k + (g_in -1)//k +1 ) , ( ((g_out -1)%k)*k + (g_in -1)%k +1 ) ,d,1) for g_in in range(1,n+1)]) # clause consisting of all grid-cells

# 5. every cell of sudoku must have all different entries
for i in range(1,n+1):
    for j in range(1,n+1):
      for d in range(1,n+1):
        formula.extend([[encode(n,0,i,j,d,-1),encode(n,1,i,j,d,-1)]]) # encoding NAND operation for inequality between 2 variables as inequality implies odd parity

def extractNum(sudoku):
    given=[]
      
    for i in range(1,2*n+1):
      for j in range(1,n+1):
        if(sudoku[i-1,j-1]!=0):
          given.append(int(encode(n,(i-1)//n,(i-1)%n +1,j,sud[i-1,j-1],1)))

    return given

def tabular(sudokuNum):
      sud=np.zeros(shape=[2*n,n],dtype=np.int8)
         
      for i in sudokuNum:
        if(i>0):
          d=decode(n,i)
          if(d[1]==0):
            sud[d[2]-1,d[3]-1]=int(d[4])
          elif(d[1]==1):
            sud[n+d[2]-1,d[3]-1]=int(d[4])

      return sud

def Cloning(l1):
    l1c=l1[:]
    return l1c

# Check if more solutions are possible
def checkuniq(given):
   i=3
   with Minisat22(bootstrap_with=formula.clauses) as l:
      if l.solve(assumptions=given) == True:
         
        #  print(given)
        #  tabular(l.get_model())

         #exclude=copy.deepcopy(formula)
         exclude=formula.copy()
         exclude.append([value * -1 for value in list(set([v for v in l.get_model() if v>0])-set(given))])
         
         with Minisat22(bootstrap_with=exclude.clauses) as m:
            if m.solve(assumptions=given) == True:
               i=0 # multiple solutions
               #print(0)
            else:
               i=1 # unique solution
               #print(1)
         m.delete()
      else:
         i=-1 # no solution
         #print(-1)
         #print(l.get_core())

   l.delete()
   return i

sud=np.array([])
with Minisat22(bootstrap_with=formula.clauses) as l:
     temp=[random.randint(1,formula.nv)]
     if l.solve(assumptions=temp) == True:
         sud=tabular(l.get_model())
     else:
         print("The given pair cannot be solved")
l.delete()

given=extractNum(sud)

random.shuffle(given)
given=[given[i] for i in range (n*n//2,len(given)-1)]

more=1
while(more==1):
    length=len(given)
    l=0
    for i in given:
      temp=[x for x in given if x!=i]
      if (checkuniq(temp)==1):
          given=temp          
      else:
          l=l+1
    if(l==len(given)):
        more=0

df=pd.DataFrame(tabular(given))
df.to_csv("output.csv")

end=timer()

print(end-start)