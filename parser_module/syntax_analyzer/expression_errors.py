# -----------------------------------------------------------------------------
# expression_errors.py - Expression-specific error checks
# -----------------------------------------------------------------------------

def check_expression_errors(p, parser, errors):
    """Check for errors specific to expressions."""
    # Flag to indicate if we handled the error
    handled = False
    
    # Check for mismatched parentheses in expressions
    if p.type == 'LPAREN':
        # Track opening parenthesis - could track the stack depth here
        pass
    
    if p.type == 'RPAREN':
        # Check if there was a matching opening parenthesis
        paren_context = False
        for i in range(len(parser.symstack)-1, 0, -1):
            if hasattr(parser.symstack[i], 'value') and parser.symstack[i].value == 'LPAREN':
                paren_context = True
                break
        
        if not paren_context:
            error_message = f"Syntax error at line {p.lineno}: Unmatched closing parenthesis ')'"
            errors.append(error_message)
            handled = True
    
    # Check for missing right operand in binary operations
    if p.type in ['PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LE', 'GE', 'LT', 'GT', 'EQ', 'NEQ']:
        next_token = parser.lookahead
        if not next_token or next_token.type in ['EOL', 'RPAREN', 'RBRACKET', 'COMMA']:
            error_message = f"Syntax error at line {p.lineno}: Missing right operand for operator '{p.value}'"
            errors.append(error_message)
            handled = True
    
    # Check for incomplete expressions in parentheses
    if p.type == 'LPAREN':
        next_token = parser.lookahead
        if next_token and next_token.type == 'RPAREN':
            error_message = f"Syntax error at line {p.lineno}: Empty parentheses in expression"
            errors.append(error_message)
            handled = True
    
    return handled