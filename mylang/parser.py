"""
mylang Parser  — Stage B of the pipeline.
Consumes the flat token list from the Lexer and builds an AST via
recursive-descent parsing.

Grammar (informal, highest → lowest precedence):
  program     → statement* EOF
  statement   → varDecl | fnDecl | ifStmt | whileStmt | forStmt
              | returnStmt | printStmt | exprStmt
  block       → "{" statement* "}"
  varDecl     → "let" IDENT "=" expression ";"
  fnDecl      → "fn" IDENT paramList block
  ifStmt      → "if" "(" expr ")" block ("else" ("if" … | block))?
  whileStmt   → "while" "(" expr ")" block
  forStmt     → "for" "(" IDENT "in" expr ")" block
  returnStmt  → "return" expr? ";"
  printStmt   → "print" "(" expr ")" ";"
  exprStmt    → expression ";"
  expression  → assignment
  assignment  → (IDENT | IndexGet) "=" assignment | logic_or
  logic_or    → logic_and ( "||" logic_and )*
  logic_and   → equality  ( "&&" equality  )*
  equality    → comparison ( ("==" | "!=") comparison )*
  comparison  → term ( ("<" | "<=" | ">" | ">=") term )*
  term        → factor ( ("+" | "-") factor )*
  factor      → unary  ( ("*" | "/" | "%") unary )*
  unary       → ("-" | "!") unary | postfix
  postfix     → primary ( "." IDENT ("(" args ")")? | "[" expr "]" | "(" args ")" )*
  primary     → NUMBER | STRING | BOOL | NULL | IDENT
              | "fn" paramList block
              | "[" elements "]"
              | "{" (expr ":" expr ("," …)*)? "}"
              | "(" expr ")"
"""

from lexer import Token, TokenType
from ast_nodes import *


