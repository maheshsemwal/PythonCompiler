from .token import Token, TokenType

class Lexer:
    def __init__(self, source):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.indentation_levels = [0]
        self.at_line_start = True

        # Python keywords
        self.keywords = {
            "def": TokenType.DEF,
            "if": TokenType.IF,
            "else": TokenType.ELSE,
            "elif": TokenType.ELIF,
            "while": TokenType.WHILE,
            "for": TokenType.FOR,
            "in": TokenType.IN,
            "return": TokenType.RETURN,
            "import": TokenType.IMPORT,
            "from": TokenType.FROM,
            "as": TokenType.AS,
            "class": TokenType.CLASS,
            "pass": TokenType.PASS,
            "break": TokenType.BREAK,
            "continue": TokenType.CONTINUE,
            "not": TokenType.NOT,
            "and": TokenType.AND,
            "or": TokenType.OR,
            "True": TokenType.TRUE,
            "False": TokenType.FALSE,
            "None": TokenType.NONE,
            "with": TokenType.WITH
        }

    def peek(self):
        if self.position >= len(self.source):
            return '\0'
        return self.source[self.position]

    def peek_next(self):
        if self.position + 1 >= len(self.source):
            return '\0'
        return self.source[self.position + 1]

    def advance(self):
        if self.position >= len(self.source):
            return '\0'
        
        current = self.source[self.position]
        self.position += 1
        
        if current == '\n':
            self.line += 1
            self.column = 1
            self.at_line_start = True
        else:
            self.column += 1
            
        return current

    def match(self, expected):
        if self.peek() != expected:
            return False
        self.advance()
        return True

    def skip_whitespace(self):
        # Don't skip newlines as they are significant in Python
        # Don't skip spaces at line start as they indicate indentation
        if self.at_line_start:
            return
        
        while self.peek() != '\n' and self.peek().isspace():
            self.advance()

    def skip_comment(self):
        # Skip until end of line
        while self.peek() != '\n' and self.peek() != '\0':
            self.advance()

    def handle_indentation(self):
        current_indent = 0
        while self.peek() == ' ' or self.peek() == '\t':
            if self.peek() == ' ':
                current_indent += 1
            else:  # tab
                current_indent += 4  # Common convention: 1 tab = 4 spaces
            self.advance()
        
        # If line is empty or comment, don't change indentation
        if self.peek() == '\n' or self.peek() == '#' or self.peek() == '\0':
            return []
        
        previous_indent = self.indentation_levels[-1]
        tokens = []
        
        if current_indent > previous_indent:
            # Indent
            self.indentation_levels.append(current_indent)
            tokens.append(Token(TokenType.INDENT, "", self.line, self.column))
        elif current_indent < previous_indent:
            # Dedent (potentially multiple levels)
            while current_indent < self.indentation_levels[-1]:
                self.indentation_levels.pop()
                tokens.append(Token(TokenType.DEDENT, "", self.line, self.column))
            
            if current_indent != self.indentation_levels[-1]:
                raise SyntaxError(f"Inconsistent indentation at line {self.line}")
        
        # No longer at line start
        self.at_line_start = False
        return tokens

    def parse_number(self):
        start_column = self.column
        number = ""
        is_float = False
        
        # Parse integer part
        while self.peek().isdigit():
            number += self.advance()
        
        # Parse decimal part if present
        if self.peek() == '.' and self.peek_next().isdigit():
            is_float = True
            number += self.advance()  # consume '.'
            
            while self.peek().isdigit():
                number += self.advance()
        
        # Parse scientific notation if present (e.g., 1.23e5)
        if self.peek() in ('e', 'E'):
            next_char = self.peek_next()
            if next_char.isdigit() or ((next_char == '+' or next_char == '-') and 
                                     self.position + 2 < len(self.source) and 
                                     self.source[self.position + 2].isdigit()):
                is_float = True
                number += self.advance()  # consume 'e' or 'E'
                
                if self.peek() in ('+', '-'):
                    number += self.advance()
                
                while self.peek().isdigit():
                    number += self.advance()
        
        if is_float:
            return Token(TokenType.FLOAT_LITERAL, float(number), self.line, start_column)
        else:
            return Token(TokenType.INTEGER_LITERAL, int(number), self.line, start_column)

    def parse_identifier(self):
        start_column = self.column
        identifier = ""
        
        # First character must be letter or underscore
        if self.peek().isalpha() or self.peek() == '_':
            identifier += self.advance()
        
        # Subsequent characters can be letters, digits, or underscores
        while self.peek().isalnum() or self.peek() == '_':
            identifier += self.advance()
        
        # Check if it's a keyword
        token_type = self.keywords.get(identifier, TokenType.IDENTIFIER)
        return Token(token_type, identifier, self.line, start_column)

    def parse_escape_sequence(self):
        self.advance()  # Skip backslash
        
        if self.peek() == 'n':
            self.advance()
            return '\n'
        elif self.peek() == 't':
            self.advance()
            return '\t'
        elif self.peek() == 'r':
            self.advance()
            return '\r'
        elif self.peek() == '\\':
            self.advance()
            return '\\'
        elif self.peek() == "'":
            self.advance()
            return "'"
        elif self.peek() == '"':
            self.advance()
            return '"'
        elif self.peek() == 'u':
            # Unicode sequence like \u0000
            self.advance()  # Skip 'u'
            hex_code = ""
            for _ in range(4):
                if not self.peek().isalnum():
                    break
                hex_code += self.advance()
            
            if len(hex_code) != 4:
                raise SyntaxError(f"Invalid Unicode escape sequence at line {self.line}")
            
            return chr(int(hex_code, 16))
        else:
            raise SyntaxError(f"Invalid escape sequence at line {self.line}")

    def parse_string(self):
        start_column = self.column
        is_f_string = False
        
        # Check for f-string prefix
        if self.peek() in ('f', 'F'):
            is_f_string = True
            self.advance()  # Skip 'f' or 'F'
        
        quote = self.advance()  # " or '
        is_triple_quote = False
        
        # Check for triple quotes
        if self.peek() == quote and self.peek_next() == quote:
            is_triple_quote = True
            self.advance()  # Skip second quote
            self.advance()  # Skip third quote
        
        string_value = ""
        
        while True:
            # End conditions
            if not is_triple_quote:
                if self.peek() == quote or self.peek() == '\0' or self.peek() == '\n':
                    break
            else:
                # For triple quotes, need three matching quotes in a row to end
                if (self.peek() == quote and self.peek_next() == quote and 
                    self.position + 2 < len(self.source) and 
                    self.source[self.position + 2] == quote):
                    break
                # Newlines are allowed in triple-quoted strings
                if self.peek() == '\0':
                    break
            
            if self.peek() == '\\':
                string_value += self.parse_escape_sequence()
            else:
                string_value += self.advance()
        
        # Check for proper termination
        if self.peek() == '\0' or (not is_triple_quote and self.peek() == '\n'):
            raise SyntaxError(f"Unterminated string at line {self.line}")
        
        # Skip closing quotes
        if not is_triple_quote:
            self.advance()  # Skip single closing quote
        else:
            self.advance()  # Skip first closing quote
            self.advance()  # Skip second closing quote
            self.advance()  # Skip third closing quote
        
        return Token(TokenType.STRING_LITERAL, string_value, self.line, start_column)

    def tokenize(self):
        tokens = []
        
        while self.position < len(self.source):
            # Handle indentation at line start
            if self.at_line_start:
                indent_tokens = self.handle_indentation()
                tokens.extend(indent_tokens)
                # If at_line_start is still True, we haven't processed any code yet
            
            current = self.peek()
            
            if current == '\0':
                break
            
            start_column = self.column
            
            # Skip comments
            if current == '#':
                self.skip_comment()
                continue
            
            # Handle newlines
            if current == '\n':
                tokens.append(Token(TokenType.NEWLINE, "\\n", self.line, start_column))
                self.advance()  # Skip newline
                self.at_line_start = True
                continue
            
            # Skip whitespace (but not at line start - that's handled by handle_indentation)
            if not self.at_line_start and current.isspace():
                self.skip_whitespace()
                continue
            
            # Handle indentation at line start
            if self.at_line_start:
                indent_tokens = self.handle_indentation()
                tokens.extend(indent_tokens)
                continue
            
            # Handle numbers
            if current.isdigit():
                tokens.append(self.parse_number())
                continue
            
            # Handle identifiers and keywords
            if current.isalpha() or current == '_':
                tokens.append(self.parse_identifier())
                continue
            
            # Handle string literals
            if current == '"' or current == "'" or (current in ('f', 'F') and 
                                                   (self.peek_next() == '"' or self.peek_next() == "'")):
                tokens.append(self.parse_string())
                continue
            
            # Handle multi-character operators
            if current == '+':
                if self.peek_next() == '=':
                    self.advance()  # Skip +
                    self.advance()  # Skip =
                    tokens.append(Token(TokenType.PLUS_ASSIGN, "+=", self.line, start_column))
                else:
                    self.advance()  # Skip +
                    tokens.append(Token(TokenType.PLUS, "+", self.line, start_column))
                continue
                
            elif current == '-':
                if self.peek_next() == '=':
                    self.advance()  # Skip -
                    self.advance()  # Skip =
                    tokens.append(Token(TokenType.MINUS_ASSIGN, "-=", self.line, start_column))
                else:
                    self.advance()  # Skip -
                    tokens.append(Token(TokenType.MINUS, "-", self.line, start_column))
                continue
                
            elif current == '*':
                if self.peek_next() == '*':
                    self.advance()  # Skip *
                    self.advance()  # Skip *
                    tokens.append(Token(TokenType.POWER, "**", self.line, start_column))
                elif self.peek_next() == '=':
                    self.advance()  # Skip *
                    self.advance()  # Skip =
                    tokens.append(Token(TokenType.MUL_ASSIGN, "*=", self.line, start_column))
                else:
                    self.advance()  # Skip *
                    tokens.append(Token(TokenType.MUL, "*", self.line, start_column))
                continue
                
            elif current == '/':
                if self.peek_next() == '=':
                    self.advance()  # Skip /
                    self.advance()  # Skip =
                    tokens.append(Token(TokenType.DIV_ASSIGN, "/=", self.line, start_column))
                elif self.peek_next() == '/':
                    self.advance()  # Skip /
                    self.advance()  # Skip /
                    tokens.append(Token(TokenType.DIV, "//", self.line, start_column))  # Integer division
                else:
                    self.advance()  # Skip /
                    tokens.append(Token(TokenType.DIV, "/", self.line, start_column))
                continue
                
            elif current == '%':
                self.advance()  # Skip %
                tokens.append(Token(TokenType.MOD, "%", self.line, start_column))
                continue
                
            elif current == '=':
                if self.peek_next() == '=':
                    self.advance()  # Skip =
                    self.advance()  # Skip =
                    tokens.append(Token(TokenType.EQ, "==", self.line, start_column))
                else:
                    self.advance()  # Skip =
                    tokens.append(Token(TokenType.ASSIGN, "=", self.line, start_column))
                continue
                
            elif current == '!':
                if self.peek_next() == '=':
                    self.advance()  # Skip !
                    self.advance()  # Skip =
                    tokens.append(Token(TokenType.NEQ, "!=", self.line, start_column))
                else:
                    raise SyntaxError(f"Unexpected character: '!' at line {self.line}")
                continue
                
            elif current == '<':
                if self.peek_next() == '=':
                    self.advance()  # Skip <
                    self.advance()  # Skip =
                    tokens.append(Token(TokenType.LTE, "<=", self.line, start_column))
                else:
                    self.advance()  # Skip <
                    tokens.append(Token(TokenType.LT, "<", self.line, start_column))
                continue
                
            elif current == '>':
                if self.peek_next() == '=':
                    self.advance()  # Skip >
                    self.advance()  # Skip =
                    tokens.append(Token(TokenType.GTE, ">=", self.line, start_column))
                else:
                    self.advance()  # Skip >
                    tokens.append(Token(TokenType.GT, ">", self.line, start_column))
                continue
            
            # Handle other single-character tokens
            token_type = None
            if current == '.':
                token_type = TokenType.DOT
            elif current == ',':
                token_type = TokenType.COMMA
            elif current == ':':
                token_type = TokenType.COLON
            elif current == ';':
                token_type = TokenType.SEMICOLON
            elif current == '(':
                token_type = TokenType.LPAREN
            elif current == ')':
                token_type = TokenType.RPAREN
            elif current == '[':
                token_type = TokenType.LBRACK
            elif current == ']':
                token_type = TokenType.RBRACK
            elif current == '{':
                token_type = TokenType.LBRACE
            elif current == '}':
                token_type = TokenType.RBRACE
            
            if token_type:
                tokens.append(Token(token_type, current, self.line, start_column))
                self.advance()
            else:
                raise SyntaxError(f"Unknown character: '{current}' at line {self.line}, column {self.column}")
        
        # Add DEDENT tokens for all remaining indentation levels
        while len(self.indentation_levels) > 1:
            self.indentation_levels.pop()
            tokens.append(Token(TokenType.DEDENT, "", self.line, self.column))
        
        # Add final END token
        tokens.append(Token(TokenType.END, "", self.line, self.column))
        
        return tokens