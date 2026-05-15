from enum import Enum, auto
from typing import Union

SUM_LEXEME = "+"


class TokenType(Enum):
    # Tokens de un solo carácter
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    MINUS = auto()
    SEMICOLON = auto()
    STAR = auto()
    PERCENT = auto()

    # Tokens de uno o mas caracteres
    SLASH = auto()
    PLUS = auto()
    PLUS_PLUS = auto()
    MINUS_MINUS = auto()
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    QUESTION = auto()
    QUESTION_QUESTION = auto()
    COLON = auto()
    ARROW_RIGHT = auto()
    EQUAL_EQUAL_EQUAL = auto()
    BANG_EQUAL_EQUAL = auto()
    DOT = auto()

    # Literales
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()
    TEMPLATE_NOSUBST = auto()  # Template sin interpolar partes
    TEMPLATE_HEAD = auto()  # Parte antes de la primera interpolacion ${
    TEMPLATE_MIDDLE = auto()  # Parte entre interpolaciones } texto ${
    TEMPLATE_TAIL = auto()  # Parte después de la ultima interpolacion } texto`

    # Keywords
    AND = auto()
    ELSE = auto()
    FALSE = auto()
    FUNCTION = auto()
    FOR = auto()
    IF = auto()
    NULL = auto()
    OR = auto()
    RETURN = auto()
    TRUE = auto()
    VAR = auto()
    LET = auto()
    WHILE = auto()
    CONST = auto()
    UNDEFINED = auto()
    NAN = auto()
    TYPEOF = auto()
    BREAK = auto()
    CONTINUE = auto()

    # Fin de archivo
    EOF = auto()


TokenLiteralType = Union[float, str, bool, None]


class Token(object):
    def __init__(
        self,
        token_type: TokenType,
        *,
        lexeme: str,
        literal: TokenLiteralType,
        line: int,
    ):
        self.token_type = token_type  # Que tipo de token es
        self.lexeme = lexeme  # Los caracteres en sí, crudos
        self.literal = literal  # Si es un literal, aprovechamos y nos almacenamos directamente el valor al que resuelve
        self.line = line  # Numero de linea donde se encuentra el caracter para devolver errores mas especificos

    def __repr__(self) -> str:
        if self.token_type == TokenType.IDENTIFIER:
            return f"{self.token_type.name}<{self.lexeme}>"

        return (
            f"{self.token_type.name}"
            if self.literal is None
            else f"{self.token_type.name}<{self.literal}>"
        )


TokenKeywords = {
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "function": TokenType.FUNCTION,
    "for": TokenType.FOR,
    "if": TokenType.IF,
    "null": TokenType.NULL,
    "return": TokenType.RETURN,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "const": TokenType.CONST,
    "let": TokenType.LET,
    "while": TokenType.WHILE,
    "undefined": TokenType.UNDEFINED,
    "NaN": TokenType.NAN,
    "typeof": TokenType.TYPEOF,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
}

# Tokens que se pueden identificar con un solo caracter
SimpleTokens = {
    "(": TokenType.LEFT_PAREN,
    ")": TokenType.RIGHT_PAREN,
    "{": TokenType.LEFT_BRACE,
    "}": TokenType.RIGHT_BRACE,
    ",": TokenType.COMMA,
    "-": TokenType.MINUS,
    ";": TokenType.SEMICOLON,
    ":": TokenType.COLON,
    "%": TokenType.PERCENT,
    ".": TokenType.DOT, 
}

# Tokens que para ser identificados necesitan mirar el siguiente caracter, como los operadores de dos caracteres
ComplexTokens = {
    "===": TokenType.EQUAL_EQUAL_EQUAL,
    "==": TokenType.EQUAL_EQUAL,
    "=": TokenType.EQUAL,
    "!==": TokenType.BANG_EQUAL_EQUAL,
    "!=": TokenType.BANG_EQUAL,
    "!": TokenType.BANG,
    "++": TokenType.PLUS_PLUS,
    "+": TokenType.PLUS,
    "--": TokenType.MINUS_MINUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "=>": TokenType.ARROW_RIGHT,
    "<=": TokenType.LESS_EQUAL,
    "<": TokenType.LESS,
    ">=": TokenType.GREATER_EQUAL,
    ">": TokenType.GREATER,
    "&&": TokenType.AND,
    "||": TokenType.OR,
    "??": TokenType.QUESTION_QUESTION,
    "?": TokenType.QUESTION,
}

ComplexTokensFirstCharacter = set(token[0] for token in ComplexTokens)
