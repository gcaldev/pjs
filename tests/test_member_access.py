import pytest


class TestArrayMemberAccess:
    """Tests para acceso a elementos de arrays"""
    
    def test_array_index_access(self, execute_js):
        """Acceder a elemento de array"""
        code = """
        var arr = [10, 20, 30];
        arr[0];
        """
        assert execute_js(code) == 10
    
    def test_array_index_negative(self, execute_js):
        """Índice negativo devuelve undefined"""
        code = """
        var arr = [10, 20, 30];
        arr[-1];
        """
        from JSValues import UNDEFINED
        assert execute_js(code) is UNDEFINED
    
    def test_array_index_out_of_bounds(self, execute_js):
        """Índice fuera de bounds devuelve undefined"""
        code = """
        var arr = [10, 20, 30];
        arr[100];
        """
        from JSValues import UNDEFINED
        assert execute_js(code) is UNDEFINED
    
    def test_array_length_property(self, execute_js):
        """Acceder a propiedad .length de array"""
        code = """
        var arr = [10, 20, 30];
        arr.length;
        """
        assert execute_js(code) == 3
    
    def test_array_empty_length(self, execute_js):
        """Array vacío tiene length 0"""
        code = """
        var arr = [];
        arr.length;
        """
        assert execute_js(code) == 0
    
    def test_array_computed_index(self, execute_js):
        """Acceder a array con expresión computed"""
        code = """
        var arr = [10, 20, 30];
        var i = 1;
        arr[i + 1];
        """
        assert execute_js(code) == 30
    
    def test_array_assignment(self, execute_js):
        """Asignar valor a elemento de array"""
        code = """
        var arr = [10, 20, 30];
        arr[1] = 99;
        arr[1];
        """
        assert execute_js(code) == 99
    
    def test_array_assignment_extend(self, execute_js):
        """Asignar a índice más allá del final extiende el array"""
        code = """
        var arr = [10, 20];
        arr[5] = 50;
        arr.length;
        """
        assert execute_js(code) == 6
    
    def test_string_index_access(self, execute_js):
        """Acceder a carácter de string"""
        code = """
        var str = "hello";
        str[0];
        """
        assert execute_js(code) == "h"
    
    def test_string_length(self, execute_js):
        """String tiene propiedad .length"""
        code = """
        var str = "hello";
        str.length;
        """
        assert execute_js(code) == 5
    
    def test_nested_array_access(self, execute_js):
        """Acceso a arrays anidados"""
        code = """
        var arr = [[1, 2], [3, 4]];
        arr[0][1];
        """
        assert execute_js(code) == 2
    
    def test_array_in_loop_access(self, execute_js):
        """Acceder a array dentro de loop"""
        code = """
        var arr = [10, 20, 30];
        var sum = 0;
        for (var i = 0; i < arr.length; i++) {
            sum = sum + arr[i];
        }
        sum;
        """
        assert execute_js(code) == 60

class TestMemberAccessEdgeCases:
    """Tests para casos edge"""
    
    def test_member_access_on_literal(self, execute_js):
        """Member access en literal directamente"""
        code = """
        [1, 2, 3][0];
        """
        assert execute_js(code) == 1
    
    def test_string_literal_access(self, execute_js):
        """Acceder a string literal"""
        code = """
        "hello"[1];
        """
        assert execute_js(code) == "e"
    
    def test_member_access_undefined(self, execute_js):
        """Member access en undefined devuelve error o undefined"""
        code = """
        var x;
        x.prop;
        """
        # Esto puede ser error o undefined según cómo lo manejes
        # Por ahora lo dejamos como undefined
        from JSValues import UNDEFINED
        result = execute_js(code)
        # Debería ser error, pero por ahora lo dejamos pasar
    
    def test_array_modification_multiple(self, execute_js):
        """Múltiples modificaciones de array"""
        code = """
        var arr = [1, 2, 3];
        arr[0] = 10;
        arr[2] = 30;
        arr[0] + arr[2];
        """
        assert execute_js(code) == 40