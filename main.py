import time
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
    use_timer = "--timer" in sys.argv

    source = read_source(multiline)
    start_time = None

    if use_timer:
        start_time = time.perf_counter()

    scanner = Scanner(source)
    tokens = scanner.scan()

    parser = Parser(tokens)
    expressions = parser.parse()
    interpreter = Interpreter()
    resolver = Resolver(interpreter)
    for expr in expressions:
        resolver.resolve(expr)
    result = interpreter.interpret(expressions, as_js_repr=True)

    if use_timer:
        end_time = time.perf_counter()
        elapsed_ms = (end_time - start_time) * 1000

    print(result)

    if use_timer:
        print(f"time = {elapsed_ms:.2f} ms")


if __name__ == "__main__":
    main()
