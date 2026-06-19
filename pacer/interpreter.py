"""
mylang Interpreter  — Stage C of the pipeline.
Tree-walks the AST and executes nodes directly using Python as the host.
Uses an Environment (scope chain) to track variable bindings.
"""

from ast_nodes import *
from stdlib import (
    register_stdlib, MylangComplex, MylangMatrix, MylangNamespace,
)


# ── Exceptions ────────────────────────────────────────────────────────────────

class ReturnSignal(Exception):
    """Non-error control-flow: unwinds call stack to the call site."""
    def __init__(self, value):
        self.value = value


class RuntimeError(Exception):
    pass


# ── Runtime value types ───────────────────────────────────────────────────────

class MylangArray:
    def __init__(self, elements: list):
        self.elements = list(elements)

    def __repr__(self):
        return "[" + ", ".join(_str(e) for e in self.elements) + "]"


class MylangHash:
    def __init__(self, pairs: dict = None):
        self.pairs: dict = pairs if pairs is not None else {}

    def __repr__(self):
        items = ", ".join(f"{_str(k)}: {_str(v)}"
                          for k, v in self.pairs.items())
        return "{" + items + "}"


class Function:
    """Named user-defined function (FnDecl), captured with its closure."""
    def __init__(self, name: str, params: list, body, closure):
        self.name    = name
        self.params  = params
        self.body    = body
        self.closure = closure

    def __repr__(self):
        return f"<fn {self.name}>"


class AnonFunction:
    """Anonymous function value (FnExpr), captured with its closure."""
    def __init__(self, params: list, body, closure):
        self.params  = params
        self.body    = body
        self.closure = closure

    def __repr__(self):
        return "<fn>"


class BuiltinFunction:
    """Native function implemented in Python."""
    def __init__(self, name: str, arity, fn):
        self.name  = name
        self.arity = arity   # int or None (variadic)
        self.fn    = fn

    def __repr__(self):
        return f"<builtin {self.name}>"


# ── Stringify helpers (module-level so stdlib can use them) ───────────────────

def _str(value) -> str:
    if value is None:                      return "null"
    if isinstance(value, bool):            return "true" if value else "false"
    if isinstance(value, MylangArray):     return repr(value)
    if isinstance(value, MylangHash):      return repr(value)
    if isinstance(value, MylangComplex):   return repr(value)
    if isinstance(value, MylangMatrix):    return repr(value)
    if isinstance(value, MylangNamespace): return repr(value)
    if isinstance(value, float):
        t = str(value)
        return t[:-2] if t.endswith(".0") else t
    return str(value)


def _type_name(v) -> str:
    if v is None:                       return "null"
    if isinstance(v, bool):             return "bool"
    if isinstance(v, (int, float)):     return "number"
    if isinstance(v, str):              return "string"
    if isinstance(v, MylangArray):      return "array"
    if isinstance(v, MylangHash):       return "hash"
    if isinstance(v, MylangComplex):    return "complex"
    if isinstance(v, MylangMatrix):     return "matrix"
    if isinstance(v, MylangNamespace):  return "namespace"
    if isinstance(v, (Function, AnonFunction, BuiltinFunction)):
        return "function"
    return "unknown"


# ── Environment (lexical scope chain) ────────────────────────────────────────

class Environment:
    def __init__(self, parent=None):
        self.vars:   dict = {}
        self.parent        = parent

    def define(self, name: str, value):
        self.vars[name] = value

    def get(self, name: str):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeError(f"Undefined variable '{name}'")

    def assign(self, name: str, value):
        if name in self.vars:
            self.vars[name] = value
            return
        if self.parent:
            self.parent.assign(name, value)
            return
        raise RuntimeError(f"Undefined variable '{name}'")


# ── Core built-in functions ───────────────────────────────────────────────────

def _b_len(args):
    v = args[0]
    if isinstance(v, MylangArray):  return len(v.elements)
    if isinstance(v, MylangHash):   return len(v.pairs)
    if isinstance(v, str):          return len(v)
    raise RuntimeError(
        f"len() expects array, hash, or string — got {_type_name(v)}")

def _b_type(args):  return _type_name(args[0])
def _b_str(args):   return _str(args[0])

def _b_num(args):
    v = args[0]
    if isinstance(v, bool):
        raise RuntimeError("num() cannot convert a bool")
    if isinstance(v, (int, float)): return v
    if isinstance(v, str):
        try:    return int(v)
        except ValueError:
            try: return float(v)
            except ValueError:
                raise RuntimeError(
                    f"num() cannot convert \"{v}\" to a number")
    raise RuntimeError(f"num() cannot convert {_type_name(v)}")

