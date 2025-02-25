# -----------------------------------------------------------------------------
# syntax_check.py - Syntax validation and error handling
# -----------------------------------------------------------------------------

# Import specific error checking functions from different modules
from parser_module.syntax_analyzer.declaration_errors import check_declaration_errors
from parser_module.syntax_analyzer.statement_errors import check_statement_errors
from parser_module.syntax_analyzer.expression_errors import check_expression_errors
from parser_module.syntax_analyzer.function_errors import check_function_errors
from parser_module.syntax_analyzer.control_flow_errors import check_control_flow_errors

# Global lists for tracking errors and expected tokens
errors = []             # Stores syntax errors encountered during parsing
expected_tokens = {}    # Stores expected tokens at different parsing states

# -----------------------------------------------------------------------------
# Helper: AST Node Creation
# -----------------------------------------------------------------------------
def create_node(type, **kwargs):
    """Create an AST node with common attributes."""
    return {
        'type': type,                       # Node type (e.g., declaration, assignment, function_call)
        'line': kwargs.get('line', 0),      # Line number where the node appears
        'column': kwargs.get('column', 0),  # Column number for precise error reporting
        **kwargs  # Additional attributes specific to the node type
    }

# -----------------------------------------------------------------------------
# Error Handling Setup
# -----------------------------------------------------------------------------
def setup_error_handler(parser):
    """Initialize the error handling system and store expected tokens."""
    global expected_tokens
    expected_tokens = {}  # Reset expected tokens mapping
    
    # Populate expected tokens at each parser state
    for state, actions in parser.action.items():
        expected = []  # List to store expected token names
        for token_id, action in actions.items():
            if token_id in parser.productions:
                token_name = parser.productions[token_id].name  # Get token name
                if token_name != 'error':  # Ignore error tokens
                    expected.append(token_name)
        expected_tokens[state] = expected  # Store expected tokens for this state

def get_expected_tokens(parser_state):
    """Retrieve expected tokens for a given parser state."""
    return expected_tokens.get(parser_state, [])

def handle_error(p, error_type, message):
    """Register a syntax error with detailed information."""
    if p:
        line_number = p.lineno(1) if hasattr(p, 'lineno') else 0  # Retrieve line number
        error_message = f"Syntax error at line {line_number}: {error_type} - {message}"  # Format error
    else:
        error_message = f"Syntax error: {error_type} - {message}"  # General error message
    
    errors.append(error_message)  # Add error to global list
    return error_message

# -----------------------------------------------------------------------------
# Main Error Handler
# -----------------------------------------------------------------------------
def handle_parser_error(p, parser):
    """Main syntax error handler that identifies and categorizes errors."""
    global errors
    
    if p:
        error_type = "Unexpected token"  # Default error type
        suggestions = ""  # Suggestions for correction
        expected = get_expected_tokens(parser.state)  # Get expected tokens
        
        # Check specific error types using predefined error handlers
        if check_declaration_errors(p, parser, errors):
            return
        if check_statement_errors(p, parser, errors):
            return
        if check_expression_errors(p, parser, errors):
            return
        if check_function_errors(p, parser, errors):
            return
        if check_control_flow_errors(p, parser, errors):
            return
        
        # Improve error message by suggesting expected tokens
        if expected:
            suggestions = f"Expected one of: {', '.join(expected)}"
        
        # Construct and store the error message
        error_message = (f"Syntax error at line {p.lineno}: {error_type} near token '{p.type}' "
                         f"with value '{p.value}'. {suggestions}")
        errors.append(error_message)
    else:
        errors.append("Syntax error: Unexpected end of file")

# -----------------------------------------------------------------------------
# Error Recovery Rules
# -----------------------------------------------------------------------------
def p_declaration_stmt_error_missing_type(p):
    '''declaration_stmt : IDENTIFIER EQUALS expression EOL'''
    error_msg = handle_error(p, "Missing type specifier", f"Missing type specifier before identifier '{p[1]}'")
    
    # Create an error node to allow parsing to continue
    p[0] = create_node('declaration',
                       var_type="ERROR",
                       name=p[1],
                       value=p[3],
                       line=p.lineno(1) if hasattr(p, 'lineno') else 0)

def p_declaration_stmt_error_missing_eol(p):
    '''declaration_stmt : type_specifier IDENTIFIER EQUALS expression'''
    error_msg = handle_error(p, "Missing end of statement", f"Missing period (EOL) after declaration of '{p[2]}'")
    
    # Create an error node to allow parsing to continue
    p[0] = create_node('declaration',
                       var_type=p[1],
                       name=p[2],
                       value=p[4],
                       line=p.lineno(1) if hasattr(p, 'lineno') else 0)

def p_assignment_stmt_error_missing_eol(p):
    '''assignment_stmt : IDENTIFIER EQUALS expression'''
    error_msg = handle_error(p, "Missing end of statement", f"Missing period (EOL) after assignment to '{p[1]}'")
    
    # Create an error node to allow parsing to continue
    p[0] = create_node('assignment',
                       target=p[1],
                       value=p[3],
                       line=p.lineno(1) if hasattr(p, 'lineno') else 0)

def p_function_call_stmt_error_missing_eol(p):
    '''function_call_stmt : function_call'''
    error_msg = handle_error(p, "Missing end of statement", "Missing period (EOL) after function call")
    
    # Create an error node to allow parsing to continue
    p[0] = p[1]

# -----------------------------------------------------------------------------
# Error Management Functions
# -----------------------------------------------------------------------------
def get_errors():
    """Retrieve the list of collected syntax errors."""
    return errors

def clear_errors():
    """Clear all stored syntax errors."""
    global errors
    errors = []
