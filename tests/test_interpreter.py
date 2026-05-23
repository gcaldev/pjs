import re
import sys
import pytest
import math
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Resolver import Resolver
from Scanner import Scanner
from Parser import Parser
from Interpreter import Interpreter
from Token import TokenType
from JSValues import UNDEFINED
from Function import Function


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


def test_hoised_variable_is_undefined():
    assert eval_first("x; var x = 5;") is UNDEFINED


def test_hoised_variable_in_function():
    src = """
    function f() {
        return x;
        var x = 10;
    }
    f();
    """
    assert eval_first(src) is UNDEFINED


def test_hoised_nested_if_variable():
    src = """
    function f() {
        if(true){
            var x = 3;
        }
        return x;
    }
    f();
    """
    assert eval_first(src) == 3


def test_function_overrides_var():
    src = """
    var a = 1;
    function a() { return 2; }
    a;
    """
    assert callable(eval_first(src))


def test_var_overrides_function_in_execution():
    src = """
    function a() { return 2; }
    var a = 1;
    a;
    """
    assert eval_first(src) == 1


def test_function_and_let_conflict():
    with pytest.raises(RuntimeError):
        eval_first("""
        function a() {}
        let a = 1;
        """)


def test_let_shadowing():
    with pytest.raises(RuntimeError):
        eval_first("""
        let x = 1;
        {
            x;
            let x = 2;
        }
        """)


def test_typeof_tdz_throws():
    with pytest.raises(RuntimeError):
        eval_first("""
        typeof x;
        let x = 1;
        """)


def test_param_vs_var():
    src = """
    function f(x) {
        var x = 2;
        return x;
    }
    f(1);
    """
    assert eval_first(src) == 2


def test_param_read_before_var():
    src = """
    function f(x) {
        return x;
        var x = 2;
    }
    f(1);
    """
    assert eval_first(src) == 1


def test_multiple_var_hoisting():
    src = """
    function f() {
        x = 1;
        var x;
        return x;
    }
    f();
    """
    assert eval_first(src) == 1


def test_var_redeclaration():
    src = """
    var x = 1;
    var x = 2;
    x;
    """
    assert eval_first(src) == 2


def test_var_let_conflict():
    with pytest.raises(RuntimeError):
        eval_first("""
        let x = 1;
        var x = 2;
        """)


def test_function_inside_block_scope():
    src = """
    {
        function f() { return 1; }
    }
    f();
    """
    assert eval_first(src) == 1


def test_nested_shadow():
    with pytest.raises(RuntimeError):
        eval_first("""
        let x = 1;
        function f() {
            x;
            let x = 2;
        }
        f();
        """)


def test_function_expression_not_hoisted():
    with pytest.raises(RuntimeError):
        eval_first("""
        f();
        let f = function() { return 1; };
        """)


def test_closure_with_hoisting():
    src = """
    function outer() {
        return inner();
        function inner() { return 2; }
    }
    outer();
    """
    assert eval_first(src) == 2


def test_var_used_before_assignment():
    src = """
    function f() {
        return x;
        var x = 5;
    }
    f();
    """
    assert eval_first(src) is UNDEFINED


def test_let_in_for_scope():
    src = """
    let x = 0;
    for (let i = 0; i < 3; i = i + 1) {
        x = x + i;
    }
    x;
    """
    assert eval_first(src) == 3


def test_return_before_var():
    src = """
    function f() {
        return x;
        var x = 10;
    }
    f();
    """
    assert eval_first(src) is UNDEFINED


def test_inner_function_hoisting():
    src = """
    function f() {
        return g();
        function g() { return 3; }
    }
    f();
    """
    assert eval_first(src) == 3


def test_function_priority_over_var():
    src = """
    function a() { return 1; }
    var a;
    a();
    """
    assert eval_first(src) == 1


