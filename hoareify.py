import ast, astunparse, codegen, unparse, copy, re
from astmonkey import transformers
from logic_statements import Int, Solver

# A object containing the type of statement and the statement itself
class HoareStmt():
    typ = ""
    value = []

    def __init__(self, typ, value):
        self.typ = typ
        self.value = value

    def __repr__(self):
        return str(self.typ + ":" + str(self.value))

# Find the different paths through the program, catagorize each statement by type,
# extract the information for the hoare logic and store them as Hoare Statements. 
class Paths(ast.NodeVisitor):
    paths = [[]] # Contains all the unique paths through each function
    function_name = "" 
    toverify = []
    precondition = ""
    postcondition = ""

    # inits the functions and sets the list of functions that need to be verified
    def __init__(self, toverify):
        self.toverify = toverify

    def visit_FunctionDef(self, node):
        self.paths = [[]]
        self.function_name = node.name

        # Find the precondition and init the corrosponding HoareStmt
        self.precondition, self.postcondition = self.find_conds(node, self.function_name)

        # Append the precondition to the current path and keep parsing
        self.paths[-1].append(self.precondition)
        self.generic_visit(node) 
        self.paths[-1].append(self.postcondition)
        return self.paths

    def visit_For(self, node):
        inv_node = [n for n in node.body if (isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and (n.value.func.id == 'invariant'))]

        pre_inv = HoareStmt("STMT", str(node.target.id +  ' == ' + str(eval(codegen.to_source(node.iter))[0])))
        post_inv = HoareStmt("STMT", str(node.target.id + '==' + str(codegen.to_source(node.iter.args[0]))))
        inv = HoareStmt('STMT', [codegen.to_source(a) for a in inv_node[0].value.args][0])
        invplus = HoareStmt("ASSIGNMENT", [node.target.id, node.target.id + '+ 1'])

        self.paths[-1].append(pre_inv)
        self.paths[-1].append(inv)
        self.paths.append([])
        
        self.paths[-1].append(inv)
        self.generic_visit(node)
        self.paths[-1].append(invplus)
        self.paths[-1].append(inv)
        self.paths.append([])

        self.paths[-1].append(inv)
        self.paths[-1].append(post_inv)
    
    def visit_While(self, node):
        inv_node = [n for n in node.body if (isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and (n.value.func.id == 'invariant'))]

        inv = HoareStmt('STMT', [codegen.to_source(a) for a in inv_node[0].value.args][0])
        post_inv = HoareStmt("STMT", str("Not" + codegen.to_source(node.test)))

        self.paths[-1].append(inv)
        self.paths.append([])

        self.paths[-1].append(inv)
        self.generic_visit(node)
        self.paths[-1].append(inv)
        self.paths.append([])

        self.paths[-1].append(inv)
        self.paths[-1].append(post_inv)

    def visit_Assign(self, node):
        print codegen.to_source(node.value)
        if isinstance(node.targets[0], ast.Name):
            assign = HoareStmt("ASSIGNMENT", [node.targets[0].id, codegen.to_source(node.value)])
            if isinstance(node.value, ast.Call):
                assign = HoareStmt("ASSIGNMENT", [node.targets[0].id, "ret" + str(codegen.to_source(node.value.func))])
            self.generic_visit(node)
            self.paths[-1].append(assign)
    
    def visit_Return(self, node):
        print ast.dump(node)
        print '(' + str(codegen.to_source(node.value)) + ')'
        ast.dump(node)
        a = HoareStmt("ASSIGNMENT",['ret' + self.function_name, codegen.to_source(node.value)])# [node.targets[0].id, codegen.to_source(node.value)])
        self.paths[-1].append(a)
        self.paths[-1].append(self.postcondition)
    
    def visit_Call(self, node):
        a = []
        if hasattr(node.func, 'id'):
            a = [f for f in  self.toverify if node.func.id == f.name]
        if len(a) > 0:
            fprecond, fpostcond = self.find_conds(a[0], a[0].name)
            self.paths[-1].append(fprecond)
            self.paths.append([])
            self.paths[-1].append(fpostcond)
            self.generic_visit(node)
        else: 
            self.generic_visit(node)
    
    def visit_If(self, node):
        pattern = re.compile(r"and|or")
        temp = pattern.split(codegen.to_source(node.test))
        ifs = HoareStmt("IFSTART", self.apply_and(temp))
        print "IFF", ifs
        ife = HoareStmt("IFEND", 7)
        self.paths[-1].append(ifs)
        self.generic_visit(node)
        self.paths[-1].append(ife)

    def find_conds(self, node, fname):
        pre = [d for d in node.decorator_list if d.func.id == 'precondition']
        post = [d for d in node.decorator_list if d.func.id == 'postcondition']
        temp = [codegen.to_source(a) for a in post[0].args]
        temp = [str(j).replace("ret", "ret" + fname) for j in temp]

        precond = HoareStmt("STMT", [codegen.to_source(p) for p in pre[0].args][0])
        postcond = HoareStmt("STMT", temp[0])

        return precond, postcond

    def apply_and(self, lst):
        if len(lst) > 1:
            return "(And(" + ','.join(lst) + "))"
        else:
            return "(" + ','.join(lst) + ")"



def if_situation(paths):
    newp = []
    for p in paths:
        ifindex = [p.index(s) for s in p if s.typ == "IFSTART"]
        ifeindex = [p.index(s) for s in p if s.typ == "IFEND"]
        if len(ifindex) > 0:
            p1 = copy.deepcopy(p)

            p[ifindex[0]] = HoareStmt("STMT", p[ifindex[0]].value)
            p1[ifindex[0]] = HoareStmt("STMT", "Not" + str(p[ifindex[0]].value))

            if ifeindex in p:
                del p[ifeindex[0]]
                del p1[ifindex[0]+1:ifeindex[0]+1]

            newp.append(p)
            newp.append(p1)
    if len(newp) > 0:
        return if_situation(newp)
    else: 
        return paths

def returns(path, fname, postcond):
    for p in range(len(path)):
        if path[p].typ == "RETURN":
            path[p] = HoareStmt("ASSIGNMENT", ["ret" + fname, path[p].value[1]])
            path.append(postcond)
    return path


def hoareify(func, toverify):
    hoareify = []
    postconditions = []

    post = [d for d in func.decorator_list if d.func.id == 'postcondition']
    temp = [codegen.to_source(a) for a in post[0].args]
    temp = [str(j).replace("ret", "ret" + func.name) for j in temp]

    postcond = HoareStmt("STMT", temp[0])
    postconditions.append(postcond)

    def walk(node):
        if not hasattr(node, 'body'):
            return
        for p in node.body:
            walk(p)

    p = Paths(toverify).visit(func)
    print "\nPATHS:\n", p
    hoareify = p

    for i in range(len(hoareify)):
        hoareify[i:i] = if_situation([hoareify[i]])
        del hoareify[i]
        
    for i in range(len(hoareify)):
        if hoareify[i][-1] == hoareify[i][-2]:
            del hoareify[i][-1]

        #for i in p:
        #    print i

    return hoareify
