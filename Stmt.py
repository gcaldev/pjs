from Expressions import Expressions as Expr
from Token import Token, TokenType


class Stmt(object):
    pass


# exprStmt       → expression ";" ;
class ExpressionStmt(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def __repr__(self) -> str:
        return f"{self.expression}"


# blockStmt       → "{" statement* "}" ;
class BlockStmt(Stmt):
    def __init__(self, statements: list[Stmt], dedicated_var_scope: bool = True):
        self.statements = statements
        self.dedicated_var_scope = dedicated_var_scope

    def __repr__(self) -> str:
        return f"{{ {'; '.join(str(stmt) for stmt in self.statements)} }}"


# varDecl        → "var" IDENTIFIER ( "=" expression )? ";" ;
class VarDecl(Stmt):
    def __init__(self, name: Token, initializer: Expr | None, var_type: TokenType):
        self.name = name
        self.initializer = initializer
        self.is_const = var_type == TokenType.CONST
        self.var_type = var_type

    def get_keyword(self) -> str:
        match self.name.token_type:
            case TokenType.VAR:
                return "VAR"
            case TokenType.LET:
                return "LET"
            case TokenType.CONST:
                return "CONST"

    def __repr__(self) -> str:
        return f"{self.get_keyword()} {self.name.lexeme} = {self.initializer}"


# funDecl        → "fun" IDENTIFIER "(" parameters? ")" blockStmt ;
class FunDecl(Stmt):
    def __init__(self, name: Token, parameters: list[Token], body: list[Stmt]):
        self.name = name
        self.parameters = parameters
        self.body = body

    def __repr__(self) -> str:
        params = ", ".join(param.lexeme for param in self.parameters)
        return f"FUN fn<{self.name.lexeme}({params})> {{ {('; '.join(str(stmt) for stmt in self.body))} }}"


# returnStmt     → "return" expression? ";" ;
class ReturnStmt(Stmt):
    def __init__(self, value: Expr | None):
        self.value = value

    def __repr__(self) -> str:
        return f"RETURN {self.value or 'NIL'}"


# ifStmt        → "if" "(" expression ")" statement ( "else" statement )? ;
class IfStmt(Stmt):
    def __init__(self, condition: Expr, then_branch: Stmt, else_branch: Stmt | None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def __repr__(self) -> str:
        if self.else_branch is None:
            return f"IF {self.condition} THEN {self.then_branch}"
        return f"IF {self.condition} THEN {self.then_branch} ELSE {self.else_branch}"


# whileStmt     → "while" "(" expression ")" statement ;
class WhileStmt(Stmt):
    def __init__(self, condition: Expr, body: Stmt):
        self.condition = condition
        self.body = body

    def __repr__(self) -> str:
        return f"WHILE {self.condition} {self.body}"
