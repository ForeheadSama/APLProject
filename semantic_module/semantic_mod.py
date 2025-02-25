"""
Semantic analysis module for the APBL language.
This module performs semantic validation on the AST created by the parser.
"""

class SemanticAnalyzer:
    def __init__(self):
        self.errors = []              # List to store semantic errors found during analysis
        self.warnings = []            # List to store warnings during analysis
        self.symbol_table = {}        # Dictionary to store function/variable declarations
        self.current_function = None  # To track the current function being analyzed

    # ----------------------------------------------------------------------
    # Main entry point for semantic analysis.
    # Returns a tuple of (success, errors, warnings, symbol_table)
    # ----------------------------------------------------------------------   
    def analyze(self, ast):

        if not ast:
            return False, ["No AST to analyze"], [], {}  # Return error if AST is empty
            
        # Start analyzing from program node
        if ast['type'] == 'program':
            self._analyze_program(ast)  # Analyze program node
        else:
            self.errors.append("Root node is not a program node")  # Error if root is not program
        
        # Return results of the analysis
        success = len(self.errors) == 0  # Success if no errors found
        return success, self.errors, self.warnings, self.symbol_table
    
    # ----------------------------------------------------------------------
    # Analyze the program node and its statements
    # ----------------------------------------------------------------------
    def _analyze_program(self, node):

        # First pass: collect all function and variable declarations
        for stmt in node.get('statements', []):
            if stmt['type'] == 'function_def':
                self._register_function(stmt)  # Register function definitions
            elif stmt['type'] == 'declaration':
                self._register_variable(stmt)  # Register variable declarations
        
        # Second pass: analyze each statement
        for stmt in node.get('statements', []):
            self._analyze_statement(stmt)  # Analyze individual statements
    
    # ----------------------------------------------------------------------
    # Analyze the program node and its statements
    # ----------------------------------------------------------------------
    def _register_function(self, node):
        """Register a function in the symbol table"""
        name = node.get('name')
        if name in self.symbol_table:
            self.errors.append(f"Line {node.get('line', 0)}: Function '{name}' is already defined")  # Error if function is redefined
        else:
            self.symbol_table[name] = {
                'type': 'function',
                'return_type': node.get('return_type'),
                'params': node.get('params', []),
                'line': node.get('line', 0)
            }

    # ----------------------------------------------------------------------
    # Register a variable in the symbol table
    # ----------------------------------------------------------------------
    def _register_variable(self, node):
        
        name = node.get('name')
        if name in self.symbol_table:
            self.errors.append(f"Line {node.get('line', 0)}: Variable '{name}' is already defined")  # Error if variable is redefined
        else:
            self.symbol_table[name] = {
                'type': 'variable',
                'var_type': node.get('var_type'),
                'line': node.get('line', 0)
            }

    # ----------------------------------------------------------------------
    # Analyze a single statement node
    # ----------------------------------------------------------------------
    def _analyze_statement(self, node):

        if not node:
            return
            
        node_type = node.get('type')  # Get the type of the statement
        
        # Call corresponding analysis function based on the type of statement
        if node_type == 'declaration':
            self._analyze_declaration(node)
        elif node_type == 'assignment':
            self._analyze_assignment(node)
        elif node_type == 'function_def':
            self._analyze_function_def(node)
        elif node_type == 'function_call':
            self._analyze_function_call(node)
        elif node_type == 'if':
            self._analyze_if_statement(node)
        elif node_type == 'while':
            self._analyze_while_statement(node)
        elif node_type == 'return':
            self._analyze_return_statement(node)
        elif node_type == 'block':
            for stmt in node.get('statements', []):
                self._analyze_statement(stmt)  # Analyze each statement in a block

    # ----------------------------------------------------------------------
    # Analyze a declaration statement for semantic errors
    # ----------------------------------------------------------------------    
    def _analyze_declaration(self, node):

        # Check for missing type specifier (should already be caught by parser)
        if node.get('var_type') == 'ERROR':
            self.errors.append(f"Line {node.get('line', 0)}: Missing type specifier for variable '{node.get('name')}'")
            return
            
        # Check expression type compatibility (literal types)
        var_type = node.get('var_type')
        value = node.get('value')
        
        if value and value.get('type') == 'literal':
            value_type = self._infer_type_from_literal(value)
            if not self._is_type_compatible(var_type, value_type):
                self.errors.append(f"Line {node.get('line', 0)}: Type mismatch in declaration of '{node.get('name')}'. Expected {var_type}, got {value_type}")
    
    # ----------------------------------------------------------------------
    # Analyze an assignment statement for semantic errors
    # ----------------------------------------------------------------------
    def _analyze_assignment(self, node):
        # Check if variable exists in the symbol table
        target = node.get('target')
        if target not in self.symbol_table:
            self.errors.append(f"Line {node.get('line', 0)}: Assignment to undeclared variable '{target}'")
            return
            
        # Check type compatibility between variable and assigned value
        var_info = self.symbol_table[target]
        value = node.get('value')
        
        if value and value.get('type') == 'literal':
            value_type = self._infer_type_from_literal(value)
            if not self._is_type_compatible(var_info.get('var_type'), value_type):
                self.errors.append(f"Line {node.get('line', 0)}: Type mismatch in assignment to '{target}'. Expected {var_info.get('var_type')}, got {value_type}")
    
    # ----------------------------------------------------------------------
    # Analyze a function definition statement for semantic errors
    # ----------------------------------------------------------------------
    def _analyze_function_def(self, node):

        prev_function = self.current_function
        self.current_function = node.get('name')  # Track current function
        
        # Analyze function body
        if 'body' in node:
            self._analyze_statement(node.get('body'))
            
        self.current_function = prev_function  # Restore previous function
    
    # ----------------------------------------------------------------------
    # Analyze a function call statement for semantic errors"
    # ----------------------------------------------------------------------
    def _analyze_function_call(self, node):

        name = node.get('name')
        
        # Check if function is defined or is a built-in
        if name not in self.symbol_table and name not in ['book', 'gen', 'reg', 'display']:
            self.errors.append(f"Line {node.get('line', 0)}: Call to undefined function '{name}'")
            return
            
        # For user-defined functions, check parameter count
        if name in self.symbol_table and self.symbol_table[name]['type'] == 'function':
            expected_params = len(self.symbol_table[name].get('params', []))
            actual_params = len(node.get('arguments', []))
            
            if expected_params != actual_params:
                self.errors.append(f"Line {node.get('line', 0)}: Function '{name}' called with {actual_params} arguments but requires {expected_params}")
    
    # ----------------------------------------------------------------------
    # Analyze an if statement for semantic errors"
    # ----------------------------------------------------------------------
    def _analyze_if_statement(self, node):

        # Ensure condition is boolean
        condition = node.get('condition')
        if condition and condition.get('type') == 'literal':
            condition_type = self._infer_type_from_literal(condition)
            if not self._is_type_compatible('bool', condition_type):
                self.warnings.append(f"Line {node.get('line', 0)}: If condition should be a boolean expression")
        
        # Analyze blocks for 'then' and 'else'
        if 'then_block' in node:
            self._analyze_statement(node.get('then_block'))
        if 'else_block' in node:
            self._analyze_statement(node.get('else_block'))
    
    # ----------------------------------------------------------------------
    # Analyze a while statement for semantic errors"
    # ----------------------------------------------------------------------
    def _analyze_while_statement(self, node):

        # Ensure condition is boolean
        condition = node.get('condition')
        if condition and condition.get('type') == 'literal':
            condition_type = self._infer_type_from_literal(condition)
            if not self._is_type_compatible('bool', condition_type):
                self.warnings.append(f"Line {node.get('line', 0)}: While condition should be a boolean expression")
        
        # Analyze body of while loop
        if 'body' in node:
            self._analyze_statement(node.get('body'))

    # ----------------------------------------------------------------------
    # Analyze a return statement for semantic errors"
    # ----------------------------------------------------------------------
    def _analyze_return_statement(self, node):

        # Check if we're inside a function
        if not self.current_function:
            self.errors.append(f"Line {node.get('line', 0)}: Return statement outside of function")
            return
            
        # Check return type matches function declaration
        if self.current_function in self.symbol_table:
            expected_type = self.symbol_table[self.current_function].get('return_type')
            
            value = node.get('value')

            if expected_type == 'void':
                if value:
                    self.errors.append(f"Line {node.get('line', 0)}: Function '{self.current_function}' is declared as void but returns a value.")
                return  ## A void function can have 'return.' without value, exit here.

            ## Handle normal return types
            if not value:
                self.errors.append(f"Line {node.get('line', 0)}: Missing return value in function '{self.current_function}'")
            elif value.get('type') == 'literal':
                value_type = self._infer_type_from_literal(value)

                ## Explicitly check for boolean-integer confusion
                if expected_type == 'bool' and value_type == 'int':
                    self.warnings.append(f"Line {node.get('line', 0)}: Possible incorrect return value in function '{self.current_function}', expected bool but got int.")

                if not self._is_type_compatible(expected_type, value_type):
                    self.errors.append(f"Line {node.get('line', 0)}: Return type mismatch in function '{self.current_function}'. Expected {expected_type}, got {value_type}")
    
    # ----------------------------------------------------------------------
    # Infer the type of a literal node
    # ----------------------------------------------------------------------    
    def _infer_type_from_literal(self, node):

        if not node or node.get('type') != 'literal':
            return None
            
        value = node.get('value')

        if isinstance(value, int):
            return 'int'
        
        elif isinstance(value, float):
            return 'float'
        
        elif isinstance(value, str):
            if value.lower() in ['true', 'false']:
                return 'bool'
            elif '-' in value and len(value.split('-')) == 3:
                return 'date'
            elif ':' in value and len(value.split(':')) == 3:
                return 'time'
            else:
                return 'string'
        
        return None
   
    # ----------------------------------------------------------------------
    # Check if the actual type is compatible with the expected type
    # ----------------------------------------------------------------------
    def _is_type_compatible(self, expected, actual):

        if expected == actual:
            return True
            
        # Add type conversion rules if needed
        # For example, int can be assigned to float
        if expected == 'float' and actual == 'int':
            return True
            
        return False

# ----------------------------------------------------------------------
# Analyze the AST for semantic errors.
# Returns a tuple of (success, errors, warnings, symbol_table)
# ----------------------------------------------------------------------
def analyze_semantics(ast):

    analyzer = SemanticAnalyzer()
    success, errors, warnings, symbol_table = analyzer.analyze(ast)
    
    # Import it here to avoid circular imports
    from utils.output_handler import write_semantic_analysis
    write_semantic_analysis({
        'errors': errors,
        'warnings': warnings,
        'symbol_table': symbol_table
    })
    
    return success, errors, warnings, symbol_table
