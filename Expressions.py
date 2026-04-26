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
    def __init__(self, name: Token, value: Expressions):
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return f"Assignment({self.name.lexeme}, {self.value})"


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
