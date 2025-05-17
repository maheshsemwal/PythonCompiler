"""
Python AST and IR Visualizer Web Application
"""

import os
import sys

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify
from lexer.lexer import Lexer
from parser.parser import Parser
from intermediate.ir_generator import IRGenerator
from intermediate.ir_printer import IRPrinter

app = Flask(__name__)

def process_code(source_code):
    """Process Python code and return AST and IR representations"""
    try:
        # Tokenize
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        # Parse into AST
        parser = Parser(tokens)
        ast_nodes = parser.parse()
        
        # Generate AST representation
        ast_representation = []
        for node in ast_nodes:
            # Convert each node to its string representation
            node_str = str(node)
            # Add proper indentation for better readability
            lines = node_str.split('\n')
            indented_lines = ['  ' + line for line in lines]
            ast_representation.extend(indented_lines)
        
        # Generate IR
        ir_generator = IRGenerator()
        ir_printer = IRPrinter()
        ir_representation = []
        
        for node in ast_nodes:
            ir = ir_generator.visit(node)
            if isinstance(ir, list):
                for item in ir:
                    ir_representation.append(str(item))
            else:
                ir_representation.append(str(ir))
        
        return {
            'success': True,
            'ast': ast_representation,
            'ir': ir_representation
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Process the submitted code"""
    source_code = request.json.get('code', '')
    result = process_code(source_code)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True) 