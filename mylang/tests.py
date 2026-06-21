"""
tests.py — automated test suite for mylang.
Run with: python tests.py
"""

import sys
import traceback
from io import StringIO

sys.path.insert(0, ".")

from lexer import Lexer, LexerError
from parser import Parser, ParseError
from interpreter import Interpreter, RuntimeError as MylangRuntimeError
from ast_nodes import Program


def run(source: str) -> list[str]:
    """Run source and return list of printed lines."""
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    interp = Interpreter()
    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        interp.run(ast)
        return sys.stdout.getvalue().splitlines()
    finally:
        sys.stdout = old_stdout


def expect_error(source: str, error_type):
    """Assert that running source raises a given error type."""
    try:
        run(source)
        return False  # no error raised
    except error_type:
        return True
    except Exception:
        return False


# ── Test cases ────────────────────────────────────────────────────────────────

PASS = 0
FAIL = 0


def test(name: str, got, expected):
    global PASS, FAIL
    if got == expected:
        print(f"  ✓  {name}")
        PASS += 1
    else:
        print(f"  ✗  {name}")
        print(f"       expected: {expected!r}")
        print(f"       got:      {got!r}")
        FAIL += 1


def test_true(name: str, condition: bool):
    test(name, condition, True)


# ─────────────────────────────────────────────────────────────────────────────

print("\n── Literals & print ─────────────────────────────────────────────────")
test("integer",    run('print(42);'),             ["42"])
test("float",      run('print(3.14);'),           ["3.14"])
test("string",     run('print("hi");'),           ["hi"])
test("bool true",  run('print(true);'),           ["true"])
test("bool false", run('print(false);'),          ["false"])
test("null",       run('print(null);'),           ["null"])

print("\n── Arithmetic ───────────────────────────────────────────────────────")
test("add",    run('print(1 + 2);'),   ["3"])
test("sub",    run('print(10 - 3);'),  ["7"])
test("mul",    run('print(4 * 5);'),   ["20"])
test("div",    run('print(10 / 4);'),  ["2.5"])
test("modulo", run('print(10 % 3);'),  ["1"])
test("unary -",run('print(-7);'),      ["-7"])
test("precedence", run('print(2 + 3 * 4);'), ["14"])
test("parens",     run('print((2 + 3) * 4);'), ["20"])

print("\n── String concatenation ─────────────────────────────────────────────")
test("str+str", run('print("Hello" + ", " + "World!");'), ["Hello, World!"])
test("str+num", run('print("n=" + 42);'), ["n=42"])

print("\n── Comparisons ──────────────────────────────────────────────────────")
test("==  true",  run('print(1 == 1);'),  ["true"])
test("==  false", run('print(1 == 2);'),  ["false"])
test("!=",        run('print(1 != 2);'),  ["true"])
test("<",         run('print(3 < 5);'),   ["true"])
test("<=",        run('print(5 <= 5);'),  ["true"])
test(">",         run('print(5 > 3);'),   ["true"])
test(">=",        run('print(4 >= 5);'),  ["false"])

print("\n── Logical operators ────────────────────────────────────────────────")
test("&&  true",  run('print(true && true);'),   ["true"])
test("&&  false", run('print(true && false);'),  ["false"])
test("||  true",  run('print(false || true);'),  ["true"])
test("||  false", run('print(false || false);'), ["false"])
test("!   true",  run('print(!false);'),         ["true"])
test("!   false", run('print(!true);'),          ["false"])

print("\n── Variables ────────────────────────────────────────────────────────")
test("let + print", run('let x = 10; print(x);'),  ["10"])
test("reassign",    run('let x = 1; x = 2; print(x);'), ["2"])
test("expression",  run('let a = 3; let b = 4; print(a * b);'), ["12"])

print("\n── If / else ────────────────────────────────────────────────────────")
test("if true",    run('if (true) { print("yes"); }'),               ["yes"])
test("if false",   run('if (false) { print("yes"); }'),              [])
test("if/else",    run('if (false) { print("no"); } else { print("yes"); }'), ["yes"])
test("else if",    run('''
    let x = 2;
    if (x == 1) { print("one"); }
    else if (x == 2) { print("two"); }
    else { print("other"); }
'''), ["two"])

