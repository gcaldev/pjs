from functools import singledispatchmethod
from typing import Union, cast

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
    Expressions as Expr,
    Binary,
    Grouping,
    Literal,
    Unary,
)
from Expressions import Variable, Assignment, Logic, Call, Ternary, Postfix
from Function import Function, ReturnValue
from Token import TokenType
from Env import Env
from JSValues import UNDEFINED, js_repr


class Interpreter(object):
    def __init__(self):
        self.globals = Env()
        self.env = self.globals

        self.local_scope_depths: dict[Variable | Assignment, int] = {}

    # Interpretar es ejecutar la lista de statements que tenemos
    def interpret(self, statements: list[Stmt], as_js_repr: bool = False):
        lastvalue_produced = None
        for statement in statements:
            # Se guarda el ultimo valor producido por un statement
            lastvalue_produced = self.execute(statement)

        if as_js_repr:
            return js_repr(lastvalue_produced)

        return lastvalue_produced

    # Guarda la profundidad en la que buscar una variable o asignación
    # Es llamado por el resolvedor de scopes para poblar el diccionario
    # antes de la ejecución del programa
    def resolve_depth(self, expression, depth: int):
        self.local_scope_depths[expression] = depth

    # ---------- Ejecutadores de Statements ---------- #

    @singledispatchmethod
    def execute(self, statement: Stmt):
        raise RuntimeError(f"Unknown statement type: `{type(statement)}`")

    @execute.register
    def _(self, statement: ExpressionStmt):
        # Ejecutar un expression statement es solamente evaluar la expresión
        return self.evaluate(statement.expression)

    @execute.register
    def _(self, statement: VarDecl):
        if statement.initializer is not None:
            value = self.evaluate(statement.initializer)
        else:
            value = UNDEFINED
        self.env.define(statement.name.lexeme, value, is_const=statement.is_const)
        return UNDEFINED

    @execute.register
    def _(self, statement: FunDecl):
        # Ejecutar una declaración de una variable es solamente...
        # 1. Construir la función
        fun = Function(statement, self.env)
        # 2. Atarla a su nombre
        self.env.define(statement.name.lexeme, fun)
        return UNDEFINED

    @execute.register
    def _(self, statement: ReturnStmt):
        returnvalue = UNDEFINED
        if statement.value is not None:
            # Si hay un valor de retorno, lo evaluamos y lo lanzamos cual error
            returnvalue = self.evaluate(statement.value)

        raise ReturnValue(returnvalue)

    @execute.register
    def _(self, statement: IfStmt):
        # El if se implementa con... un if
        # Si la condición resuelve a verdadero, ejecuto el bloque del then
        # si no, ejecuto el bloque del else
        if self.is_truthy(self.evaluate(statement.condition)):
            self.execute(statement.then_branch)
        elif statement.else_branch is not None:
            # Si la condición es falsa y hay un bloque de else, lo ejecuto
            self.execute(statement.else_branch)

    @execute.register
    def _(self, statement: WhileStmt):
        # El while se implementa con... un while
        while self.is_truthy(self.evaluate(statement.condition)):
            self.execute(statement.body)

    @execute.register
    def _(self, statement: BlockStmt):
        return self.execute_block(statement.statements, Env(enclosing=self.env))

    def execute_block(self, statements: list[Stmt], block_env: Env):
        # Para ejecutar un bloque de statements, tenemos que crear un nuevo entorno
        # y ejecutar los statements ahí
        # Tenemos que guardarnos el entorno del bloque, y después acordarnos de volver al previo
        previous_env = self.env
        self.env = block_env
        # Ojo con los returns! Hacemos un try/finally para asegurarnos de
        # recuperar el entorno previo pase lo que pase
        try:
            self.env = block_env
            for s in statements:
                self.execute(s)
        finally:
            self.env = previous_env

    # ---------- Evaluadores de Expresiones ---------- #

    # Evalua cualquier expresión y devuelve su valor
    @singledispatchmethod
    def evaluate(self, expression: Expr):
        raise RuntimeError(f"Unknown expression type: `{type(expression)}`")

    @evaluate.register
    def _(self, expression: Literal):
        # Evaluar expresiones literales es solamente devolver el valor  ya escaneado
        return expression.value

    @evaluate.register
    def _(self, expression: Grouping):
        # Para evaluar expresiones agrupadas, solo hay que evaluar la expresión contenida
        return self.evaluate(expression.expression)

    @evaluate.register
    def _(self, expression: Unary):
        right = self.evaluate(expression.right)

        match expression.operator.token_type:
            case TokenType.MINUS:
                rnum = self.to_number(right)
                return -rnum
            case TokenType.BANG:
                return not self.is_truthy(right)
            case _:
                raise RuntimeError(f"Unknown unary operator: `{expression.operator}`")

    @evaluate.register
    def _(self, expression: Binary):
        left = self.evaluate(expression.left)
        right = self.evaluate(expression.right)

        match expression.operator.token_type:
            case TokenType.PLUS:
                if self.is_string(left) or self.is_string(right):
                    return js_repr(left) + js_repr(right)
                lnum = self.to_number(left)
                rnum = self.to_number(right)
                return lnum + rnum
            case TokenType.MINUS:
                lnum = self.to_number(left)
                rnum = self.to_number(right)
                return lnum - rnum
            case TokenType.STAR:
                lnum = self.to_number(left)
                rnum = self.to_number(right)
                return lnum * rnum
            case TokenType.SLASH:
                lnum = self.to_number(left)
                rnum = self.to_number(right)
                if self.is_nan(rnum):
                    return float("nan")
                if self.is_nan(lnum):
                    return float("nan")
                if rnum == 0:
                    if lnum == 0:
                        return float("nan")
                    return float("inf") if lnum > 0 else float("-inf")
                return lnum / rnum
            case TokenType.PERCENT:
                lnum = self.to_number(left)
                rnum = self.to_number(right)
                if self.is_nan(rnum) or rnum == 0:
                    return float("nan")
                return lnum % rnum
            case TokenType.GREATER:
                # Relational: ToPrimitive, then if both strings compare lexicographically,
                # else ToNumber and numeric comparison. If any operand is NaN, return False.
                if self.is_string(left, right):
                    return left > right
                lnum = self.to_number(left)
                rnum = self.to_number(right)
                if self.any_is_nan(lnum, rnum):
                    return False
                return lnum > rnum
            case TokenType.GREATER_EQUAL:
                if self.is_string(left, right):
                    return left >= right
                lnum = self.to_number(left)
                rnum = self.to_number(right)
                if self.any_is_nan(lnum, rnum):
                    return False
                return lnum >= rnum
            case TokenType.LESS:
                if self.is_string(left, right):
                    return left < right
                lnum = self.to_number(left)
                rnum = self.to_number(right)
                if self.any_is_nan(lnum, rnum):
                    return False
                return lnum < rnum
            case TokenType.LESS_EQUAL:
                if self.is_string(left, right):
                    return left <= right
                lnum = self.to_number(left)
                rnum = self.to_number(right)
                if self.any_is_nan(lnum, rnum):
                    return False
                return lnum <= rnum
            case TokenType.EQUAL_EQUAL:
                return self.equal_with_coersion(left, right)
            case TokenType.EQUAL_EQUAL_EQUAL:
                if type(left) is not type(right):
                    return False
                if self.any_is_nan(left, right):
                    return False
                return left == right
            case TokenType.BANG_EQUAL:
                return left != right
            case _:
                raise RuntimeError(f"Unknown binary operator: `{expression.operator}`")

    def equal_with_coersion(self, left, right):
        """
        Igualdad con coerción al estilo JavaScript para el operador ==.
        """
        if type(left) == type(right):
            return left == right

        if (left is None and right is UNDEFINED) or (
            left is UNDEFINED and right is None
        ):
            return True

        if type(left) is bool:
            return self.equal_with_coersion(self.to_number(left), right)
        if type(right) is bool:
            return self.equal_with_coersion(left, self.to_number(right))

        if self.is_number(left) and self.is_string(right):
            try:
                return left == self.to_number(right)
            except Exception:
                return False
        if self.is_string(left) and self.is_number(right):
            try:
                return self.to_number(left) == right
            except Exception:
                return False

        if self.any_is_nan(left, right):
            return False
        return left == right

    def to_number(self, value):
        if value is UNDEFINED:
            return float("nan")
        if value is None:
            return 0
        if type(value) is bool:
            return 1 if value else 0
        if self.is_number(value):
            return value
        if self.is_string(value):
            s = value.strip()
            if s == "":
                return 0
            try:
                if "." not in s and "e" not in s and "E" not in s:
                    return int(s)
                return float(s)
            except ValueError:
                return float("nan")
        return float("nan")

    @evaluate.register
    def _(self, expression: Variable):
        # Si la variable se encuentra en nuestro diccionario de scope local,
        # la buscamos con esa profundidad.
        if expression in self.local_scope_depths:
            depth = self.local_scope_depths[expression]
            return self.env.get(expression.name.lexeme, depth)

        # Si no, la buscamos dinámicamente en el entorno global
        return self.globals.get(expression.name.lexeme)

    @evaluate.register
    def _(self, expression: Assignment):
        value = self.evaluate(expression.value)

        # Si la variable se encuentra en nuestro diccionario de scope local,
        # la asignamos en esa profundidad.
        if expression in self.local_scope_depths:
            depth = self.local_scope_depths[expression]
            self.env.assign(expression.name.lexeme, value, depth)
            return value

        # Si no, la asignamos en el entorno global
        self.globals.assign(expression.name.lexeme, value)
        return value

    @evaluate.register
    def _(self, expression: Logic):
        left = self.evaluate(expression.left)

        if expression.operator.token_type == TokenType.OR:
            if self.is_truthy(left):
                return left

        if expression.operator.token_type == TokenType.AND:
            if not self.is_truthy(left):
                return left

        return self.evaluate(expression.right)

    @evaluate.register
    def _(self, expression: Call):
        callee = self.evaluate(expression.callee)
        arguments = [self.evaluate(arg) for arg in expression.arguments]

        if not callable(callee):
            raise RuntimeError(f"Cannot call non-callable object: `{callee}`")

        if not hasattr(callee, "arity"):
            raise RuntimeError(f"Callable object missing arity: `{callee}`")

        if len(arguments) != callee.arity:
            raise RuntimeError(
                f"Expected {callee.arity} arguments, got {len(arguments)}"
            )

        return callee(self, arguments)

    @evaluate.register
    def _(self, expression: Ternary):
        condition = self.evaluate(expression.condition)
        if self.is_truthy(condition):
            return self.evaluate(expression.true_branch)
        return self.evaluate(expression.false_branch)

    @evaluate.register
    def _(self, expression: Postfix):
        # TODO: this cast is not ok
        left = cast(Variable | Assignment, expression.left)

        # definimos funciones lambda para obtener el valor viejo y asignar el nuevo
        if (
            left in self.local_scope_depths
        ):  # si la variable se encuentra en nuestro diccionario de scope local, la buscamos y asignamos con esa profundidad
            depth = self.local_scope_depths[left]
            getvalue = lambda: self.env.get(left.name.lexeme, depth)
            assignvalue = lambda newvalue: self.env.assign(
                left.name.lexeme, newvalue, depth
            )
        else:  # en caso contrario, la buscamos y asignamos dinámicamente en el entorno global
            getvalue = lambda: self.globals.get(left.name.lexeme)
            assignvalue = lambda newvalue: self.globals.assign(
                left.name.lexeme, newvalue
            )

        oldvalue = (
            getvalue()
        )  # la funcion lambda para obtener el valor viejo depende de si la variable se encuentra en nuestro diccionario de scope local o no

        # el operador ++ solo funciona sobre números
        if not self.is_number(oldvalue):
            raise RuntimeError(f"Operand of ++ must be a number, got: `{oldvalue}++`")

        newvalue = cast(float, oldvalue) + 1
        assignvalue(
            newvalue
        )  # la funcion lambda para asignar el valor nuevo depende de si la variable se encuentra en nuestro diccionario de scope local o no

        # devolvemos el valor viejo
        return oldvalue

    # ---------- Helpers ---------- #

    # Devuelve si el valor es truthy (es decir, si evalua a verdadero)
    def is_truthy(self, value):
        if value is None or value is UNDEFINED:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            # 0 y NaN son falsy
            return value != 0 and not self.is_nan(value)
        if self.is_string(value):
            return value != ""
        return True

    # Devuelve si los valores recibidos son un número según Lox
    def is_number(self, *values):
        return all(type(value) is int or type(value) is float for value in values)

    # Devuelve si los valores recibidos son una cadena según Lox
    def is_string(self, *values):
        return all(type(value) is str for value in values)

    def is_nan(self, value):
        return isinstance(value, float) and value != value

    def any_is_nan(self, *values):
        return any(self.is_nan(v) for v in values)
