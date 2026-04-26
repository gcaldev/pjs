from Token import Token, TokenType
from Expressions import (
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
)
from Stmt import (
    Stmt,
    ExpressionStmt,
    BlockStmt,
    VarDecl,
    FunDecl,
    IfStmt,
    WhileStmt,
    ReturnStmt,
)


class Parser(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.errors = []

    def parse(self):
        """Parse a list of statements and expressions"""
        statements = []
        while not self._is_at_end():
            statements.append(self.statement())
        return statements

    def statement(self):
        if self._match(TokenType.VAR, TokenType.LET, TokenType.CONST):
            return self.variable_declaration()

        if self._match(TokenType.FUNCTION):
            return self.function_declaration()

        if self._match(TokenType.RETURN):
            return self.return_statement()

        if self._match(TokenType.IF):
            return self.if_statement()

        if self._match(TokenType.WHILE):
            return self.while_statement()

        if self._match(TokenType.FOR):
            return self.for_statement()

        if self._match(TokenType.LEFT_BRACE):
            return self.block_statement()

        if self._match(TokenType.RETURN):
            return self.return_statement()

        return self.expression_statement()

    def expression_statement(self) -> ExpressionStmt:
        expr = self.expression()

        if not self._match(TokenType.SEMICOLON):
            if not self._is_at_end() and not self._check(TokenType.RIGHT_BRACE):
                self._error("Expected ';' after expression")
                while not self._is_at_end() and not self._check(TokenType.SEMICOLON):
                    self._advance()
                if self._check(TokenType.SEMICOLON):
                    self._advance()
        return ExpressionStmt(expr)

    def block_statement(self) -> BlockStmt:
        return BlockStmt(self.block())

    def block(self) -> list[Stmt]:
        statements = []
        while not self._is_at_end() and not self._check(TokenType.RIGHT_BRACE):
            statements.append(self.statement())
        if not self._match(TokenType.RIGHT_BRACE):
            self._error("Expected '}' after block")
        return statements

    def while_statement(self) -> WhileStmt:
        if not self._match(TokenType.LEFT_PAREN):
            self._error("Expected '(' after 'while'")
        condition = self.expression()
        if not self._match(TokenType.RIGHT_PAREN):
            self._error("Expected ')' after condition")
        body = self.statement()
        return WhileStmt(condition, body)

    def if_statement(self) -> IfStmt:
        if not self._match(TokenType.LEFT_PAREN):
            self._error("Expected '(' after 'if'")
        condition = self.expression()
        if not self._match(TokenType.RIGHT_PAREN):
            self._error("Expected ')' after condition")
        then_branch = self.statement()
        else_branch = None
        if self._match(TokenType.ELSE):
            else_branch = self.statement()
        return IfStmt(condition, then_branch, else_branch)

    def for_statement(self) -> Stmt:
        # syntactic sugar: for (init; cond; inc) body -> {
        #   init; while (cond) { body; inc; }
        if not self._match(TokenType.LEFT_PAREN):
            self._error("Expected '(' after 'for'")
        initializer = None
        if self._match(TokenType.SEMICOLON):
            initializer = None
        elif self._match(TokenType.VAR):
            initializer = self.variable_declaration()
        else:
            initializer = self.expression_statement()

        if not self._check(TokenType.SEMICOLON):
            condition = self.expression()
        else:
            condition = Literal(True)
        if not self._match(TokenType.SEMICOLON):
            self._error("Expected ';' after for loop condition")

        if not self._check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        else:
            increment = None
        if not self._match(TokenType.RIGHT_PAREN):
            self._error("Expected ')' after for clauses")

        body = self.statement()
        if increment is not None:
            body = BlockStmt([body, ExpressionStmt(increment)])
        if condition is None:
            condition = Literal(True)
        body = WhileStmt(condition, body)
        if initializer is not None:
            body = BlockStmt([initializer, body])
        return body

    def return_statement(self) -> ReturnStmt:
        value = None
        if not self._check(TokenType.SEMICOLON):
            value = self.expression()
        if not self._match(TokenType.SEMICOLON):
            if not self._is_at_end() and not self._check(TokenType.RIGHT_BRACE):
                self._error("Expected ';' after return statement")
        return ReturnStmt(value)

    def function_declaration(self) -> FunDecl:
        if not self._match(TokenType.IDENTIFIER):
            self._error("Expected function name")
            name = self._previous()
        else:
            name = self._previous()

        parameters = []
        if not self._match(TokenType.LEFT_PAREN):
            self._error("Expected '(' after function name")
        while not self._is_at_end() and not self._check(TokenType.RIGHT_PAREN):
            if not self._match(TokenType.IDENTIFIER):
                self._error("Expected parameter name")
                break
            parameters.append(self._previous())
            if not self._match(TokenType.COMMA):
                break
        if not self._match(TokenType.RIGHT_PAREN):
            self._error("Expected ')' after function parameters")
        if not self._match(TokenType.LEFT_BRACE):
            self._error("Expected '{' before function body")
        body = self.block()
        return FunDecl(name, parameters, body)

    def variable_declaration(self) -> VarDecl:
        if not self._match(TokenType.IDENTIFIER):
            self._error("Expected variable name")
            name = self._previous()
        else:
            name = self._previous()

        initializer = None
        if self._match(TokenType.EQUAL):
            initializer = self.expression()

        if not self._match(TokenType.SEMICOLON):
            if not self._is_at_end() and not self._check(TokenType.RIGHT_BRACE):
                self._error("Expected ';' after variable declaration")
        return VarDecl(name, initializer)

    def expression(self):
        """Entry point: lowest precedence"""
        return self.assignment()

    def assignment(self):
        expr = self.conditional()
        if self._match(TokenType.EQUAL):
            value = self.assignment()
            if not isinstance(expr, Variable):
                self._error("Invalid assignment target")
                return expr
            return Assignment(expr.name, value)

        return expr

    def conditional(self):
        expr = self.logic_or()
        if self._match(TokenType.QUESTION):
            true_branch = self.assignment()
            if not self._match(TokenType.COLON):
                self._error("Expected ':' after ternary true-branch")
                return expr
            false_branch = self.assignment()
            return Ternary(expr, true_branch, false_branch)
        return expr

    def logic_or(self):
        expr = self.logic_and()
        while self._match(TokenType.OR):
            operator = self._previous()
            right = self.logic_and()
            expr = Logic(expr, operator, right)
        return expr

    def logic_and(self):
        expr = self.equality()
        while self._match(TokenType.AND):
            operator = self._previous()
            right = self.equality()
            expr = Logic(expr, operator, right)
        return expr

    def equality(self):
        """Handle == != === !=="""
        expr = self.comparison()

        while self._match(
            TokenType.EQUAL_EQUAL,
            TokenType.BANG_EQUAL,
            TokenType.EQUAL_EQUAL_EQUAL,
            TokenType.BANG_EQUAL_EQUAL,
        ):
            operator = self._previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    def comparison(self):
        """Handle < > <= >="""
        expr = self.term()

        while self._match(
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
        ):
            operator = self._previous()
            right = self.term()
            expr = Binary(expr, operator, right)

        return expr

    def term(self):
        """Handle + -"""
        expr = self.factor()

        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous()
            right = self.factor()
            expr = Binary(expr, operator, right)

        return expr

    def factor(self):
        expr = self.unary()

        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            operator = self._previous()
            right = self.unary()
            expr = Binary(expr, operator, right)

        return expr

    def unary(self):
        # a diferencia de las reglas de expresiones binarias,
        # acá el operador es un prefijo.
        # primero chequeamos el operador, y después seguimos
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._previous()
            right = self.unary()
            return Unary(operator, right)

        if self._match(TokenType.PLUS_PLUS):
            operator = self._previous()
            right = self.unary()

            # solo se puede aplicar ++ sobre variables. Si no tenemos una variable, es un error
            if not isinstance(right, Variable):
                raise SyntaxError(
                    f"Invalid prefix target, got `{self._lookahead()}` instead"
                )

            # usamos el operador ++ como un syntatic sugar de una suma: x = x + 1
            # lo parseamos como una asignación para modificar el valor de la variable
            return Assignment(
                right.name,
                Binary(
                    right,
                    Token(
                        TokenType.PLUS,
                        lexeme="+",
                        literal=None,
                        line=self._previous().line,
                    ),
                    Literal(1),
                ),
            )

        # Si no tuve recursividad de unarios, entonces tengo una llamada a un prefijo
        return self.postfix()

    def postfix(self):
        expr = self.call()

        if self._match(TokenType.PLUS_PLUS):
            plus_plus_token = self._previous()
            if not isinstance(expr, Variable):
                self._error("Invalid postfix target")
                return expr
            expr = Postfix(expr, plus_plus_token)

        return expr

    def call(self):
        expr = self.primary()

        while self._match(TokenType.LEFT_PAREN):
            arguments = []
            while not self._is_at_end() and not self._check(TokenType.RIGHT_PAREN):
                arguments.append(self.expression())
                if not self._match(TokenType.COMMA):
                    break

            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after function arguments")
            expr = Call(expr, arguments)

        return expr

    def primary(self):
        """Handle literals, identifiers, grouping"""
        if self._match(TokenType.TRUE):
            return Literal(True)

        if self._match(TokenType.FALSE):
            return Literal(False)

        if self._match(TokenType.NULL):
            return Literal(None)

        if self._match(TokenType.UNDEFINED):
            return Literal(None)

        if self._match(TokenType.NUMBER):
            return Literal(self._previous().literal)

        if self._match(TokenType.STRING):
            return Literal(self._previous().literal)

        if self._match(TokenType.IDENTIFIER):
            return Variable(self._previous())

        if self._match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression")
            return Grouping(expr)

        self._error("Expect expression")
        return None

    # ===== Helper methods =====
    def _match(self, *types: TokenType) -> bool:
        """Check if current token matches any of the given types"""
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False

    def _check(self, token_type: TokenType) -> bool:
        """Check if current token is of given type"""
        if self._is_at_end():
            return False
        return self._peek().token_type == token_type

    def _advance(self) -> Token:
        """Move to next token"""
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        """Check if we reached EOF"""
        return self._peek().token_type == TokenType.EOF

    def _peek(self) -> Token:
        """Get current token"""
        return self.tokens[self.current]

    def _previous(self) -> Token:
        """Get previous token"""
        return self.tokens[self.current - 1]

    def _consume(self, token_type: TokenType, message: str) -> Token:
        """Consume a token of expected type or error"""
        if self._check(token_type):
            return self._advance()
        self._error(message)
        return self._previous()

    def _error(self, message: str):
        """Report an error"""
        token = self._peek()
        error_msg = f"[Line {token.line}] Error at '{token.lexeme}': {message}"
        self.errors.append(error_msg)
        print(error_msg)
        raise Exception(
            error_msg
        )  # TODO: Revisar si hay que handlearla en algun lado para evitar que se imprima el stack trace completo.
