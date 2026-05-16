import pytest
import sys
from pathlib import Path

# Agrega el directorio pjs al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Scanner import Scanner
from Parser import Parser
from Interpreter import Interpreter
from Resolver import Resolver


@pytest.fixture
def execute_js():
    """
    Fixture que ejecuta código JavaScript y retorna el resultado.
    """
    def _execute(code: str):
        interpreter = Interpreter()
        scanner = Scanner(code)
        tokens = scanner.scan()
        parser = Parser(tokens)
        stmts = parser.parse()
        
        resolver = Resolver(interpreter)
        for stmt in stmts:
            resolver.resolve(stmt)
        
        result = interpreter.interpret(stmts, as_js_repr=False)
        return result
    
    return _execute