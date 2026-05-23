from Resolver import Resolver
from Scanner import Scanner
from Parser import Parser
from Interpreter import Interpreter
import sys


def read_source(multiline=False):
    if multiline:
        print("Enter source code:")
        print("Windows: Ctrl+Z, Enter to end input")
        print("Unix/Linux/Mac: Ctrl+D to end input")

        return sys.stdin.read()

    return input("Enter source code: ")


def main():
    multiline = "--multiline" in sys.argv

    source = read_source(multiline)

    scanner = Scanner(source)
    tokens = scanner.scan()

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
