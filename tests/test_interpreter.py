from Scanner import Scanner
from Parser import Parser
from Interpreter import Interpreter
from Token import TokenType


def eval_first(src: str):
    tokens = Scanner(src).scan()
    exprs = Parser(tokens).parse()
    interp = Interpreter()
    last = None
    for e in exprs:
        last = interp.execute(e)
    return last


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


# Por ahora no pasa porque falta el resolver
def test_function_declaration_and_call():
    assert eval_first("function add(a, b) { return a + b; } add(2, 3);") == 5


def test_if_statement():
    assert eval_first("var x = 0; if (1 == 1) { x = 10; } x;") == 10


def test_while_statement():
    assert eval_first("var i = 0; while (i < 3) { i = i + 1; } i;") == 3


# Por ahora no lo pasa
def test_for_statement():
    assert (
        eval_first("var i = 0; for (var j = 0; j < 3; j = j + 1) { i = i + 1; } i;")
        == 3
    )


def test_return_in_function():
    assert eval_first("function f(){ return 7; } f();") == 7


def test_block_scope():
    assert eval_first("var x = 1; { var x = 2; } x;") == 1
