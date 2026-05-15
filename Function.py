from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Interpreter import Interpreter

from Stmt import FunDecl
from Env import Env
from JSValues import UNDEFINED


class ReturnValue(Exception):
    def __init__(self, value: object):
        super().__init__(f"Return Value: {value}")
        self.value = value

class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

class Function(object):
    def __init__(
        self,
        declaration: FunDecl,
        closure_env: Env,
    ):
        self.closure_env = closure_env
        self.declaration = declaration
        self.arity = len(declaration.parameters)

    # La invocación! La parte mas linda. El código toma vida
    def __call__(self, interpreter: "Interpreter", arguments: list):
        # Creamos un nuevo entorno, solo para esta invocación
        function_env = Env(enclosing=self.closure_env)

        # Definimos los parámetros en el nuevo entorno
        # con el valor de los argumentos
        for param, arg in zip(self.declaration.parameters, arguments):
            function_env.define(param.lexeme, arg)

        # Ejecutamos el cuerpo de la función y devolvemos el return value que salte
        try:
            previous_function_env = interpreter.current_function_env
            interpreter.current_function_env = function_env
            interpreter.execute_block(
                self.declaration.body, function_env, hoist_env=function_env
            )
        except ReturnValue as returnvalue:
            interpreter.current_function_env = previous_function_env
            return returnvalue.value

        interpreter.current_function_env = previous_function_env
        return UNDEFINED

    def __repr__(self) -> str:
        params = ", ".join(param.lexeme for param in self.declaration.parameters)
        name = self.declaration.name.lexeme if self.declaration.name else "(anonymous)"
        return f"<fn {name}({params})>"
