import pytest
import Scanner
from Token import (
    TokenType,
)
from Scanner import Scanner
import pytest


def test_hello_world():
    tokens = Scanner("2+2").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.NUMBER,
        TokenType.PLUS,
        TokenType.NUMBER,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type


def test_string_literal():
    tokens = Scanner('"hello world"').scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.STRING,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type
    assert tokens[0].literal == "hello world"


def test_multiline_strings():
    tokens = Scanner("'hello world'").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.STRING,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type
    assert tokens[0].literal == "hello world"

    tokens = Scanner("""`comentario
con salto de linea`""").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.STRING,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type
    assert tokens[0].literal == "comentario\ncon salto de linea"


def test_number_literal():
    tokens = Scanner("123.45").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.NUMBER,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type
    assert tokens[0].literal == 123.45


def test_error_unterminated_string():
    with pytest.raises(Exception) as excinfo:
        Scanner('"hello world').scan()
    assert "Unterminated string" in str(excinfo.value)

    with pytest.raises(Exception) as excinfo:
        Scanner("""
            'comillas simples
            no son multilinea'
            """).scan()
    assert "Unterminated string" in str(excinfo.value)

    with pytest.raises(Exception) as excinfo:
        Scanner("""
            "hello
            world
            """).scan()
    assert "Unterminated string" in str(excinfo.value)


def test_identifiers():
    tokens = Scanner("foo bar trueman t0").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type
    assert tokens[0].lexeme == "foo"
    assert tokens[1].lexeme == "bar"
    assert tokens[2].lexeme == "trueman"


def test_error_unexpected_character():
    with pytest.raises(Exception) as excinfo:
        Scanner("@").scan()
    assert "Unexpected character" in str(excinfo.value)


def test_remove_whitespace():
    expected_tokens_type = [
        TokenType.EOF,
    ]

    tokens = Scanner(" ").scan()
    tokens_type = [token.token_type for token in tokens]
    assert tokens_type == expected_tokens_type

    tokens = Scanner("  ").scan()
    tokens_type = [token.token_type for token in tokens]
    assert tokens_type == expected_tokens_type

    tokens = Scanner("\r").scan()
    tokens_type = [token.token_type for token in tokens]
    assert tokens_type == expected_tokens_type

    tokens = Scanner("""

        """).scan()
    tokens_type = [token.token_type for token in tokens]
    assert tokens_type == expected_tokens_type


def test_remove_comments():
    expected_tokens_type = [
        TokenType.EOF,
    ]

    tokens = Scanner("// aaaa").scan()
    tokens_type = [token.token_type for token in tokens]
    assert tokens_type == expected_tokens_type


def test_remove_multiline_comments():
    expected_tokens_type = [
        TokenType.EOF,
    ]

    tokens = Scanner("""
        /*
        comentario multilinea
        */
        """).scan()
    tokens_type = [token.token_type for token in tokens]
    assert tokens_type == expected_tokens_type

    tokens = Scanner("""
        /*
        comentario multilinea
        /*
        comentario multilinea anidado
        */
        // otro comentario mas
        */
        """).scan()
    tokens_type = [token.token_type for token in tokens]
    assert tokens_type == expected_tokens_type

    with pytest.raises(Exception) as excinfo:
        Scanner("""
            /*
            comentario multilinea
            /*
            comentario multilinea anidado
            */
            // otro comentario mas
            """).scan()
    assert "Unterminated comment" in str(excinfo.value)


def test_single_char_tokens():
    tokens = Scanner("(){},-+;*/%:?*").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.LEFT_PAREN,
        TokenType.RIGHT_PAREN,
        TokenType.LEFT_BRACE,
        TokenType.RIGHT_BRACE,
        TokenType.COMMA,
        TokenType.MINUS,
        TokenType.PLUS,
        TokenType.SEMICOLON,
        TokenType.STAR,
        TokenType.SLASH,
        TokenType.PERCENT,
        TokenType.COLON,
        TokenType.QUESTION,
        TokenType.STAR,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type


def test_double_char_tokens():
    tokens = Scanner("! != = == < <= > >=").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.BANG,
        TokenType.BANG_EQUAL,
        TokenType.EQUAL,
        TokenType.EQUAL_EQUAL,
        TokenType.LESS,
        TokenType.LESS_EQUAL,
        TokenType.GREATER,
        TokenType.GREATER_EQUAL,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type