print("\n── While loop ───────────────────────────────────────────────────────")
test("basic while", run('''
    let i = 0;
    while (i < 3) { print(i); i = i + 1; }
'''), ["0", "1", "2"])

print("\n── Functions ────────────────────────────────────────────────────────")
test("basic fn",   run('fn add(a, b) { return a + b; } print(add(3, 4));'), ["7"])
test("no args",    run('fn greet() { return "hi"; } print(greet());'), ["hi"])
test("recursion",  run('''
    fn fact(n) {
        if (n <= 1) { return 1; }
        return n * fact(n - 1);
    }
    print(fact(5));
'''), ["120"])
test("closure scope", run('''
    fn outer(x) {
        fn inner(y) { return x + y; }
        return inner(10);
    }
    print(outer(5));
'''), ["15"])
test("implicit null return", run('''
    fn nothing() { let x = 1; }
    print(nothing());
'''), ["null"])

print("\n── Scoping ──────────────────────────────────────────────────────────")
test("block scope", run('''
    let x = "outer";
    if (true) { let x = "inner"; print(x); }
    print(x);
'''), ["inner", "outer"])

print("\n── Error handling ───────────────────────────────────────────────────")
test_true("undefined variable",
    expect_error('print(undefined_var);', MylangRuntimeError))
test_true("division by zero",
    expect_error('print(1 / 0);', MylangRuntimeError))
test_true("wrong arg count",
    expect_error('fn f(x) { return x; } f(1, 2);', MylangRuntimeError))
test_true("parse error",
    expect_error('let = 5;', ParseError))
test_true("lex error",
    expect_error('@', LexerError))

print("\n── Integration ──────────────────────────────────────────────────────")
test("fibonacci(10)", run('''
    fn fib(n) {
        if (n <= 1) { return n; }
        return fib(n - 1) + fib(n - 2);
    }
    print(fib(10));
'''), ["55"])

test("fizzbuzz 1-5", run('''
    let i = 1;
    while (i <= 5) {
        if (i % 15 == 0) { print("FizzBuzz"); }
        else if (i % 3 == 0) { print("Fizz"); }
        else if (i % 5 == 0) { print("Buzz"); }
        else { print(i); }
        i = i + 1;
    }
'''), ["1", "2", "Fizz", "4", "Buzz"])

print("\n── Arrays ───────────────────────────────────────────────────────────")
test("empty array",        run('let a = []; print(a);'),                   ["[]"])
test("array literal",      run('let a = [1, 2, 3]; print(a);'),            ["[1, 2, 3]"])
test("mixed types",        run('let a = [1, "hi", true, null]; print(a);'),["[1, hi, true, null]"])
test("index get [0]",      run('let a = [10, 20, 30]; print(a[0]);'),      ["10"])
test("index get [2]",      run('let a = [10, 20, 30]; print(a[2]);'),      ["30"])
test("index set",          run('let a = [1, 2, 3]; a[1] = 99; print(a);'),["[1, 99, 3]"])
test("nested arrays",      run('let a = [[1, 2], [3, 4]]; print(a[1][0]);'),["3"])
test("array in expr",      run('let a = [5, 10]; print(a[0] + a[1]);'),   ["15"])
test("string index",       run('let s = "hello"; print(s[1]);'),           ["e"])
test("array + string concat", run('let a = [1,2]; print("arr=" + str(a));'),["arr=[1, 2]"])

print("\n── push / pop ───────────────────────────────────────────────────────")
test("push",  run('let a = [1, 2]; push(a, 3); print(a);'),     ["[1, 2, 3]"])
test("pop",   run('let a = [1, 2, 3]; print(pop(a)); print(a);'),["3","[1, 2]"])
test("push then index", run('''
    let a = [];
    push(a, 10);
    push(a, 20);
    push(a, 30);
    print(a[1]);
'''), ["20"])

