"""
Intermediate Representation (IR) Nodes

This module defines the classes for representing intermediate code.
The IR is a simplified representation of the program that's easier to optimize
and translate to target code.
"""

class IRNode:
    """Base class for all IR nodes"""
    def __init__(self):
        self.next = None  # Link to next instruction for control flow

    def __str__(self):
        return self.__class__.__name__

class IRProgram(IRNode):
    """Represents the entire program"""
    def __init__(self, functions):
        super().__init__()
        self.functions = functions  # List of IRFunction nodes

    def __str__(self):
        return "\n\n".join(str(func) for func in self.functions)

class IRFunction(IRNode):
    """Represents a function definition"""
    def __init__(self, name, params, body):
        super().__init__()
        self.name = name
        self.params = params
        self.body = body
        self.locals = set()  # Set of local variables

    def __str__(self):
        params_str = ", ".join(self.params)
        body_str = "\n".join(f"    {str(instr)}" for instr in self.body)
        return f"Function {self.name}({params_str}):\n{body_str}"

class IRBlock(IRNode):
    """Represents a block of instructions"""
    def __init__(self, instructions):
        super().__init__()
        self.instructions = instructions

    def __str__(self):
        return "\n".join(str(instr) for instr in self.instructions)

class IRBinaryOp(IRNode):
    """Represents a binary operation"""
    def __init__(self, op, left, right, result):
        super().__init__()
        self.op = op
        self.left = left
        self.right = right
        self.result = result

    def __str__(self):
        return f"{self.result} = {self.left} {self.op} {self.right}"

class IRUnaryOp(IRNode):
    """Represents a unary operation"""
    def __init__(self, op, operand, result):
        super().__init__()
        self.op = op
        self.operand = operand
        self.result = result

    def __str__(self):
        return f"{self.result} = {self.op}{self.operand}"

class IRLoad(IRNode):
    """Load a value into a variable"""
    def __init__(self, value, target):
        super().__init__()
        self.value = value
        self.target = target

    def __str__(self):
        return f"{self.target} = load {self.value}"

class IRStore(IRNode):
    """Store a value into a variable"""
    def __init__(self, source, target):
        super().__init__()
        self.source = source
        self.target = target

    def __str__(self):
        return f"store {self.source} -> {self.target}"

class IRCall(IRNode):
    """Function call"""
    def __init__(self, func, args, result):
        super().__init__()
        self.func = func
        self.args = args
        self.result = result

    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self.args)
        return f"{self.result} = call {self.func}({args_str})"

class IRReturn(IRNode):
    """Return statement"""
    def __init__(self, value=None):
        super().__init__()
        self.value = value

    def __str__(self):
        if self.value:
            return f"return {self.value}"
        return "return"

class IRJump(IRNode):
    """Unconditional jump"""
    def __init__(self, target):
        super().__init__()
        self.target = target

    def __str__(self):
        return f"jump {self.target}"

class IRCondJump(IRNode):
    """Conditional jump"""
    def __init__(self, condition, true_target, false_target):
        super().__init__()
        self.condition = condition
        self.true_target = true_target
        self.false_target = false_target

    def __str__(self):
        return f"if {self.condition} jump {self.true_target} else {self.false_target}"

class IRConstant(IRNode):
    """Constant value"""
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __str__(self):
        if isinstance(self.value, str):
            return f'"{self.value}"'
        return str(self.value)

class IRVariable(IRNode):
    """Variable reference"""
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __str__(self):
        return self.name

class IRMethodCall(IRNode):
    """Method call on an object"""
    def __init__(self, obj, method, args, result):
        super().__init__()
        self.obj = obj
        self.method = method
        self.args = args
        self.result = result

    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self.args)
        return f"{self.result} = call {self.obj}.{self.method}({args_str})"

class IRConstructorCall(IRNode):
    """Constructor call for class instantiation"""
    def __init__(self, class_name, args, result):
        super().__init__()
        self.class_name = class_name
        self.args = args
        self.result = result

    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self.args)
        return f"{self.result} = new {self.class_name}({args_str})" 