def test_string_literal():
    tokens = Scanner('"hello world"').scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.STRING,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type
    assert tokens[0].literal == "hello world"


def test_number_literal():
    tokens = Scanner("123.45").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.NUMBER,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type
    assert tokens[0].literal == 123.45


def test_error_unterminated_string():
    with pytest.raises(Exception) as excinfo:
        Scanner('"hello world').scan()
    assert "Unterminated string" in str(excinfo.value)


def test_identifiers():
    tokens = Scanner("foo bar trueman").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type
    assert tokens[0].lexeme == "foo"
    assert tokens[1].lexeme == "bar"
    assert tokens[2].lexeme == "trueman"


def test_keywords():
    tokens = Scanner(
        "else false function for if null undefined return true var const let while"
    ).scan()

    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.ELSE,
        TokenType.FALSE,
        TokenType.FUNCTION,
        TokenType.FOR,
        TokenType.IF,
        TokenType.NULL,
        TokenType.UNDEFINED,
        TokenType.RETURN,
        TokenType.TRUE,
        TokenType.VAR,
        TokenType.CONST,
        TokenType.LET,
        TokenType.WHILE,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type


def test_error_invalid_numbers():
    with pytest.raises(Exception) as excinfo:
        Scanner("1..2").scan()
    assert "Invalid number" in str(excinfo.value)

    with pytest.raises(Exception) as excinfo:
        Scanner("1.5.2").scan()
    assert "Invalid number" in str(excinfo.value)

    with pytest.raises(Exception) as excinfo:
        Scanner("1.").scan()
    assert "Invalid number" in str(excinfo.value)

    with pytest.raises(Exception) as excinfo:
        Scanner(".2").scan()
    assert "Unexpected character" in str(excinfo.value)


def test_scanner_plus_plus_token():
    tokens = Scanner("++").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [TokenType.PLUS_PLUS, TokenType.EOF]

    assert tokens_type == expected_tokens_type


def test_plus_plus_token_and_plus_token():
    tokens = Scanner("+++").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [TokenType.PLUS_PLUS, TokenType.PLUS, TokenType.EOF]

    assert tokens_type == expected_tokens_type


def test_triple_equals_tokens():
    tokens = Scanner("=== !==").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.EQUAL_EQUAL_EQUAL,
        TokenType.BANG_EQUAL_EQUAL,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type


def test_logical_operators():
    tokens = Scanner("&& ||").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.AND,
        TokenType.OR,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type


def test_arrow_function_token():
    tokens = Scanner("=>").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.ARROW_RIGHT,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type


def test_complex_operator_priority():
    tokens = Scanner("==== !===").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.EQUAL_EQUAL_EQUAL,
        TokenType.EQUAL,
        TokenType.BANG_EQUAL_EQUAL,
        TokenType.EQUAL,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type


def test_keyword_vs_identifier():
    tokens = Scanner("truex falsey function1").scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type


def test_mixed_expression():
    tokens = Scanner(
        "var x = 10; if (x >= 10) { x++; }; const y = 20; let z = 30; z = 40"
    ).scan()
    tokens_type = [token.token_type for token in tokens]

    expected_tokens_type = [
        TokenType.VAR,
        TokenType.IDENTIFIER,
        TokenType.EQUAL,
        TokenType.NUMBER,
        TokenType.SEMICOLON,
        TokenType.IF,
        TokenType.LEFT_PAREN,
        TokenType.IDENTIFIER,
        TokenType.GREATER_EQUAL,
        TokenType.NUMBER,
        TokenType.RIGHT_PAREN,
        TokenType.LEFT_BRACE,
        TokenType.IDENTIFIER,
        TokenType.PLUS_PLUS,
        TokenType.SEMICOLON,
        TokenType.RIGHT_BRACE,
        TokenType.SEMICOLON,
        TokenType.CONST,
        TokenType.IDENTIFIER,
        TokenType.EQUAL,
        TokenType.NUMBER,
        TokenType.SEMICOLON,
        TokenType.LET,
        TokenType.IDENTIFIER,
        TokenType.EQUAL,
        TokenType.NUMBER,
        TokenType.SEMICOLON,
        TokenType.IDENTIFIER,
        TokenType.EQUAL,
        TokenType.NUMBER,
        TokenType.EOF,
    ]

    assert tokens_type == expected_tokens_type
