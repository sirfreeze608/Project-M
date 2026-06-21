# mylang — Complete Language Reference & User Guide

> **mylang** is a dynamically-typed, interpreted scripting language designed for
> mathematics, statistics, and electrical engineering, built directly into the
> **Pacer** code editor.  Files use the `.ml` extension.  Press **F5** inside
> Pacer to run any `.ml` file instantly — no compilation step, no terminal needed.

---

## Table of Contents

1. [Getting Started — Hello World](#1-getting-started)
2. [Running Code in Pacer](#2-running-code-in-pacer)
3. [Language Basics](#3-language-basics)
4. [Control Flow](#4-control-flow)
5. [Functions](#5-functions)
6. [Arrays](#6-arrays)
7. [Hash Maps](#7-hash-maps)
8. [String Methods](#8-string-methods)
9. [Math Library](#9-math-library)
10. [Statistics Library](#10-statistics-library)
11. [Electrical Engineering Library](#11-electrical-engineering-library)
12. [Complex Numbers](#12-complex-numbers)
13. [Matrices](#13-matrices)
14. [First-Class Functions](#14-first-class-functions)
15. [Real-World Use Cases](#15-real-world-use-cases)
16. [Pacer AI Commands](#16-pacer-ai-commands)
17. [Built-in Quick Reference](#17-built-in-quick-reference)
18. [Common Errors & Fixes](#18-common-errors--fixes)

---

## 1. Getting Started

### Hello World

```ml
print("Hello, World!");
```

That's it. No imports, no `main()`, no boilerplate.  Every statement ends with a
semicolon `;`.  Run it with **F5** in Pacer, or from the terminal:

```bash
mylang hello.ml
```

### Your second program — variables and maths

```ml
let name   = "Alice";
let radius = 5;
let area   = PI * radius * radius;

print("Hello, " + name + "!");
print("Circle area: " + str(round(area, 2)));
```

Output:
```
Hello, Alice!
Circle area: 78.54
```

### Comments

```ml
// This is a single-line comment

let x = 42;   // inline comment
```

---

## 2. Running Code in Pacer

| Action | How |
|--------|-----|
| New `.ml` file | **Ctrl+N** — always opens a mylang file |
| New file (other type) | **Ctrl+Shift+N** — pick from a list |
| Run current file | **F5** or type `/run` in the command bar |
| Save | **Ctrl+S** — auto-appends `.ml` if no extension typed |
| Save As | **Ctrl+Shift+S** |
| Open docs | **mylang menu → Open Documentation** |

**Unsaved files** show a `●` dot in the tab name.  The dot clears when you save.

**Output panel** (bottom-left) shows your program's `print()` output and any
runtime errors in red.

**AI Assistant panel** (bottom-right) responds to `/` commands:

```
/run          — execute the current .ml file
/debug        — ask AI to find bugs in your code
/fix          — ask AI to repair errors (offers to replace your code)
/complete     — ask AI to finish your half-written code
/explain      — ask AI what the code does, step by step
/mylang <q>   — ask anything about mylang syntax or built-ins
/help         — list all commands
```

---

## 3. Language Basics

### Variables

```ml
let x     = 10;
let name  = "mylang";
let flag  = true;
let empty = null;
let pi    = 3.14159;
```

Re-assign any time (no `let` needed):

```ml
let score = 0;
score = score + 1;   // score is now 1
```

### Data Types

| Type | Example | Notes |
|------|---------|-------|
| number | `42`, `3.14`, `1e-6` | integers and floats unified |
| string | `"hello"` | double quotes only |
| bool | `true`, `false` | |
| null | `null` | absence of value |
| array | `[1, 2, 3]` | ordered, mixed types OK |
| hash | `{"key": value}` | dictionary / map |
| complex | `complex(3, 4)` | 3+4j |
| matrix | `matrix([[1,2],[3,4]])` | 2-D numeric matrix |
| function | `fn(x) { return x*2; }` | first-class value |

Check type at runtime:

```ml
print(type(42));        // number
print(type("hi"));      // string
print(type([1,2,3]));   // array
print(type(null));      // null
```

### Operators

```ml
// Arithmetic
let a = 10 + 3;    // 13
let b = 10 - 3;    // 7
let c = 10 * 3;    // 30
let d = 10 / 3;    // 3.3333...
let e = 10 % 3;    // 1  (modulo)

// Comparison  → returns true/false
10 == 10    // true
10 != 5     // true
10 > 5      // true
10 <= 10    // true

// Logical
true && false   // false
true || false   // true
!true           // false

// String concatenation
"Hello" + ", " + "World!"   // "Hello, World!"
"Value: " + str(42)         // "Value: 42"
```

### Scientific Notation

```ml
let cap  = 1e-6;    // 0.000001  (1 µF)
let mega = 1e6;     // 1000000
let pico = 4.7e-12; // 4.7 pF
```

---

## 4. Control Flow

### If / Else If / Else

```ml
let grade = 85;

if (grade >= 90) {
    print("A");
} else if (grade >= 80) {
    print("B");
} else if (grade >= 70) {
    print("C");
} else {
    print("F");
}
```

### While Loop

```ml
let i = 1;
while (i <= 5) {
    print(i);
    i = i + 1;
}
// prints 1 2 3 4 5
```

### For-In Loop

Iterate over **arrays**, **strings**, **hashes**, or `range()`:

```ml
// Array
for (fruit in ["apple", "banana", "cherry"]) {
    print(fruit);
}

// String (character by character)
for (ch in "hello") {
    print(ch);
}

// range(stop)
for (i in range(5)) {
    print(i);    // 0 1 2 3 4
}

// range(start, stop)
for (i in range(2, 8)) {
    print(i);    // 2 3 4 5 6 7
}

// range(start, stop, step)
for (i in range(0, 20, 5)) {
    print(i);    // 0 5 10 15
}

// Hash — iterates over keys
let config = {"host": "localhost", "port": 8080};
for (key in config) {
    print(key + " = " + str(config[key]));
}
```

### Nested loops — multiplication table

```ml
for (i in range(1, 4)) {
    for (j in range(1, 4)) {
        print(str(i) + " × " + str(j) + " = " + str(i * j));
    }
}
```

---

## 5. Functions

### Named functions

```ml
fn greet(name) {
    return "Hello, " + name + "!";
}

print(greet("Alice"));   // Hello, Alice!
print(greet("Bob"));     // Hello, Bob!
```

### Multiple parameters

```ml
fn power_dissipated(voltage, resistance) {
    return (voltage * voltage) / resistance;
}

print(power_dissipated(12, 100));   // 1.44  watts
```

### Default-style pattern (check null)

```ml
fn greet_with_title(name, title) {
    if (title == null) {
        return "Hello, " + name + "!";
    }
    return "Hello, " + title + " " + name + "!";
}
```

### Recursion

```ml
fn factorial(n) {
    if (n <= 1) { return 1; }
    return n * factorial(n - 1);
}

print(factorial(10));   // 3628800
```

### Functions returning multiple values via hash

```ml
fn stats_summary(data) {
    return {
        "mean":   mean(data),
        "stdev":  stdev(data),
        "min":    min(data),
        "max":    max(data)
    };
}

let results = stats_summary([4, 8, 15, 16, 23, 42]);
print("Mean:  " + str(round(results["mean"], 2)));
print("Stdev: " + str(round(results["stdev"], 2)));
```

---

## 6. Arrays

```ml
let nums = [10, 20, 30, 40, 50];

// Access
print(nums[0]);         // 10
print(nums[4]);         // 50

// Modify
nums[2] = 99;
print(nums);            // [10, 20, 99, 40, 50]

// Length
print(len(nums));       // 5

// Add / remove
push(nums, 60);         // append
let last = pop(nums);   // remove & return last
```

### Array methods

```ml
let data = [3, 1, 4, 1, 5, 9, 2, 6];

print(data.reverse());              // [6, 2, 9, 5, 1, 4, 1, 3]
print(data.slice(2, 5));            // [4, 1, 5]
print(data.contains(9));            // true
print(data.index_of(5));            // 4
print(data.join(", "));             // "3, 1, 4, 1, 5, 9, 2, 6"

// Functional methods
let doubled = data.map(fn(x) { return x * 2; });
let evens   = data.filter(fn(x) { return x % 2 == 0; });
let total   = data.reduce(fn(acc, x) { return acc + x; }, 0);

print(doubled);   // [6, 2, 8, 2, 10, 18, 4, 12]
print(evens);     // [4, 2, 6]
print(total);     // 31
```

### Building arrays dynamically

```ml
fn squares_up_to(n) {
    let result = [];
    for (i in range(1, n + 1)) {
        push(result, i * i);
    }
    return result;
}

print(squares_up_to(6));   // [1, 4, 9, 16, 25, 36]
```

### Nested arrays (2-D grid)

```ml
let grid = [[1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]];

print(grid[1][2]);    // 6  (row 1, col 2)
grid[0][0] = 99;
print(grid[0]);       // [99, 2, 3]
```

---

## 7. Hash Maps

```ml
let person = {
    "name":   "Alice",
    "age":    30,
    "active": true
};

// Read
print(person["name"]);     // Alice

// Write / add key
person["email"] = "alice@example.com";
person["age"]   = 31;

// Check existence
print(person.has("email"));   // true
print(person.has("phone"));   // false

// Delete a key
person.del("active");

// Iterate
for (key in person) {
    print(key + ": " + str(person[key]));
}

// Keys and values as arrays
print(person.keys());     // [name, age, email]
print(person.values());   // [Alice, 31, alice@example.com]
print(person.len());      // 3
```

### Hash as a record / struct

```ml
fn make_resistor(value, tolerance, power_rating) {
    return {
        "value":        value,
        "tolerance":    tolerance,
        "power_rating": power_rating,
        "label":        str(value) + "Ω ±" + str(tolerance) + "%"
    };
}

let r1 = make_resistor(10000, 5, 0.25);
print(r1["label"]);            // 10000Ω ±5%
print(r1["power_rating"]);     // 0.25
```

---

## 8. String Methods

```ml
let s = "  Hello, World!  ";

print(s.trim());                         // "Hello, World!"
print(s.trim().upper());                 // "HELLO, WORLD!"
print(s.trim().lower());                 // "hello, world!"
print(s.trim().replace("World", "mylang")); // "Hello, mylang!"
print(s.trim().slice(0, 5));             // "Hello"
print(s.trim().contains("World"));       // true
print(s.trim().starts_with("Hello"));    // true
print(s.trim().ends_with("!"));          // true
print(s.trim().index_of("World"));       // 7

// Split and join
let csv  = "1,2,3,4,5";
let nums = csv.split(",");               // [1, 2, 3, 4, 5]
let tsv  = nums.join("\t");             // "1\t2\t3\t4\t5"

// String indexing
let word = "hello";
print(word[0]);    // "h"
print(word[4]);    // "o"
print(len(word));  // 5
```

---

## 9. Math Library

All functions work both as **top-level** (`sin(x)`) and **namespaced** (`math.sin(x)`).

### Constants

```ml
print(PI);     // 3.141592653589793
print(E);      // 2.718281828459045
print(TAU);    // 6.283185307179586  (2π)
print(PHI);    // 1.618033988749895  (golden ratio)
print(INF);    // Infinity
```

### Core functions

```ml
// Roots & powers
sqrt(144)        // 12
cbrt(27)         // 3
pow(2, 10)       // 1024

// Rounding
floor(3.9)       // 3
ceil(3.1)        // 4
round(3.14159, 2) // 3.14
abs(-42)         // 42
sign(-5)         // -1
clamp(15, 0, 10) // 10

// Trig (radians)
sin(PI / 2)      // 1
cos(0)           // 1
tan(PI / 4)      // 1

// Degree/radian conversion
deg(PI)          // 180
rad(90)          // 1.5707...

// Exponential / logarithm
exp(1)           // 2.718...  (e^1)
log(E)           // 1
log(1000, 10)    // 3
log2(8)          // 3
log10(100)       // 2
```

### Combinatorics

```ml
factorial(6)     // 720
comb(10, 3)      // 120   (10 choose 3)
perm(5, 2)       // 20    (5 permute 2)
gcd(48, 18)      // 6
lcm(4, 6)        // 12
```

### Quadratic solver

```ml
// x² - 5x + 6 = 0
let roots = quadratic(1, -5, 6);
print(roots[0]);    // 3
print(roots[1]);    // 2

// x² + 1 = 0  →  complex roots
let c = quadratic(1, 0, 1);
print(c[0]);        // 0+1j
print(c[1]);        // 0-1j
```

### Random numbers

```ml
rand_seed(42);               // reproducible results
print(random());             // 0.0–1.0
print(rand_int(1, 100));     // integer between 1 and 100
```

---

## 10. Statistics Library

All functions: `stats.fn(args)` or bare `fn(args)`.

```ml
let data = [12, 15, 14, 10, 18, 14, 16, 13, 11, 15];

// Descriptives
print(stats.mean(data));        // 13.8
print(stats.median(data));      // 14
print(stats.mode(data));        // [14, 15]
print(stats.stdev(data));       // sample standard deviation
print(stats.variance(data));    // sample variance
print(stats.min(data));         // 10
print(stats.max(data));         // 18
print(stats.sum(data));         // 138
print(stats.data_range(data));  // 8

// Rank statistics
print(stats.percentile(data, 25));   // Q1
print(stats.percentile(data, 75));   // Q3
print(stats.quartiles(data));        // [Q1, Q2, Q3]

// Normalisation
print(stats.zscore(data));       // z-scores (mean=0, std=1)
print(stats.normalize(data));    // scale to [0, 1]

// Relationships
let xs = [1, 2, 3, 4, 5];
let ys = [2.1, 3.9, 6.2, 7.8, 10.1];
print(stats.correlation(xs, ys));   // ~0.999

let model = stats.linreg(xs, ys);
print(model["slope"]);              // ~2.0
print(model["intercept"]);          // ~0.06
print(model["r2"]);                 // ~0.998

// Normal distribution
print(stats.normal_pdf(0, 0, 1));   // peak ≈ 0.3989
print(stats.normal_cdf(1.96, 0, 1));// ≈ 0.975  (95% confidence)

// Histogram
let h = stats.histogram(data, 5);
print(h["edges"]);
print(h["counts"]);
```

---

## 11. Electrical Engineering Library

All functions: `ee.fn(args)` or bare `fn(args)`.

### Ohm's Law

```ml
let V = ee.voltage(2, 100);       // V = I × R = 200 V
let I = ee.current(12, 4);        // I = V / R = 3 A
let R = ee.resistance(9, 3);      // R = V / I = 3 Ω

// Power
let P1 = ee.power(12, 2);         // P = V × I = 24 W
let P2 = ee.power_r(2, 10);       // P = I²R   = 40 W
let P3 = ee.power_v(10, 50);      // P = V²/R  = 2 W
```

### Resistor Networks

```ml
let Rs = ee.series([100, 200, 300]);          // 600 Ω
let Rp = ee.parallel([100, 100, 100]);        // 33.33 Ω

// Voltage divider
let vout = ee.voltage_divider(9, 10000, 4700);  // ≈ 2.91 V

// Current divider (fraction through R1)
let i1 = ee.current_divider(0.1, 1000, 2000);  // A
```

### Capacitors & Inductors

```ml
// 10 µF capacitors
let Cs = ee.cap_series([10e-6, 10e-6]);     // 5 µF
let Cp = ee.cap_parallel([10e-6, 10e-6]);   // 20 µF

// Inductors
let Ls = ee.ind_series([1e-3, 2e-3]);       // 3 mH
let Lp = ee.ind_parallel([4e-3, 4e-3]);     // 2 mH
```

### Reactance & Impedance

```ml
let f  = 1000;      // 1 kHz

let Xc = ee.xc(f, 1e-6);     // Xc = 1/(2πfC) = 159.15 Ω
let Xl = ee.xl(f, 10e-3);    // Xl = 2πfL     = 62.83 Ω

// Full RLC impedance (returns complex number)
let Z = ee.impedance_rlc(100, f, 10e-3, 1e-6);
print(Z);                          // complex number
print(Z.abs());                    // magnitude |Z|
print(round(Z.angle(), 2));        // phase angle in degrees
```

### RC / RL Circuits

```ml
// Time constants
let tau_rc = ee.rc_tau(1000, 100e-6);   // τ = RC = 0.1 s
let tau_rl = ee.rl_tau(50e-3, 100);     // τ = L/R = 0.5 ms

// RC charging: V(t) = Vs(1 − e^(−t/τ))
for (t in [0, 0.05, 0.1, 0.2, 0.5]) {
    let vc = ee.rc_charge(5.0, t, 1000, 100e-6);
    print("t=" + str(t) + "s  Vc=" + str(round(vc, 3)) + "V");
}
```

### Resonance

```ml
let f0 = ee.resonant_freq(10e-3, 1e-6);     // f₀ = 1/(2π√LC)
let Q  = ee.q_factor(f0, 500);              // Q = f₀ / BW
let BW = ee.bandwidth(f0, 10);              // BW = f₀ / Q
```

### dB & Signal Level

```ml
print(ee.to_db(2));            // +6.02 dB   (voltage ratio)
print(ee.to_db_power(10));     // +10 dB     (power ratio)
print(ee.from_db(6));          // ≈ 1.995
print(ee.vrms(340));           // ≈ 240.4 V  (mains peak → RMS)
print(ee.vpeak(230));          // ≈ 325.3 V  (mains RMS → peak)
```

### Phasors

```ml
let V1   = ee.phasor(10, 0);     // 10 V at 0°
let V2   = ee.phasor(10, 90);    // 10 V at 90°
let Vsum = ee.complex_add(V1, V2);

print(round(ee.phasor_mag(Vsum), 4));     // 14.1421 V
print(round(ee.phasor_angle(Vsum), 1));   // 45.0°
```

### Thevenin / Norton

```ml
// Given open-circuit voltage 12 V, short-circuit current 0.5 A
let th = ee.thevenin(12, 0.5);
print(th["vth"]);    // 12 V
print(th["rth"]);    // 24 Ω

let no = ee.norton(12, 0.5);
print(no["in_"]);    // 0.5 A
print(no["rn"]);     // 24 Ω
```

### Energy Storage

```ml
let E_cap = ee.energy_cap(100e-6, 12);   // E = ½CV² = 7.2 mJ
let E_ind = ee.energy_ind(10e-3, 2);     // E = ½LI² = 20 mJ
let Q_cap = ee.charge(100e-6, 12);       // Q = CV   = 1.2 mC
```

### Physical Constants

```ml
print(ee.EPSILON0);   // 8.854e-12 F/m   (permittivity of free space)
print(ee.MU0);        // 1.257e-6  H/m   (permeability of free space)
print(ee.ELECTRON);   // 1.602e-19 C     (elementary charge)
print(ee.BOLTZMANN);  // 1.381e-23 J/K
print(ee.PLANCK);     // 6.626e-34 J·s
print(ee.C_LIGHT);    // 299792458 m/s
```

---

## 12. Complex Numbers

```ml
let z1 = complex(3, 4);    // 3 + 4j
let z2 = complex(1, -2);   // 1 - 2j

// Properties (call as methods)
print(z1.real());     // 3
print(z1.imag());     // 4
print(z1.abs());      // 5.0  (magnitude = √(3²+4²))
print(z1.angle());    // 53.13°
print(z1.conj());     // 3 - 4j

// Arithmetic
let sum  = ee.complex_add(z1, z2);   // 4+2j
let prod = ee.complex_mul(z1, z2);   // 11-2j
let quot = ee.complex_div(z1, z2);   // -1+2j

// Check if quadratic roots are complex
let roots = quadratic(1, 0, 1);      // x²+1=0
print(type(roots[0]));               // "complex"
```

---

## 13. Matrices

```ml
// Create
let A = matrix([[1, 2, 3],
                [4, 5, 6],
                [7, 8, 9]]);

// Utility constructors
let I = mat_identity(3);    // 3×3 identity
let Z = mat_zeros(2, 4);    // 2×4 zero matrix

// Access / mutate
print(mat_get(A, 1, 2));    // 6  (row 1, col 2)
mat_set(A, 0, 0, 99);

// Arithmetic
let C = mat_add(A, B);
let D = mat_mul(A, B);      // matrix multiplication
let S = mat_scale(A, 2);    // scalar multiplication

// Properties
print(mat_det(A));           // determinant
print(mat_trace(A));         // sum of diagonal
print(mat_transpose(A));     // transpose

// Shape
let sh = mat_shape(A);
print(sh["rows"] + " × " + sh["cols"]);

// Method-call style (same results)
print(A.det());
print(A.trace());
print(A.transpose());
```

### Solve a 2×2 linear system with Cramer's Rule

```ml
// 2x + y = 5
// x + 3y = 10
let coeff = matrix([[2, 1], [1, 3]]);
let Dx    = matrix([[5, 1], [10, 3]]);
let Dy    = matrix([[2, 5], [1, 10]]);

let x = mat_det(Dx) / mat_det(coeff);   // 1
let y = mat_det(Dy) / mat_det(coeff);   // 3

print("x = " + str(x));
print("y = " + str(y));
```

---

## 14. First-Class Functions

Functions are values. Store them, pass them, return them.

```ml
// Store in a variable
let double = fn(x) { return x * 2; };
let square = fn(x) { return x * x; };

print(double(5));   // 10
print(square(5));   // 25

// Pass as argument
fn apply(f, x) {
    return f(x);
}
print(apply(double, 7));    // 14
print(apply(square, 7));    // 49

// Return from function (closure)
fn make_multiplier(factor) {
    return fn(x) { return x * factor; };
}
let times3 = make_multiplier(3);
let times7 = make_multiplier(7);
print(times3(10));   // 30
print(times7(10));   // 70

// Store in array or hash
let ops = {
    "add":  fn(a, b) { return a + b; },
    "sub":  fn(a, b) { return a - b; },
    "mul":  fn(a, b) { return a * b; }
};
print(ops["add"](10, 3));   // 13
print(ops["mul"](10, 3));   // 30
```

### Map, Filter, Reduce

```ml
let nums = range(1, 11);       // [1..10]

let squared  = nums.map(fn(x) { return x * x; });
let odds     = nums.filter(fn(x) { return x % 2 != 0; });
let total    = nums.reduce(fn(acc, x) { return acc + x; }, 0);

print(squared);   // [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
print(odds);      // [1, 3, 5, 7, 9]
print(total);     // 55

// Chain
let result = range(1, 21)
    .filter(fn(x) { return x % 3 == 0; })
    .map(fn(x) { return x * x; });
print(result);    // [9, 36, 81, 144, 225, 324]
```

---

## 15. Real-World Use Cases

### 15.1 — Grade Calculator

```ml
fn letter_grade(score) {
    if (score >= 90) { return "A"; }
    else if (score >= 80) { return "B"; }
    else if (score >= 70) { return "C"; }
    else if (score >= 60) { return "D"; }
    else { return "F"; }
}

let scores = [92, 78, 85, 61, 95, 73, 88];

print("=== Grade Report ===");
print("Mean:   " + str(round(stats.mean(scores), 1)));
print("Median: " + str(stats.median(scores)));
print("Stdev:  " + str(round(stats.stdev(scores), 1)));
print("");

for (s in scores) {
    print(str(s) + "  →  " + letter_grade(s));
}
```

---

### 15.2 — Voltage Divider Network Designer

```ml
// Design a 3.3 V rail from 5 V using a resistor divider
let Vin    = 5.0;
let Vout   = 3.3;
let R2     = 10000;    // fix R2 at 10 kΩ
let R1     = R2 * (Vin - Vout) / Vout;

print("R1 = " + str(round(R1, 0)) + " Ω");
print("R2 = " + str(R2) + " Ω");

let actual = ee.voltage_divider(Vin, R1, R2);
print("Actual Vout = " + str(round(actual, 3)) + " V");
print("Error       = " + str(round((actual - Vout) / Vout * 100, 4)) + "%");
```

---

### 15.3 — RC Low-Pass Filter Analysis

```ml
let R  = 1000;     // 1 kΩ
let C  = 1e-6;     // 1 µF
let f3 = 1 / (2 * PI * R * C);

print("Cutoff frequency: " + str(round(f3, 2)) + " Hz");
print("Time constant:    " + str(ee.rc_tau(R, C) * 1000) + " ms");
print("");
print("Frequency response:");

let freqs = [10, 50, 100, 159, 500, 1000, 5000];
for (f in freqs) {
    let Xc   = ee.xc(f, C);
    let Z    = sqrt(R * R + Xc * Xc);
    let gain = Xc / Z;
    let db   = ee.to_db(gain);
    print(str(f) + " Hz → " + str(round(db, 2)) + " dB");
}
```

---

### 15.4 — RLC Resonance Sweep

```ml
let R  = 50;
let L  = 10e-3;
let C  = 1e-6;
let f0 = ee.resonant_freq(L, C);
let Q  = f0 * L / R;         // Q = ω₀L/R for series circuit
let BW = ee.bandwidth(f0, Q);

print("Resonant frequency: " + str(round(f0, 2)) + " Hz");
print("Q factor:           " + str(round(Q, 2)));
print("Bandwidth:          " + str(round(BW, 2)) + " Hz");
print("Lower -3dB:         " + str(round(f0 - BW/2, 2)) + " Hz");
print("Upper -3dB:         " + str(round(f0 + BW/2, 2)) + " Hz");
```

---

### 15.5 — Linear Regression on Sensor Data

```ml
// Temperature sensor calibration: raw ADC counts → °C
let adc_counts = [102, 215, 328, 441, 554, 667, 780];
let temps_c    = [10,   20,  30,  40,  50,  60,  70];

let model = stats.linreg(adc_counts, temps_c);
print("Calibration model:");
print("  slope:     " + str(round(model["slope"], 6)));
print("  intercept: " + str(round(model["intercept"], 4)));
print("  R²:        " + str(round(model["r2"], 6)));

// Use the model to convert a new reading
fn adc_to_temp(adc) {
    return model["slope"] * adc + model["intercept"];
}
print("ADC 500 → " + str(round(adc_to_temp(500), 2)) + " °C");
```

---

### 15.6 — Signal Statistics (noise analysis)

```ml
rand_seed(7);

// Simulate 20 ADC readings with noise
let readings = [];
let i = 0;
while (i < 20) {
    let noise = (random() - 0.5) * 0.1;   // ±0.05 V noise
    push(readings, round(3.3 + noise, 4));
    i = i + 1;
}

print("Readings: " + str(readings));
print("Mean:     " + str(round(stats.mean(readings), 4)) + " V");
print("Stdev:    " + str(round(stats.stdev(readings), 4)) + " V");
print("SNR:      " + str(round(
    ee.to_db(stats.mean(readings) / stats.stdev(readings)), 2)) + " dB");
```

---

### 15.7 — Fibonacci using closures

```ml
// Generator-style Fibonacci using a closure
fn make_fib() {
    let a = 0;
    let b = 1;
    return fn() {
        let val = a;
        let tmp = a + b;
        a = b;
        b = tmp;
        return val;
    };
}

let next = make_fib();
let sequence = [];
let i = 0;
while (i < 12) {
    push(sequence, next());
    i = i + 1;
}
print(sequence);
// [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
```

---

### 15.8 — Matrix: 2-D rotation

```ml
// Rotate a point (x, y) by angle θ using a rotation matrix
fn rotation_matrix(theta_deg) {
    let theta = rad(theta_deg);
    return matrix([
        [cos(theta), -sin(theta)],
        [sin(theta),  cos(theta)]
    ]);
}

fn rotate_point(x, y, angle_deg) {
    let Rm = rotation_matrix(angle_deg);
    let pt = matrix([[x], [y]]);    // column vector
    let rp = mat_mul(Rm, pt);
    return {
        "x": round(mat_get(rp, 0, 0), 6),
        "y": round(mat_get(rp, 1, 0), 6)
    };
}

let p = rotate_point(1, 0, 90);
print("Rotated: (" + str(p["x"]) + ", " + str(p["y"]) + ")");
// Rotated: (0, 1)
```

---

## 16. Pacer AI Commands

Inside Pacer's command bar (bottom panel):

| Command | What it does |
|---------|-------------|
| `/run` | Execute the current `.ml` file — output appears in the Output panel |
| `/debug` | AI analyses your code and explains every bug |
| `/fix` | AI repairs errors and offers to replace the file contents |
| `/complete` | AI finishes your half-written code |
| `/explain` | AI describes what your code does, step by step |
| `/mylang how do I use .reduce()?` | Ask any mylang question |
| `/help` | List all commands |

The AI commands are **mylang-aware** — when working on a `.ml` file the AI
automatically receives the full language syntax reference, so suggestions will
always use correct mylang syntax rather than Python or JavaScript idioms.

---

## 17. Built-in Quick Reference

### Global functions

```
len(x)        type(x)       str(x)        num(x)
push(arr, v)  pop(arr)      range(n)      range(a,b)    range(a,b,step)
keys(h)       values(h)     has(h,k)      del(h,k)
complex(r,i)  real(z)       imag(z)       complex_abs(z)
matrix(arrs)  mat_zeros(r,c) mat_identity(n)
mat_add(A,B)  mat_sub(A,B)  mat_mul(A,B)  mat_scale(A,s)
mat_transpose(A)  mat_det(A)  mat_trace(A)
mat_get(A,r,c)    mat_set(A,r,c,v)  mat_shape(A)
```

### math.*  (or bare name)

```
sqrt  cbrt  pow  abs  floor  ceil  round  sign  clamp
sin   cos   tan  asin acos  atan  atan2  sinh  cosh  tanh
deg   rad   exp  log  log2  log10
factorial  gcd  lcm  comb  perm
random  rand_int  rand_seed
quadratic(a,b,c)
```

### Constants: `PI  E  TAU  PHI  INF  NAN`

### stats.*  (or bare name)

```
mean  median  mode  stdev  pstdev  variance  pvariance
min   max     sum   data_range
percentile(data,p)  quartiles(data)
correlation(xs,ys)  covariance(xs,ys)  linreg(xs,ys)
normalize  zscore  histogram(data,bins)
normal_pdf(x,µ,σ)  normal_cdf(x,µ,σ)
```

### ee.*  (or bare name)

```
voltage(i,r)    current(v,r)    resistance(v,i)
power(v,i)      power_r(i,r)    power_v(v,r)
series(arr)     parallel(arr)
cap_series      cap_parallel    ind_series    ind_parallel
xc(f,c)         xl(f,l)
impedance_rc(r,f,c)  impedance_rl(r,f,l)  impedance_rlc(r,f,l,c)
resonant_freq(l,c)   q_factor(f0,bw)      bandwidth(f0,q)
rc_tau(r,c)     rl_tau(l,r)
rc_charge(v0,t,r,c)  rc_discharge(v0,t,r,c)
to_db  to_db_power  from_db  from_db_power  vrms  vpeak
phasor(mag,deg)  phasor_mag  phasor_angle
complex_add  complex_mul  complex_div  complex_conj
voltage_divider(vin,r1,r2)  current_divider(iin,r1,r2)
thevenin(voc,isc)  norton(voc,isc)
energy_cap(c,v)  energy_ind(l,i)  charge(c,v)
```

### EE constants

```
ee.EPSILON0  ee.MU0  ee.C_LIGHT  ee.PLANCK  ee.BOLTZMANN  ee.ELECTRON
```

---

## 18. Common Errors & Fixes

| Error message | Cause | Fix |
|---------------|-------|-----|
| `ParseError at ';': Expected expression` | Missing value before `;` | Check for empty `let x = ;` |
| `Undefined variable 'x'` | Used before `let` | Add `let x = ...;` first |
| `'foo' is not callable` | Called something that isn't a function | Check spelling and that `fn foo` was declared |
| `Index 5 out of bounds (length 3)` | Array index too large | Use `len(arr)` to guard the index |
| `Division by zero` | Dividing by `0` | Add a guard: `if (b != 0) { ... }` |
| `ParseError at '=': Expected '('` | Wrote `fn name =` instead of `fn name(` | Functions need `()` after the name |
| `stdev() requires at least 2 values` | Only one data point | Pass at least 2 values |
| `Expected ';' after expression` | Missing semicolon | End every statement with `;` |
| `LexerError: Unexpected character '@'` | Invalid character | mylang doesn't use `@`, `#`, `$` |

### Formatting rules at a glance

```ml
// ✓ CORRECT
let x = 5;
fn add(a, b) { return a + b; }
if (x > 0) { print("positive"); }
for (i in range(10)) { print(i); }

// ✗ WRONG — missing semicolons
let x = 5          // needs ;
print("hi")        // needs ;

// ✗ WRONG — missing braces
if (x > 0) print("positive")     // needs { }
fn add(a, b) return a + b        // needs { }

// ✗ WRONG — Python-style syntax
def add(a, b):         // use fn, not def
    return a + b       // no colons, uses { }
```

---

*mylang is open and designed to grow. Use `/mylang <question>` inside Pacer
to get AI help specific to your language at any time.*
