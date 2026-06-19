"""
mylang AST Node definitions.
Plain dataclasses — easy to inspect, walk, and extend.
"""

from dataclasses import dataclass, field


# ── Expressions ──────────────────────────────────────────────────────────────

@dataclass
class NumberLiteral:
    value: float | int

@dataclass
class ComplexJLiteral:
    """Imaginary literal: 4j → complex(0, 4)"""
    imag: float

@dataclass
class StringLiteral:
    value: str

@dataclass
class BoolLiteral:
    value: bool

@dataclass
class NullLiteral:
    pass

@dataclass
class Identifier:
    name: str

@dataclass
class BinaryOp:
    op:    str
    left:  object
    right: object

@dataclass
class LogicalOp:
    op:    str      # "&&"  "||"
    left:  object
    right: object

@dataclass
class UnaryOp:
    op:      str    # "-"  "!"
    operand: object

@dataclass
class Assign:
    name:  str
    value: object

@dataclass
class ArrayLiteral:
    elements: list = field(default_factory=list)

@dataclass
class HashLiteral:
    """{ key: value, ... }"""
    pairs: list = field(default_factory=list)   # [(key_expr, val_expr), ...]

@dataclass
class IndexGet:
    """arr[index]  or  map[key]  or  namespace.CONST"""
    array: object
    index: object

@dataclass
class IndexSet:
    """arr[index] = value  or  map[key] = value"""
    array: object
    index: object
    value: object

@dataclass
class MethodCall:
    """expr.method(args)"""
    object: object
    method: str
    args:   list = field(default_factory=list)

@dataclass
class Call:
    callee: str
    args:   list = field(default_factory=list)

@dataclass
class FnExpr:
    """Anonymous function: fn(params) { body }"""
    params: list = field(default_factory=list)
    body:   object = None


# ── Statements ────────────────────────────────────────────────────────────────

@dataclass
class VarDecl:
    name:        str
    initializer: object

@dataclass
class ExprStmt:
    expr: object

@dataclass
class PrintStmt:
    expr: object

@dataclass
class Block:
    statements: list = field(default_factory=list)

@dataclass
class IfStmt:
    condition:   object
    then_branch: object
    else_branch: object = None

@dataclass
class WhileStmt:
    condition: object
    body:      object

@dataclass
class ForStmt:
    """for (var in iterable) { body }"""
    var:      str
    iterable: object
    body:     object

@dataclass
class FnDecl:
    name:   str
    params: list = field(default_factory=list)
    body:   object = None

@dataclass
class ReturnStmt:
    value: object = None

@dataclass
class Program:
    statements: list = field(default_factory=list)
