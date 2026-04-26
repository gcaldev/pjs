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


UNDEFINED = _UndefinedType()
NAN = float("nan")


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
