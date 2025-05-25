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

def ast_node_to_dict(node, node_id=0):
    """Convert AST node to dictionary format for tree visualization"""
    if node is None:
        return None
    
    result = {
        'id': node_id,
        'name': node.__class__.__name__,
        'children': []
    }
    
    # Add node-specific data
    if hasattr(node, 'value'):
        result['value'] = str(node.value)
    elif hasattr(node, 'name'):
        result['value'] = str(node.name)
    elif hasattr(node, 'op'):
        result['value'] = str(node.op)
    
    current_id = node_id + 1
    
    # Handle different node types and their children
    if hasattr(node, 'left') and hasattr(node, 'right'):  # BinaryOpNode
        left_child = ast_node_to_dict(node.left, current_id)
        if left_child:
            result['children'].append(left_child)
            current_id += count_nodes(node.left)
        
        right_child = ast_node_to_dict(node.right, current_id)
        if right_child:
            result['children'].append(right_child)
            current_id += count_nodes(node.right)
    
    elif hasattr(node, 'target') and hasattr(node, 'value'):  # AssignmentNode
        target_child = ast_node_to_dict(node.target, current_id)
        if target_child:
            result['children'].append(target_child)
            current_id += count_nodes(node.target)
        
        value_child = ast_node_to_dict(node.value, current_id)
        if value_child:
            result['children'].append(value_child)
            current_id += count_nodes(node.value)
    
    elif hasattr(node, 'callable') and hasattr(node, 'arguments'):  # FunctionCallNode
        callable_child = ast_node_to_dict(node.callable, current_id)
        if callable_child:
            result['children'].append(callable_child)
            current_id += count_nodes(node.callable)
        
        for arg in node.arguments:
            arg_child = ast_node_to_dict(arg, current_id)
            if arg_child:
                result['children'].append(arg_child)
                current_id += count_nodes(arg)
    
    elif hasattr(node, 'parameters') and hasattr(node, 'body'):  # FunctionDefNode
        for param in node.parameters:
            param_child = ast_node_to_dict(param, current_id)
            if param_child:
                result['children'].append(param_child)
                current_id += count_nodes(param)
        
        for stmt in node.body:
            stmt_child = ast_node_to_dict(stmt, current_id)
            if stmt_child:
                result['children'].append(stmt_child)
                current_id += count_nodes(stmt)
    
    elif hasattr(node, 'body'):  # ClassDefNode or other nodes with body
        for stmt in node.body:
            stmt_child = ast_node_to_dict(stmt, current_id)
            if stmt_child:
                result['children'].append(stmt_child)
                current_id += count_nodes(stmt)
    
    elif hasattr(node, 'value') and node.__class__.__name__ == 'ReturnNode':  # ReturnNode
        if node.value:
            value_child = ast_node_to_dict(node.value, current_id)
            if value_child:
                result['children'].append(value_child)
    
    return result

def count_nodes(node):
    """Count the total number of nodes in an AST subtree"""
    if node is None:
        return 0
    
    count = 1
    
    if hasattr(node, 'left') and hasattr(node, 'right'):
        count += count_nodes(node.left) + count_nodes(node.right)
    elif hasattr(node, 'target') and hasattr(node, 'value'):
        count += count_nodes(node.target) + count_nodes(node.value)
    elif hasattr(node, 'callable') and hasattr(node, 'arguments'):
        count += count_nodes(node.callable)
        for arg in node.arguments:
            count += count_nodes(arg)
    elif hasattr(node, 'parameters') and hasattr(node, 'body'):
        for param in node.parameters:
            count += count_nodes(param)
        for stmt in node.body:
            count += count_nodes(stmt)
    elif hasattr(node, 'body'):
        for stmt in node.body:
            count += count_nodes(stmt)
    elif hasattr(node, 'value') and node.__class__.__name__ == 'ReturnNode':
        if node.value:
            count += count_nodes(node.value)
    
    return count

def process_code(source_code):
    """Process Python code and return AST and IR representations"""
    try:
        # Tokenize
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        # Parse into AST
        parser = Parser(tokens)
        ast_nodes = parser.parse()
        
        # Generate AST text representation
        ast_text_representation = []
        for node in ast_nodes:
            node_str = str(node)
            lines = node_str.split('\n')
            indented_lines = ['  ' + line for line in lines]
            ast_text_representation.extend(indented_lines)
        
        # Generate AST tree representation
        ast_tree_data = []
        current_id = 0
        for node in ast_nodes:
            tree_node = ast_node_to_dict(node, current_id)
            if tree_node:
                ast_tree_data.append(tree_node)
                current_id += count_nodes(node)
        
        # Generate IR
        ir_generator = IRGenerator()
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
            'ast_text': ast_text_representation,
            'ast_tree': ast_tree_data,
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