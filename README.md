# Python AST and IR Generator

This project is a Python code analyzer that generates Abstract Syntax Trees (AST) and Intermediate Representation (IR) for Python code. It includes a lexer, parser, AST generator, and intermediate code generator, along with a web interface for visualizing the outputs.

## Project Overview

The project consists of several components:

1. **Lexer**: Tokenizes Python source code
2. **Parser**: Parses tokens into an Abstract Syntax Tree (AST)
3. **AST Nodes**: Represents the structure of the code
4. **IR Generator**: Converts AST to Three-Address Code (TAC) intermediate representation
5. **Web Interface**: Visualizes AST and IR representations

## Features

- Lexical analysis of Python code
- Parsing and AST generation
- Intermediate code generation in TAC form
- Web-based visualization interface
- Support for:
  - Function definitions and calls
  - Class definitions and methods
  - Variable assignments
  - Control flow statements
  - Method calls
  - Return statements

## Command Line Usage

You can use the command line interface to generate AST and IR for Python code:

```bash
python python_ast_main.py example.py --show-ir
```

This will display both the AST and IR for the specified Python file.

## Web Interface

The project includes a web interface for visualizing the AST and IR representations.

### Running the Web Interface

1. Install the required dependencies:
```bash
cd web
pip install -r requirements.txt
```

2. Run the Flask application:
```bash
python app.py
```

3. Open your browser and navigate to http://localhost:5000

### Using the Web Interface

The web interface consists of three panels:
- **Left Panel**: Python code editor with syntax highlighting
- **Middle Panel**: Abstract Syntax Tree (AST) representation
- **Right Panel**: Intermediate Representation (IR) in TAC form

You can:
1. Write or paste Python code in the editor
2. Click "Analyze Code" or press Ctrl+Enter to analyze the code
3. View the AST and IR representations of your code

## Intermediate Representation (IR)

The IR is a Three-Address Code (TAC) representation that simplifies the code into basic operations. For example:

```
Function hello(name):
    t1 = call print("Hello,", name)
    return name

Function Person.__init__(self, name, age):
    store name -> self.name
    store age -> self.age
    return

Function Person.greet(self):
    t1 = call hello(self.name)
    return t1

t2 = new Person("Alice", 30)
store t2 -> person
t3 = call person.greet()
store t3 -> result
```

The IR uses:
- Temporary variables (t1, t2, t3) for intermediate results
- Explicit function calls and returns
- Object instantiation with the `new` keyword
- Method calls with explicit object references
- Simple variable assignments

## Project Structure

```
pythonAST/
├── lexer/                 # Lexical analyzer
├── parser/                # Parser and AST nodes
├── intermediate/          # IR generator
├── web/                   # Web interface
│   ├── static/            # CSS and JavaScript files
│   └── templates/         # HTML templates
├── python_ast_main.py     # Command-line interface
└── README.md              # Project documentation
```

## Example

Here's a simple example that illustrates the AST and IR generation:

```python
def hello(name):
    print("Hello,", name)
    return name

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        return hello(self.name)

# Create a person object
person = Person("Alice", 30)
result = person.greet()
```

## Future Enhancements

Potential future enhancements include:
- More comprehensive Python language support
- Code optimizations in the IR generation
- Code generation to target languages
- Additional visualizations and interactive elements
- Support for more complex Python features (decorators, generators, etc.)

## Contributing

Contributions are welcome! Feel free to submit pull requests or open issues for bugs or feature requests.