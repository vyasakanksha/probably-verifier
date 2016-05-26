import sys

if len(sys.argv) < 2:
   sys.stderr.write('You need an input file\n')
   exit(1)

with open(sys.argv[1]) as f:
    code = f.readlines()

fn_count = 0
fn = []

for i in range(len(code)):
   if 'def ' in code[i]:
      fn_count = fn_count + 1
   print code[i].strip()

for c in range(fn_count):
   fn.append(c)
   fn[c] = []

f = False
c = 0
for i in range(len(code)):
   if 'precondition: ' in code[i]:
      f = True   
   if 'postcondition: ' not in code[i] and f:
      fn[c].append(code[i])
   elif 'postcondition: ' in code[i]:
      fn[c].append(code[i])
      f = False
      c = c+1


for f in fn:
   for i in range(len(f)):
      print f[i]
      temp = f[i].strip().split()
      if temp and temp[0].strip() == "precondition:":
         f[i] = [f[i], 'PRE']
      if temp and temp[0].strip() == "postcondition:":
         f[i] = [f[i], 'POST']
      if temp and temp[0].strip() == "if ":
         f[i] = [f[i], 'IF']
      if temp and temp[0].strip() == "else ":
         f[i] = [f[i], 'ELSE']
      if temp and temp[0].strip() == "while ":
         f[i] = [f[i], 'WHILE']
      if temp and temp[0].strip() == "for ":
         f[i] = [f[i], 'FOR']

print fn_count
print fn