def test_var_shadowing():
    src = """
    var x = 1;
    function f() {
        var x = 2;
        function g() {
            return x;
        }
        return g();
    }
    f();
    """
    assert eval_first(src) == 2


def test_global_vs_local_hoisting():
    src = """
    var x = 1;
    function f() {
        return x;
        var x = 2;
    }
    f();
    """
    assert eval_first(src) is UNDEFINED


def test_template_literal_basic():
    assert eval_first("`hola`") == "hola"


def test_template_literal_with_expression():
    assert eval_first("`hola ${1 + 2}`") == "hola 3"


def test_template_literal_multiple_expressions():
    assert eval_first("`${1}${2}${3}`") == "123"


def test_template_literal_variable_interpolation():
    assert eval_first("var x = 5; `x = ${x}`;") == "x = 5"


def test_template_literal_string_expression():
    assert eval_first('`hola ${"mundo"}`') == "hola mundo"


def test_template_literal_boolean_expression():
    assert eval_first("`valor: ${true}`") == "valor: true"
    assert eval_first("`valor: ${false}`") == "valor: false"


def test_template_literal_null_and_undefined():
    assert eval_first("`a=${null}`") == "a=null"
    assert eval_first("`b=${undefined}`") == "b=undefined"


def test_template_literal_nested_arithmetic():
    assert eval_first("`resultado=${1 + 2 * 3}`") == "resultado=7"


def test_template_literal_function_call():
    src = """
    function add(a, b) {
        return a + b;
    }
    `sum=${add(2, 3)}`;
    """
    assert eval_first(src) == "sum=5"


def test_template_literal_multiple_lines():
    src = "`hola\\nmundo`"
    assert eval_first(src) == "hola\nmundo"


def test_template_literal_empty():
    assert eval_first("``") == ""


def test_template_literal_only_expression():
    assert eval_first("`${10}`") == "10"


def test_template_literal_expression_with_ternary():
    assert eval_first("`${true ? 'a' : 'b'}`") == "a"


def test_template_literal_expression_with_concat():
    assert eval_first('`${"a" + "b"}`') == "ab"


def test_template_literal_nested_template():
    assert eval_first("`${`hola ${1 + 1}`}`") == "hola 2"


def test_template_literal_with_nan():
    result = eval_first("`valor=${NaN}`")
    assert result == "valor=NaN"


def test_template_literal_with_postfix_increment():
    src = """
    var x = 1;
    `x=${x++}, after=${x}`;
    """
    assert eval_first(src) == "x=1, after=2"


def test_template_literal_preserves_spaces():
    assert eval_first("`  hola ${1}  `") == "  hola 1  "


def test_template_literal_with_object_like_string():
    assert eval_first('`[${"a"}, ${"b"}]`') == "[a, b]"


def test_template_literal_inside_function():
    src = """
    function greet(name) {
        return `hola ${name}`;
    }
    greet("juan");
    """
    assert eval_first(src) == "hola juan"


def test_unterminated_template_literal():
    with pytest.raises(Exception, match="Unterminated template literal"):
        eval_first("`hola")


def test_unterminated_template_expression():
    with pytest.raises(Exception, match="Unterminated template literal"):
        eval_first("`hola ${1 + 2`")


def test_missing_expression_inside_template():
    with pytest.raises(
        Exception,
        match=re.escape("[Line 1] Error at '': Expect expression"),
    ):
        eval_first("`hola ${}`")


def test_nullish_coalescing_null_returns_right():
    assert eval_first("null ?? 5;") == 5


def test_nullish_coalescing_undefined_returns_right():
    assert eval_first("undefined ?? 10;") == 10


def test_nullish_coalescing_zero_returns_left():
    assert eval_first("0 ?? 5;") == 0


def test_nullish_coalescing_false_returns_left():
    assert eval_first("false ?? true;") == False


def test_nullish_coalescing_empty_string_returns_left():
    assert eval_first('"" ?? "fallback";') == ""


