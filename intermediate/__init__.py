"""
Intermediate Representation Package

This package provides functionality for generating and manipulating
intermediate representation (IR) of Python code.
"""

from .ir_nodes import *
from .ir_generator import IRGenerator
from .ir_printer import IRPrinter

__all__ = ['IRGenerator', 'IRPrinter'] 