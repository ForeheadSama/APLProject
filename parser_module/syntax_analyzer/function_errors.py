# -----------------------------------------------------------------------------
# function_errors.py - Function-specific error checks
# -----------------------------------------------------------------------------

def check_function_errors(p, parser, errors):
    """Check for errors specific to function declarations and calls."""
    # Flag to indicate if we handled the error
    handled = False
    
    # Check for missing return type in function definition
    if p.type == 'FUNCTION':
        next_token = parser.lookahead
        if next_token and next_token.type not in ['INT_TYPE', 'FLOAT_TYPE', 'STRING_TYPE', 
                                                 'BOOL_TYPE', 'DATE_TYPE', 'TIME_TYPE', 'VOID']:
            error_message = f"Syntax error at line {p.lineno}: Missing return type after 'function' keyword"
            errors.append(error_message)
            handled = True
    
    # Check for missing function name
    if p.type in ['INT_TYPE', 'FLOAT_TYPE', 'STRING_TYPE', 'BOOL_TYPE', 'DATE_TYPE', 'TIME_TYPE', 'VOID']:
        # Check if we're in a function definition context
        func_context = False
        for i in range(len(parser.symstack)-1, max(0, len(parser.symstack)-2), -1):
            if hasattr(parser.symstack[i], 'value') and parser.symstack[i].value == 'FUNCTION':
                func_context = True
                break
        
        if func_context:
            next_token = parser.lookahead
            if next_token and next_token.type != 'IDENTIFIER':
                error_message = f"Syntax error at line {p.lineno}: Missing function name after return type"
                errors.append(error_message)
                handled = True
    
    # Check for missing opening parenthesis in function definition
    if p.type == 'IDENTIFIER' and len(parser.symstack) > 2:
        # Check if we're in a function definition context
        func_context = False
        for i in range(len(parser.symstack)-2, max(0, len(parser.symstack)-3), -1):
            if (hasattr(parser.symstack[i], 'value') and 
                parser.symstack[i].value in ['INT_TYPE', 'FLOAT_TYPE', 'STRING_TYPE', 
                                           'BOOL_TYPE', 'DATE_TYPE', 'TIME_TYPE', 'VOID']):
                # And check if one more step back is FUNCTION
                if (i > 0 and hasattr(parser.symstack[i-1], 'value') and 
                    parser.symstack[i-1].value == 'FUNCTION'):
                    func_context = True
                    break
        
        if func_context:
            next_token = parser.lookahead
            if next_token and next_token.type != 'LPAREN':
                error_message = f"Syntax error at line {p.lineno}: Missing opening parenthesis '(' after function name '{p.value}'"
                errors.append(error_message)
                handled = True
    
    # Check for missing closing parenthesis in function definition or call
    if p.type in ['IDENTIFIER', 'COMMA'] and len(parser.symstack) > 3:
        # Check if we're in a parameter list context
        param_context = False
        paren_depth = 0
        for i in range(len(parser.symstack)-1, 0, -1):
            if hasattr(parser.symstack[i], 'value'):
                if parser.symstack[i].value == 'LPAREN':
                    paren_depth += 1
                    param_context = True
                elif parser.symstack[i].value == 'RPAREN':
                    paren_depth -= 1
        
        # If we're in an unclosed parameter list and the next token isn't a closing paren or comma
        if param_context and paren_depth > 0:
            next_token = parser.lookahead
            if (next_token and next_token.type not in ['RPAREN', 'COMMA'] and 
                p.type != 'COMMA' and p.value != ','):
                error_message = f"Syntax error at line {p.lineno}: Missing closing parenthesis ')' or comma in parameter list"
                errors.append(error_message)
                handled = True
    
    # Check for missing opening bracket in function body
    if p.type == 'RPAREN' and len(parser.symstack) > 3:
        # Check if we're in a function definition context
        func_context = False
        for i in range(len(parser.symstack)-3, max(0, len(parser.symstack)-7), -1):
            if (hasattr(parser.symstack[i], 'value') and 
                parser.symstack[i].value == 'FUNCTION'):
                func_context = True
                break
        
        if func_context:
            next_token = parser.lookahead
            if next_token and next_token.type != 'LBRACKET':
                error_message = f"Syntax error at line {p.lineno}: Missing opening bracket '{{' for function body"
                errors.append(error_message)
                handled = True
    
    # Check for missing arguments in function call
    if p.type == 'LPAREN':
        # Check if we're in a function call context
        func_call_context = False
        for i in range(len(parser.symstack)-1, max(0, len(parser.symstack)-2), -1):
            if (hasattr(parser.symstack[i], 'value') and 
                hasattr(parser.symstack[i].value, 'type') and 
                parser.symstack[i].value.type == 'callable'):
                func_call_context = True
                break
        
        if func_call_context:
            next_token = parser.lookahead
            if next_token and next_token.type not in ['RPAREN']:
                # We don't have an error here, as empty argument lists are valid
                pass
    
    return handled