def test_nullish_coalescing_nan_returns_left():
    assert math.isnan(eval_first("NaN ?? 42;"))


def test_nullish_coalescing_left_to_right():
    assert eval_first("null ?? undefined ?? 7;") == 7


def test_nullish_coalescing_short_circuit():
    assert eval_first("""
        var x = 0;
        function inc() {
            x = x + 1;
            return 99;
        }

        1 ?? inc();
        x;
    """) == 0


def test_nullish_coalescing_evaluates_right_when_needed():
    assert eval_first("""
        var x = 0;
        function inc() {
            x = x + 1;
            return 99;
        }

        null ?? inc();
        x;
    """) == 1


def test_nullish_coalescing_with_variable():
    assert eval_first("""
        let a = undefined;
        a ?? "default";
    """) == "default"


def test_nullish_coalescing_with_assignment():
    assert eval_first("""
        let a = null;
        let b = a ?? 20;
        b;
    """) == 20


def test_nullish_coalescing_with_function_left_returns_function():
    assert isinstance(
        eval_first("""
        function f() {}
        f ?? 123;
    """),
        Function,
    )


def test_nullish_coalescing_with_nested_expression():
    assert eval_first("""
        (null ?? 2) + 3;
    """) == 5


def test_nullish_coalescing_precedence_with_or():
    assert eval_first("""
        null || undefined ?? 5;
    """) == 5


def test_nullish_coalescing_precedence_with_and():
    assert eval_first("""
        true && null ?? 8;
    """) == 8


def test_nullish_coalescing_with_ternary():
    assert eval_first("""
        true ? null ?? 7 : 0;
    """) == 7


def test_arrow_single_param_expression_body():
    assert eval_first("const f = x => x + 1; f(5);") == 6


def test_arrow_multi_param_expression_body():
    assert eval_first("const add = (a, b) => a + b; add(3, 4);") == 7


def test_arrow_no_params_expression_body():
    assert eval_first("const f = () => 99; f();") == 99


def test_arrow_block_body_explicit_return():
    assert eval_first("const f = x => { return x * 2; }; f(6);") == 12


def test_arrow_block_body_no_return_is_undefined():
    assert eval_first("const f = () => { 1 + 1; }; f();") is UNDEFINED


def test_arrow_implicit_return_is_expression_value():
    assert eval_first("const f = x => x * x; f(4);") == 16


def test_arrow_closes_over_outer_variable():
    assert eval_first("""
        let x = 10;
        const f = () => x;
        f();
    """) == 10


def test_arrow_closes_over_outer_variable_after_mutation():
    assert eval_first("""
        let x = 1;
        const f = () => x;
        x = 42;
        f();
    """) == 42


def test_arrow_as_argument():
    assert eval_first("""
        function apply(f, x) { return f(x); }
        apply(n => n + 1, 9);
    """) == 10


def test_arrow_returning_arrow():
    assert eval_first("""
        const add = a => b => a + b;
        add(3)(4);
    """) == 7


def test_arrow_nested():
    assert eval_first("""
        const outer = x => {
            const inner = y => x + y;
            return inner(2);
        };
        outer(5);
    """) == 7


def test_arrow_with_ternary_body():
    assert eval_first("""
        const abs = x => x < 0 ? -x : x;
        abs(-7);
    """) == 7


def test_arrow_with_template_literal_body():
    assert eval_first("""
        const greet = name => `hola ${name}`;
        greet("mundo");
    """) == "hola mundo"


def test_arrow_is_function_instance():
    assert isinstance(eval_first("const f = x => x; f;"), Function)


def test_arrow_multi_statement_block():
    assert eval_first("""
        const f = x => {
            let y = x * 2;
            return y + 1;
        };
        f(3);
    """) == 7


def test_arrow_immediately_invoked():
    assert eval_first("(x => x + 1)(10);") == 11


def test_arrow_no_params_immediately_invoked():
    assert eval_first("(() => 42)();") == 42
