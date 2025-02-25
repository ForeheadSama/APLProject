import ply.lex as lex
from utils.output_handler import write_lexical_analysis

# ----------------------------------------------------------------------
# Reserved Words Definition
# ----------------------------------------------------------------------
# Dictionary of all keywords in the language mapped to their token types
reserved = {
    # Built-in Functions
    'book': 'BOOK',           # For booking a ticket
    'gen': 'GEN',             # For generating user ID
    'reg': 'REG',             # For registering a user     
    'display': 'DISPLAY',     # For displaying output
    
    # Control Flow Keywords
    'if': 'IF',
    'while': 'WHILE',
    'foreach': 'FOREACH',
    'until': 'UNTIL',
    'return': 'RETURN',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    
    # Data Structure Keywords
    'array': 'ARRAY',
    'dictionary': 'DICTIONARY',
    'map': 'MAP',
    'set': 'SET',
    
    # Data Type Keywords
    'int': 'INT_TYPE',        # Integer type
    'float': 'FLOAT_TYPE',    # Floating-point type
    'string': 'STRING_TYPE',  # String type
    'bool': 'BOOL_TYPE',      # Boolean type
    'date': 'DATE_TYPE',      # Date type
    'time': 'TIME_TYPE',      # Time type
    
    # Logical Operators
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    
    # Other Keywords
    'then': 'THEN',
    'else': 'ELSE',
    'function': 'FUNCTION',
    'void': 'VOID',  # Add void type
}

# ----------------------------------------------------------------------
# Token List Definition
# ----------------------------------------------------------------------
# Complete list of all tokens in the language
tokens = [
    'NUMBER',
    'FLOAT_NUM',
    'STRING_LITERAL',
    'BOOLEAN_VAL',
    'DATE_VAL',
    'TIME_VAL',
    'IDENTIFIER',
    'EQUALS',
    'EQ',
    'NEQ',
    'LT',
    'GT',
    'LE',
    'GE',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'LBRACKET',
    'RBRACKET',
    'COMMA',
    'EOL',
] + list(reserved.values())

# ----------------------------------------------------------------------
# Simple Token Rules
# ----------------------------------------------------------------------
# Regular expression rules for simple tokens
t_LPAREN   = r'\('
t_RPAREN   = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COMMA    = r','

t_IF = r'if'
t_ELSE = r'else'
t_WHILE = r'while'
t_FUNCTION = r'function'
t_RETURN = r'return'

# ----------------------------------------------------------------------
# Complex Token Rules
# ----------------------------------------------------------------------
# Rules for tokens that need more complex processing

# Comparison Operators
def t_EQ(t):
    r'=='
    return t

def t_NEQ(t):
    r'!='
    return t

def t_LE(t):
    r'<='
    return t

def t_GE(t):
    r'>='
    return t

def t_LT(t):
    r'<'
    return t

def t_GT(t):
    r'>'
    return t

# Assignment operator
t_EQUALS = r'='

# Mathematical operators
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'

# ----------------------------------------------------------------------
# Literal Value Rules
# ----------------------------------------------------------------------

def t_FLOAT_NUM(t):
    r'\d*\.\d+'
    """Match floating point numbers (e.g., 2.95)"""
    t.value = float(t.value)  # Convert string to float
    return t

def t_NUMBER(t):
    r'\d+'
    """Match integer numbers (e.g., 123)"""
    t.value = int(t.value)  # Convert string to integer
    return t

def t_BOOLEAN_VAL(t):
    r'True|False'
    """Match boolean literals"""
    t.value = t.value == 'True'  # Convert to Python boolean
    return t

def t_DATE_VAL(t):
    r'"[0-9]{4}-[0-9]{2}-[0-9]{2}"'
    """Match date literals in format YYYY-MM-DD"""
    t.value = t.value[1:-1]  # Remove quotes
    return t

def t_TIME_VAL(t):
    r'"[0-9]{2}:[0-9]{2}:[0-9]{2}"'
    """Match time literals in format HH:MM:SS"""
    t.value = t.value[1:-1]  # Remove quotes
    return t

class LexerError(Exception):
    def __init__(self, message, line, value=None):
        self.message = message
        self.line = line
        self.value = value
        
        # Format error message with context if value is provided
        msg = f"{message} at line {line}"
        if value:
            msg += f": '{value}'"
        super().__init__(msg)

def t_STRING_LITERAL(t):
    r'"[^"\n]*"?'
    """Match string literals and detect missing quotes"""
    if t.value[0] != '"':
        raise LexerError("String must begin with a quote", t.lineno, t.value)
    if t.value[-1] != '"':
        raise LexerError("String is missing closing quote", t.lineno, t.value)
    t.value = t.value[1:-1]
    return t

# ----------------------------------------------------------------------
# Special Token Rules
# ----------------------------------------------------------------------

def t_EOL(t):
    r'\.'
    """Match end-of-line (EOL) token
    
    The EOL token (.) is required at the end of each statement
    to mark its completion.
    """
    return t

def t_IDENTIFIER(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    """Match identifiers and check for reserved words"""
    # Check if identifier is a reserved word
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

# ----------------------------------------------------------------------
# Comment Rules
# ----------------------------------------------------------------------

def t_COMMENT(t):
    r'\$\$.*'
    """Match and ignore single-line comments starting with $$"""
    pass  # No return - comments are discarded

def t_MLCOMMENT(t):
    r'\$<[\s\S]*?\>\$'
    """Match and ignore multi-line comments between $< and >$"""
    t.lexer.lineno += t.value.count('\n')  # Update line count
    pass  # No return - comments are discarded

# ----------------------------------------------------------------------
# Whitespace and Error Handling
# ----------------------------------------------------------------------

def t_newline(t):
    r'\n+'
    """Track line numbers"""
    t.lexer.lineno += len(t.value)

# Characters to ignore (whitespace and tabs)
t_ignore = ' \t'

def t_error(t):
    """Error handling for illegal characters"""
    raise LexerError("Invalid character", t.lineno, t.value[0])

# ----------------------------------------------------------------------
# Lexer Creation and Interface
# ----------------------------------------------------------------------

# Create the lexer
lexer = lex.lex()

# Export tokens and lexer for use by parser
__all__ = ['tokens', 'lexer']

def tokenize(source_code):
    """Perform lexical analysis and return tokens"""
    lexer.input(source_code)
    tokens = []
    
    while True:
        tok = lexer.token()
        if not tok:
            break
        # Ensure each token has lineno and lexpos
        tok.lineno = getattr(tok, 'lineno', lexer.lineno)
        tok.lexpos = getattr(tok, 'lexpos', lexer.lexpos)
        tokens.append(tok)
    
    write_lexical_analysis(tokens)
    return tokens

# Attach tokenize method to lexer
lexer.tokenize = tokenize

