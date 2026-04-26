import pytest
import math

from Resolver import Resolver
from Scanner import Scanner
from Parser import Parser
from Interpreter import Interpreter
from Token import TokenType
from JSValues import UNDEFINED


def eval_first(src: str):
    tokens = Scanner(src).scan()
    exprs = Parser(tokens).parse()
    interp = Interpreter()
    resolver = Resolver(interp)
    for expr in exprs:
        resolver.resolve(expr)

    return interp.interpret(exprs)


def test_arithmetic_add():
    assert eval_first("2+2") == 4


def test_arithmetic_precedence():
    assert eval_first("2+3*4") == 14


def test_grouping_and_unary():
    assert eval_first("-(1 + 2) * 3") == -9


def test_string_concat():
    assert eval_first('"a" + "b"') == "ab"


def test_boolean_literals():
    assert eval_first("true") is True
    assert eval_first("false") is False


def test_number_literal():
    assert eval_first("123.45") == 123.45


def test_equality_operators():
    assert eval_first("1 == 1") is True
    assert eval_first("1 == 2") is False
    assert eval_first("1 != 2") is True
    assert eval_first("2 != 2") is False


"""def test_variable_assignment():
    assert eval_first("x = 1; x + 2") == 3"""


def test_equality():
    assert eval_first("1 == 1") is True
    assert eval_first("1 == 2") is False
    assert eval_first("1 != 2") is True
    assert eval_first("1 != 1") is False


def test_ternary_operator():
    assert eval_first("1 == 1 ? 10 : 20") == 10
    assert eval_first("1 == 2 ? 10 : 20") == 20


def test_logic_short_circuit_or_and_and():
    assert eval_first("true || (1/0)") is True
    assert eval_first("false && (1/0)") is False
    assert eval_first("1 || 2") == 1


def test_postfix_increment():
    assert eval_first("var x = 1; x++; x;") == 2


def test_var_declaration():
    assert eval_first("var x = 2; x;") == 2


def test_function_declaration_and_call():
    assert eval_first("function add(a, b) { return a + b; } add(2, 3);") == 5


def test_if_statement():
    assert eval_first("var x = 0; if (1 == 1) { x = 10; } x;") == 10


def test_while_statement():
    assert eval_first("var i = 0; while (i < 3) { i = i + 1; } i;") == 3


def test_for_statement():
    assert (
        eval_first("var i = 0; for (var j = 0; j < 3; j = j + 1) { i = i + 1; } i;")
        == 3
    )


def test_return_in_function():
    assert eval_first("function f(){ return 7; } f();") == 7


def test_block_scope():
    assert eval_first("var x = 1; { var x = 2; } x;") == 1


def test_undefined_default_value():
    assert eval_first("var x; x;") is UNDEFINED


def test_undefined_literal():
    assert eval_first("undefined;") is UNDEFINED


def test_null_is_not_undefined():
    assert eval_first("null;") is None
    assert eval_first("null;") is not UNDEFINED


def test_js_truthiness_zero_is_falsy():
    assert eval_first("0 ? 1 : 2") == 2


def test_js_truthiness_empty_string_is_falsy():
    assert eval_first('"" ? 1 : 2') == 2


def test_js_truthiness_null_is_falsy():
    assert eval_first("null ? 1 : 2") == 2


def test_js_truthiness_undefined_is_falsy():
    assert eval_first("undefined ? 1 : 2") == 2


def test_js_truthiness_nonzero_is_truthy():
    assert eval_first("1 ? 1 : 2") == 1
    assert eval_first("-1 ? 1 : 2") == 1


def test_js_truthiness_nonempty_string_is_truthy():
    assert eval_first('"a" ? 1 : 2') == 1
    assert eval_first('"0" ? 1 : 2') == 1


def test_js_truthiness_false_is_falsy():
    assert eval_first("false ? 1 : 2") == 2


def test_js_truthiness_true_is_truthy():
    assert eval_first("true ? 1 : 2") == 1


def test_let_basic():
    assert eval_first("let x = 3; x;") == 3


def test_let_block_scope():
    assert eval_first("let x = 1; { let x = 2; } x;") == 1


def test_const_basic():
    assert eval_first("const x = 5; x;") == 5


def test_const_reassignment_raises():
    with pytest.raises(RuntimeError, match="constant"):
        eval_first("const x = 1; x = 2;")


def test_const_redeclaration_raises():
    with pytest.raises(RuntimeError, match="constant"):
        eval_first("const x = 1; var x = 2;")


def test_const_in_block():
    assert eval_first("var x = 1; { const y = 10; } x;") == 1


def test_var_and_let_coexist():
    assert eval_first("var a = 1; let b = 2; a + b;") == 3


def test_nan_literal():
    result = eval_first("NaN;")
    assert math.isnan(result)


def test_nan_is_falsy():
    assert eval_first("NaN ? 1 : 2") == 2


def test_nan_not_equal_to_itself():
    assert eval_first("NaN == NaN") is False


def test_nested_function_same_var_name():
    src = """
    function a() {
        var x = 1;
        function b() {
            var x = 2;
            return x;
        }
        return b() + x;
    }
    a();
    """
    assert eval_first(src) == 3


def test_nested_function_same_const_name():
    src = """
    function a() {
        const x = 1;
        function b() {
            const x = 2;
            return x;
        }
        return b() + x;
    }
    a();
    """
    assert eval_first(src) == 3


def test_let_variable_can_be_reassigned():
    assert eval_first("let x = 1; x = 2; x;") == 2


def test_variable_definition_returns_undefined():
    assert eval_first("var x = 5;") is UNDEFINED


def test_equality_coersion():
    assert eval_first('1 == "1"') is True
    assert eval_first("0 == false") is True
    assert eval_first('"" == false') is True
    assert eval_first("null == undefined") is True
    assert eval_first("0 == null") is False
    assert eval_first("0 == undefined") is False
    assert eval_first('"" == null') is False
    assert eval_first('"" == undefined') is False
    assert eval_first("1 == true") is True
    assert eval_first("NaN == NaN") is False


def test_strict_equality_no_coersion():
    assert eval_first('1 === "1"') is False
    assert eval_first("0 === false") is False
    assert eval_first('"" === false') is False
    assert eval_first("null === undefined") is False
    assert eval_first("0 === null") is False
    assert eval_first("0 === undefined") is False
    assert eval_first('"" === null') is False
    assert eval_first('"" === undefined') is False
    assert eval_first("1 === true") is False
    assert eval_first("NaN === NaN") is False


def test_plus_coercion_string_number():
    assert eval_first('"1" + 2') == "12"
    assert eval_first('1 + "2"') == "12"


def test_minus_coercion_string_number():
    assert eval_first('"3" - 1') == 2
    assert math.isnan(eval_first('"a" - 1'))


def test_multiply_divide_coercion():
    assert eval_first('"3" * "2"') == 6
    assert eval_first('"6" / "3"') == 2
    assert eval_first("1 / 0") == float("inf")
    assert math.isnan(eval_first("0 / 0"))


def test_modulo_coercion():
    assert eval_first('5 % "2"') == 1
    assert math.isnan(eval_first("5 % 0"))


def test_boolean_numeric_coercion():
    assert eval_first("true + 1") == 2
    assert eval_first("false * 2") == 0


def test_relational_string_and_number():
    assert eval_first('"2" > 1') is True
    assert eval_first('"b" > "a"') is True
    assert eval_first('"a" < 2') is False


def test_plus_boolean_concat():
    assert eval_first('true + "!"') == "true!"