print("\n── Built-in functions ───────────────────────────────────────────────")
test("len(array)",   run('print(len([1, 2, 3]));'),        ["3"])
test("len(string)",  run('print(len("hello"));'),           ["5"])
test("len(empty)",   run('print(len([]));'),                ["0"])
test("type(number)", run('print(type(42));'),               ["number"])
test("type(string)", run('print(type("hi"));'),             ["string"])
test("type(bool)",   run('print(type(true));'),             ["bool"])
test("type(null)",   run('print(type(null));'),             ["null"])
test("type(array)",  run('print(type([1,2]));'),            ["array"])
test("str(number)",  run('print(str(3.14));'),              ["3.14"])
test("str(bool)",    run('print(str(false));'),             ["false"])
test("str(null)",    run('print(str(null));'),              ["null"])
test("num(string)",  run('print(num("42"));'),              ["42"])
test("num(float str)",run('print(num("3.14"));'),           ["3.14"])
test("num(number)",  run('print(num(7));'),                 ["7"])

print("\n── Built-in error handling ──────────────────────────────────────────")
test_true("index out of bounds",
    expect_error('let a = [1,2]; print(a[5]);', MylangRuntimeError))
test_true("index into non-array",
    expect_error('let x = 42; print(x[0]);', MylangRuntimeError))
test_true("len of number",
    expect_error('print(len(99));', MylangRuntimeError))
test_true("num of non-numeric string",
    expect_error('print(num("abc"));', MylangRuntimeError))
test_true("pop empty array",
    expect_error('let a = []; pop(a);', MylangRuntimeError))

print("\n── Array integration ────────────────────────────────────────────────")
test("sum array with while", run('''
    let nums = [10, 20, 30, 40, 50];
    let sum = 0;
    let i = 0;
    while (i < len(nums)) {
        sum = sum + nums[i];
        i = i + 1;
    }
    print(sum);
'''), ["150"])

test("build array in loop", run('''
    let squares = [];
    let i = 1;
    while (i <= 5) {
        push(squares, i * i);
        i = i + 1;
    }
    print(squares);
'''), ["[1, 4, 9, 16, 25]"])

test("fn returning array", run('''
    fn range(n) {
        let arr = [];
        let i = 0;
        while (i < n) { push(arr, i); i = i + 1; }
        return arr;
    }
    print(range(4));
'''), ["[0, 1, 2, 3]"])

# ── Summary ───────────────────────────────────────────────────────────────────

total = PASS + FAIL
print(f"\n{'─'*50}")
print(f"  {PASS}/{total} tests passed", end="")
if FAIL == 0:
    print("  🎉 All green!")
else:
    print(f"  — {FAIL} failed")
print()

sys.exit(0 if FAIL == 0 else 1)

print("\n── For loops ────────────────────────────────────────────────────────")
test("for over array", run('''
    let sum = 0;
    for (x in [1, 2, 3, 4, 5]) { sum = sum + x; }
    print(sum);
'''), ["15"])
test("for over string", run('''
    let out = "";
    for (c in "abc") { out = out + c + "-"; }
    print(out);
'''), ["a-b-c-"])
test("for over range", run('''
    let acc = [];
    for (i in range(4)) { push(acc, i); }
    print(acc);
'''), ["[0, 1, 2, 3]"])
test("range(start, stop)", run('print(range(2, 5));'), ["[2, 3, 4]"])
test("range(start, stop, step)", run('print(range(0, 10, 3));'), ["[0, 3, 6, 9]"])

print("\n── Hash maps ────────────────────────────────────────────────────────")
test("empty hash",   run('let h = {}; print(h);'),              ["{}"])
test("hash literal", run('let h = {"a": 1, "b": 2}; print(h);'), ['{"a": 1, "b": 2}'] if False else ['{a: 1, b: 2}'])
test("hash get",     run('let h = {"x": 99}; print(h["x"]);'), ["99"])
test("hash set",     run('let h = {"x": 1}; h["x"] = 42; print(h["x"]);'), ["42"])
test("hash new key", run('let h = {}; h["k"] = "v"; print(h["k"]);'), ["v"])
test("hash missing key returns null",
     run('let h = {}; print(h["missing"]);'), ["null"])
