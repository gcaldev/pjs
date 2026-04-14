from Token import Token, TokenType
from Expressions import Binary, Grouping, Literal, Unary

class Parser(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.errors = []

    def parse(self):
        """Parse a list of expressions"""
        statements = []
        while not self._is_at_end():
            expr = self.expression()
            if expr:
                statements.append(expr)
            # Consume semicolon if present
            if self._match(TokenType.SEMICOLON):
                pass
        return statements
    
    def expression(self):
        """Entry point: lowest precedence"""
        return self.equality()
    
    def equality(self):
        """Handle == != === !=="""
        expr = self.comparison()
        
        while self._match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL, 
                          TokenType.EQUAL_EQUAL_EQUAL, TokenType.BANG_EQUAL_EQUAL):
            operator = self._previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def comparison(self):
        """Handle < > <= >="""
        expr = self.term()
        
        while self._match(TokenType.LESS, TokenType.LESS_EQUAL, 
                          TokenType.GREATER, TokenType.GREATER_EQUAL):
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
        """Handle * / %"""
        expr = self.unary()
        
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            operator = self._previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        
        return expr

    def unary(self):
        """Handle ! - + (prefix operators)"""
        if self._match(TokenType.BANG, TokenType.MINUS, TokenType.PLUS):
            operator = self._previous()
            expr = self.unary()
            return Unary(operator, expr)
        
        return self.primary()

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
            return Literal(self._previous().lexeme)  # Por ahora como string
        
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