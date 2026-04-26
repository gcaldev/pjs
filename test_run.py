from Scanner import Scanner
from Parser import Parser
from Interpreter import Interpreter

s = "2+2;"
scanner = Scanner(s)
tokens = scanner.scan()
parser = Parser(tokens)
exprs = parser.parse()
print("PARSED:", exprs)
interp = Interpreter()
print("EVAL:", interp.execute(exprs[0]))
