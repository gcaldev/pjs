from Token import (
    ComplexTokensFirstCharacter,
    ComplexTokens,
    SimpleTokens,
    Token,
    TokenKeywords,
    TokenType,
)


class Scanner(object):
    def __init__(self, source: str):
        self.escape_map = {
            "n": "\n",
            "t": "\t",
            "r": "\r",
            "\\": "\\",
            "`": "`",
            "$": "$",
        }
        self.tokens: list[Token] = []
        self.source = source
        self.start = 0
        self.current = 0
        self.line = 1

    def scan(self) -> list[Token]:
        while not self._is_at_end():
            self.start = self.current
            self.scan_token()

        self.start = self.current
        self.add_token(TokenType.EOF)

        return self.tokens

    def lexeme(self) -> str:
        return self.source[self.start : self.current]

    def add_token(self, token_type: TokenType, literal=None):
        self.tokens.append(
            Token(token_type, lexeme=self.lexeme(), literal=literal, line=self.line)
        )

    def scan_token(self):
        c = self._advance()
        match c:
            case "/":
                self._handle_slash()
            case _ if c in ComplexTokensFirstCharacter:
                self._handle_complex_token()
            case _ if c in SimpleTokens:
                self.add_token(SimpleTokens[c])
            case " " | "\r" | "\t":
                pass
            case "\n":
                self.line += 1
            case "'" | '"':
                self._handle_string(delimiter=c)
            case "`":
                self._handle_template_literal()
            case _ if str.isdigit(c):
                self._handle_number()
            case _ if self._is_alpha(c):
                self._handle_alphanumeric()
            case _:
                raise Exception(f"Unexpected character: `{c}`")

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _lookahead(self) -> str:
        if self._is_at_end():
            return "\0"

        return self.source[self.current]

    def _advance(self) -> str:
        lookahead = self._lookahead()
        self.current += 1
        return lookahead

    def _previous(self) -> str:
        return self.source[self.current - 1]

    def _next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def _match(self, expected: str) -> bool:
        lookahead = self._lookahead()
        if not lookahead == expected:
            return False

        self._advance()
        return True

    def _handle_slash(self):
        if self._match("/"):
            while not self._lookahead() == "\n" and not self._is_at_end():
                self._advance()
            return

        if self._match("*"):
            level = 1
            while level > 0 and not self._is_at_end():
                if self._match("\n"):
                    self.line += 1
                    continue
                if self._match("*") and self._match("/"):
                    level -= 1
                    continue
                if self._match("/") and self._match("*"):
                    level += 1
                    continue
                self._advance()
            if level > 0:
                raise Exception(f"Unterminated comment: `{self.lexeme()}`")
            return

        if self._match("="):
            self.add_token(TokenType.SLASH_EQUAL)
            return

        self.add_token(TokenType.SLASH)

    def _handle_string(self, delimiter: str):
        while not self._is_at_end():
            if self._lookahead() == delimiter:
                break

            if self._lookahead() == "\n":
                raise Exception(f"Unterminated string: `{self.lexeme()}`")

            if self._lookahead() == "\n":
                self.line += 1

            self._advance()

        if self._is_at_end():
            raise Exception(f"Unterminated string: `{self.lexeme()}`")

        self._advance()

        value = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, literal=value)

    def _read_raw_part(self) -> str:
        """
        Lectura hasta el proximo backtick o ${
        """
        part: list[str] = []
        while not self._is_at_end():
            ch = self._lookahead()
            if ch == "`":
                break
            if ch == "$" and self._next() == "{":
                break
            if ch == "\\":
                self._advance()
                escaped = self._lookahead()
                part.append(self.escape_map.get(escaped, escaped))
                self._advance()
                continue
            if ch == "\n":
                self.line += 1
            part.append(ch)
            self._advance()
        return "".join(part)

    def _make_template_token(self, token_type, content, line):
        return Token(token_type, lexeme="", literal=content, line=line)

    def _handle_template_literal(self):
        """
        Escanea un template literal, emitiendo tokens TEMPLATE_NOSUBST, TEMPLATE_HEAD, TEMPLATE_MIDDLE y TEMPLATE_TAIL segun corresponda
        """
        line = self.line

        part = self._read_raw_part()
        if self._is_at_end():
            raise Exception("Unterminated template literal")

        if self._lookahead() == "`":
            self._advance()
            self.tokens.append(
                self._make_template_token(TokenType.TEMPLATE_NOSUBST, part, line)
            )
            return

        # Hasta aca tenemos un TEMPLATE_HEAD, falta el ${ y el TEMPLATE_MIDDLE/TEMPLATE_TAIL
        self._emit_template_chunk(TokenType.TEMPLATE_HEAD, part, line)

        while True:
            part = self._read_raw_part()
            if self._is_at_end():
                raise Exception("Unterminated template literal")
            if self._lookahead() == "`":
                self._advance()  # consume closing `
                self.tokens.append(
                    self._make_template_token(TokenType.TEMPLATE_TAIL, part, line)
                )
                return

            self._emit_template_chunk(TokenType.TEMPLATE_MIDDLE, part, line)

    def _emit_template_chunk(self, token_type, part, line):
        """Emite un token de template literal con el contenido dado"""
        self._advance()  # $
        self._advance()  # {
        self.tokens.append(self._make_template_token(token_type, part, line))
        self._scan_template_expr()

    def _scan_template_expr(self):
        """
        Escaneo tokens normales hasta encontrar el cierre de la expresión del template literal }
        """
        depth = 1
        while not self._is_at_end():
            ch = self._lookahead()
            if ch == "}":
                depth -= 1
                if depth == 0:
                    self._advance()
                    return
            elif ch == "{":
                depth += 1
            self.start = self.current
            self.scan_token()
        raise Exception("Unterminated template expression")

    def _handle_number(self):
        scanned_dots_counter = 0

        while not self._is_at_end() and self._lookahead() in "0123456789.":
            if self._lookahead() == ".":
                scanned_dots_counter += 1

            self._advance()

        if scanned_dots_counter > 1:
            raise Exception(f"Invalid number: `{self.lexeme()}`")

        if self._previous() == ".":
            raise Exception(f"Invalid number: `{self.lexeme()}`")

        numvalue = float(self.lexeme())
        self.add_token(TokenType.NUMBER, literal=numvalue)

    def _handle_complex_token(self):
        for length in (3, 2, 1):
            text = self.source[self.current - 1 : self.current - 1 + length]
            if text in ComplexTokens:
                self.current += length - 1
                self.add_token(ComplexTokens[text])
                return
        raise Exception(f"Unexpected character: `{self._previous()}`")

    def _handle_alphanumeric(self):
        while not self._is_at_end() and self._is_alphanumeric(self._lookahead()):
            self._advance()

        lexeme = self.lexeme()

        if lexeme in TokenKeywords:
            self.add_token(TokenKeywords[lexeme])
        else:
            self.add_token(TokenType.IDENTIFIER)

    def _is_alphanumeric(self, c: str) -> bool:
        return str.isalnum(c) or c == "_"

    def _is_alpha(self, c: str) -> bool:
        return str.isalpha(c) or c == "_"
