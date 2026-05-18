import pytest
from JSValues import UNDEFINED


class TestCompoundAssignmentOperators:
    """Tests para operadores de asignación compuesta"""
    
    def test_plus_equal_basic(self, execute_js):
        """Prueba += básico"""
        code = """
        var x = 5;
        x += 3;
        x;
        """
        assert execute_js(code) == 8
    
    def test_minus_equal_basic(self, execute_js):
        """Prueba -= básico"""
        code = """
        var x = 10;
        x -= 4;
        x;
        """
        assert execute_js(code) == 6
    
    def test_star_equal_basic(self, execute_js):
        """Prueba *= básico"""
        code = """
        var x = 6;
        x *= 2;
        x;
        """
        assert execute_js(code) == 12
    
    def test_slash_equal_basic(self, execute_js):
        """Prueba /= básico"""
        code = """
        var x = 20;
        x /= 4;
        x;
        """
        assert execute_js(code) == 5
    
    def test_percent_equal_basic(self, execute_js):
        """Prueba %= básico"""
        code = """
        var x = 17;
        x %= 5;
        x;
        """
        assert execute_js(code) == 2
    
    def test_plus_equal_string_concatenation(self, execute_js):
        """Prueba += con strings"""
        code = """
        var str = "hello";
        str += " world";
        str;
        """
        assert execute_js(code) == "hello world"
    
    def test_plus_equal_with_expression(self, execute_js):
        """Prueba += con expresión compleja"""
        code = """
        var x = 5;
        var y = 3;
        x += y * 2;
        x;
        """
        assert execute_js(code) == 11
    
    def test_compound_assignment_with_array_element(self, execute_js):
        """Prueba += en elemento de array"""
        code = """
        var arr = [1, 2, 3];
        arr[0] += 10;
        arr[0];
        """
        assert execute_js(code) == 11
    
    def test_compound_assignment_with_object_property(self, execute_js):
        """Prueba += en propiedad de objeto"""
        code = """
        var obj = {value: 5};
        obj.value += 3;
        obj.value;
        """
        assert execute_js(code) == 8
    
    def test_multiple_compound_assignments(self, execute_js):
        """Prueba múltiples asignaciones compuestas seguidas"""
        code = """
        var x = 10;
        x += 5;
        x -= 3;
        x *= 2;
        x;
        """
        assert execute_js(code) == 24  # ((10 + 5) - 3) * 2 = 24
    
    def test_compound_assignment_with_coercion(self, execute_js):
        """Prueba += con coerción de tipos"""
        code = """
        var x = 5;
        x += "10";
        x;
        """
        assert execute_js(code) == "510"
    
    def test_compound_assignment_let(self, execute_js):
        """Prueba += con let"""
        code = """
        let x = 7;
        x += 2;
        x;
        """
        assert execute_js(code) == 9
    
    def test_compound_assignment_const_raises(self, execute_js):
        """Prueba que += en const lanza error"""
        code = """
        const x = 5;
        x += 3;
        """
        with pytest.raises(RuntimeError, match="constant"):
            execute_js(code)
    
    def test_compound_assignment_returns_value(self, execute_js):
        """Prueba que compound assignment devuelve el valor asignado"""
        code = """
        var x = 5;
        var y = (x += 3);
        y;
        """
        assert execute_js(code) == 8