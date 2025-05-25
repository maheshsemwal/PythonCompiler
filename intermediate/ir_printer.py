"""
IR Printer

This module provides functionality to print the intermediate representation
in a human-readable format.
"""

from intermediate.ir_nodes import *

class IRPrinter:
    def __init__(self):
        self.indent_level = 0
        self.indent_str = "    "

    def indent(self):
        """Increase indentation level"""
        self.indent_level += 1

    def dedent(self):
        """Decrease indentation level"""
        self.indent_level -= 1

    def get_indent(self):
        """Get current indentation string"""
        return self.indent_str * self.indent_level

    def print_node(self, node):
        """Print an IR node"""
        method_name = f'print_{node.__class__.__name__}'
        printer = getattr(self, method_name, self.generic_print)
        return printer(node)

    def generic_print(self, node):
        """Default printer method"""
        print(f"{self.get_indent()}{node}")

    def print_IRProgram(self, node):
        """Print program node"""
        for func in node.functions:
            self.print_node(func)
            print()  # Add blank line between functions

    def print_IRFunction(self, node):
        """Print function node"""
        print(f"Function {node.name}({', '.join(node.params)}):")
        self.indent()
        for instr in node.body:
            self.print_node(instr)
        self.dedent()

    def print_IRBlock(self, node):
        """Print block node"""
        print(f"{self.get_indent()}Block:")
        self.indent()
        for instr in node.instructions:
            self.print_node(instr)
        self.dedent()

    def print_IRBinaryOp(self, node):
        """Print binary operation"""
        print(f"{self.get_indent()}{node.result} = {node.left} {node.op} {node.right}")

    def print_IRUnaryOp(self, node):
        """Print unary operation"""
        print(f"{self.get_indent()}{node.result} = {node.op}{node.operand}")

    def print_IRLoad(self, node):
        """Print load operation"""
        print(f"{self.get_indent()}{node.target} = load {node.value}")

    def print_IRStore(self, node):
        """Print store operation"""
        print(f"{self.get_indent()}store {node.source} -> {node.target}")

    def print_IRCall(self, node):
        """Print function call"""
        args_str = ", ".join(str(arg) for arg in node.args)
        print(f"{self.get_indent()}{node.result} = call {node.func}({args_str})")

    def print_IRReturn(self, node):
        """Print return statement"""
        if node.value:
            print(f"{self.get_indent()}return {node.value}")
        else:
            print(f"{self.get_indent()}return")

    def print_IRJump(self, node):
        """Print jump instruction"""
        print(f"{self.get_indent()}jump {node.target}")

    def print_IRCondJump(self, node):
        """Print conditional jump"""
        print(f"{self.get_indent()}if {node.condition} jump {node.true_target} else {node.false_target}")

    def print_IRConstant(self, node):
        """Print constant value"""
        if isinstance(node.value, str):
            return f'"{node.value}"'
        return str(node.value)

    def print_IRVariable(self, node):
        """Print variable reference"""
        return node.name

    def print_IRLabel(self, node):
        print(f"{self.get_indent()}{node.name}:") 