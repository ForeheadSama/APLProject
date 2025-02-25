# -----------------------------------------------------------------------------
# statement_errors.py - Statement-specific error checks
# -----------------------------------------------------------------------------

def check_statement_errors(p, parser, errors):
    """Check for errors specific to statement syntax."""
    # Flag to indicate if we handled the error
    handled = False
    
    # Check for missing EOL in assignment
    if hasattr(parser, 'symstack') and len(parser.symstack) > 3:
        if (p.type in ['NUMBER', 'FLOAT_NUM', 'STRING_LITERAL', 'BOOLEAN_VAL', 'DATE_VAL', 'TIME_VAL', 'IDENTIFIER'] and
            any(hasattr(parser.symstack[i], 'value') and 
                hasattr(parser.symstack[i].value, 'type') and 
                parser.symstack[i].value.type == 'EQUALS' 
                for i in range(len(parser.symstack)-3, len(parser.symstack)))):
            
            next_token = parser.lookahead
            if next_token and next_token.type != 'EOL' and next_token.type not in ['RPAREN', 'RBRACKET']:
                error_message = f"Syntax error at line {p.lineno}: Missing period (.) at the end of statement"
                errors.append(error_message)
                handled = True
    
    # Check for missing EOL in function call
    if p.type == 'RPAREN' and len(parser.symstack) > 2:
        # Try to detect if we're in a function call context
        func_call_context = False
        for i in range(len(parser.symstack)-1, max(0, len(parser.symstack)-4), -1):
            if hasattr(parser.symstack[i], 'value') and hasattr(parser.symstack[i].value, 'type'):
                if parser.symstack[i].value.type == 'LPAREN':
                    func_call_context = True
                    break
        
        if func_call_context:
            next_token = parser.lookahead
            if next_token and next_token.type != 'EOL' and next_token.type != 'RBRACKET':
                error_message = f"Syntax error at line {p.lineno}: Missing period (.) at the end of function call"
                errors.append(error_message)
                handled = True
    
    # Check for missing EOL in return statement
    if (p.type in ['NUMBER', 'FLOAT_NUM', 'STRING_LITERAL', 'BOOLEAN_VAL', 'DATE_VAL', 'TIME_VAL', 'IDENTIFIER'] and 
        len(parser.symstack) > 2):
        
        return_context = False
        for i in range(len(parser.symstack)-1, max(0, len(parser.symstack)-3), -1):
            if hasattr(parser.symstack[i], 'value') and parser.symstack[i].value == 'RETURN':
                return_context = True
                break
        
        if return_context:
            next_token = parser.lookahead
            if next_token and next_token.type != 'EOL':
                error_message = f"Syntax error at line {p.lineno}: Missing period (.) at the end of return statement"
                errors.append(error_message)
                handled = True
    
    return handled