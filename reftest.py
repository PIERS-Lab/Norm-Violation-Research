# classes are mutable, which means that they can be changed after init
'''everything is an obj in python, so immutable things mereley just point to new when reassigned, so rather than a var being a container, 
it is just a name for a pre-existing obj, thus why basic data types like integers can't be passed by ref (1, 2, 3, etc are all their own individual objects)'''\

'''Sussinctly, variables in python are not their own spaces in memory like other languages, they merely point to pre-existing objects
in the immutable case, or newly made ones in the mutable case ''' 
class foo:
    def __init__(self, num):
        self.x = num
    def set_num(self,num):
        self.x = num

def change_foo(fooObj):
    fooObj.set_num(4)
    print("funct foo: ", fooObj.x)
def assign_foo(fooObj):
    fooObj = foo(4)
    print("funct foo: ", fooObj.x)

orig = foo(8)
print("starting val: ", (orig.x))
print("changing via assign")
'''When python performs a funct call, the function makes a copy of the refrence
because variables are just names here, reassignment has no affect on the object we passed
we just told the function to point it's variable at a new point in memory rather than overwrite the one it has'''
assign_foo(orig)
print("after call: ", orig.x)
print("changing via setter")
'''What makes classes mutable is their setters, these members function act on the class itself, instead of poinitng somewhere else 
like assignment does. Thus we actually change orig by calling it's setter as we are efectvely passing by refrence'''
change_foo(orig)
print("after call: ", orig.x)
cool = True

