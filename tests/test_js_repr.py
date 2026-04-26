import math

from JSValues import UNDEFINED, js_repr


def test_js_repr_booleans():
    assert js_repr(True) == "true"
    assert js_repr(False) == "false"


def test_js_repr_null():
    assert js_repr(None) == "null"


def test_js_repr_undefined():
    assert js_repr(UNDEFINED) == "undefined"


def test_js_repr_nan():
    assert js_repr(float("nan")) == "NaN"


def test_js_repr_integer_float():
    assert js_repr(3.0) == "3"
    assert js_repr(3.5) == "3.5"


def test_js_repr_string():
    assert js_repr("hello") == "hello"
