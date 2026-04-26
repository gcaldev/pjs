from Resolver import Resolver
from Scanner import Scanner
from Parser import Parser
from Interpreter import Interpreter
from JSValues import js_repr, UNDEFINED


def main():
    source = input("Enter source code: ")
    scanner = Scanner(source)
    tokens = scanner.scan()
    for token in tokens:
        print(token)

    parser = Parser(tokens)
    expressions = parser.parse()
    interpreter = Interpreter()
    resolver = Resolver(interpreter)
    for expr in expressions:
        resolver.resolve(expr)
    result = interpreter.interpret(expressions, as_js_repr=True)
    print(result)


if __name__ == "__main__":
    main()
