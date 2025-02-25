"""
Main compiler module that integrates lexer, parser, and semantic analyzer
"""

from lexer_module.lexer import tokenize
from parser_module.parser_mod import parse
from semantic_module.semantic_mod import SemanticAnalyzer

def compile_file(filename):
    """
    Complete compilation process for an APBL file.
    """
    try:
        # Read source code
        with open(filename, 'r') as f:
            source_code = f.read() # Store file contents separately

        # Print file name
        print(f"\nCompiling {filename}...") 
        
        # [1] Lexical Analysis
        tokens = tokenize(source_code)
        if not tokens:
            print("Lexical analysis failed.")
            return False
        
        print(f"\n==> Lexical analysis completed. Found {len(tokens)} tokens.")
        
        # [2] Syntax Analysis
        #-- TO FIX: 
        #    1. Extensive errors 
        print("==> Syntax analysis completed.")
        ast, syntax_errors = parse(tokens)
        
        # [3] Semantic Analysis
        #-- TO FIX: 
        #    1. Extensive errors (if i type fffalse instead of false, it shows no errors)
        analyzer = SemanticAnalyzer()
        success, semantic_errors, warnings, symbol_table = analyzer.analyze(ast)
        print("==> Semantic analysis completed.")
        
        # if warnings:
        #     print(f"Found {len(warnings)} warnings:")
        #     for warning in warnings:
        #         print(f"  {warning}")
    
        return success and not syntax_errors

    except Exception as e:
        print(f"\nError compiling APBL file: {str(e)}")
        return False

# Main
if __name__ == "__main__": 
    compile_file("sample_code.apbl")
    