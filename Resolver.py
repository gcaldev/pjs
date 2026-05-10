from functools import singledispatchmethod

from Token import TokenType

from Interpreter import Interpreter
from Stmt import (
    Stmt,
    ExpressionStmt,
    VarDecl,
    FunDecl,
    BlockStmt,
    IfStmt,
    WhileStmt,
    ReturnStmt,
)
from Expressions import (
    Expressions,
    Binary,
    Grouping,
    Literal,
    Unary,
    Variable,
    Assignment,
    Logic,
    Call,
    Ternary,
    Postfix,
    FunctionExpr,
)


class VarInformation:
    def __init__(self, defined: bool, used: bool, var_type: TokenType = None):
        self.defined = defined
        self.used = used
        self.var_type = var_type


class Resolver(object):
    def __init__(self, interpreter: Interpreter):
        # Nos guardamos un stack de scopes, para saber cuan anidados estamos
        # En cada scope tenemos una tabla que nos dice si bajo un nombre tenemos
        # una variable declarada y usada (ver VarInformation)
        self.scopes: list[dict[str, VarInformation]] = []

        # Nos guardamos una lista con los warnings generados
        self.warnings: list[str] = []

        # Indice para manejar el hoisting de funciones y vars
        self.function_scope_index: int | None = None

        # Una referencia al intérprete, para poder resolver las variables
        self.interpreter = interpreter

        # Hacer esto nos permite manejar redefiniciones en scope global de var
        self.begin_scope()

    def begin_scope(self):
        # Empezar un scope es apilar una tabla
        self.scopes.append({})

    def end_scope(self):
        # Terminar un scope es desapilar la tabla
        scope = self.scopes.pop()
        for name, var_info in scope.items():
            if name.startswith("_"):
                # Por convencion, si la variable empieza con "_" omitimos el warning
                continue

            if var_info.used is False:
                warning = f'[warning] Variable "{name}" is never used.'
                self.warnings.append(warning)

    def declare(
        self, name: str, var_type: TokenType = None, validate_existence: bool = True
    ):
        if not self.scopes:
            return

        if name in self.scopes[-1]:
            existing = self.scopes[-1][name]
            if (
                existing.var_type == var_type
                and var_type in (TokenType.LET, TokenType.CONST)
                and not existing.defined
            ):
                return
            if var_type in (TokenType.LET, TokenType.CONST):
                raise RuntimeError(
                    f"Cannot redeclare '{name}' with let/const: already declared"
                )
            if existing.var_type in (TokenType.LET, TokenType.CONST):
                keyword = "constant" if existing.var_type == TokenType.CONST else "let"
                raise RuntimeError(
                    f"Cannot redeclare '{name}': already declared as {keyword}"
                )
            if var_type == TokenType.VAR:
                return
            if validate_existence:
                raise RuntimeError(f"Variable `{name}` already exists")

        self.scopes[-1][name] = VarInformation(
            defined=False, used=False, var_type=var_type
        )

    def define(self, name: str):
        if not self.scopes:
            return
        existing = self.scopes[-1].get(name)
        var_type = existing.var_type if existing else None
        used = existing.used if existing else False
        self.scopes[-1][name] = VarInformation(
            defined=True, used=used, var_type=var_type
        )

    def mark_used(self, var_info: VarInformation):
        # Marca una variable como usada (le agrega la informacion a VarInformation)
        var_info.used = True

    def _hoist_vars(self, statements: list, hoist_scope_index: int = -1):
        """
        Recorre statements y hoistea var y FunDecl al scope dado.
        """
        for stmt in statements:
            if isinstance(stmt, VarDecl) and stmt.var_type == TokenType.VAR:
                if self.scopes:
                    name = stmt.name.lexeme
                    if name not in self.scopes[hoist_scope_index]:
                        self.scopes[hoist_scope_index][name] = VarInformation(
                            defined=True, used=False, var_type=TokenType.VAR
                        )
                    elif self.scopes[hoist_scope_index][name].var_type in (
                        TokenType.LET,
                        TokenType.CONST,
                    ):
                        raise RuntimeError(
                            f"Cannot declare '{name}': already declared as let/const"
                        )
            elif isinstance(stmt, FunDecl):
                if self.scopes:
                    name = stmt.name.lexeme
                    if name in self.scopes[hoist_scope_index]:
                        if self.scopes[hoist_scope_index][name].var_type in (
                            TokenType.LET,
                            TokenType.CONST,
                        ):
                            raise RuntimeError(
                                f"Cannot declare '{name}': already declared as let/const"
                            )
                    self.scopes[hoist_scope_index][name] = VarInformation(
                        defined=True, used=False, var_type=TokenType.FUNCTION
                    )
            elif isinstance(stmt, BlockStmt):
                self._hoist_vars(stmt.statements, hoist_scope_index)
            elif isinstance(stmt, IfStmt):
                self._hoist_vars([stmt.then_branch], hoist_scope_index)
                if stmt.else_branch is not None:
                    self._hoist_vars([stmt.else_branch], hoist_scope_index)
            elif isinstance(stmt, WhileStmt):
                self._hoist_vars([stmt.body], hoist_scope_index)

    def _tdz_prescan(self, statements: list):
        """
        Asigna TDZ a variables declaradas con let/const para detectar referencias antes de la inicialización
        """
        for stmt in statements:
            if isinstance(stmt, VarDecl) and stmt.var_type in (
                TokenType.LET,
                TokenType.CONST,
            ):
                name = stmt.name.lexeme
                if self.scopes and name not in self.scopes[-1]:
                    self.scopes[-1][name] = VarInformation(
                        defined=False, used=False, var_type=stmt.var_type
                    )

    @singledispatchmethod
    def resolve(self, arg: Stmt | Expressions):
        raise NameError(f"Unknown statement or expression type: `{type(arg)}`")

    # ---------- Resolver Statements  ---------- #

    @resolve.register
    def _(self, statement: BlockStmt):
        # Los bloques arrancan su propio scope
        self.begin_scope()
        self._tdz_prescan(statement.statements)
        if self.function_scope_index is not None and self.scopes:
            self._hoist_vars(statement.statements, self.function_scope_index)
        for stmt in statement.statements:
            self.resolve(stmt)
        self.end_scope()

    @resolve.register
    def _(self, statement: VarDecl):
        self.declare(statement.name.lexeme, var_type=statement.var_type)
        if statement.initializer is not None:
            self.resolve(statement.initializer)
        self.define(statement.name.lexeme)

    @resolve.register
    def _(self, statement: FunDecl):
        # Las funciones arrancan un scope nuevo después del nombre de la función
        # fun nombre() { <scope nuevo> }
        if not (self.scopes and statement.name.lexeme in self.scopes[-1]):
            self.declare(statement.name.lexeme, var_type=TokenType.FUNCTION)
        self.define(statement.name.lexeme)
        self._resolve_function_body(statement.parameters, statement.body)

    def _resolve_function_body(self, parameters, body):
        self.begin_scope()
        previous_function_scope = self.function_scope_index
        self.function_scope_index = len(self.scopes) - 1
        for param in parameters:
            self.declare(param.lexeme)
            self.define(param.lexeme)
        self._tdz_prescan(body)
        self._hoist_vars(body, self.function_scope_index)
        for stmt in body:
            self.resolve(stmt)
        self.end_scope()
        self.function_scope_index = previous_function_scope

    ## El resto de los statements son triviales de resolver

    @resolve.register
    def _(self, statement: ExpressionStmt):
        self.resolve(statement.expression)

    @resolve.register
    def _(self, statement: ReturnStmt):
        if statement.value is not None:
            self.resolve(statement.value)

    @resolve.register
    def _(self, statement: IfStmt):
        self.resolve(statement.condition)
        self.resolve(statement.then_branch)
        if statement.else_branch is not None:
            self.resolve(statement.else_branch)

    @resolve.register
    def _(self, statement: WhileStmt):
        self.resolve(statement.condition)
        self.resolve(statement.body)

    # ---------- Resolver Expresiones ---------- #

    @resolve.register
    def _(self, expression: Variable):
        # Si la variable esta declarada e intenta ser referenciada antes de ser definida,
        # es decir, si defined es False, en vez de ser True,
        # lanzamos un error
        # Básicamente, el error frente a `var x = x;`

        actual_var_info = (
            self.scopes[-1].get(expression.name.lexeme, None) if self.scopes else None
        )
        if actual_var_info is not None and actual_var_info.defined is False:
            raise RuntimeError(
                f"Cannot access '{expression.name.lexeme}' before initialization"
            )

        # Luego, agregamos al intérprete la profundidad del scope
        # en la que buscar la variable referenciada, partiendo
        # desde el top del stack
        for i, scope in enumerate(reversed(self.scopes)):
            if expression.name.lexeme in scope:
                self.interpreter.resolve_depth(expression, i)
                # Marcamos la variable como usada
                self.mark_used(scope[expression.name.lexeme])
                return

    @resolve.register
    def _(self, expression: Assignment):
        value = self.resolve(expression.value)

        # Agregamos al intérprete la profundidad del scope en la que
        # se tiene que asignar el valor de la variable
        for i, scope in enumerate(reversed(self.scopes)):
            if expression.name.lexeme in scope:
                self.interpreter.resolve_depth(expression, i)
                return value

        return value

    @resolve.register
    def _(self, expression: Literal):
        # Los literales son lo más chico que hay en el lenguaje,
        # no queda nada por resolver!
        return

    ## El resto de las resoluciones son triviales de resolver

    @resolve.register
    def _(self, expression: Grouping):
        self.resolve(expression.expression)

    @resolve.register
    def _(self, expression: Unary):
        self.resolve(expression.right)

    @resolve.register
    def _(self, expression: Binary):
        self.resolve(expression.left)
        self.resolve(expression.right)

    @resolve.register
    def _(self, expression: Logic):
        self.resolve(expression.left)
        self.resolve(expression.right)

    @resolve.register
    def _(self, expression: Call):
        self.resolve(expression.callee)
        for arg in expression.arguments:
            self.resolve(arg)

    @resolve.register
    def _(self, expression: Ternary):
        self.resolve(expression.condition)
        self.resolve(expression.true_branch)
        self.resolve(expression.false_branch)

    @resolve.register
    def _(self, expr: Postfix):
        self.resolve(expr.left)

    @resolve.register
    def _(self, expression: FunctionExpr):
        self._resolve_function_body(expression.parameters, expression.body)
