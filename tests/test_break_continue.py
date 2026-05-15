import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Scanner import Scanner
from Parser import Parser
from Interpreter import Interpreter
from Resolver import Resolver

@pytest.fixture
def js_interpreter():
    """Fixture que proporciona un intérprete JS limpio para cada test"""
    return Interpreter()


@pytest.fixture
def execute_js():
    """Fixture que ejecuta código JS y retorna el resultado"""
    def _execute(code: str, interpreter=None):
        if interpreter is None:
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


class TestBreakStatement:
    """Tests para el statement break"""
    
    def test_break_in_while_loop(self, execute_js):
        """Break debe salir del while loop"""
        code = """
        var i = 0;
        while (true) {
            if (i == 3) {
                break;
            }
            i++;
        }
        i;
        """
        assert execute_js(code) == 3
    
    def test_break_in_for_loop(self, execute_js):
        """Break debe salir del for loop"""
        code = """
        var sum = 0;
        for (var i = 0; i < 10; i++) {
            if (i == 5) {
                break;
            }
            sum = sum + i;
        }
        sum;
        """
        assert execute_js(code) == 10  # 0+1+2+3+4
    
    def test_break_nested_loops(self, execute_js):
        """Break solo debe salir del loop más interno"""
        code = """
        var result = 0;
        for (var i = 0; i < 3; i++) {
            for (var j = 0; j < 3; j++) {
                if (i == 1 && j == 1) {
                    break;
                }
                result = result + 1;
            }
        }
        result;
        """
        assert execute_js(code) == 7
    
    def test_break_in_do_while(self, execute_js):
        """Break en do-while (cuando esté implementado)"""
        code = """
        var i = 0;
        while (true) {
            i++;
            if (i == 5) {
                break;
            }
        }
        i;
        """
        assert execute_js(code) == 5


class TestContinueStatement:
    """Tests para el statement continue"""
    
    def test_continue_in_while_loop(self, execute_js):
        """Continue debe saltar a la siguiente iteración"""
        code = """
        var i = 0;
        while (i < 5) {
            i++;
            if (i == 3) {
                continue;
            }
        }
        i;
        """
        assert execute_js(code) == 5
    
    def test_continue_in_for_loop_skips_body(self, execute_js):
        """Continue en for debe saltar el body pero ejecutar el increment"""
        code = """
        var sum = 0;
        for (var i = 0; i < 5; i++) {
            if (i == 2) {
                continue;
            }
            sum = sum + i;
        }
        sum;
        """
        # 0 + 1 + 3 + 4 = 8 (salta el 2)
        assert execute_js(code) == 8
    
    def test_continue_executes_increment(self, execute_js):
        """Continue DEBE ejecutar el increment del for"""
        code = """
        var count = 0;
        for (var i = 0; i < 3; i++) {
            if (i == 1) {
                continue;
            }
            count = count + 1;
        }
        count;
        """
        # Entra 2 veces (i=0, i=2), salta i=1
        assert execute_js(code) == 2
    
    def test_continue_nested_loops(self, execute_js):
        """Continue solo afecta el loop más interno"""
        code = """
        var result = 0;
        for (var i = 0; i < 2; i++) {
            for (var j = 0; j < 3; j++) {
                if (j == 1) {
                    continue;
                }
                result = result + 1;
            }
        }
        result;
        """
        # Cada i: j=0,2 (salta j=1) = 2 iteraciones
        # 2 valores de i × 2 = 4
        assert execute_js(code) == 4


class TestBreakContinueCombined:
    """Tests combinados de break y continue"""
    
    def test_break_and_continue_together(self, execute_js):
        """Break y continue en el mismo loop"""
        code = """
        var sum = 0;
        for (var i = 0; i < 10; i++) {
            if (i == 2) {
                continue;
            }
            if (i == 7) {
                break;
            }
            sum = sum + i;
        }
        sum;
        """
        # 0 + 1 + 3 + 4 + 5 + 6 = 19 (salta 2, rompe en 7)
        assert execute_js(code) == 19
    
    def test_multiple_nested_breaks_continues(self, execute_js):
        """Múltiples breaks y continues en loops anidados"""
        code = """
        var result = 0;
        for (var i = 0; i < 4; i++) {
            if (i == 3) {
                break;
            }
            for (var j = 0; j < 4; j++) {
                if (j == 1) {
                    continue;
                }
                if (j == 3) {
                    break;
                }
                result = result + 1;
            }
        }
        result;
        """
        # Por cada i (0,1,2): j entra (0,2) = 2
        # 3 × 2 = 6
        assert execute_js(code) == 6


class TestEdgeCases:
    """Tests de casos edge"""
    
    def test_break_at_start(self, execute_js):
        """Break al inicio del loop"""
        code = """
        var i = 0;
        while (true) {
            break;
            i++;
        }
        i;
        """
        assert execute_js(code) == 0
    
    def test_continue_at_start(self, execute_js):
        """Continue al inicio del loop"""
        code = """
        var i = 0;
        while (i < 3) {
            continue;
            i++;
        }
        i;
        """
        # Infinito porque i nunca incrementa... pero con timeout debería fallar
        # Por ahora lo omitimos
        pass
    
    def test_break_in_if_inside_loop(self, execute_js):
        """Break dentro de if dentro de loop"""
        code = """
        var i = 0;
        while (true) {
            if (true) {
                if (i == 2) {
                    break;
                }
            }
            i++;
        }
        i;
        """
        assert execute_js(code) == 2
    
    def test_sum_with_break_and_continue(self, execute_js):
        """Test realista: sumar números filtrando con continue y parando con break"""
        code = """
        var sum = 0;
        for (var i = 1; i <= 10; i++) {
            if (i % 2 == 0) {
                continue;
            }
            if (i > 7) {
                break;
            }
            sum = sum + i;
        }
        sum;
        """
        # Números impares: 1, 3, 5, 7 = 16
        assert execute_js(code) == 16