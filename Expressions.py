from Token import Token, TokenLiteralType


class Expressions(object):
    pass


class Binary(Expressions):
    def __init__(self, left: Expressions, operator: Token, right: Expressions):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"Binary({self.left}, {self.operator}, {self.right})"


class Grouping(Expressions):
    def __init__(self, expression: Expressions):
        self.expression = expression

    def __repr__(self):
        return f"Grouping({self.expression})"


class Literal(Expressions):
    def __init__(self, value: TokenLiteralType):
        self.value = value

    def __repr__(self) -> str:
        if isinstance(self.value, str):
            return f"Literal('{self.value}')"
        if isinstance(self.value, bool):
            return f"Literal({str(self.value).lower()})"
        if isinstance(self.value, (int, float)):
            return f"Literal({self.value})"
        if self.value is None:
            return "Literal(null)"

        return f"Literal({self.value})"


class Unary(Expressions):
    def __init__(self, operator: Token, right: Expressions):
        self.operator = operator
        self.right = right

    def __repr__(self) -> str:
        return f"Unary({self.operator}, {self.right})"


class Call(Expressions):
    def __init__(self, callee: Expressions, arguments: list[Expressions]):
        self.callee = callee
        self.arguments = arguments

    def __repr__(self) -> str:
        args = ", ".join(str(arg) for arg in self.arguments)
        return f"Call({self.callee}, [{args}])"


class Variable(Expressions):
    def __init__(self, name: Token):
        self.name = name

    def __repr__(self) -> str:
        return f"Variable({self.name.lexeme})"


class Assignment(Expressions):
    def __init__(self, name_or_member, value: Expressions):
        self.name_or_member = name_or_member  # Puede ser Token o MemberExpression
        self.value = value
        # Para compatibilidad con código viejo, pq puede ser Token o Member
        self.name = name_or_member if isinstance(name_or_member, Token) else None

    def __repr__(self) -> str:
        if isinstance(self.name_or_member, Token):
            return f"Assignment({self.name_or_member.lexeme}, {self.value})"
        return f"Assignment({self.name_or_member}, {self.value})"


class Logic(Expressions):
    def __init__(self, left: Expressions, operator: Token, right: Expressions):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self) -> str:
        return f"Logic({self.left}, {self.operator}, {self.right})"


class Postfix(Expressions):
    def __init__(self, left: Expressions, operator: Token):
        self.left = left
        self.operator = operator

    def __repr__(self) -> str:
        return f"Postfix({self.left}, {self.operator})"


class Ternary(Expressions):
    def __init__(
        self,
        condition: Expressions,
        true_branch: Expressions,
        false_branch: Expressions,
    ):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

    def __repr__(self) -> str:
        return f"Ternary({self.condition}, {self.true_branch}, {self.false_branch})"


class FunctionExpr(Expressions):
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body

    def __repr__(self) -> str:
        params = ", ".join(p.lexeme for p in self.parameters)
        name = self.name.lexeme if self.name else "(anonymous)"
        return f"FunctionExpr({name}({params}))"


class ArrayExpression(Expressions):
    """
    Representa un array literal: [1, 2, 3]

    elements: list[Expressions] - los elementos del array
    """

    def __init__(self, elements: list["Expressions"]):
        self.elements = elements

    def __repr__(self) -> str:
        elems = ", ".join(str(e) for e in self.elements)
        return f"ArrayExpression([{elems}])"


class MemberExpression(Expressions):
    """
    Representa acceso a miembro: arr[0], obj.prop, obj[expr]

    object: Expressions - el objeto/array del cual accedemos
    property: Expressions - la propiedad (para bracket notation)
    computed: bool - True si es bracket notation [expr], False si es dot notation .prop

    Ejemplos:
        arr[0]          → MemberExpression(Variable(arr), Literal(0), computed=True)
        obj.name        → MemberExpression(Variable(obj), Literal("name"), computed=False)
        obj[key]        → MemberExpression(Variable(obj), Variable(key), computed=True)
        arr[i + 1]      → MemberExpression(Variable(arr), Binary(...), computed=True)
    """

    def __init__(self, object: Expressions, property: Expressions, computed: bool):
        self.object = object
        self.property = property
        self.computed = computed

    def __repr__(self) -> str:
        if self.computed:
            return f"MemberExpression({self.object}[{self.property}])"
        return f"MemberExpression({self.object}.{self.property})"


class ObjectLiteral(Expressions):
    """
    Representa un object literal: {a: 1, b: 2}

    properties: list[tuple(str, Expressions)] - lista de (clave, valor)

    Ejemplos:
        {a: 1, b: 2}        → ObjectLiteral([("a", Literal(1)), ("b", Literal(2))])
        {x: y + 1}          → ObjectLiteral([("x", Binary(...))])
        {a: 1, b: {c: 2}}   → ObjectLiteral([("a", Literal(1)), ("b", ObjectLiteral(...))])
    """

    def __init__(self, properties: list[tuple[str, "Expressions"]]):
        self.properties = properties

    def __repr__(self) -> str:
        props = ", ".join(f"{key}: {value}" for key, value in self.properties)
        return f"ObjectLiteral({{{props}}})"
