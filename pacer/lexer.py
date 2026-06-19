"""
mylang Lexer  — Stage A of the pipeline.
Scans source text character by character and emits a flat list of Tokens.
Supports: integers, floats, scientific notation (1e-6, 4.7e+12),
          double-quoted strings, keywords, identifiers, all operators,
          and single-line comments (//).
"""

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    # Literals
    NUMBER      = auto()
    STRING      = auto()
    BOOL        = auto()
    COMPLEX_J   = auto()   # imaginary literal:  4j  3.14j  1e-6j

    # Identifiers & keywords
    IDENTIFIER  = auto()
    LET         = auto()
    IF          = auto()
    ELSE        = auto()
    WHILE       = auto()
    FOR         = auto()
    IN          = auto()
    FN          = auto()
    RETURN      = auto()
    PRINT       = auto()
    TRUE        = auto()
    FALSE       = auto()
    NULL        = auto()

    # Arithmetic operators
    PLUS        = auto()
    MINUS       = auto()
    STAR        = auto()
    SLASH       = auto()
    PERCENT     = auto()

    # Comparison / logical operators
    EQ          = auto()   # =
    EQ_EQ       = auto()   # ==
    BANG_EQ     = auto()   # !=
    LT          = auto()   # <
    LT_EQ       = auto()   # <=
    GT          = auto()   # >
    GT_EQ       = auto()   # >=
    BANG        = auto()   # !
    AND         = auto()   # &&
    OR          = auto()   # ||

    # Delimiters
    LPAREN      = auto()
    RPAREN      = auto()
    LBRACE      = auto()
    RBRACE      = auto()
    LBRACKET    = auto()
    RBRACKET    = auto()
    COMMA       = auto()
    SEMICOLON   = auto()
    DOT         = auto()
    COLON       = auto()

    EOF         = auto()


KEYWORDS = {
    "let":    TokenType.LET,
    "if":     TokenType.IF,
    "else":   TokenType.ELSE,
    "while":  TokenType.WHILE,
    "for":    TokenType.FOR,
    "in":     TokenType.IN,
    "fn":     TokenType.FN,
    "return": TokenType.RETURN,
    "print":  TokenType.PRINT,
    "true":   TokenType.TRUE,
    "false":  TokenType.FALSE,
    "null":   TokenType.NULL,
}


@dataclass
class Token:
    type:  TokenType
    value: object
    line:  int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, line={self.line})"


