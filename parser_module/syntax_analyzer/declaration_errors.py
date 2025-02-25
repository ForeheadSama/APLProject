# -----------------------------------------------------------------------------
# declaration_errors.py - Declaration-specific error checks
# -----------------------------------------------------------------------------

def check_declaration_errors(p, parser, errors):
    """Check for errors specific to declarations."""
    # Flag to indicate if we handled the error
    handled = False
    
    # Check for missing type specifier in declaration
    if p.type == 'IDENTIFIER' and len(parser.symstack) > 1:
        if hasattr(parser.symstack[-1], 'type') and parser.symstack[-1].type == 'statement_list':
            error_message = f"Syntax error at line {p.lineno}: Missing type specifier before identifier '{p.value}'"
            errors.append(error_message)
            handled = True
    
    # Check for missing equals in declaration
    if p.type == 'IDENTIFIER' and len(parser.symstack) > 2:
        if (hasattr(parser.symstack[-2], 'type') and 
            parser.symstack[-2].type in ['INT_TYPE', 'FLOAT_TYPE', 'STRING_TYPE', 'BOOL_TYPE', 'DATE_TYPE', 'TIME_TYPE']):
            next_token = parser.lookahead
            if next_token and next_token.type != 'EQUALS':
                error_message = f"Syntax error at line {p.lineno}: Missing '=' after identifier '{p.value}' in declaration"
                errors.append(error_message)
                handled = True
    
    # Check for missing expression in declaration
    if p.type == 'EQUALS' and len(parser.symstack) > 2:
        if (hasattr(parser.symstack[-2], 'value') and 
            hasattr(parser.symstack[-2].value, 'type') and 
            parser.symstack[-2].value.type == 'IDENTIFIER'):
            next_token = parser.lookahead
            if next_token and next_token.type == 'EOL':
                error_message = f"Syntax error at line {p.lineno}: Missing expression after '=' in declaration"
                errors.append(error_message)
                handled = True
    
    # Check for missing EOL in declaration
    if (p.type in ['NUMBER', 'FLOAT_NUM', 'STRING_LITERAL', 'BOOLEAN_VAL', 'DATE_VAL', 'TIME_VAL', 'IDENTIFIER'] 
        and len(parser.symstack) > 4):
        # Try to detect if we're in a declaration context
        decl_context = False
        for i in range(len(parser.symstack)-1, max(0, len(parser.symstack)-4), -1):
            if hasattr(parser.symstack[i], 'value') and hasattr(parser.symstack[i].value, 'type'):
                if parser.symstack[i].value.type == 'EQUALS':
                    decl_context = True
                    break
        
        if decl_context:
            next_token = parser.lookahead
            if next_token and next_token.type != 'EOL':
                error_message = f"Syntax error at line {p.lineno}: Missing period (.) at the end of declaration"
                errors.append(error_message)
                handled = True
    
    return handled