class ParseError(Exception):
    def __init__(self, token: Token, message: str):
        super().__init__(
            f"[line {token.line}] ParseError at {token.value!r}: {message}")
        self.token = token


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos    = 0

    # ── helpers ───────────────────────────────────────────────────────────────

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def previous(self) -> Token:
        return self.tokens[self.pos - 1]

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def advance(self) -> Token:
        if not self.is_at_end():
            self.pos += 1
        return self.previous()

    def check(self, *types: TokenType) -> bool:
        return self.peek().type in types

    def match(self, *types: TokenType) -> bool:
        if self.check(*types):
            self.advance()
            return True
        return False

    def expect(self, ttype: TokenType, message: str) -> Token:
        if self.check(ttype):
            return self.advance()
        raise ParseError(self.peek(), message)

    # ── entry point ───────────────────────────────────────────────────────────

    def parse(self) -> Program:
        stmts = []
        while not self.is_at_end():
            stmts.append(self._statement())
        return Program(stmts)

    # ── statements ────────────────────────────────────────────────────────────

    def _statement(self):
        if self.match(TokenType.LET):    return self._var_decl()
        if self.match(TokenType.FN):     return self._fn_decl()
        if self.match(TokenType.IF):     return self._if_stmt()
        if self.match(TokenType.WHILE):  return self._while_stmt()
        if self.match(TokenType.FOR):    return self._for_stmt()
        if self.match(TokenType.RETURN): return self._return_stmt()
        if self.match(TokenType.PRINT):  return self._print_stmt()
        return self._expr_stmt()

    def _var_decl(self) -> VarDecl:
        name = self.expect(TokenType.IDENTIFIER,
                           "Expected variable name after 'let'")
        self.expect(TokenType.EQ, "Expected '=' after variable name")
        init = self._expression()
        self.expect(TokenType.SEMICOLON, "Expected ';' after variable declaration")
        return VarDecl(name.value, init)

    def _fn_decl(self) -> FnDecl:
        name   = self.expect(TokenType.IDENTIFIER,
                             "Expected function name after 'fn'")
        params = self._param_list()
        body   = self._block()
        return FnDecl(name.value, params, body)

    def _param_list(self) -> list:
        self.expect(TokenType.LPAREN, "Expected '(' for parameter list")
        params = []
        if not self.check(TokenType.RPAREN):
            params.append(
                self.expect(TokenType.IDENTIFIER, "Expected parameter name").value)
            while self.match(TokenType.COMMA):
                params.append(
                    self.expect(TokenType.IDENTIFIER, "Expected parameter name").value)
        self.expect(TokenType.RPAREN, "Expected ')' after parameters")
        return params

    def _if_stmt(self) -> IfStmt:
        self.expect(TokenType.LPAREN, "Expected '(' after 'if'")
        cond = self._expression()
        self.expect(TokenType.RPAREN, "Expected ')' after condition")
        then = self._block()
        else_branch = None
        if self.match(TokenType.ELSE):
            if self.match(TokenType.IF):
                else_branch = self._if_stmt()
            else:
                else_branch = self._block()
        return IfStmt(cond, then, else_branch)

    def _while_stmt(self) -> WhileStmt:
        self.expect(TokenType.LPAREN, "Expected '(' after 'while'")
        cond = self._expression()
        self.expect(TokenType.RPAREN, "Expected ')' after condition")
        return WhileStmt(cond, self._block())

    def _for_stmt(self) -> ForStmt:
        self.expect(TokenType.LPAREN, "Expected '(' after 'for'")
        var = self.expect(TokenType.IDENTIFIER,
                          "Expected variable name in 'for'")
        self.expect(TokenType.IN, "Expected 'in' after variable in 'for'")
        iterable = self._expression()
        self.expect(TokenType.RPAREN, "Expected ')' after iterable in 'for'")
        return ForStmt(var.value, iterable, self._block())

    def _return_stmt(self) -> ReturnStmt:
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self._expression()
        self.expect(TokenType.SEMICOLON, "Expected ';' after return value")
        return ReturnStmt(value)

    def _print_stmt(self) -> PrintStmt:
        self.expect(TokenType.LPAREN, "Expected '(' after 'print'")
        expr = self._expression()
        self.expect(TokenType.RPAREN, "Expected ')' after print argument")
        self.expect(TokenType.SEMICOLON, "Expected ';' after print statement")
        return PrintStmt(expr)

    def _expr_stmt(self) -> ExprStmt:
        expr = self._expression()
        self.expect(TokenType.SEMICOLON, "Expected ';' after expression")
        return ExprStmt(expr)

    def _block(self) -> Block:
        self.expect(TokenType.LBRACE, "Expected '{'")
        stmts = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            stmts.append(self._statement())
        self.expect(TokenType.RBRACE, "Expected '}'")
        return Block(stmts)

    # ── expressions (recursive descent) ──────────────────────────────────────

    def _expression(self):
        return self._assignment()

    def _assignment(self):
        expr = self._logic_or()
        if self.match(TokenType.EQ):
            value = self._assignment()
            if isinstance(expr, Identifier):
                return Assign(expr.name, value)
            if isinstance(expr, IndexGet):
                return IndexSet(expr.array, expr.index, value)
            raise ParseError(self.previous(), "Invalid assignment target")
        return expr

    def _logic_or(self):
        left = self._logic_and()
        while self.match(TokenType.OR):
            left = LogicalOp("||", left, self._logic_and())
        return left

    def _logic_and(self):
        left = self._equality()
        while self.match(TokenType.AND):
            left = LogicalOp("&&", left, self._equality())
        return left

    def _equality(self):
        left = self._comparison()
        while self.match(TokenType.EQ_EQ, TokenType.BANG_EQ):
            sym  = "==" if self.previous().type == TokenType.EQ_EQ else "!="
            left = BinaryOp(sym, left, self._comparison())
        return left

    def _comparison(self):
        left = self._term()
        OPS  = {TokenType.LT: "<", TokenType.LT_EQ: "<=",
                TokenType.GT: ">", TokenType.GT_EQ: ">="}
        while self.check(*OPS):
            sym  = OPS[self.advance().type]
            left = BinaryOp(sym, left, self._term())
        return left

    def _term(self):
        left = self._factor()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            sym  = "+" if self.previous().type == TokenType.PLUS else "-"
            left = BinaryOp(sym, left, self._factor())
        return left

    def _factor(self):
        left = self._unary()
        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            sym  = {TokenType.STAR: "*", TokenType.SLASH: "/",
                    TokenType.PERCENT: "%"}[self.previous().type]
            left = BinaryOp(sym, left, self._unary())
        return left

    def _unary(self):
        if self.match(TokenType.BANG):  return UnaryOp("!", self._unary())
        if self.match(TokenType.MINUS): return UnaryOp("-", self._unary())
        return self._postfix()

    def _postfix(self):
        """Left-associative postfix: dot access, index, and call."""
        expr = self._primary()
        while True:
            if self.match(TokenType.DOT):
                # property or method: expr.name  or  expr.name(args)
                name = self.expect(TokenType.IDENTIFIER,
                                   "Expected name after '.'")
                if self.check(TokenType.LPAREN):
                    self.advance()  # consume "("
                    args = self._arg_list()
                    self.expect(TokenType.RPAREN,
                                "Expected ')' after method arguments")
                    expr = MethodCall(expr, name.value, args)
                else:
                    # Property / constant access  →  expr["name"]
                    expr = IndexGet(expr, StringLiteral(name.value))

            elif self.match(TokenType.LBRACKET):
                index = self._expression()
                self.expect(TokenType.RBRACKET, "Expected ']' after index")
                expr = IndexGet(expr, index)

            elif self.match(TokenType.LPAREN):
                if not isinstance(expr, Identifier):
                    raise ParseError(self.previous(),
                                     "Can only call named functions directly")
                args = self._arg_list()
                self.expect(TokenType.RPAREN, "Expected ')' after arguments")
                expr = Call(expr.name, args)

            else:
                break
        return expr

    def _arg_list(self) -> list:
        args = []
        if not self.check(TokenType.RPAREN):
            args.append(self._expression())
            while self.match(TokenType.COMMA):
                args.append(self._expression())
        return args

    def _primary(self):
        if self.match(TokenType.NUMBER):
            return NumberLiteral(self.previous().value)
        if self.match(TokenType.COMPLEX_J):
            return ComplexJLiteral(float(self.previous().value))
        if self.match(TokenType.STRING):
            return StringLiteral(self.previous().value)
        if self.match(TokenType.BOOL):
            return BoolLiteral(self.previous().value)
        if self.match(TokenType.NULL):
            return NullLiteral()
        if self.match(TokenType.IDENTIFIER):
            return Identifier(self.previous().value)

        # Anonymous function:  fn(params) { body }
        if self.match(TokenType.FN):
            params = self._param_list()
            body   = self._block()
            return FnExpr(params, body)

        # Array literal:  [e1, e2, ...]
        if self.match(TokenType.LBRACKET):
            elements = []
            if not self.check(TokenType.RBRACKET):
                elements.append(self._expression())
                while self.match(TokenType.COMMA):
                    elements.append(self._expression())
            self.expect(TokenType.RBRACKET, "Expected ']' after array elements")
            return ArrayLiteral(elements)

        # Hash literal:  { key: value, ... }
        if self.match(TokenType.LBRACE):
            pairs = []
            if not self.check(TokenType.RBRACE):
                key = self._expression()
                self.expect(TokenType.COLON, "Expected ':' after hash key")
                val = self._expression()
                pairs.append((key, val))
                while self.match(TokenType.COMMA):
                    key = self._expression()
                    self.expect(TokenType.COLON, "Expected ':' after hash key")
                    val = self._expression()
                    pairs.append((key, val))
            self.expect(TokenType.RBRACE, "Expected '}' after hash literal")
            return HashLiteral(pairs)

        # Grouped expression:  ( expr )
        if self.match(TokenType.LPAREN):
            expr = self._expression()
            self.expect(TokenType.RPAREN, "Expected ')' after expression")
            return expr

        raise ParseError(self.peek(), "Expected expression")
