import pytest


class TestArrayLiterals:
    """Tests para array literals"""
    
    def test_empty_array(self, execute_js):
        """Array vacío"""
        code = "[];"
        result = execute_js(code)
        assert result == []
    
    def test_array_with_numbers(self, execute_js):
        """Array con números"""
        code = "[1, 2, 3];"
        result = execute_js(code)
        assert result == [1, 2, 3]
    
    def test_array_with_strings(self, execute_js):
        """Array con strings"""
        code = '["a", "b", "c"];'
        result = execute_js(code)
        assert result == ["a", "b", "c"]
    
    def test_array_with_mixed_types(self, execute_js):
        """Array con tipos mixtos"""
        code = '[1, "hello", true, null];'
        result = execute_js(code)
        assert result == [1, "hello", True, None]
    
    def test_array_with_expressions(self, execute_js):
        """Array con expresiones"""
        code = """
        var x = 5;
        var y = 10;
        [x, y + 2, x * y];
        """
        result = execute_js(code)
        assert result == [5, 12, 50]
    
    def test_nested_arrays(self, execute_js):
        """Arrays anidados"""
        code = "[1, [2, 3], [4, [5, 6]]];"
        result = execute_js(code)
        assert result == [1, [2, 3], [4, [5, 6]]]
    
    def test_array_with_function_calls(self, execute_js):
        """Array con llamadas a funciones"""
        code = """
        function add(a, b) {
            return a + b;
        }
        [add(1, 2), add(3, 4)];
        """
        result = execute_js(code)
        assert result == [3, 7]
    
    def test_array_with_undefined(self, execute_js):
        """Array con undefined"""
        code = "[undefined, null];"
        result = execute_js(code)
        from JSValues import UNDEFINED
        assert result[0] is UNDEFINED
        assert result[1] is None
    
    def test_array_trailing_comma(self, execute_js):
        """Array con coma al final (JS permite)"""
        code = "[1, 2, 3,];"
        result = execute_js(code)
        assert result == [1, 2, 3]
    
    def test_array_assignment_to_variable(self, execute_js):
        """Asignar array a variable"""
        code = """
        var arr = [10, 20, 30];
        arr;
        """
        result = execute_js(code)
        assert result == [10, 20, 30]
    
    def test_multiple_arrays(self, execute_js):
        """Múltiples arrays en expresiones"""
        code = """
        var a = [1, 2];
        var b = [3, 4];
        [a, b];
        """
        result = execute_js(code)
        assert result == [[1, 2], [3, 4]]


class TestArrayExpressions:
    """Tests para expresiones dentro de arrays"""
    
    def test_array_with_ternary(self, execute_js):
        """Array con operador ternario"""
        code = """
        var x = 5;
        [x > 3 ? "big" : "small", x];
        """
        result = execute_js(code)
        assert result == ["big", 5]
    
    def test_array_with_logical_operators(self, execute_js):
        """Array con operadores lógicos"""
        code = """
        var x = true;
        var y = false;
        [x && y, x || y];
        """
        result = execute_js(code)
        assert result == [False, True]


class TestArrayEdgeCases:
    """Tests para casos edge"""
    
    def test_array_in_loop(self, execute_js):
        """Array creado dentro de loop"""
        code = """
        var result = [];
        for (var i = 0; i < 3; i++) {
            result = [i];
        }
        result;
        """
        result = execute_js(code)
        assert result == [2]
    
    def test_deeply_nested_arrays(self, execute_js):
        """Arrays muy anidados"""
        code = """
        [[[[[1]]]]];
        """
        result = execute_js(code)
        assert result == [[[[[1]]]]]