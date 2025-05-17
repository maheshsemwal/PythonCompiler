"""
IR Generator

This module converts AST nodes into intermediate representation (IR) nodes.
"""

from parser.ast_nodes import *
from intermediate.ir_nodes import *

class IRGenerator:
    def __init__(self):
        self.current_function = None
        self.temp_counter = 0
        self.label_counter = 0
        self.current_class = None

    def generate_temp(self):
        """Generate a unique temporary variable name"""
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp

    def generate_label(self):
        """Generate a unique label name"""
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label

    def visit(self, node):
        """Visit an AST node and generate corresponding IR"""
        if node is None:
            return None
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Default visitor method"""
        raise NotImplementedError(f"No visitor method for {node.__class__.__name__}")

    def visit_ProgramNode(self, node):
        """Convert program node to IR"""
        functions = []
        for stmt in node.statements:
            if isinstance(stmt, (FunctionDefNode, ClassDefNode)):
                result = self.visit(stmt)
                if isinstance(result, list):
                    functions.extend(result)
                else:
                    functions.append(result)
        return IRProgram(functions)

    def visit_FunctionDefNode(self, node):
        """Convert function definition to IR"""
        prev_function = self.current_function
        self.current_function = node.name
        params = [param.name for param in node.parameters]
        body = []
        
        # Generate IR for function body
        for stmt in node.body:
            ir = self.visit(stmt)
            if isinstance(ir, list):
                body.extend(ir)
            else:
                body.append(ir)
        
        self.current_function = prev_function
        return IRFunction(node.name, params, body)

    def visit_ClassDefNode(self, node):
        """Convert class definition to IR"""
        prev_class = self.current_class
        self.current_class = node.name
        functions = []
        
        # Find and process __init__ method
        init_method = None
        for stmt in node.body:
            if isinstance(stmt, FunctionDefNode) and stmt.name == "__init__":
                init_method = stmt
                break
        
        # Process all methods
        for stmt in node.body:
            if isinstance(stmt, FunctionDefNode):
                # Add 'self' as first parameter for methods
                stmt.parameters.insert(0, ParameterNode('self'))
                functions.append(self.visit(stmt))
        
        self.current_class = prev_class
        return functions

    def visit_BinaryOpNode(self, node):
        """Convert binary operation to IR"""
        left = self.visit(node.left)
        right = self.visit(node.right)
        result = self.generate_temp()
        
        return IRBinaryOp(node.op, left, right, result)

    def visit_UnaryOpNode(self, node):
        """Convert unary operation to IR"""
        operand = self.visit(node.operand)
        result = self.generate_temp()
        
        return IRUnaryOp(node.op, operand, result)

    def visit_IntLiteralNode(self, node):
        """Convert integer literal to IR"""
        return IRConstant(node.value)

    def visit_FloatLiteralNode(self, node):
        """Convert float literal to IR"""
        return IRConstant(node.value)

    def visit_StringLiteralNode(self, node):
        """Convert string literal to IR"""
        return IRConstant(node.value)

    def visit_BoolLiteralNode(self, node):
        """Convert boolean literal to IR"""
        return IRConstant(node.value)

    def visit_NoneLiteralNode(self, node):
        """Convert None literal to IR"""
        return IRConstant(None)

    def visit_IdentifierNode(self, node):
        """Convert identifier to IR"""
        return IRVariable(node.name)

    def visit_AssignmentNode(self, node):
        """Convert assignment to IR"""
        value = self.visit(node.value)
        target = self.visit(node.target)
        return IRStore(value, target.name)

    def visit_FunctionCallNode(self, node):
        """Convert function call to IR"""
        func = self.visit(node.callable)
        args = [self.visit(arg) for arg in node.arguments]
        result = self.generate_temp()
        
        # Handle method calls
        if isinstance(node.callable, AttributeNode):
            obj = self.visit(node.callable.value)
            return IRMethodCall(obj, node.callable.attr, args, result)
        
        # Handle constructor calls
        if isinstance(node.callable, IdentifierNode) and self.current_class:
            return IRConstructorCall(node.callable.name, args, result)
        
        return IRCall(func.name, args, result)

    def visit_IfNode(self, node):
        """Convert if statement to IR"""
        condition = self.visit(node.condition)
        true_label = self.generate_label()
        false_label = self.generate_label()
        end_label = self.generate_label()
        
        # Generate IR for condition
        cond_jump = IRCondJump(condition, true_label, false_label)
        
        # Generate IR for true branch
        true_block = []
        for stmt in node.then_body:
            ir = self.visit(stmt)
            if isinstance(ir, list):
                true_block.extend(ir)
            else:
                true_block.append(ir)
        
        # Generate IR for false branch
        false_block = []
        for stmt in node.else_body:
            ir = self.visit(stmt)
            if isinstance(ir, list):
                false_block.extend(ir)
            else:
                false_block.append(ir)
        
        # Combine all parts
        result = [cond_jump]
        result.append(IRJump(end_label))  # Jump to end after true block
        result.extend(true_block)
        result.append(IRJump(end_label))
        result.extend(false_block)
        result.append(IRJump(end_label))
        
        return result

    def visit_WhileNode(self, node):
        """Convert while loop to IR"""
        start_label = self.generate_label()
        body_label = self.generate_label()
        end_label = self.generate_label()
        
        condition = self.visit(node.condition)
        
        # Generate IR for loop body
        body_ir = []
        for stmt in node.body:
            ir = self.visit(stmt)
            if isinstance(ir, list):
                body_ir.extend(ir)
            else:
                body_ir.append(ir)
        
        # Combine all parts
        result = [
            IRJump(start_label),
            IRCondJump(condition, body_label, end_label),
            *body_ir,
            IRJump(start_label)
        ]
        
        return result

    def visit_ReturnNode(self, node):
        """Convert return statement to IR"""
        if node.value:
            value = self.visit(node.value)
            return IRReturn(value)
        return IRReturn()

    def visit_AttributeNode(self, node):
        """Convert attribute access to IR"""
        obj = self.visit(node.value)
        return IRVariable(f"{obj.name}.{node.attr}") 