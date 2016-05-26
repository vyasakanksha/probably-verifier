from tokenize import tokenize
import sys, nltk

pre = 0 
post = 0
func = 0
wloop = 0
ploop = 0
ifitr = 0

if len(sys.argv) < 2:
   sys.stderr.write('You need an input file\n')
   exit(1)

with open(sys.argv[1]) as fl:
   f = fl.read()

print(type(f))
f = f.splitlines()

f_new = []

for i in f:
   if "precondition" in i and '#' in i:
      f_new.append(i)
      pre = pre + 1
   if "postcondition" in i and '#' in i:
      f_new.append(i)
      func = func + 1
   if "def " in i and '#' not in i:
      f_new.append(i)
      post = post + 1

if pre != func or post != func:
   print("The number of precondtions and post conditions don't match the number of functions")
   exit(0)

for i in f:
   if "while " in i and '#' not in i:
      f_new.append(i)
      wloop = wloop + 1
   
   if "if " in i and '#' not in i:
      f_new.append(i)
      ifitr = wloop + 1
   
   if "for " in i and '#' not in i:
      f_new.append(i)
      ploop = wloop + 1
   
   if "midcondition" in i and '#' in i:
      f_new.append(i)
      wloop = wloop + 1

print(f_new)

# NEXT STEP -- LINE NUMBERS + FUNCTIONS
