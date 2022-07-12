import datetime
import pandas as pd
import numpy as np

# Input

# read csv file
filename=input("Enter name of file 'without .csv extension'\n")
data=pd.read_csv(filename+".csv")
data.fillna(0,inplace=True)
begin_time = datetime.datetime.now()
k= int((data.size/2)**0.25)  # sqrt(no. of col in csv file )
n=k**2 # no. of rows and columns

sud=np.array(data)[::,1::]
print(sud)
#Functions

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


# Solving the Part1 of the Assignment:

#Encoding Problem: using the effecient-type encoding (Weber 2005)
# i.e. Cell_d ∧ Row_u ∧ Col_u ∧ Block_u ∧ CorrespCell ∧ Assigned


from pysat.formula import CNF
from pysat.solvers import Minisat22

formula = CNF()

# 1 every cell has atmost 1 entry (definedness)
for u in range (0,2):
  for i in range(1,n+1):
    for j in range(1,n+1):
      for d1 in range(1,n):
        formula.extend([[encode(n,u,i,j,d1,-1), encode(n,u,i,j,d2,-1)] for d2 in range(d1+1,n+1)]) # encoding NAND operation for this

# 1.2 every cell has atleast 1 entry (uniqueness)
for u in range (0,2):
  for i in range(1,n+1):
    for j in range(1,n+1):
      formula.extend([[encode(n,u,i,j,d,1) for d in range(1,n+1)]])
          
# 2. every number appears atleast once in each column(uniqueness)
for u in range (0,2):
  for j in range(1,n+1):
    for d in range(1,n+1):
      formula.append([encode(n,u,i,j,d,1) for i in range(1,n+1)]) # clause consisting of all rows

# 3. every number appears atleast once in each row(uniqueness)
for u in range (0,2):
  for i in range(1,n+1):
    for d in range(1,n+1):
      formula.append([encode(n,u,i,j,d,1) for j in range(1,n+1)]) # clause consisting of all columns

# 4. every number appears atleast once in each grid/block (uniqueness)
# every sudoku can be viewed as a grid of kxk within each grid of kxk
for u in range (0,2):
  for g_out in range(1,n+1):
    for d in range(1,n+1):
      formula.append([encode(n,u,( ((g_out -1)//k)*k + (g_in -1)//k +1 ) , ( ((g_out -1)%k)*k + (g_in -1)%k +1 ) ,d,1) for g_in in range(1,n+1)]) # clause consisting of all grid-cells

# 5. every cell of sudoku must have all different entries 
for i in range(1,n+1):
    for j in range(1,n+1):
      formula.extend([[encode(n,0,i,j,d,-1),encode(n,1,i,j,d,-1)] for d in range(1,n+1)]) # encoding NAND operation for inequality between 2 variables as inequality implies odd parity

# Taking assumptions
# here we are supplying the solver with what all information that we can conclude directly, thereby reducing its work.

given=[]

for i in range(1,2*n+1):
  for j in range(1,n+1):
    if(sud[i-1,j-1]!=0):
      sudoku=(i-1)//n
      row=(i-1)%n +1
      col=j
      dig=sud[i-1,j-1]

      # directly coding the results
      given.append(int(encode(n,sudoku,row,col,dig,1)))
      
      # #remove corresponding of the same row,col
      # given.extend([int(encode(n,sudoku,row,col,d,-1)) for d in range(1,n+1) if d!=dig])

      # #remove corresponding of the same row,dig,
      # given.extend([int(encode(n,sudoku,row,c,dig,-1)) for c in range(1,n+1) if c!=col])

      # #remove corresponding of the same col,dig
      # given.extend([int(encode(n,sudoku,r,col,dig,-1)) for r in range(1,n+1) if r!=row])

      # #remove corresponding of the same block
      # br=row - (row-1)%k
      # bc=col - (col-1)%k
      # given.extend([int(encode(n,sudoku,br+ind//k,bc + ind%k,dig,-1)) for ind in range(0,n) if ind!=(((row-1)%k)*k + ((col-1)%k))])

#Solving
with Minisat22(bootstrap_with=formula.clauses) as l:
    if l.solve(assumptions=given) == True:
    
      sud=np.zeros(shape=[2*n,n],dtype=np.int8)
         
      for i in l.get_model():
        if(i>0):
          d=decode(n,i)
          if(d[1]==0):
            sud[d[2]-1,d[3]-1]=int(d[4])
          elif(d[1]==1):
            sud[n+d[2]-1,d[3]-1]=int(d[4])
      
      df = pd.DataFrame(sud)
      df.to_csv(filename+'_output.csv')
      print("Output generated in the file named '", filename, "_output.csv'.")
    else:
          print("None")
          
          

l.delete()

print("Time :" + str(datetime.datetime.now() - begin_time))