def _b_push(args):
    arr, val = args
    if not isinstance(arr, MylangArray):
        raise RuntimeError(f"push() expects array — got {_type_name(arr)}")
    arr.elements.append(val)
    return arr

def _b_pop(args):
    arr = args[0]
    if not isinstance(arr, MylangArray):
        raise RuntimeError(f"pop() expects array — got {_type_name(arr)}")
    if not arr.elements:
        raise RuntimeError("pop() called on empty array")
    return arr.elements.pop()

def _b_keys(args):
    h = args[0]
    if not isinstance(h, MylangHash):
        raise RuntimeError(f"keys() expects hash — got {_type_name(h)}")
    return MylangArray(list(h.pairs.keys()))

def _b_values(args):
    h = args[0]
    if not isinstance(h, MylangHash):
        raise RuntimeError(f"values() expects hash — got {_type_name(h)}")
    return MylangArray(list(h.pairs.values()))

def _b_has(args):
    h, key = args
    if not isinstance(h, MylangHash):
        raise RuntimeError(f"has() expects hash — got {_type_name(h)}")
    return key in h.pairs

def _b_del(args):
    h, key = args
    if not isinstance(h, MylangHash):
        raise RuntimeError(f"del() expects hash — got {_type_name(h)}")
    h.pairs.pop(key, None)
    return h

def _b_range(args):
    if len(args) == 1:
        start, stop, step = 0, args[0], 1
    elif len(args) == 2:
        start, stop, step = args[0], args[1], 1
    else:
        start, stop, step = args
    for v in (start, stop, step):
        if not isinstance(v, (int, float)):
            raise RuntimeError("range() arguments must be numbers")
    return MylangArray(list(range(int(start), int(stop), int(step))))


BUILTINS = {
    "len":    BuiltinFunction("len",    1,    _b_len),
    "type":   BuiltinFunction("type",   1,    _b_type),
    "str":    BuiltinFunction("str",    1,    _b_str),
    "num":    BuiltinFunction("num",    1,    _b_num),
    "push":   BuiltinFunction("push",   2,    _b_push),
    "pop":    BuiltinFunction("pop",    1,    _b_pop),
    "keys":   BuiltinFunction("keys",   1,    _b_keys),
    "values": BuiltinFunction("values", 1,    _b_values),
    "has":    BuiltinFunction("has",    2,    _b_has),
    "del":    BuiltinFunction("del",    2,    _b_del),
    "range":  BuiltinFunction("range",  None, _b_range),
}


# ── String methods ────────────────────────────────────────────────────────────

def _string_method(obj: str, method: str, args: list):
    if method == "upper":      return obj.upper()
    if method == "lower":      return obj.lower()
    if method == "trim":       return obj.strip()
    if method == "split":
        sep = args[0] if args else " "
        if not isinstance(sep, str):
            raise RuntimeError("split() separator must be a string")
        return MylangArray(obj.split(sep))
    if method == "replace":
        if len(args) != 2:
            raise RuntimeError("replace(old, new) requires 2 arguments")
        old, new = args
        if not isinstance(old, str) or not isinstance(new, str):
            raise RuntimeError("replace() arguments must be strings")
        return obj.replace(old, new)
    if method == "contains":
        if not args or not isinstance(args[0], str):
            raise RuntimeError("contains() requires a string argument")
        return args[0] in obj
    if method == "starts_with":
        if not args or not isinstance(args[0], str):
            raise RuntimeError("starts_with() requires a string argument")
        return obj.startswith(args[0])
    if method == "ends_with":
        if not args or not isinstance(args[0], str):
            raise RuntimeError("ends_with() requires a string argument")
        return obj.endswith(args[0])
    if method == "slice":
        if len(args) < 1:
            raise RuntimeError("slice(start[, end]) requires at least 1 argument")
        start = int(args[0])
        end   = int(args[1]) if len(args) > 1 else len(obj)
        return obj[start:end]
    if method == "index_of":
        if not args or not isinstance(args[0], str):
            raise RuntimeError("index_of() requires a string argument")
        return obj.find(args[0])
    raise RuntimeError(f"String has no method '{method}'")


# ── Array methods ─────────────────────────────────────────────────────────────