class LexerError(Exception):
    pass


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos    = 0
        self.line   = 1
        self.tokens: list[Token] = []

    # ── helpers ───────────────────────────────────────────────────────────────

    def peek(self, offset: int = 0) -> str:
        i = self.pos + offset
        return self.source[i] if i < len(self.source) else "\0"

    def advance(self) -> str:
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
        return ch

    def match(self, expected: str) -> bool:
        if self.peek() == expected:
            self.advance()
            return True
        return False

    def emit(self, ttype: TokenType, value=None):
        self.tokens.append(Token(ttype, value, self.line))

    # ── main scan loop ────────────────────────────────────────────────────────

    def tokenize(self) -> list[Token]:
        while self.pos < len(self.source):
            self._scan_token()
        self.emit(TokenType.EOF)
        return self.tokens

    def _scan_token(self):
        ch = self.advance()

        # Whitespace
        if ch in " \t\r\n":
            return

        # Single-line comments
        if ch == "/" and self.peek() == "/":
            while self.peek() not in ("\n", "\0"):
                self.advance()
            return

        # Single-character tokens
        SIMPLE = {
            "(": TokenType.LPAREN,  ")": TokenType.RPAREN,
            "{": TokenType.LBRACE,  "}": TokenType.RBRACE,
            "[": TokenType.LBRACKET,"]": TokenType.RBRACKET,
            ",": TokenType.COMMA,   ";": TokenType.SEMICOLON,
            ".": TokenType.DOT,     ":": TokenType.COLON,
            "+": TokenType.PLUS,    "*": TokenType.STAR,
            "/": TokenType.SLASH,   "%": TokenType.PERCENT,
        }
        if ch in SIMPLE:
            self.emit(SIMPLE[ch])
            return

        # One-or-two character tokens
        if ch == "-":
            self.emit(TokenType.MINUS)
        elif ch == "=":
            self.emit(TokenType.EQ_EQ if self.match("=") else TokenType.EQ)
        elif ch == "!":
            self.emit(TokenType.BANG_EQ if self.match("=") else TokenType.BANG)
        elif ch == "<":
            self.emit(TokenType.LT_EQ if self.match("=") else TokenType.LT)
        elif ch == ">":
            self.emit(TokenType.GT_EQ if self.match("=") else TokenType.GT)
        elif ch == "&" and self.match("&"):
            self.emit(TokenType.AND)
        elif ch == "|" and self.match("|"):
            self.emit(TokenType.OR)

        # String literals
        elif ch == '"':
            self._scan_string()

        # Numbers (integer, float, scientific notation)
        elif ch.isdigit():
            self._scan_number(ch)

        # Identifiers and keywords
        elif ch.isalpha() or ch == "_":
            self._scan_identifier(ch)

        else:
            raise LexerError(
                f"[line {self.line}] Unexpected character: {ch!r}")

    def _scan_string(self):
        start_line = self.line
        buf = []
        while self.peek() not in ('"', "\0"):
            c = self.advance()
            if c == "\\" and self.peek() in ('"', "\\", "n", "t", "r"):
                esc = self.advance()
                buf.append({"n": "\n", "t": "\t", "r": "\r",
                            '"': '"', "\\": "\\"}.get(esc, esc))
            else:
                buf.append(c)
        if self.peek() == "\0":
            raise LexerError(
                f"[line {start_line}] Unterminated string literal")
        self.advance()  # closing "
        self.emit(TokenType.STRING, "".join(buf))

    def _scan_number(self, first: str):
        buf = [first]
        while self.peek().isdigit():
            buf.append(self.advance())
        # Optional decimal part
        if self.peek() == "." and self.peek(1).isdigit():
            buf.append(self.advance())  # "."
            while self.peek().isdigit():
                buf.append(self.advance())
        # Optional scientific notation: e / E followed by optional +/- and digits
        if self.peek() in ("e", "E"):
            nxt = self.peek(1)
            if nxt.isdigit() or nxt in ("+", "-"):
                buf.append(self.advance())          # e / E
                if self.peek() in ("+", "-"):
                    buf.append(self.advance())      # sign
                while self.peek().isdigit():
                    buf.append(self.advance())
                # j suffix after scientific notation  e.g. 4.7e-12j
                if self.peek() == "j":
                    self.advance()
                    val = float("".join(buf))
                    self.emit(TokenType.COMPLEX_J, val)
                    return
                self.emit(TokenType.NUMBER, float("".join(buf)))
                return
        # j suffix for imaginary literal: 4j  3.14j
        if self.peek() == "j":
            self.advance()
            text = "".join(buf)
            val  = float(text) if "." in text else float(text)
            self.emit(TokenType.COMPLEX_J, val)
            return
        text = "".join(buf)
        self.emit(TokenType.NUMBER,
                  float(text) if "." in text else int(text))

    def _scan_identifier(self, first: str):
        buf = [first]
        while self.peek().isalnum() or self.peek() == "_":
            buf.append(self.advance())
        word  = "".join(buf)
        ttype = KEYWORDS.get(word, TokenType.IDENTIFIER)
        if ttype == TokenType.TRUE:
            self.emit(TokenType.BOOL, True)
        elif ttype == TokenType.FALSE:
            self.emit(TokenType.BOOL, False)
        elif ttype == TokenType.NULL:
            self.emit(ttype, None)
        else:
            self.emit(ttype, word)