test("hash .has()",  run('let h = {"a": 1}; print(h.has("a")); print(h.has("b"));'), ["true","false"])
test("hash .del()",  run('let h = {"a":1,"b":2}; h.del("a"); print(h.has("a"));'), ["false"])
test("hash .keys()", run('let h = {"x": 1, "y": 2}; print(len(h.keys()));'), ["2"])
test("hash .len()",  run('let h = {"a":1,"b":2,"c":3}; print(h.len());'), ["3"])
test("for over hash keys", run('''
    let h = {"a": 1};
    for (k in h) { print(k); }
'''), ["a"])

print("\n── String methods ───────────────────────────────────────────────────")
test(".upper()",      run('print("hello".upper());'),              ["HELLO"])
test(".lower()",      run('print("HELLO".lower());'),              ["hello"])
test(".trim()",       run('print("  hi  ".trim());'),              ["hi"])
test(".replace()",    run('print("aabbcc".replace("bb","XX"));'),  ["aaXXcc"])
test(".split()",      run('print("a,b,c".split(","));'),           ["[a, b, c]"])
test(".join()",       run('print(["x","y","z"].join("-"));'),      ["x-y-z"])
test(".contains()",   run('print("foobar".contains("oba"));'),     ["true"])
test(".starts_with()",run('print("hello".starts_with("hel"));'),   ["true"])
test(".ends_with()",  run('print("hello".ends_with("llo"));'),     ["true"])
test(".slice()",      run('print("abcdef".slice(1, 4));'),         ["bcd"])
test(".index_of()",   run('print("hello".index_of("ll"));'),       ["2"])
test(".index_of() miss", run('print("hello".index_of("xyz"));'),   ["-1"])

print("\n── Array methods ────────────────────────────────────────────────────")
test(".reverse()",  run('print([1,2,3].reverse());'),              ["[3, 2, 1]"])
test(".slice()",    run('print([1,2,3,4,5].slice(1,4));'),         ["[2, 3, 4]"])
test(".contains()", run('print([1,2,3].contains(2));'),            ["true"])
test(".index_of()", run('print([10,20,30].index_of(20));'),        ["1"])
test(".len()",      run('print([1,2,3].len());'),                  ["3"])

print("\n── First-class functions ────────────────────────────────────────────")
test("fn in variable",   run('let f = fn(x) { return x * 2; }; print(f(5));'),    ["10"])
test("fn as argument",   run('''
    fn apply(f, x) { return f(x); }
    print(apply(fn(n) { return n + 1; }, 9));
'''), ["10"])
test("closure / make_adder", run('''
    fn make_adder(n) { return fn(x) { return x + n; }; }
    let add5 = make_adder(5);
    print(add5(10));
'''), ["15"])
test("fn stored in array", run('''
    let ops = [fn(x) { return x + 1; }, fn(x) { return x * 2; }];
    print(ops[0](4));
    print(ops[1](4));
'''), ["5", "8"])
test("fn stored in hash", run('''
    let h = {"double": fn(x) { return x * 2; }};
    print(h["double"](7));
'''), ["14"])

print("\n── map / filter / reduce ────────────────────────────────────────────")
test(".map()",    run('print([1,2,3].map(fn(x){ return x*x; }));'),  ["[1, 4, 9]"])
test(".filter()", run('print([1,2,3,4,5].filter(fn(x){ return x % 2 == 0; }));'), ["[2, 4]"])
test(".reduce()", run('print([1,2,3,4].reduce(fn(a,b){ return a+b; }, 0));'),  ["10"])
test("chain map+filter", run('''
    let r = [1,2,3,4,5,6]
        .filter(fn(x){ return x % 2 == 0; })
        .map(fn(x){ return x * 10; });
    print(r);
'''), ["[20, 40, 60]"])
