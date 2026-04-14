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
    