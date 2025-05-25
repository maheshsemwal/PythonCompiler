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
        main_body = []
        
        # Process all statements
        for stmt in node.statements:
            if isinstance(stmt, FunctionDefNode):
                result = self.visit(stmt)
                if isinstance(result, list):
                    functions.extend(result)
                else:
                    functions.append(result)
            else:
                # Add non-function statements to main body
                ir = self.visit(stmt)
                if isinstance(ir, list):
                    main_body.extend(ir)
                else:
                    main_body.append(ir)
        
        # Create main function if there are any statements
        if main_body:
            main_function = IRFunction("main", [], main_body)
            functions.append(main_function)
        
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
        
        # Handle nested binary operations
        steps = []
        
        # Process left operand if it's a binary operation
        if isinstance(left, list):
            steps.extend(left)
            left = left[-1].result
        elif isinstance(left, IRBinaryOp):
            steps.append(left)
            left = left.result
        
        # Process right operand if it's a binary operation
        if isinstance(right, list):
            steps.extend(right)
            right = right[-1].result
        elif isinstance(right, IRBinaryOp):
            steps.append(right)
            right = right.result
        
        # Add the current operation
        steps.append(IRBinaryOp(node.op, left, right, result))
        return steps

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
        
        # Handle complex expressions
        if isinstance(value, list):
            steps = value
            steps.append(IRStore(steps[-1].result, target.name))
            return steps
        
        return IRStore(value, target.name)

    def visit_FunctionCallNode(self, node):
        """Convert function call to IR"""
        func = self.visit(node.callable)
        args = []
        
        # Process arguments
        for arg in node.arguments:
            arg_ir = self.visit(arg)
            if isinstance(arg_ir, list):
                args.extend(arg_ir)
                args.append(arg_ir[-1].result)
            else:
                args.append(arg_ir)
        
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
        if isinstance(condition, list):
            steps = condition
            cond_jump = IRCondJump(steps[-1].result, true_label, false_label)
        else:
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
        
        # Combine all parts with labels
        result = []
        if isinstance(condition, list):
            result.extend(condition)
        result.append(cond_jump)
        result.append(IRLabel(true_label))
        result.extend(true_block)
        result.append(IRJump(end_label))
        result.append(IRLabel(false_label))
        result.extend(false_block)
        result.append(IRLabel(end_label))
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
        
        # Combine all parts with labels
        result = [
            IRLabel(start_label),
        ]
        if isinstance(condition, list):
            result.extend(condition)
            cond = condition[-1].result
        else:
            cond = condition
        result.append(IRCondJump(cond, body_label, end_label))
        result.append(IRLabel(body_label))
        result.extend(body_ir)
        result.append(IRJump(start_label))
        result.append(IRLabel(end_label))
        return result

    def visit_ReturnNode(self, node):
        """Convert return statement to IR"""
        if node.value:
            value = self.visit(node.value)
            if isinstance(value, list):
                steps = value
                steps.append(IRReturn(steps[-1].result))
                return steps
            return IRReturn(value)
        return IRReturn()

    def visit_AttributeNode(self, node):
        """Convert attribute access to IR"""
        obj = self.visit(node.value)
        return IRVariable(f"{obj.name}.{node.attr}") 