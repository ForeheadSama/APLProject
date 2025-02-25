# -----------------------------------------------------------------------------
# grammar_rules.py - Grammar rules for the language parser
# -----------------------------------------------------------------------------
from parser_module.syntax_analyzer.syntax_check import create_node, handle_error  # Import helper functions for AST creation and error handling

# -----------------------------------------------------------------------------
# Program and Statement List
# -----------------------------------------------------------------------------
def p_program(p):
    '''program : statement_list'''
    p[0] = create_node('program', statements=p[1] if p[1] else [])  # Create a program node with a list of statements

def p_statement_list(p):
    '''statement_list : statement_list statement
                      | statement'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]    # Append the new statement to the existing list
    else:
        p[0] = [p[1]]           # Start a new list with a single statement

def p_statement_list_opt(p):
    '''statement_list_opt : statement_list
                          | empty'''
    p[0] = p[1] if p[1] is not None else []  # Ensure the list is never None

# -----------------------------------------------------------------------------
# Statements
# -----------------------------------------------------------------------------
def p_statement(p):
    '''statement : declaration_stmt
                 | assignment_stmt
                 | function_def_stmt
                 | function_call_stmt
                 | if_stmt
                 | while_stmt
                 | return_stmt'''
    p[0] = p[1]  # Assign the parsed statement directly

# -----------------------------------------------------------------------------
# Declarations and Type Specifiers
# -----------------------------------------------------------------------------
def p_declaration_stmt(p):
    '''declaration_stmt : type_specifier IDENTIFIER EQUALS expression EOL'''
    p[0] = create_node('declaration',
                       var_type=p[1],
                       name=p[2],
                       value=p[4],
                       line=p.lineno(1))  # Store variable type, name, and assigned value

def p_type_specifier(p):
    '''type_specifier : INT_TYPE
                      | FLOAT_TYPE
                      | STRING_TYPE
                      | BOOL_TYPE
                      | DATE_TYPE
                      | TIME_TYPE
                      | VOID'''
    p[0] = p[1]  # Return the type specifier token

# -----------------------------------------------------------------------------
# Assignment
# -----------------------------------------------------------------------------
def p_assignment_stmt(p):
    '''assignment_stmt : IDENTIFIER EQUALS expression EOL'''
    p[0] = create_node('assignment',
                       target=p[1],
                       value=p[3],
                       line=p.lineno(1))  # Store assignment details

# -----------------------------------------------------------------------------
# Function Definitions and Parameters
# -----------------------------------------------------------------------------
def p_function_def_stmt(p):
    '''function_def_stmt : FUNCTION type_specifier IDENTIFIER LPAREN param_list RPAREN block_stmt'''
    p[0] = create_node('function_def',
                       return_type=p[2],
                       name=p[3],
                       params=p[5],
                       body=p[7],
                       line=p.lineno(1))  # Store function details including name, return type, and body

def p_param_list(p):
    '''param_list : param_list COMMA param
                  | param
                  | empty'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]  # Append new parameter
    elif p[1] is None:
        p[0] = []   # Return an empty list if no parameters exist
    else:
        p[0] = [p[1]]  # Wrap a single parameter in a list

def p_param(p):
    '''param : type_specifier IDENTIFIER'''
    p[0] = create_node('parameter',
                       param_type=p[1],
                       name=p[2],
                       line=p.lineno(1))  # Store parameter details

# -----------------------------------------------------------------------------
# Block Statements
# -----------------------------------------------------------------------------
def p_block_stmt(p):
    '''block_stmt : LBRACKET statement_list_opt RBRACKET'''
    p[0] = create_node('block', statements=p[2])  # Store a block containing statements

# -----------------------------------------------------------------------------
# Function Calls
# -----------------------------------------------------------------------------
def p_callable(p):
    '''callable : IDENTIFIER
                | BOOK
                | GEN
                | REG
                | DISPLAY'''
    p[0] = p[1]  # Return callable function name

def p_function_call_stmt(p):
    '''function_call_stmt : function_call EOL'''
    p[0] = p[1]  # Store function call

def p_function_call(p):
    '''function_call : callable LPAREN arg_list RPAREN'''
    p[0] = create_node('function_call',
                       name=p[1],
                       arguments=p[3],
                       line=p.lineno(1))  # Store function call details including arguments

def p_arg_list(p):
    '''arg_list : arg_list COMMA expression
                | expression
                | empty'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]  # Append argument
    elif p[1] is None:
        p[0] = []  # Return empty list if no arguments exist
    else:
        p[0] = [p[1]]  # Wrap a single argument in a list

# -----------------------------------------------------------------------------
# Control Structures
# -----------------------------------------------------------------------------
def p_if_stmt(p):
    '''if_stmt : IF LPAREN expression RPAREN block_stmt
               | IF LPAREN expression RPAREN block_stmt ELSE block_stmt'''
    if len(p) == 6:
        p[0] = create_node('if',
                           condition=p[3],
                           then_block=p[5],
                           line=p.lineno(1))
    else:
        p[0] = create_node('if',
                           condition=p[3],
                           then_block=p[5],
                           else_block=p[7],
                           line=p.lineno(1))

def p_while_stmt(p):
    '''while_stmt : WHILE LPAREN expression RPAREN block_stmt'''
    p[0] = create_node('while',
                       condition=p[3],
                       body=p[5],
                       line=p.lineno(1))  # Store while-loop details

def p_return_stmt(p):
    '''return_stmt : RETURN expression EOL'''
    p[0] = create_node('return',
                       value=p[2],
                       line=p.lineno(1))  # Store return statement

# -----------------------------------------------------------------------------
# Unified Expression Productions
# -----------------------------------------------------------------------------
def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression LE expression
                  | expression GE expression
                  | expression LT expression
                  | expression GT expression
                  | expression EQ expression
                  | expression NEQ expression'''
    p[0] = create_node('binary_op',
                       op=p[2],
                       left=p[1],
                       right=p[3],
                       line=p.lineno(2))  # Store binary operation details

def p_expression_paren(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]  # Return expression inside parentheses

def p_expression_atom(p):
    '''expression : NUMBER
                  | FLOAT_NUM
                  | STRING_LITERAL
                  | BOOLEAN_VAL
                  | DATE_VAL
                  | TIME_VAL
                  | IDENTIFIER
                  | function_call'''
    token_type = p.slice[1].type
    if token_type in ('NUMBER', 'FLOAT_NUM', 'STRING_LITERAL', 'BOOLEAN_VAL', 'DATE_VAL', 'TIME_VAL'):
        p[0] = create_node('literal', value=p[1], line=p.lineno(1))
    elif token_type == 'IDENTIFIER':
        p[0] = create_node('identifier', name=p[1], line=p.lineno(1))
    else:
        p[0] = p[1]

# -----------------------------------------------------------------------------
# Empty Production
# -----------------------------------------------------------------------------
def p_empty(p):
    'empty :'
    p[0] = None
