# -----------------------------------------------------------------------------
# control_flow_errors.py - Control flow-specific error checks
# -----------------------------------------------------------------------------

def check_control_flow_errors(p, parser, errors):
    """Check for errors specific to control flow statements (if, while, etc.)."""
    # Flag to indicate if we handled the error
    handled = False
    
    # Check for missing opening parenthesis in if statement
    if p.type == 'IF':
        next_token = parser.lookahead
        if next_token and next_token.type != 'LPAREN':
            error_message = f"Syntax error at line {p.lineno}: Missing opening parenthesis '(' after 'if' keyword"
            errors.append(error_message)
            handled = True
    
    # Check for missing opening parenthesis in while statement
    if p.type == 'WHILE':
        next_token = parser.lookahead
        if next_token and next_token.type != 'LPAREN':
            error_message = f"Syntax error at line {p.lineno}: Missing opening parenthesis '(' after 'while' keyword"
            errors.append(error_message)
            handled = True
    
    # Check for missing condition in if statement
    if p.type == 'LPAREN':
        # Check if we're in an if statement context
        if_context = False
        for i in range(len(parser.symstack)-1, max(0, len(parser.symstack)-2), -1):
            if hasattr(parser.symstack[i], 'value') and parser.symstack[i].value == 'IF':
                if_context = True
                break
        
        if if_context:
            next_token = parser.lookahead
            if next_token and next_token.type == 'RPAREN':
                error_message = f"Syntax error at line {p.lineno}: Missing condition in if statement"
                errors.append(error_message)
                handled = True
    
    # Check for missing condition in while statement
    if p.type == 'LPAREN':
        # Check if we're in a while statement context
        while_context = False
        for i in range(len(parser.symstack)-1, max(0, len(parser.symstack)-2), -1):
            if hasattr(parser.symstack[i], 'value') and parser.symstack[i].value == 'WHILE':
                while_context = True
                break
        
        if while_context:
            next_token = parser.lookahead
            if next_token and next_token.type == 'RPAREN':
                error_message = f"Syntax error at line {p.lineno}: Missing condition in while statement"
                errors.append(error_message)
                handled = True
    
    # Check for missing closing parenthesis in if or while statement
    if p.type in ['NUMBER', 'FLOAT_NUM', 'STRING_LITERAL', 'BOOLEAN_VAL', 'DATE_VAL', 'TIME_VAL', 'IDENTIFIER']:
        # Check if we're in an if or while condition context
        control_context = False
        control_keyword = None
        
        for i in range(len(parser.symstack)-1, 0, -1):
            if hasattr(parser.symstack[i], 'value'):
                if parser.symstack[i].value in ['IF', 'WHILE']:
                    control_context = True
                    control_keyword = parser.symstack[i].value
                    break
        
        if control_context:
            next_token = parser.lookahead
            paren_found = False
            # Look ahead a few tokens to see if there's a closing paren
            for i in range(3):  # Look ahead up to 3 tokens
                if next_token and next_token.type == 'RPAREN':
                    paren_found = True
                    break
                # Try to get the next token
                if hasattr(parser, 'token_stream') and hasattr(parser.token_stream, 'tokens'):
                    current_index = parser.token_stream.index
                    if current_index + i < len(parser.token_stream.tokens):
                        next_token = parser.token_stream.tokens[current_index + i]
            
            if not paren_found:
                error_message = f"Syntax error at line {p.lineno}: Missing closing parenthesis ')' after condition in {control_keyword.lower()} statement"
                errors.append(error_message)
                handled = True
    
    # Check for missing opening bracket in if or while body
    if p.type == 'RPAREN':
        # Check if we're in an if or while statement context
        control_context = False
        control_keyword = None
        
        for i in range(len(parser.symstack)-1, 0, -1):
            if hasattr(parser.symstack[i], 'value'):
                if parser.symstack[i].value in ['IF', 'WHILE']:
                    control_context = True
                    control_keyword = parser.symstack[i].value
                    break
        
        if control_context:
            next_token = parser.lookahead
            if next_token and next_token.type != 'LBRACKET':
                error_message = f"Syntax error at line {p.lineno}: Missing opening bracket '{{' for {control_keyword.lower()} statement body"
                errors.append(error_message)
                handled = True
    
    # Check for missing else block in if-else statement
    if p.type == 'ELSE':
        next_token = parser.lookahead
        if next_token and next_token.type != 'LBRACKET':
            error_message = f"Syntax error at line {p.lineno}: Missing opening bracket '{{' after 'else' keyword"
            errors.append(error_message)
            handled = True
    
    # Check for missing expression in return statement
    if p.type == 'RETURN':
        next_token = parser.lookahead
        if next_token and next_token.type == 'EOL':
            error_message = f"Syntax error at line {p.lineno}: Missing expression in return statement"
            errors.append(error_message)
            handled = True
    
    return handled