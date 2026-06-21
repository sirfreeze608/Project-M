"""
mylang  — command-line entry point.

Usage:
  python main.py <file.ml>              Run a source file
  python main.py --tokens <file.ml>     Dump token stream and run
  python main.py --ast    <file.ml>     Dump AST and run
  python main.py --repl                 Interactive REPL
  python main.py --version              Show version
"""

import sys
import os
import textwrap
from pathlib import Path

# Allow running from the mylang/ folder directly
_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

from lexer       import Lexer,  LexerError
from parser      import Parser, ParseError
from interpreter import Interpreter, RuntimeError as MylangRuntimeError
from ast_nodes   import *

__version__ = "0.4.0"


# ── AST pretty-printer ────────────────────────────────────────────────────────

def pretty_ast(node, indent: int = 0) -> str:
    pad  = "  " * indent
    name = type(node).__name__

    if isinstance(node, Program):
        body = "\n".join(pretty_ast(s, indent + 1) for s in node.statements)
        return f"{pad}Program\n{body}"
    if isinstance(node, (NumberLiteral, StringLiteral, BoolLiteral)):
        return f"{pad}{name}({node.value!r})"
    if isinstance(node, NullLiteral):
        return f"{pad}NullLiteral"
    if isinstance(node, Identifier):
        return f"{pad}Identifier({node.name})"
    if isinstance(node, VarDecl):
        return (f"{pad}VarDecl({node.name})\n"
                f"{pretty_ast(node.initializer, indent + 1)}")
    if isinstance(node, BinaryOp):
        return (f"{pad}BinaryOp({node.op})\n"
                f"{pretty_ast(node.left,  indent + 1)}\n"
                f"{pretty_ast(node.right, indent + 1)}")
    if isinstance(node, LogicalOp):
        return (f"{pad}LogicalOp({node.op})\n"
                f"{pretty_ast(node.left,  indent + 1)}\n"
                f"{pretty_ast(node.right, indent + 1)}")
    if isinstance(node, UnaryOp):
        return (f"{pad}UnaryOp({node.op})\n"
                f"{pretty_ast(node.operand, indent + 1)}")
    if isinstance(node, Assign):
        return (f"{pad}Assign({node.name})\n"
                f"{pretty_ast(node.value, indent + 1)}")
    if isinstance(node, Call):
        args = "\n".join(pretty_ast(a, indent + 2) for a in node.args)
        base = f"{pad}Call({node.callee})"
        return f"{base}\n{'  '*(indent+1)}args:\n{args}" if args else base
    if isinstance(node, MethodCall):
        args = "\n".join(pretty_ast(a, indent + 2) for a in node.args)
        base = f"{pad}MethodCall(.{node.method})\n{pretty_ast(node.object, indent+1)}"
        return f"{base}\n{'  '*(indent+1)}args:\n{args}" if args else base
    if isinstance(node, PrintStmt):
        return f"{pad}PrintStmt\n{pretty_ast(node.expr, indent + 1)}"
    if isinstance(node, ExprStmt):
        return f"{pad}ExprStmt\n{pretty_ast(node.expr, indent + 1)}"
    if isinstance(node, Block):
        body = "\n".join(pretty_ast(s, indent + 1) for s in node.statements)
        return f"{pad}Block\n{body}"
    if isinstance(node, IfStmt):
        parts = [f"{pad}IfStmt",
                 f"{'  '*(indent+1)}condition:",
                 pretty_ast(node.condition, indent + 2),
                 f"{'  '*(indent+1)}then:",
                 pretty_ast(node.then_branch, indent + 2)]
        if node.else_branch:
            parts += [f"{'  '*(indent+1)}else:",
                      pretty_ast(node.else_branch, indent + 2)]
        return "\n".join(parts)
    if isinstance(node, WhileStmt):
        return (f"{pad}WhileStmt\n"
                f"{'  '*(indent+1)}condition:\n"
                f"{pretty_ast(node.condition, indent+2)}\n"
                f"{'  '*(indent+1)}body:\n"
                f"{pretty_ast(node.body, indent+2)}")
    if isinstance(node, ForStmt):
        return (f"{pad}ForStmt({node.var} in …)\n"
                f"{pretty_ast(node.iterable, indent+1)}\n"
                f"{pretty_ast(node.body, indent+1)}")
    if isinstance(node, FnDecl):
        params = ", ".join(node.params)
        return (f"{pad}FnDecl({node.name})  params=({params})\n"
                f"{pretty_ast(node.body, indent + 1)}")
    if isinstance(node, FnExpr):
        params = ", ".join(node.params)
        return (f"{pad}FnExpr  params=({params})\n"
                f"{pretty_ast(node.body, indent + 1)}")
    if isinstance(node, ReturnStmt):
        if node.value is None:
            return f"{pad}ReturnStmt"
        return f"{pad}ReturnStmt\n{pretty_ast(node.value, indent + 1)}"
    if isinstance(node, ArrayLiteral):
        elems = "\n".join(pretty_ast(e, indent+1) for e in node.elements)
        return f"{pad}ArrayLiteral\n{elems}" if elems else f"{pad}ArrayLiteral([])"
    if isinstance(node, HashLiteral):
        pairs = "\n".join(
            f"{pretty_ast(k, indent+1)} : {pretty_ast(v, indent+1)}"
            for k, v in node.pairs)
        return f"{pad}HashLiteral\n{pairs}" if pairs else f"{pad}HashLiteral({{}})"
    if isinstance(node, IndexGet):
        return (f"{pad}IndexGet\n"
                f"{pretty_ast(node.array, indent+1)}\n"
                f"{pretty_ast(node.index, indent+1)}")
    if isinstance(node, IndexSet):
        return (f"{pad}IndexSet\n"
                f"{pretty_ast(node.array, indent+1)}\n"
                f"{pretty_ast(node.index, indent+1)}\n"
                f"{pretty_ast(node.value, indent+1)}")
    return f"{pad}{name}(?)"