def _array_method(obj: MylangArray, method: str, args: list, interp):
    if method == "push":
        if not args: raise RuntimeError("push() requires 1 argument")
        obj.elements.append(args[0]); return obj
    if method == "pop":
        if not obj.elements: raise RuntimeError("pop() on empty array")
        return obj.elements.pop()
    if method == "len":
        return len(obj.elements)
    if method == "slice":
        start = int(args[0]) if args else 0
        end   = int(args[1]) if len(args) > 1 else len(obj.elements)
        return MylangArray(obj.elements[start:end])
    if method == "contains":
        if not args: raise RuntimeError("contains() requires 1 argument")
        return args[0] in obj.elements
    if method == "index_of":
        if not args: raise RuntimeError("index_of() requires 1 argument")
        try:    return obj.elements.index(args[0])
        except ValueError: return -1
    if method == "reverse":
        return MylangArray(list(reversed(obj.elements)))
    if method == "join":
        sep = args[0] if args else ""
        if not isinstance(sep, str):
            raise RuntimeError("join() separator must be a string")
        return sep.join(_str(e) for e in obj.elements)
    if method == "map":
        if not args: raise RuntimeError("map() requires a function argument")
        fn = args[0]
        return MylangArray([interp._call_fn(fn, [e]) for e in obj.elements])
    if method == "filter":
        if not args: raise RuntimeError("filter() requires a function argument")
        fn = args[0]
        return MylangArray([e for e in obj.elements
                            if interp._is_truthy(interp._call_fn(fn, [e]))])
    if method == "reduce":
        if not args: raise RuntimeError("reduce(fn, init) requires arguments")
        fn    = args[0]
        items = obj.elements
        acc   = args[1] if len(args) > 1 else (items[0] if items else None)
        start = 1 if len(args) < 2 else 0
        for e in items[start:]:
            acc = interp._call_fn(fn, [acc, e])
        return acc
    raise RuntimeError(f"Array has no method '{method}'")


# ── Hash methods ──────────────────────────────────────────────────────────────

def _hash_method(obj: MylangHash, method: str, args: list):
    if method == "keys":   return MylangArray(list(obj.pairs.keys()))
    if method == "values": return MylangArray(list(obj.pairs.values()))
    if method == "has":
        if not args: raise RuntimeError("has() requires 1 argument")
        return args[0] in obj.pairs
    if method == "del":
        if not args: raise RuntimeError("del() requires 1 argument")
        obj.pairs.pop(args[0], None); return obj
    if method == "len":
        return len(obj.pairs)
    raise RuntimeError(f"Hash has no method '{method}'")


# ── Interpreter ───────────────────────────────────────────────────────────────

