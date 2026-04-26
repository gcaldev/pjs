from Scanner import Scanner
from Parser import Parser
from Interpreter import Interpreter


def main():
    source = input("Enter source code: ")
    scanner = Scanner(source)
    tokens = scanner.scan()
    for token in tokens:
        print(token)

    parser = Parser(tokens)
    expressions = parser.parse()

    interpreter = Interpreter()
    for expr in expressions:
        result = interpreter.execute(expr)
        print(result)


if __name__ == "__main__":
    main()