# ── Pipeline helper ───────────────────────────────────────────────────────────

def run_source(source: str,
               show_tokens: bool = False,
               show_ast:    bool = False) -> int:
    """Run source text.  Returns 0 on success, 1 on error."""
    try:
        # Stage A — Lex
        tokens = Lexer(source).tokenize()
        if show_tokens:
            print("=== TOKENS ===")
            for tok in tokens:
                print(f"  {tok}")
            print()

        # Stage B — Parse
        ast = Parser(tokens).parse()
        if show_ast:
            print("=== AST ===")
            print(pretty_ast(ast))
            print()

        # Stage C — Interpret
        Interpreter().run(ast)
        return 0

    except LexerError as e:
        print(f"LexerError: {e}", file=sys.stderr)
    except ParseError as e:
        print(f"ParseError: {e}", file=sys.stderr)
    except MylangRuntimeError as e:
        print(f"RuntimeError: {e}", file=sys.stderr)
    except Exception as e:
        print(f"InternalError: {e}", file=sys.stderr)
    return 1


# ── REPL ──────────────────────────────────────────────────────────────────────

def repl():
    print(f"mylang {__version__} REPL")
    print("Type 'exit' to quit, '.tokens' / '.ast' to toggle debug output.\n")

    interpreter  = Interpreter()
    show_tokens  = False
    show_ast     = False

    while True:
        try:
            line = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if line == "exit":
            print("Bye!")
            break
        if line == ".tokens":
            show_tokens = not show_tokens
            print(f"Token dump: {'on' if show_tokens else 'off'}")
            continue
        if line == ".ast":
            show_ast = not show_ast
            print(f"AST dump: {'on' if show_ast else 'off'}")
            continue
        if not line:
            continue

        # Auto-semicolon for bare expressions/statements without one
        if not line.endswith(";") and not line.endswith("}"):
            line += ";"

        try:
            tokens = Lexer(line).tokenize()
            if show_tokens:
                for tok in tokens:
                    print(f"  {tok}")
            ast = Parser(tokens).parse()
            if show_ast:
                print(pretty_ast(ast))
            interpreter.run(ast)
        except (LexerError, ParseError, MylangRuntimeError) as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"InternalError: {e}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if not args or "--repl" in args:
        repl()
        return

    if "--version" in args:
        print(f"mylang {__version__}")
        return

    show_tokens = "--tokens" in args
    show_ast    = "--ast"    in args
    files       = [a for a in args if not a.startswith("--")]

    if not files:
        print("Usage: python main.py [--tokens] [--ast] <file.ml>")
        print("       python main.py --repl")
        sys.exit(1)

    path = Path(files[0])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    source = path.read_text(encoding="utf-8")
    sys.exit(run_source(source, show_tokens=show_tokens, show_ast=show_ast))


if __name__ == "__main__":
    main()
