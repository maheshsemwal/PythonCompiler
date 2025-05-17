class ASTNode:
    """Base class for all AST nodes"""
    def print_node(self, indent=0):
        """Return the string representation of the node with indentation"""
        raise NotImplementedError("Each AST node must implement print_node")

    def __str__(self):
        """Convert the node to a string representation"""
        return self.print_node(0)


class IntLiteralNode(ASTNode):
    """Node for integer literals"""
    def __init__(self, value):
        self.value = value
    
    def print_node(self, indent=0):
        return ' ' * indent + f"IntLiteral({self.value})"


class FloatLiteralNode(ASTNode):
    """Node for float literals"""
    def __init__(self, value):
        self.value = value
    
    def print_node(self, indent=0):
        return ' ' * indent + f"FloatLiteral({self.value})"


class StringLiteralNode(ASTNode):
    """Node for string literals"""
    def __init__(self, value, is_f_string=False):
        self.value = value
        self.is_f_string = is_f_string
    
    def print_node(self, indent=0):
        node_type = "FString" if self.is_f_string else "StringLiteral"
        return ' ' * indent + f'{node_type}("{self.value}")'


class BoolLiteralNode(ASTNode):
    """Node for boolean literals"""
    def __init__(self, value):
        self.value = value
    
    def print_node(self, indent=0):
        return ' ' * indent + f"BoolLiteral({str(self.value)})"


class NoneLiteralNode(ASTNode):
    """Node for None literal"""
    def print_node(self, indent=0):
        return ' ' * indent + "None"


class IdentifierNode(ASTNode):
    """Node for identifiers"""
    def __init__(self, name):
        self.name = name
    
    def print_node(self, indent=0):
        return ' ' * indent + f"Identifier({self.name})"


class BinaryOpNode(ASTNode):
    """Node for binary operations"""
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right
    
    def print_node(self, indent=0):
        return ' ' * indent + f"BinaryOp({self.op})"


class AssignmentNode(ASTNode):
    """Node for assignment statements"""
    def __init__(self, target, value):
        self.target = target
        self.value = value
    
    def print_node(self, indent=0):
        lines = []
        lines.append(' ' * indent + "Assignment")
        lines.append(' ' * (indent + 2) + "Target:")
        lines.append(self.target.print_node(indent + 4))
        lines.append(' ' * (indent + 2) + "Value:")
        lines.append(self.value.print_node(indent + 4))
        return '\n'.join(lines)


class FunctionCallNode(ASTNode):
    """Node for function calls"""
    def __init__(self, callable_obj, arguments=None, keyword_args=None):
        self.callable = callable_obj
        self.arguments = arguments or []
        self.keyword_args = keyword_args or {}
    
    def print_node(self, indent=0):
        lines = []
        lines.append(' ' * indent + "FunctionCall")
        lines.append(' ' * (indent + 2) + "Callable:")
        lines.append(self.callable.print_node(indent + 4))
        
        if self.arguments:
            lines.append(' ' * (indent + 2) + "Arguments:")
            for arg in self.arguments:
                lines.append(arg.print_node(indent + 4))
        
        if self.keyword_args:
            lines.append(' ' * (indent + 2) + "Keyword Arguments:")
            for key, value in self.keyword_args.items():
                lines.append(' ' * (indent + 4) + f"{key}:")
                lines.append(value.print_node(indent + 6))
        
        return '\n'.join(lines)


class ParameterNode(ASTNode):
    """Node for function parameters"""
    def __init__(self, name, default_value=None, is_keyword_only=False):
        self.name = name
        self.default_value = default_value
        self.is_keyword_only = is_keyword_only
    
    def print_node(self, indent=0):
        param_info = self.name
        if self.is_keyword_only:
            param_info += ", keyword-only"
        lines = [' ' * indent + f"Parameter({param_info})"]
        
        if self.default_value:
            lines.append(' ' * (indent + 2) + "Default Value:")
            lines.append(self.default_value.print_node(indent + 4))
        
        return '\n'.join(lines)


