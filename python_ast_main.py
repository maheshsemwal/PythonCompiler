#!/usr/bin/env python3
"""
Python AST Generator 

This module provides a command-line interface for parsing Python code
and generating an Abstract Syntax Tree (AST) and intermediate representation (IR).
"""

import sys
import argparse
from lexer.lexer import Lexer
from parser.parser import Parser
from intermediate.ir_generator import IRGenerator
from intermediate.ir_printer import IRPrinter

def read_file(filename):
    """Read content from a file."""
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

def main():
    # Parse command line arguments
    arg_parser = argparse.ArgumentParser(
        description='Generate AST and IR for Python code.'
    )
    arg_parser.add_argument(
        'input_file', 
        help='Path to the Python source file'
    )
    arg_parser.add_argument(
        '--show-ir',
        action='store_true',
        help='Show intermediate representation'
    )
    args = arg_parser.parse_args()

    try:
        # Read source code from input file
        source = read_file(args.input_file)
        
        # Create lexer and tokenize the source
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Create parser and parse tokens into AST
        parser = Parser(tokens)
        ast_nodes = parser.parse()
        
        # Print the AST
        print(f"Abstract Syntax Tree for {args.input_file}:")
        print("-" * 50)
        for node in ast_nodes:
            node.print_node()
        
        # Generate and print IR if requested
        if args.show_ir:
            print("\nIntermediate Representation:")
            print("-" * 50)
            ir_generator = IRGenerator()
            ir_printer = IRPrinter()
            
            # Generate IR for each AST node
            for node in ast_nodes:
                ir = ir_generator.visit(node)
                ir_printer.print_node(ir)
        
    except FileNotFoundError:
        print(f"Error: Could not open file {args.input_file}")
        return 1
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())