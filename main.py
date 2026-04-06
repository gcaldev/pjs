from Scanner import Scanner
from .Parser import Parser

def main():
    source = input("Enter source code: ")
    scanner = Scanner(source)
    tokens = scanner.scan()
    for token in tokens:
        print(token)
    
    parser = Parser(tokens)
    expressions = parser.parse()
    
    for expr in expressions:
        print(expr)

if __name__ == "__main__":
    main()
    
    
    