class FunctionDefNode(ASTNode):
    """Node for function definitions"""
    def __init__(self, name, parameters=None, body=None):
        self.name = name
        self.parameters = parameters or []
        self.body = body or []
    
    def print_node(self, indent=0):
        lines = []
        lines.append(' ' * indent + f"FunctionDef({self.name})")
        
        lines.append(' ' * (indent + 2) + "Parameters:")
        for param in self.parameters:
            lines.append(param.print_node(indent + 4))
        
        lines.append(' ' * (indent + 2) + "Body:")
        for stmt in self.body:
            lines.append(stmt.print_node(indent + 4))
        
        return '\n'.join(lines)


class ClassDefNode(ASTNode):
    """Node for class definitions"""
    def __init__(self, name, bases=None, body=None):
        self.name = name
        self.bases = bases or []
        self.body = body or []
    
    def print_node(self, indent=0):
        lines = []
        lines.append(' ' * indent + f"ClassDef({self.name})")
        
        if self.bases:
            lines.append(' ' * (indent + 2) + "Bases:")
            for base in self.bases:
                lines.append(base.print_node(indent + 4))
        
        lines.append(' ' * (indent + 2) + "Body:")
        for stmt in self.body:
            lines.append(stmt.print_node(indent + 4))
        
        return '\n'.join(lines)


class ReturnNode(ASTNode):
    """Node for return statements"""
    def __init__(self, value=None):
        self.value = value
    
    def print_node(self, indent=0):
        lines = [' ' * indent + "Return"]
        if self.value:
            lines.append(self.value.print_node(indent + 2))
        return '\n'.join(lines)


class ImportNode(ASTNode):
    """Node for import statements"""
    def __init__(self, module, alias=""):
        self.module = module
        self.alias = alias
    
    def print_node(self, indent=0):
        import_info = self.module
        if self.alias:
            import_info += f" as {self.alias}"
        return ' ' * indent + f"Import({import_info})"


class FromImportNode(ASTNode):
    """Node for from ... import statements"""
    def __init__(self, module, imports=None):
        self.module = module
        self.imports = imports or []  # List of (name, alias) tuples
    
    def print_node(self, indent=0):
        return ' ' * indent + f"FromImport({self.module})"


class IfNode(ASTNode):
    """Node for if statements"""
    def __init__(self, condition, then_body=None, else_body=None):
        self.condition = condition
        self.then_body = then_body or []
        self.else_body = else_body or []
    
    def print_node(self, indent=0):
        return ' ' * indent + "If"


class WhileNode(ASTNode):
    """Node for while loops"""
    def __init__(self, condition, body=None):
        self.condition = condition
        self.body = body or []
    
    def print_node(self, indent=0):
        return ' ' * indent + "While"


class ForNode(ASTNode):
    """Node for for loops"""
    def __init__(self, target, iterable, body=None):
        self.target = target
        self.iterable = iterable
        self.body = body or []
    
    def print_node(self, indent=0):
        return ' ' * indent + "For"


class AttributeNode(ASTNode):
    """Node for attribute access (e.g., obj.attr)"""
    def __init__(self, value, attr):
        self.value = value
        self.attr = attr
    
    def print_node(self, indent=0):
        lines = []
        lines.append(' ' * indent + f"Attribute({self.attr})")
        lines.append(' ' * (indent + 2) + "Value:")
        lines.append(self.value.print_node(indent + 4))
        return '\n'.join(lines)


class ListNode(ASTNode):
    """Node for list literals"""
    def __init__(self, elements=None):
        self.elements = elements or []
    
    def print_node(self, indent=0):
        return ' ' * indent + "List"


class DictNode(ASTNode):
    """Node for dictionary literals"""
    def __init__(self, items=None):
        self.items = items or []  # List of (key, value) tuples
    
    def print_node(self, indent=0):
        return ' ' * indent + "Dict"


class SubscriptNode(ASTNode):
    """Node for subscript access (e.g., list[index])"""
    def __init__(self, value, index):
        self.value = value
        self.index = index
    
    def print_node(self, indent=0):
        return ' ' * indent + "Subscript"


class PassNode(ASTNode):
    """Node for pass statements"""
    def print_node(self, indent=0):
        return ' ' * indent + "Pass"


class BreakNode(ASTNode):
    """Node for break statements"""
    def print_node(self, indent=0):
        return ' ' * indent + "Break"


class ContinueNode(ASTNode):
    """Node for continue statements"""
    def print_node(self, indent=0):
        return ' ' * indent + "Continue"