import pytest


class TestObjectLiterals:
    """Tests para object literals básicos"""
    
    def test_empty_object(self, execute_js):
        code = "var obj = {}; obj;"
        result = execute_js(code)
        assert result == {}
    
    def test_object_single_property(self, execute_js):
        """Objeto con una propiedad"""
        code = """
        var obj = {a: 1};
        obj;
        """
        result = execute_js(code)
        assert result == {"a": 1}
    
    def test_object_multiple_properties(self, execute_js):
        """Objeto con múltiples propiedades"""
        code = """
        var obj = {a: 1, b: 2, c: 3};
        obj;
        """
        result = execute_js(code)
        assert result == {"a": 1, "b": 2, "c": 3}
    
    def test_object_string_keys(self, execute_js):
        """Objeto con keys entre comillas"""
        code = """
        var obj = {"name": "Julian", "age": 25};
        obj;
        """
        result = execute_js(code)
        assert result == {"name": "Julian", "age": 25}
    
    def test_object_mixed_types(self, execute_js):
        """Objeto con diferentes tipos de valores"""
        code = """
        var obj = {a: 1, b: "hello", c: true, d: null};
        obj;
        """
        result = execute_js(code)
        assert result == {"a": 1, "b": "hello", "c": True, "d": None}
    
    def test_object_with_expressions(self, execute_js):
        """Objeto con expresiones como valores"""
        code = """
        var x = 5;
        var obj = {a: x + 1, b: x * 2, c: x > 3};
        obj;
        """
        result = execute_js(code)
        assert result == {"a": 6, "b": 10, "c": True}
    
    def test_object_trailing_comma(self, execute_js):
        """Objeto con coma al final"""
        code = """
        var obj = {a: 1, b: 2,};
        obj;
        """
        result = execute_js(code)
        assert result == {"a": 1, "b": 2}
    
    def test_nested_objects(self, execute_js):
        """Objetos anidados"""
        code = """
        var obj = {a: 1, b: {c: 2, d: 3}};
        obj;
        """
        result = execute_js(code)
        assert result == {"a": 1, "b": {"c": 2, "d": 3}}
    
    def test_object_assignment_to_variable(self, execute_js):
        """Asignar objeto a variable"""
        code = """
        var obj = {x: 10, y: 20};
        obj;
        """
        result = execute_js(code)
        assert result == {"x": 10, "y": 20}


class TestObjectWithMemberAccess:
    """Tests combinando object literals con member access"""
    
    def test_object_dot_access(self, execute_js):
        """Acceder a propiedad con dot notation"""
        code = """
        var obj = {name: "Julian", age: 25};
        obj.name;
        """
        assert execute_js(code) == "Julian"
    
    def test_object_bracket_access(self, execute_js):
        """Acceder a propiedad con bracket notation"""
        code = """
        var obj = {name: "Julian"};
        obj["name"];
        """
        assert execute_js(code) == "Julian"
    
    def test_object_property_assignment(self, execute_js):
        """Asignar valor a propiedad"""
        code = """
        var obj = {name: "Julian"};
        obj.name = "Carlos";
        obj.name;
        """
        assert execute_js(code) == "Carlos"
    
    def test_object_new_property_assignment(self, execute_js):
        """Crear nueva propiedad asignando"""
        code = """
        var obj = {a: 1};
        obj.b = 2;
        obj.b;
        """
        assert execute_js(code) == 2
    
    def test_object_property_undefined(self, execute_js):
        """Acceder a propiedad inexistente"""
        code = """
        var obj = {a: 1};
        obj.b;
        """
        from JSValues import UNDEFINED
        assert execute_js(code) is UNDEFINED
    
    def test_nested_object_access(self, execute_js):
        """Acceder a propiedades anidadas"""
        code = """
        var obj = {user: {name: "Julian", age: 25}};
        obj.user.name;
        """
        assert execute_js(code) == "Julian"
    
    def test_object_with_array_property(self, execute_js):
        """Objeto con propiedad que es un array"""
        code = """
        var obj = {items: [1, 2, 3]};
        obj.items[1];
        """
        assert execute_js(code) == 2
    
    def test_array_with_object_elements(self, execute_js):
        """Array de objetos"""
        code = """
        var arr = [{name: "Julian"}, {name: "Carlos"}];
        arr[0].name;
        """
        assert execute_js(code) == "Julian"


class TestComplexObjects:
    """Tests para casos complejos"""
    
    def test_object_with_multiple_access_chains(self, execute_js):
        """Cadenas complejas de acceso"""
        code = """
        var data = {
            users: [
                {profile: {name: "Julian"}},
                {profile: {name: "Carlos"}}
            ]
        };
        data.users[1].profile.name;
        """
        assert execute_js(code) == "Carlos"
    
    def test_object_modifications(self, execute_js):
        """Múltiples modificaciones de objeto"""
        code = """
        var obj = {a: 1, b: 2};
        obj.a = 10;
        obj.c = 30;
        obj.a + obj.b + obj.c;
        """
        assert execute_js(code) == 42
    
    def test_object_in_function(self, execute_js):
        """Usar objetos en funciones"""
        code = """
        function createPerson(name, age) {
            return {name: name, age: age};
        }
        var person = createPerson("Julian", 25);
        person.name;
        """
        assert execute_js(code) == "Julian"


class TestObjectEdgeCases:
    """Tests para casos edge"""
    
    def test_object_literal_expression(self, execute_js):
        """Object literal en expresión directa"""
        code = """
        {a: 1, b: 2}.a;
        """
        assert execute_js(code) == 1
    
    def test_object_number_keys(self, execute_js):
        """Objeto con number keys"""
        code = """
        var obj = {1: "one", 2: "two"};
        obj;
        """
        result = execute_js(code)
        # Los number keys se convierten a strings
        assert result == {"1": "one", "2": "two"}
    
    def test_deeply_nested_objects(self, execute_js):
        """Objetos muy anidados"""
        code = """
        var obj = {a: {b: {c: {d: {e: 1}}}}};
        obj.a.b.c.d.e;
        """
        assert execute_js(code) == 1