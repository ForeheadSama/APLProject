# -----------------------------------------------------------------------------
# parser_mod.py - Parser module for the language
# -----------------------------------------------------------------------------
import ply.yacc as yacc  # Import PLY's Yacc for parsing

# Import necessary modules
from lexer_module.lexer import tokens  # Import token definitions from the lexer
from parser_module.grammar_rules import *  # Import grammar rules for the parser
from parser_module.syntax_analyzer.syntax_check import (
    setup_error_handler,    # Function to initialize error handling
    handle_parser_error,    # Function to handle syntax errors during parsing
    clear_errors,           # Function to clear previous errors before parsing
    get_errors              # Function to retrieve stored errors after parsing
)

# -----------------------------------------------------------------------------
# Precedence Rules
# -----------------------------------------------------------------------------
precedence = (
    ('nonassoc', 'LE', 'GE', 'LT', 'GT', 'EQ', 'NEQ'),  # Non-associative operators (comparison)
    ('left', 'PLUS', 'MINUS'),                          # Left-associative addition and subtraction
    ('left', 'TIMES', 'DIVIDE'),                        # Left-associative multiplication and division
)

# -----------------------------------------------------------------------------
# Token Stream Wrapper
# -----------------------------------------------------------------------------
class TokenStream:
    """
    A simple wrapper that accepts a list of tokens and provides
    the token() method required by yacc.
    Also keeps track of the current line number for error reporting.
    """
    def __init__(self, tokens):
        self.tokens = tokens                    # Store the list of tokens
        self.index = 0                          # Initialize index to track the current token
        self.current_line = 1 if tokens else 0  # Track the current line number
        
    def token(self):
        """Returns the next token in the list."""
        if self.index < len(self.tokens):       # Ensure we haven't reached the end
            tok = self.tokens[self.index]       # Get the current token
            self.current_line = getattr(tok, 'lineno', self.current_line)  # Update line number
            self.index += 1                     # Move to the next token
            return tok                          # Return the current token
        return None                             # Return None when all tokens are processed
    
    @property
    def lineno(self):
        """Returns the current line number for error reporting."""
        if self.index < len(self.tokens):       # Ensure we haven't reached the end
            return getattr(self.tokens[self.index], 'lineno', self.current_line)  # Get line number from token
        return self.current_line                # Return the last known line number

# -----------------------------------------------------------------------------
# Error function
# -----------------------------------------------------------------------------
def p_error(p):
    """Handles parsing errors and reports them using the error handler."""
    handle_parser_error(p, parser)  # Call error handling function

# -----------------------------------------------------------------------------
# Build the Parser
# -----------------------------------------------------------------------------
parser = yacc.yacc(debug=True, optimize=False, errorlog=yacc.NullLogger())  # Build the parser with debugging enabled

# Set up error handling
setup_error_handler(parser)  # Initialize the parser's error handling mechanism

# -----------------------------------------------------------------------------
# Parse Function
# -----------------------------------------------------------------------------
def parse(token_list):
    """
    Accepts a list of tokens (produced by the lexer) and returns the AST.
    
    Args:
        token_list: List of tokens from the lexer
        
    Returns:
        tuple: (AST, list of errors)
    """
    # Clear any previous errors before starting a new parse session
    clear_errors()
    
    try:
        # Create a token stream wrapper around the token list
        ts = TokenStream(token_list)
        
        # Store the token stream in the parser for error handling purposes
        parser.token_stream = ts
        
        # Parse the input token stream and generate an AST
        ast = parser.parse(lexer=ts, tracking=True)
        
        # Retrieve any errors that occurred during parsing
        errors = get_errors()
        
        # Write the parsing result (AST and errors) if output handling is available
        try:
            from utils.output_handler import write_syntax_analysis  # Import function for output handling
            write_syntax_analysis(ast, errors)                      # Write AST and errors to output
        except ImportError:
            pass  # If output handler is not available, just continue without writing
        
        return ast, errors  # Return the generated AST and errors
    
    except Exception as e:
        # Handle unexpected exceptions during parsing
        error_msg = f"Parsing error: {str(e)}"  # Create an error message
        errors = get_errors()                   # Retrieve existing errors
        errors.append(error_msg)                # Append the new error
        return None, errors                     # Return None as AST and the list of errors
