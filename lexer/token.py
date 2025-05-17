from enum import Enum, auto

class TokenType(Enum):
    # Python keywords
    DEF = auto()
    IF = auto()
    ELSE = auto()
    ELIF = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    RETURN = auto()
    IMPORT = auto()
    FROM = auto()
    AS = auto()
    CLASS = auto()
    PASS = auto()
    BREAK = auto()
    CONTINUE = auto()
    NOT = auto()
    AND = auto()
    OR = auto()
    TRUE = auto()
    FALSE = auto()
    NONE = auto()
    WITH = auto()

    # Identifiers and literals
    IDENTIFIER = auto()
    INTEGER_LITERAL = auto()
    FLOAT_LITERAL = auto()
    STRING_LITERAL = auto()

    # Operators
    PLUS = auto()          # +
    MINUS = auto()         # -
    MUL = auto()           # *
    DIV = auto()           # /
    MOD = auto()           # %
    POWER = auto()         # **
    EQ = auto()            # ==
    NEQ = auto()           # !=
    LT = auto()            # <
    GT = auto()            # >
    LTE = auto()           # <=
    GTE = auto()           # >=
    ASSIGN = auto()        # =
    PLUS_ASSIGN = auto()   # +=
    MINUS_ASSIGN = auto()  # -=
    MUL_ASSIGN = auto()    # *=
    DIV_ASSIGN = auto()    # /=

    # Punctuation
    DOT = auto()           # .
    COMMA = auto()         # ,
    COLON = auto()         # :
    SEMICOLON = auto()     # ;
    LPAREN = auto()        # (
    RPAREN = auto()        # )
    LBRACK = auto()        # [
    RBRACK = auto()        # ]
    LBRACE = auto()        # {
    RBRACE = auto()        # }

    # Special
    INDENT = auto()
    DEDENT = auto()
    NEWLINE = auto()
    END = auto()


class Token:
    def __init__(self, token_type, value, line, column):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column
    
    def __str__(self):
        if self.type == TokenType.IDENTIFIER:
            return f"{self.type.name}({self.value})"
        elif self.type in (TokenType.INTEGER_LITERAL, TokenType.FLOAT_LITERAL, TokenType.STRING_LITERAL):
            return f"{self.type.name}({self.value})"
        else:
            return self.type.name