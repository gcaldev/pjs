from Token import SUM_LEXEME, Token, TokenType
from JSValues import UNDEFINED, NAN
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
    FunctionExpr,
    ArrayExpression,
    MemberExpression,
    ObjectLiteral,
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
    BreakStmt,
    ContinueStmt,
    ForBodyStmt,
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
            var_type = self._previous().token_type
            return self.variable_declaration(var_type=var_type)

        if self._match(TokenType.FUNCTION):
            return self.function_declaration()

        if self._match(TokenType.RETURN):
            return self.return_statement()
        
        if self._match(TokenType.BREAK): 
            self._consume(TokenType.SEMICOLON, "Expected ';' after 'break'")
            return BreakStmt()

        if self._match(TokenType.CONTINUE):
            self._consume(TokenType.SEMICOLON, "Expected ';' after 'continue'")
            return ContinueStmt()

        if self._match(TokenType.IF):
            return self.if_statement()

        if self._match(TokenType.WHILE):
            return self.while_statement()

        if self._match(TokenType.FOR):
            return self.for_statement()

        # Para hacer retrocompatible este metodo
        # Lookahead para diferenciar entre block { ... } 
        # y object literal { key: value }
        if self._check(TokenType.LEFT_BRACE):
            saved_pos = self.current
            self._advance()  # consume {
            
            is_object_literal = False
            
            # Si está vacío: {} - es un bloque vacío por defecto
            if self._check(TokenType.RIGHT_BRACE):
                is_object_literal = False
            # Si empieza con algo que parece una propiedad: IDENTIFIER/STRING/NUMBER seguido de :
            elif self._check(TokenType.IDENTIFIER) or self._check(TokenType.STRING) or self._check(TokenType.NUMBER):
                self._advance()  # avanza para mirar el siguiente token
                if self._check(TokenType.COLON):
                    # Es un object literal: {key: ...}
                    is_object_literal = True
            
            # Restaura la posición original
            self.current = saved_pos
            
            if is_object_literal:
                # Parsea como expression statement (que parseará el object literal)
                return self.expression_statement()
            else:
                # Parsea como block statement
                self._advance()  # consume {
                return self.block_statement()

        if self._match(TokenType.RETURN):
            return self.return_statement()

        return self.expression_statement()

    def expression_statement(self) -> ExpressionStmt:
        expr = self.expression()
        
        # Semicolon es opcional (ASI - Automatic Semicolon Insertion)
        # Igual que JavaScript real
        self._match(TokenType.SEMICOLON)
        
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
        elif self._match(TokenType.VAR, TokenType.LET, TokenType.CONST):
            initializer = self.variable_declaration(
                var_type=self._previous().token_type
            )
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
            body = ForBodyStmt(body, ExpressionStmt(increment))
            
        if condition is None:
            condition = Literal(True)
        body = WhileStmt(condition, body)
        if initializer is not None:
            body = BlockStmt([initializer, body], dedicated_var_scope=False)
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

    def variable_declaration(self, var_type: TokenType) -> VarDecl:
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
        return VarDecl(name, initializer, var_type=var_type)

    def expression(self):
        """Entry point: lowest precedence"""
        return self.assignment()

    def assignment(self):
        expr = self.conditional()
        if self._match(TokenType.EQUAL):
            value = self.assignment()
            if isinstance(expr, Variable):
                return Assignment(expr.name, value)
            # Ahora lo que hago es permitir asignación a member expressions
            if isinstance(expr, MemberExpression):
                return Assignment(expr, value)  # La "asignación" guarda la MemberExpression
            self._error("Invalid assignment target")
            return expr

        return expr

    def conditional(self):
        expr = self.nullish()
        if self._match(TokenType.QUESTION):
            true_branch = self.assignment()
            if not self._match(TokenType.COLON):
                self._error("Expected ':' after ternary true-branch")
                return expr
            false_branch = self.assignment()
            return Ternary(expr, true_branch, false_branch)
        return expr

    def nullish(self):
        expr = self.logic_or()
        while self._match(TokenType.QUESTION_QUESTION):
            operator = self._previous()
            right = self.logic_or()
            expr = Logic(expr, operator, right)
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
        if self._match(TokenType.TYPEOF):
            operator = self._previous()
            right = self.unary()
            return Unary(operator, right)

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
                        lexeme=SUM_LEXEME,
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
    
    def assignment(self):
        expr = self.conditional()
        
        if self._match(TokenType.EQUAL):
            value = self.assignment()
            if isinstance(expr, Variable):
                return Assignment(expr.name, value)
            if isinstance(expr, MemberExpression):
                return Assignment(expr, value)
            self._error("Invalid assignment target")
            return expr
        
        # Manejar compound assignment operators
        if self._match(
            TokenType.PLUS_EQUAL,
            TokenType.MINUS_EQUAL,
            TokenType.STAR_EQUAL,
            TokenType.SLASH_EQUAL,
            TokenType.PERCENT_EQUAL,
        ):
            operator = self._previous()
            value = self.assignment()
            
            # Convertir += a +, -= a -, etc.
            binary_op_type = self._get_binary_operator_from_compound(operator.token_type)
            binary_operator = Token(
                binary_op_type,
                lexeme=operator.lexeme[:-1],  # Remover el '='
                literal=None,
                line=operator.line,
            )
            
            # x += 5 se convierte en x = x + 5
            if isinstance(expr, Variable):
                binary_expr = Binary(expr, binary_operator, value)
                return Assignment(expr.name, binary_expr)
            if isinstance(expr, MemberExpression):
                binary_expr = Binary(expr, binary_operator, value)
                return Assignment(expr, binary_expr)
            
            self._error("Invalid assignment target")
            return expr
        
        return expr

    def _get_binary_operator_from_compound(self, compound_op: TokenType) -> TokenType:
        """Convierte un compound assignment operator a su operador binario equivalente"""
        mapping = {
            TokenType.PLUS_EQUAL: TokenType.PLUS,
            TokenType.MINUS_EQUAL: TokenType.MINUS,
            TokenType.STAR_EQUAL: TokenType.STAR,
            TokenType.SLASH_EQUAL: TokenType.SLASH,
            TokenType.PERCENT_EQUAL: TokenType.PERCENT,
        }
        return mapping.get(compound_op, TokenType.PLUS)
    def call(self):
        expr = self.primary()

        while True:
            # Maneja member access con dot notation: obj.prop
            if self._match(TokenType.DOT):
                if not self._match(TokenType.IDENTIFIER):
                    self._error("Expected property name after '.'")
                    prop_name = self._previous()
                else:
                    prop_name = self._previous()
                # Convierte obj.prop a MemberExpression(obj, "prop", computed=False)
                expr = MemberExpression(
                    expr,
                    Literal(prop_name.lexeme),  # La propiedad como string
                    computed=False
                )
            
            # Maneja member access con bracket notation: arr[expr]
            elif self._match(TokenType.LEFT_BRACKET):
                index = self.expression()
                self._consume(TokenType.RIGHT_BRACKET, "Expect ']' after computed member expression")
                expr = MemberExpression(expr, index, computed=True)
            
            # Maneja function calls: func() Este es el original que habia
            elif self._match(TokenType.LEFT_PAREN):
                arguments = []
                while not self._is_at_end() and not self._check(TokenType.RIGHT_PAREN):
                    arguments.append(self.expression())
                    if not self._match(TokenType.COMMA):
                        break

                self._consume(TokenType.RIGHT_PAREN, "Expect ')' after function arguments")
                expr = Call(expr, arguments)
            
            else:
                break

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
            return Literal(UNDEFINED)

        if self._match(TokenType.NAN):
            return Literal(NAN)

        if self._match(TokenType.NUMBER):
            return Literal(self._previous().literal)

        if self._match(TokenType.STRING):
            return Literal(self._previous().literal)

        if self._match(TokenType.TEMPLATE_NOSUBST):
            return Literal(self._previous().literal)

        if self._match(TokenType.TEMPLATE_HEAD):
            return self._handle_template_literal_parse()

        if self._match(TokenType.IDENTIFIER):
            name_token = self._previous()
            if self._match(TokenType.ARROW_RIGHT):
                return self._parse_arrow_body([name_token])
            return Variable(name_token)

        if self._match(TokenType.FUNCTION):
            return self._handle_function_expr_parse()

        if self._match(TokenType.LEFT_PAREN):
            arrow = self._try_arrow_from_paren()
            if arrow is not None:
                return arrow
            expr = self.expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression")
            return Grouping(expr)

        if self._match(TokenType.LEFT_BRACKET):
            elements = []
            while not self._is_at_end() and not self._check(TokenType.RIGHT_BRACKET):
                elements.append(self.expression())
                if not self._match(TokenType.COMMA):
                    break
            
            self._consume(TokenType.RIGHT_BRACKET, "Expect ']' after array elements")
            return ArrayExpression(elements)
            
        if self._match(TokenType.LEFT_BRACE):
            properties = []
            
            # Si es {} vacío, retorna inmediatamente
            if self._check(TokenType.RIGHT_BRACE):
                self._advance()
                return ObjectLiteral(properties)
            
            # Parsea pares key: value
            while not self._is_at_end() and not self._check(TokenType.RIGHT_BRACE):
                # La clave puede ser:
                # 1. IDENTIFIER (sin comillas): {a: 1}
                # 2. STRING: {"name": "Julian"}
                # 3. NUMBER: {1: "one"}
                
                if self._match(TokenType.IDENTIFIER):
                    key = self._previous().lexeme
                elif self._match(TokenType.STRING):
                    key = self._previous().literal
                elif self._match(TokenType.NUMBER):
                    key = str(int(self._previous().literal))
                else:
                    self._error("Expected property name")
                    break
                
                # Espera el ':'
                if not self._match(TokenType.COLON):
                    self._error("Expected ':' after property name")
                    break
                
                # Parsea el valor (puede ser cualquier expresión)
                value = self.expression()
                properties.append((key, value))
                
                # Si no hay coma, sale del loop
                if not self._match(TokenType.COMMA):
                    break
            
            if not self._match(TokenType.RIGHT_BRACE):
                self._error("Expected '}' after object properties")
            
            return ObjectLiteral(properties)
        
        self._error("Expect expression")
        return None

    # ===== Helper methods =====
    def _make_plus_expr(self, left, right, line):
        plus = Token(
            TokenType.PLUS,
            lexeme=SUM_LEXEME,
            literal=None,
            line=line,
        )
        return Binary(left, plus, right)

    def _handle_template_literal_parse(self):
        """
        Considero el template literal como una concatenación de strings y expresiones normal con el operador +
        """
        head = self._previous()
        result = self._make_plus_expr(
            Literal(head.literal), self.expression(), head.line
        )

        while self._match(TokenType.TEMPLATE_MIDDLE):
            mid = self._previous()

            result = self._make_plus_expr(
                result,
                Literal(mid.literal),
                mid.line,
            )

            result = self._make_plus_expr(
                result,
                self.expression(),
                mid.line,
            )

        if not self._match(TokenType.TEMPLATE_TAIL):
            self._error("Expected end of template literal")
        tail = self._previous()

        return self._make_plus_expr(
            result,
            Literal(tail.literal),
            tail.line,
        )

    def _handle_function_expr_parse(self):
        name = None
        if self._check(TokenType.IDENTIFIER):
            self._advance()
            name = self._previous()
        parameters = []
        if not self._match(TokenType.LEFT_PAREN):
            self._error("Expected '(' after function")
        while not self._is_at_end() and not self._check(TokenType.RIGHT_PAREN):
            if not self._match(TokenType.IDENTIFIER):
                self._error("Expected parameter name")
                break
            parameters.append(self._previous())
            if not self._match(TokenType.COMMA):
                break
        if not self._match(TokenType.RIGHT_PAREN):
            self._error("Expected ')' after parameters")
        if not self._match(TokenType.LEFT_BRACE):
            self._error("Expected '{' before function body")
        body = self.block()
        return FunctionExpr(name, parameters, body)

    def _end_arrow_parse(self, saved, params):
        if self._match(TokenType.ARROW_RIGHT):
            return self._parse_arrow_body(params)
        self.current = saved
        return None

    def _try_arrow_from_paren(self):
        """
        Intenta parsear una arrow function con sintaxis de parentesis, en caso de no lograrlo vuelve al estado anterior
        """
        saved = self.current
        params = []
        if self._match(TokenType.RIGHT_PAREN):
            return self._end_arrow_parse(saved, params)

        while True:
            if not self._match(TokenType.IDENTIFIER):
                self.current = saved
                return None
            params.append(self._previous())
            if self._match(TokenType.RIGHT_PAREN):
                return self._end_arrow_parse(saved, params)
            if not self._match(TokenType.COMMA):
                self.current = saved
                return None

    def _parse_arrow_body(self, params):
        """
        Parsea el cuerpo de una arrow function, que puede ser un bloque o una expresion
        """
        if self._match(TokenType.LEFT_BRACE):
            body = self.block()
        else:
            expr = self.assignment()
            body = [ReturnStmt(expr)]
        return FunctionExpr(None, params, body)

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
