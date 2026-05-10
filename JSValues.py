import math


class _UndefinedType:
    _instance = None

    def __new__(clazz):
        if clazz._instance is None:
            clazz._instance = super().__new__(clazz)
        return clazz._instance

    def __repr__(self) -> str:
        return "undefined"

    def __bool__(self) -> bool:
        return False


class _TDZType:
    _instance = None

    def __new__(clazz):
        if clazz._instance is None:
            clazz._instance = super().__new__(clazz)
        return clazz._instance

    def __repr__(self) -> str:
        return "<TDZ>"


class TDZError(RuntimeError):
    """Error lanzado al acceder a una variable en Temporal Dead Zone."""

    pass


UNDEFINED = _UndefinedType()
TDZ = _TDZType()
NAN = float("nan")


def typeof_value(value) -> str:
    if value is UNDEFINED:
        return "undefined"
    if value is None:
        return "object"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if callable(value):
        return "function"
    return "object"


def js_repr(value) -> str:
    """Convierte un valor runtime a su representación string de JavaScript."""
    if value is UNDEFINED:
        return "undefined"
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        if math.isnan(value):
            return "NaN"
        if math.isinf(value):
            return "Infinity" if value > 0 else "-Infinity"
        if value == int(value):
            # Si es un float entero lo muestro sin el punto decimal
            return str(int(value))
        return str(value)
    if isinstance(value, int):
        return str(value)
    return str(value)
