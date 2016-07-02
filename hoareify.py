import ast, astunparse, codegen, unparse, copy
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
        self.precondition, self.postcondition = self.find_conds(node)

        # Append the precondition to the current path and keep parsing
        self.paths[-1].append(self.precondition)
        self.generic_visit(node) 
        self.paths[-1].append(self.postcondition)
        return self.paths

    def visit_For(self, node):
        inv_node = [n for n in node.body if (isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and (n.value.func.id == 'invariant'))]

        pre_inv = HoareStmt("STMT", str(node.target.id +  ' = ' + str(eval(codegen.to_source(node.iter))[0])))
        post_inv = HoareStmt("STMT", str(node.target.id + '=' + str(codegen.to_source(node.iter.args[0]))))
        inv = HoareStmt('STMT',  [codegen.to_source(a) for a in inv_node[0].value.args])
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

        inv = HoareStmt('STMT',  [codegen.to_source(a) for a in inv_node[0].value.args])
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
        if isinstance(node.targets[0], ast.Name):
            assign = HoareStmt("ASSIGNMENT", [node.targets[0].id, codegen.to_source(node.value)])
            self.generic_visit(node)
            self.paths[-1].append(assign)
    
    def visit_Return(self, node):
        ast.dump(node)
        a = HoareStmt("RETURN",['ret' + self.function_name, node.value.id])# [node.targets[0].id, codegen.to_source(node.value)])
        self.paths[-1].append(a)
        self.paths.append(self.postcondition)
    
    def visit_Call(self, node):
        a = [f for f in  self.toverify if node.func.id == f.name]
        if len(a) > 0:
            fprecond, fpostcond = self.find_conds(a[0])
            self.paths[-1].append(fprecond)
            self.paths.append([])
            self.paths[-1].append(fpostcond)
            self.generic_visit(node)
        else: 
            self.generic_visit(node)
    
    def visit_If(self, node):
        ifs = HoareStmt("IFSTART", codegen.to_source(node.test))
        ife = HoareStmt("IFEND", 7)
        self.paths[-1].append(ifs)
        self.generic_visit(node)
        self.paths[-1].append(ife)

    def find_conds(self, node):
        pre = [d for d in node.decorator_list if d.func.id == 'precondition']
        post = [d for d in node.decorator_list if d.func.id == 'postcondition']

        precond = HoareStmt("STMT",  [codegen.to_source(p) for p in pre[0].args])
        postcond = HoareStmt("STMT", [codegen.to_source(p) for p in post[0].args])

        return precond, postcond


def if_situation(paths):
    newp = []
    for p in paths:
        print p
        ifindex = [p.index(s) for s in p if s.typ == "IFSTART"]
        ifeindex = [p.index(s) for s in p if s.typ == "IFEND"]
        if len(ifindex) > 0:
            p1 = copy.deepcopy(p)

            p[ifindex[0]] = HoareStmt("STMT", p[ifindex[0]].value)
            p1[ifindex[0]] = HoareStmt("STMT", "Not" + str(p[ifindex[0]].value))

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
            path[p] = HoareStmt("RETURN", ["ret" + fname, path[p].value[1]])
            path.append(postcond)
    return path


def hoareify(toverify):
    hoareify = []
    postconditions = []

    for i in range(len(toverify)):
        post = [d for d in toverify[i].decorator_list if d.func.id == 'postcondition']
        temp =  [codegen.to_source(a) for a in post[0].args]

        postcond = HoareStmt("STMT", temp)
        postconditions.append(postcond)

        def walk(node):
            if not hasattr(node, 'body'):
                return
            for p in node.body:
                walk(p)

        p = Paths(toverify).visit(toverify[i])
        hoareify.append(p)

    for j in range(len(hoareify)):
        print toverify[j].name
        p = hoareify[j]
        for i in range(len(p)):
            p[i:i] = if_situation([p[i]])
            del p[i]
            
#        for i in range(len(p)):
 #           p[i] = returns(p[i], toverify[j].name, postconditions[j])
        
        for i in p:
            print i

