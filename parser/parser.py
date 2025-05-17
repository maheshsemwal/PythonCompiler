from lexer.token import TokenType
from parser.ast_nodes import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
    
    def peek(self):
        """Return the current token without consuming it"""
        if self.current >= len(self.tokens):
            return None
        return self.tokens[self.current]
    
    def advance(self):
        """Consume the current token and return it"""
        token = self.peek()
        if token:
            self.current += 1
        return token
    
    def match(self, *types):
        """Check if the current token matches any of the given types"""
        token = self.peek()
        if token and token.type in types:
            return self.advance()
        return None
    
    def expect(self, type_, message):
        """Expect a token of specific type, raise error if not found"""
        token = self.peek()
        if token and token.type == type_:
            return self.advance()
        
        if token:
            raise SyntaxError(f"{message} at line {token.line}, column {token.column}")
        else:
            raise SyntaxError(f"{message} at end of file")
    
    def parse(self):
        """Parse the tokens into an AST"""
        ast_nodes = []
        
        while self.peek() and self.peek().type != TokenType.END:
            try:
                node = self.parse_statement()
                if node:
                    ast_nodes.append(node)
            except Exception as e:
                print(f"Error: {e}")
                # Skip to the next statement to continue parsing
                self.synchronize()
        
        return ast_nodes
    
    def synchronize(self):
        """Recover from a parsing error by advancing to a safe point"""
        while self.peek() and self.peek().type not in (
            TokenType.NEWLINE, TokenType.SEMICOLON, TokenType.END
        ):
            self.advance()
        
        # Skip the newline/semicolon
        if self.peek() and self.peek().type in (TokenType.NEWLINE, TokenType.SEMICOLON):
            self.advance()
    
    def parse_statement(self):
        """Parse a statement"""
        token = self.peek()
        
        if token.type == TokenType.DEF:
            return self.parse_function_def()
        elif token.type == TokenType.CLASS:
            return self.parse_class_def()
        elif token.type == TokenType.IF:
            return self.parse_if_statement()
        elif token.type == TokenType.WHILE:
            return self.parse_while_loop()
        elif token.type == TokenType.FOR:
            return self.parse_for_loop()
        elif token.type == TokenType.RETURN:
            return self.parse_return()
        elif token.type == TokenType.IMPORT:
            return self.parse_import()
        elif token.type == TokenType.FROM:
            return self.parse_from_import()
        elif token.type == TokenType.PASS:
            self.advance()  # Consume 'pass'
            self.match(TokenType.NEWLINE)  # Optional newline
            return PassNode()
        elif token.type == TokenType.BREAK:
            self.advance()  # Consume 'break'
            self.match(TokenType.NEWLINE)  # Optional newline
            return BreakNode()
        elif token.type == TokenType.CONTINUE:
            self.advance()  # Consume 'continue'
            self.match(TokenType.NEWLINE)  # Optional newline
            return ContinueNode()
        elif token.type == TokenType.NEWLINE:
            self.advance()  # Skip empty lines
            return None
        else:
            # Expression statements (including assignments)
            expr = self.parse_expression()
            self.match(TokenType.NEWLINE)  # Optional newline
            return expr
    
    def parse_block(self):
        """Parse an indented block of code"""
        self.expect(TokenType.COLON, "Expected ':' before indented block")
        self.match(TokenType.NEWLINE)  # Skip optional newline after colon
        
        # Check for the INDENT token that starts a block
        if not self.match(TokenType.INDENT):
            # If no INDENT, this might be a single-line block like "if x: pass"
            stmt = self.parse_statement()
            return [stmt] if stmt else []
        
        statements = []
        while self.peek() and self.peek().type != TokenType.DEDENT:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        self.match(TokenType.DEDENT)  # Consume the DEDENT
        return statements
    
    def parse_function_def(self):
        """Parse a function definition"""
        self.advance()  # Consume 'def'
        name_token = self.expect(TokenType.IDENTIFIER, "Expected function name")
        name = name_token.value
        
        self.expect(TokenType.LPAREN, "Expected '(' after function name")
        parameters = self.parse_parameters()
        self.expect(TokenType.RPAREN, "Expected ')' after parameters")
        
        body = self.parse_block()
        return FunctionDefNode(name, parameters, body)
    
    def parse_parameters(self):
        """Parse function parameters"""
        parameters = []
        
        # Empty parameter list
        if self.peek().type == TokenType.RPAREN:
            return parameters
        
        # Parse the first parameter
        parameters.append(self.parse_parameter())
        
        # Parse remaining parameters
        while self.match(TokenType.COMMA):
            parameters.append(self.parse_parameter())
        
        return parameters
    
    def parse_parameter(self):
        """Parse a single function parameter"""
        name_token = self.expect(TokenType.IDENTIFIER, "Expected parameter name")
        name = name_token.value
        
        default_value = None
        if self.match(TokenType.ASSIGN):
            default_value = self.parse_expression()
        
        return ParameterNode(name, default_value)
    
    def parse_class_def(self):
        """Parse a class definition"""
        self.advance()  # Consume 'class'
        name_token = self.expect(TokenType.IDENTIFIER, "Expected class name")
        name = name_token.value
        
        bases = []
        if self.match(TokenType.LPAREN):
            # Parse base classes
            if self.peek().type != TokenType.RPAREN:
                bases.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    bases.append(self.parse_expression())
            self.expect(TokenType.RPAREN, "Expected ')' after base classes")
        
        body = self.parse_block()
        return ClassDefNode(name, bases, body)
    
    def parse_if_statement(self):
        """Parse an if statement"""
        self.advance()  # Consume 'if'
        condition = self.parse_expression()
        
        then_body = self.parse_block()
        else_body = []
        
        # Check for 'else' or 'elif'
        if self.match(TokenType.ELSE):
            else_body = self.parse_block()
        elif self.match(TokenType.ELIF):
            # An 'elif' is treated as an 'else' with a nested 'if'
            condition2 = self.parse_expression()
            then_body2 = self.parse_block()
            else_body2 = []
            
            # Check for more 'elif' or 'else'
            if self.peek() and self.peek().type in (TokenType.ELIF, TokenType.ELSE):
                else_body2 = [self.parse_if_statement()]
            
            else_body = [IfNode(condition2, then_body2, else_body2)]
        
        return IfNode(condition, then_body, else_body)
    
    def parse_while_loop(self):
        """Parse a while loop"""
        self.advance()  # Consume 'while'
        condition = self.parse_expression()
        
        body = self.parse_block()
        return WhileNode(condition, body)
    
    def parse_for_loop(self):
        """Parse a for loop"""
        self.advance()  # Consume 'for'
        target = self.parse_expression()  # This will parse identifiers or more complex targets
        
        self.expect(TokenType.IN, "Expected 'in' after for-loop target")
        iterable = self.parse_expression()
        
        body = self.parse_block()
        return ForNode(target, iterable, body)
    
    def parse_return(self):
        """Parse a return statement"""
        self.advance()  # Consume 'return'
        
        value = None
        if self.peek().type not in (TokenType.NEWLINE, TokenType.SEMICOLON):
            value = self.parse_expression()
        
        self.match(TokenType.NEWLINE)  # Optional newline
        return ReturnNode(value)
    
    def parse_import(self):
        """Parse an import statement"""
        self.advance()  # Consume 'import'
        
        module_token = self.expect(TokenType.IDENTIFIER, "Expected module name")
        module = module_token.value
        
        alias = ""
        if self.match(TokenType.AS):
            alias_token = self.expect(TokenType.IDENTIFIER, "Expected alias after 'as'")
            alias = alias_token.value
        
        self.match(TokenType.NEWLINE)  # Optional newline
        return ImportNode(module, alias)
    
    def parse_from_import(self):
        """Parse a from...import statement"""
        self.advance()  # Consume 'from'
        
        module_token = self.expect(TokenType.IDENTIFIER, "Expected module name")
        module = module_token.value
        
        self.expect(TokenType.IMPORT, "Expected 'import' after module name")
        
        imports = []
        if self.match(TokenType.MUL):  # from module import *
            imports.append(("*", ""))
        else:
            name_token = self.expect(TokenType.IDENTIFIER, "Expected name to import")
            
            alias = ""
            if self.match(TokenType.AS):
                alias_token = self.expect(TokenType.IDENTIFIER, "Expected alias after 'as'")
                alias = alias_token.value
            
            imports.append((name_token.value, alias))
            
            # Handle multiple imports: from module import name1, name2, ...
            while self.match(TokenType.COMMA):
                name_token = self.expect(TokenType.IDENTIFIER, "Expected name to import")
                
                alias = ""
                if self.match(TokenType.AS):
                    alias_token = self.expect(TokenType.IDENTIFIER, "Expected alias after 'as'")
                    alias = alias_token.value
                
                imports.append((name_token.value, alias))
        
        self.match(TokenType.NEWLINE)  # Optional newline
        return FromImportNode(module, imports)
    
    def parse_expression(self):
        """Parse an expression (assignment, binary operation, etc.)"""
        expr = self.parse_logical_or()
        
        # Handle assignment
        if self.match(TokenType.ASSIGN):
            value = self.parse_expression()
            return AssignmentNode(expr, value)
        elif self.match(TokenType.PLUS_ASSIGN):
            value = self.parse_expression()
            return AssignmentNode(expr, BinaryOpNode("+", expr, value))
        elif self.match(TokenType.MINUS_ASSIGN):
            value = self.parse_expression()
            return AssignmentNode(expr, BinaryOpNode("-", expr, value))
        elif self.match(TokenType.MUL_ASSIGN):
            value = self.parse_expression()
            return AssignmentNode(expr, BinaryOpNode("*", expr, value))
        elif self.match(TokenType.DIV_ASSIGN):
            value = self.parse_expression()
            return AssignmentNode(expr, BinaryOpNode("/", expr, value))
        
        return expr
    
    def parse_logical_or(self):
        """Parse logical OR expressions"""
        expr = self.parse_logical_and()
        
        while self.match(TokenType.OR):
            right = self.parse_logical_and()
            expr = BinaryOpNode("or", expr, right)
        
        return expr
    
    def parse_logical_and(self):
        """Parse logical AND expressions"""
        expr = self.parse_equality()
        
        while self.match(TokenType.AND):
            right = self.parse_equality()
            expr = BinaryOpNode("and", expr, right)
        
        return expr
    
    def parse_equality(self):
        """Parse equality expressions (==, !=)"""
        expr = self.parse_comparison()
        
        while True:
            if self.match(TokenType.EQ):
                right = self.parse_comparison()
                expr = BinaryOpNode("==", expr, right)
            elif self.match(TokenType.NEQ):
                right = self.parse_comparison()
                expr = BinaryOpNode("!=", expr, right)
            else:
                break
        
        return expr
    
    def parse_comparison(self):
        """Parse comparison expressions (<, >, <=, >=)"""
        expr = self.parse_term()
        
        while True:
            if self.match(TokenType.LT):
                right = self.parse_term()
                expr = BinaryOpNode("<", expr, right)
            elif self.match(TokenType.GT):
                right = self.parse_term()
                expr = BinaryOpNode(">", expr, right)
            elif self.match(TokenType.LTE):
                right = self.parse_term()
                expr = BinaryOpNode("<=", expr, right)
            elif self.match(TokenType.GTE):
                right = self.parse_term()
                expr = BinaryOpNode(">=", expr, right)
            else:
                break
        
        return expr
    
    def parse_term(self):
        """Parse term expressions (+, -)"""
        expr = self.parse_factor()
        
        while True:
            if self.match(TokenType.PLUS):
                right = self.parse_factor()
                expr = BinaryOpNode("+", expr, right)
            elif self.match(TokenType.MINUS):
                right = self.parse_factor()
                expr = BinaryOpNode("-", expr, right)
            else:
                break
        
        return expr
    
    def parse_factor(self):
        """Parse factor expressions (*, /, %)"""
        expr = self.parse_unary()
        
        while True:
            if self.match(TokenType.MUL):
                right = self.parse_unary()
                expr = BinaryOpNode("*", expr, right)
            elif self.match(TokenType.DIV):
                right = self.parse_unary()
                expr = BinaryOpNode("/", expr, right)
            elif self.match(TokenType.MOD):
                right = self.parse_unary()
                expr = BinaryOpNode("%", expr, right)
            else:
                break
        
        return expr
    
    def parse_unary(self):
        """Parse unary expressions (-, not)"""
        if self.match(TokenType.MINUS):
            right = self.parse_unary()
            return BinaryOpNode("-", IntLiteralNode(0), right)  # -x is treated as 0-x
        elif self.match(TokenType.NOT):
            right = self.parse_unary()
            # For simplicity, we'll use a binary op node for 'not' as well
            return BinaryOpNode("not", right, None)
        
        return self.parse_power()
    
    def parse_power(self):
        """Parse power expressions (**)"""
        expr = self.parse_primary()
        
        while self.match(TokenType.POWER):
            right = self.parse_unary()  # Power is right-associative
            expr = BinaryOpNode("**", expr, right)
        
        return expr
    
    def parse_primary(self):
        """Parse primary expressions (literals, identifiers, groups, etc.)"""
        token = self.peek()
        
        if self.match(TokenType.INTEGER_LITERAL):
            return IntLiteralNode(token.value)
        elif self.match(TokenType.FLOAT_LITERAL):
            return FloatLiteralNode(token.value)
        elif self.match(TokenType.STRING_LITERAL):
            return StringLiteralNode(token.value)
        elif self.match(TokenType.TRUE):
            return BoolLiteralNode(True)
        elif self.match(TokenType.FALSE):
            return BoolLiteralNode(False)
        elif self.match(TokenType.NONE):
            return NoneLiteralNode()
        elif self.match(TokenType.IDENTIFIER):
            return self.finish_identifier(token.value)
        elif self.match(TokenType.LPAREN):
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN, "Expected ')'")
            return expr
        elif self.match(TokenType.LBRACK):
            # Parse list literal [elem1, elem2, ...]
            elements = []
            if self.peek().type != TokenType.RBRACK:
                elements.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    if self.peek().type == TokenType.RBRACK:
                        break  # Allow trailing comma
                    elements.append(self.parse_expression())
            self.expect(TokenType.RBRACK, "Expected ']'")
            return ListNode(elements)
        elif self.match(TokenType.LBRACE):
            # Parse dict literal {key: value, ...}
            items = []
            if self.peek().type != TokenType.RBRACE:
                key = self.parse_expression()
                self.expect(TokenType.COLON, "Expected ':' in dictionary literal")
                value = self.parse_expression()
                items.append((key, value))
                
                while self.match(TokenType.COMMA):
                    if self.peek().type == TokenType.RBRACE:
                        break  # Allow trailing comma
                    key = self.parse_expression()
                    self.expect(TokenType.COLON, "Expected ':' in dictionary literal")
                    value = self.parse_expression()
                    items.append((key, value))
            self.expect(TokenType.RBRACE, "Expected '}'")
            return DictNode(items)
        else:
            raise SyntaxError(f"Unexpected token {token} in expression")
    
    def finish_identifier(self, name):
        """Finish parsing an identifier (handle attribute access, method calls, etc.)"""
        expr = IdentifierNode(name)
        
        while True:
            if self.match(TokenType.DOT):
                # Handle attribute access: obj.attr
                attr_token = self.expect(TokenType.IDENTIFIER, "Expected attribute name after '.'")
                expr = AttributeNode(expr, attr_token.value)
            elif self.match(TokenType.LPAREN):
                # Handle function call: func(args)
                args = []
                kwargs = {}
                
                if self.peek().type != TokenType.RPAREN:
                    # Parse positional arguments
                    arg = self.parse_expression()
                    
                    # Check if it's a keyword argument
                    if (isinstance(arg, BinaryOpNode) and arg.op == "=" and 
                            isinstance(arg.left, IdentifierNode)):
                        kwargs[arg.left.name] = arg.right
                    else:
                        args.append(arg)
                    
                    while self.match(TokenType.COMMA):
                        if self.peek().type == TokenType.RPAREN:
                            break  # Allow trailing comma
                        
                        arg = self.parse_expression()
                        
                        # Check if it's a keyword argument
                        if (isinstance(arg, BinaryOpNode) and arg.op == "=" and 
                                isinstance(arg.left, IdentifierNode)):
                            kwargs[arg.left.name] = arg.right
                        else:
                            args.append(arg)
                
                self.expect(TokenType.RPAREN, "Expected ')' after function arguments")
                expr = FunctionCallNode(expr, args, kwargs)
            elif self.match(TokenType.LBRACK):
                # Handle subscript access: obj[index]
                index = self.parse_expression()
                self.expect(TokenType.RBRACK, "Expected ']' after subscript")
                expr = SubscriptNode(expr, index)
            else:
                break
        
        return expr