class Interpreter:
    def __init__(self):
        self.globals = Environment()
        for name, fn in BUILTINS.items():
            self.globals.define(name, fn)
        register_stdlib(self)          # math / stats / ee / matrix / complex
        self.env    = self.globals
        self.output: list[str] = []

    def run(self, program: Program):
        for stmt in program.statements:
            self._exec(stmt)

    # ── dispatch ──────────────────────────────────────────────────────────────

    def _exec(self, node):
        m = getattr(self, "_exec_" + type(node).__name__, None)
        if m is None:
            raise RuntimeError(
                f"No exec handler for {type(node).__name__}")
        return m(node)

    def _eval(self, node):
        m = getattr(self, "_eval_" + type(node).__name__, None)
        if m is None:
            raise RuntimeError(
                f"No eval handler for {type(node).__name__}")
        return m(node)

    # ── statement handlers ────────────────────────────────────────────────────

    def _exec_VarDecl(self, node: VarDecl):
        self.env.define(node.name, self._eval(node.initializer))

    def _exec_FnDecl(self, node: FnDecl):
        self.env.define(node.name,
            Function(node.name, node.params, node.body, self.env))

    def _exec_ExprStmt(self, node: ExprStmt):
        self._eval(node.expr)

    def _exec_PrintStmt(self, node: PrintStmt):
        text = _str(self._eval(node.expr))
        print(text)
        self.output.append(text)

    def _exec_Block(self, node: Block, env: Environment = None):
        prev     = self.env
        self.env = env or Environment(self.env)
        try:
            for stmt in node.statements:
                self._exec(stmt)
        finally:
            self.env = prev

    def _exec_IfStmt(self, node: IfStmt):
        if self._is_truthy(self._eval(node.condition)):
            self._exec(node.then_branch)
        elif node.else_branch:
            self._exec(node.else_branch)

    def _exec_WhileStmt(self, node: WhileStmt):
        while self._is_truthy(self._eval(node.condition)):
            self._exec(node.body)

    def _exec_ForStmt(self, node: ForStmt):
        iterable = self._eval(node.iterable)
        if isinstance(iterable, MylangArray):
            items = iterable.elements
        elif isinstance(iterable, str):
            items = list(iterable)
        elif isinstance(iterable, MylangHash):
            items = list(iterable.pairs.keys())
        else:
            raise RuntimeError(
                f"Cannot iterate over {_type_name(iterable)}")
        for item in items:
            loop_env = Environment(self.env)
            loop_env.define(node.var, item)
            self._exec_Block(node.body, env=loop_env)

    def _exec_ReturnStmt(self, node: ReturnStmt):
        raise ReturnSignal(
            self._eval(node.value) if node.value is not None else None)

    # ── expression handlers ───────────────────────────────────────────────────

    def _eval_NumberLiteral(self, n): return n.value
    def _eval_ComplexJLiteral(self, n): return MylangComplex(0.0, n.imag)
    def _eval_StringLiteral(self, n): return n.value
    def _eval_BoolLiteral(self,   n): return n.value
    def _eval_NullLiteral(self,   n): return None
    def _eval_Identifier(self,    n): return self.env.get(n.name)

    def _eval_FnExpr(self, node: FnExpr):
        return AnonFunction(node.params, node.body, self.env)

    def _eval_Assign(self, node: Assign):
        value = self._eval(node.value)
        self.env.assign(node.name, value)
        return value

    def _eval_ArrayLiteral(self, node: ArrayLiteral):
        return MylangArray([self._eval(e) for e in node.elements])

    def _eval_HashLiteral(self, node: HashLiteral):
        pairs = {}
        for k_expr, v_expr in node.pairs:
            key = self._eval(k_expr)
            if not isinstance(key, (str, int, float, bool)):
                raise RuntimeError(
                    f"Hash key must be a string or number — got {_type_name(key)}")
            pairs[key] = self._eval(v_expr)
        return MylangHash(pairs)

    def _eval_IndexGet(self, node: IndexGet):
        obj   = self._eval(node.array)
        index = self._eval(node.index)
        if isinstance(obj, MylangNamespace):
            if not isinstance(index, str):
                raise RuntimeError("Namespace key must be a string")
            return obj.get_constant(index)
        if isinstance(obj, MylangArray):
            self._check_index(obj, index)
            return obj.elements[int(index)]
        if isinstance(obj, MylangHash):
            return obj.pairs.get(index, None)
        if isinstance(obj, str):
            if not isinstance(index, (int, float)):
                raise RuntimeError("String index must be a number")
            i = int(index)
            if i < 0 or i >= len(obj):
                raise RuntimeError(f"String index {i} out of bounds")
            return obj[i]
        raise RuntimeError(f"Cannot index into {_type_name(obj)}")

    def _eval_IndexSet(self, node: IndexSet):
        obj   = self._eval(node.array)
        index = self._eval(node.index)
        value = self._eval(node.value)
        if isinstance(obj, MylangArray):
            self._check_index(obj, index)
            obj.elements[int(index)] = value
        elif isinstance(obj, MylangHash):
            obj.pairs[index] = value
        else:
            raise RuntimeError(f"Cannot assign into {_type_name(obj)}")
        return value

    def _eval_MethodCall(self, node: MethodCall):
        obj  = self._eval(node.object)
        args = [self._eval(a) for a in node.args]

        if isinstance(obj, MylangNamespace):
            return obj.call(node.method, args)
        if isinstance(obj, str):
            return _string_method(obj, node.method, args)
        if isinstance(obj, MylangArray):
            return _array_method(obj, node.method, args, self)
        if isinstance(obj, MylangHash):
            return _hash_method(obj, node.method, args)

        if isinstance(obj, MylangComplex):
            import cmath as _cm, math as _m
            if node.method == "real":  return obj.real
            if node.method == "imag":  return obj.imag
            if node.method == "abs":   return abs(obj.value)
            if node.method == "conj":  return MylangComplex(obj.real, -obj.imag)
            if node.method == "angle": return _m.degrees(_cm.phase(obj.value))
            raise RuntimeError(f"Complex has no method '{node.method}'")

        if isinstance(obj, MylangMatrix):
            from stdlib import (
                _mat_transpose, _mat_det, _mat_trace, _mat_get, _mat_set,
                _mat_shape, _mat_to_array, _mat_scale,
            )
            dispatch = {
                "transpose": _mat_transpose, "det":      _mat_det,
                "trace":     _mat_trace,     "get":      _mat_get,
                "set":       _mat_set,       "shape":    _mat_shape,
                "to_array":  _mat_to_array,  "scale":    _mat_scale,
            }
            if node.method in dispatch:
                return dispatch[node.method]([obj] + args)
            raise RuntimeError(f"Matrix has no method '{node.method}'")

        raise RuntimeError(
            f"Value of type {_type_name(obj)} has no method '{node.method}'")

    def _eval_UnaryOp(self, node: UnaryOp):
        v = self._eval(node.operand)
        if node.op == "-":
            if not isinstance(v, (int, float)):
                raise RuntimeError(
                    f"Unary '-' requires a number — got {_type_name(v)}")
            return -v
        if node.op == "!":
            return not self._is_truthy(v)

    def _eval_BinaryOp(self, node: BinaryOp):
        left  = self._eval(node.left)
        right = self._eval(node.right)
        op    = node.op

        # Native complex arithmetic: any operand being MylangComplex promotes both
        if isinstance(left, MylangComplex) or isinstance(right, MylangComplex):
            def _to_c(v):
                if isinstance(v, MylangComplex): return v.value
                if isinstance(v, (int, float)):  return complex(v)
                raise RuntimeError(
                    f"Operator '{op}' cannot mix complex with {_type_name(v)}")
            lc, rc = _to_c(left), _to_c(right)
            if op == "+": r = lc + rc
            elif op == "-": r = lc - rc
            elif op == "*": r = lc * rc
            elif op == "/":
                if rc == 0: raise RuntimeError("Complex division by zero")
                r = lc / rc
            elif op == "==": return lc == rc
            elif op == "!=": return lc != rc
            else: raise RuntimeError(
                f"Operator '{op}' not supported on complex numbers")
            return MylangComplex(r.real, r.imag)

        if op == "+":
            if isinstance(left, str) or isinstance(right, str):
                return _str(left) + _str(right)
            self._nums(left, right, op)
            return left + right
        if op == "-":  self._nums(left, right, op); return left - right
        if op == "*":  self._nums(left, right, op); return left * right
        if op == "/":
            self._nums(left, right, op)
            if right == 0: raise RuntimeError("Division by zero")
            return left / right
        if op == "%":
            self._nums(left, right, op)
            if right == 0: raise RuntimeError("Modulo by zero")
            return left % right
        if op == "==": return self._eq(left, right)
        if op == "!=": return not self._eq(left, right)
        if op in ("<", "<=", ">", ">="):
            self._nums(left, right, op)
            return {"<": left < right, "<=": left <= right,
                    ">": left > right,  ">=": left >= right}[op]
        raise RuntimeError(f"Unknown operator '{op}'")

    def _eval_LogicalOp(self, node: LogicalOp):
        left = self._eval(node.left)
        if node.op == "||":
            return left if self._is_truthy(left) else self._eval(node.right)
        if node.op == "&&":
            return self._eval(node.right) if self._is_truthy(left) else left

    def _eval_Call(self, node: Call):
        callee = self.env.get(node.callee)
        args   = [self._eval(a) for a in node.args]
        return self._dispatch_call(node.callee, callee, args)

    # ── call helpers (reused by map / filter / reduce) ────────────────────────

    def _call_fn(self, fn, args: list):
        return self._dispatch_call("<anon>", fn, args)

    def _dispatch_call(self, name: str, callee, args: list):
        if isinstance(callee, BuiltinFunction):
            if callee.arity is not None and len(args) != callee.arity:
                raise RuntimeError(
                    f"'{callee.name}' expects {callee.arity} arg(s)"
                    f" — got {len(args)}")
            return callee.fn(args)

        if isinstance(callee, (Function, AnonFunction)):
            params  = callee.params
            body    = callee.body
            closure = callee.closure
            if len(args) != len(params):
                label = getattr(callee, "name", name)
                raise RuntimeError(
                    f"'{label}' expects {len(params)} arg(s)"
                    f" — got {len(args)}")
            call_env = Environment(closure)
            for p, a in zip(params, args):
                call_env.define(p, a)
            try:
                self._exec_Block(body, env=call_env)
            except ReturnSignal as r:
                return r.value
            return None

        raise RuntimeError(
            f"'{name}' is not callable — got {_type_name(callee)}")

    # ── helpers ───────────────────────────────────────────────────────────────

    def _is_truthy(self, v) -> bool:
        if v is None or v is False: return False
        return True

    def _eq(self, a, b) -> bool:
        if a is None and b is None: return True
        if a is None or b is None:  return False
        return a == b

    def _nums(self, a, b, op: str):
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise RuntimeError(
                f"Operator '{op}' requires numbers"
                f" — got {_type_name(a)} and {_type_name(b)}")

    def _check_index(self, arr: MylangArray, index):
        if not isinstance(index, (int, float)):
            raise RuntimeError(
                f"Array index must be a number — got {_type_name(index)}")
        i = int(index)
        if i < 0 or i >= len(arr.elements):
            raise RuntimeError(
                f"Index {i} out of bounds (length {len(arr.elements)})")
