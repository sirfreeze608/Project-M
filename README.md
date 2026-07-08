Boredom can also help with creativity



I spent the last few weeks wandering what I could do with vibe coding. After long thoughts I decided to start building a code editor for personal use, then the thought how about I add an AI assistant to fix errors in my code. I finally got through that hurdle after several changes and tries. 



At this point i wasn't really into UI experience I just wanted it to work with editing commonly known programming languages for instance python scripts, html files, javascript, C and xml. Once I got that part going I got into making sure it ran in dark mode which is my favorite mode to use. I also named the Code Editor "Pacer Code Editor"



Now that I got that part out of the way I start looking at syntax highlighting since it aided in identifying commands and error handling. 



In the heat of excitement of building something fulfilling with an AI a curious thought crossed my mind, since i have a long background in Mathematics, Statistics and Electrical Engineering, how about I build an entirely new programming language that can relate to these fields.



So I started work on my new programming language called "MyLang" started with the base figuring out what the file extension would be (".ml") for source code files & (".mylang") for libraries and trained the AI with several books related to these topics and got the interpreter and lexer ready. after a few days I had a working base language that could do some basic computational stuff. 


The idea got to my head so I started making it more and more complex. Added some more real world useable features for electrical engineers and statistical computation 


This whole process was a little frustrating as there were moments the AI broke the hard work I have achieved and I had to revert to old versions and start all over to keep the project on track and not sway from the original design and purpose.


In order to verify if this was a unique language I did several test paths with AI agents to show that it was indeed a new language and had its own unique way of handling code and memory management. In noticing the stability of the first version I added crypto, csv parsing as features.


Well today I am glad to say it is fully operational now and ready for real world testing, my only fear is how this would be used and the security side of things. I am making it open source and hopefully looking for people's input and opinions and hopefully some help testing use cases. 


I am making the whole code readily available on Github with the hope of reaching like minded persons to jump in the fun, if you do understand basic programming language technics, principles and verbatim it would be pretty easy to follow, not to worry i have attached a handbook as well


Lets find bugs 😀 for fun



[The Pacer and MyLang Handbook.html](https://github.com/user-attachments/files/29148351/The.Pacer.and.MyLang.Handbook.html)
<img width="2720" height="2960" alt="pacer_mylang_architecture" src="https://github.com/user-attachments/assets/809dc7cd-d1a4-446f-bcdd-6209b0945060" />
# Pacer + mylang

> **Pacer** is a dark-themed Python code editor with a built-in interpreter
> for **mylang** — a custom scripting language designed for maths, statistics,
> and electrical engineering.  No installation of a separate compiler is needed;
> press **F5** and your `.ml` file runs instantly inside the editor.

---

## Quick Start

<img width="1482" height="575" alt="image" src="https://github.com/user-attachments/assets/4cd644ff-9a45-4166-b98d-589d369148a6" />


### 1. Install dependencies

```bash
pip install PyQt5 anthropic
```

### 2. Set your API key (for AI features)

```bash
# macOS / Linux — add to ~/.zshrc or ~/.bashrc
export ANTHROPIC_API_KEY="sk-ant-..."

# Windows CMD
set ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Arrange the project files

```
your-project/
├── Pacer_mylang.py      ← the editor
├── MYLANG_DOCS.md       ← full language reference (opens in editor)
├── README.md            ← this file
└── mylang/              ← the language engine
    ├── lexer.py
    ├── parser.py
    ├── interpreter.py
    ├── ast_nodes.py
    ├── stdlib.py
    ├── main.py
    └── examples/
        ├── hello.ml
        ├── fibonacci.ml
        ├── fizzbuzz.ml
        ├── showcase.ml
        ├── math_stats.ml
        ├── ee_showcase.ml
        └── complex_matrix.ml
```

### 4. Launch Pacer

```bash
python Pacer_mylang.py
```

Pacer opens with a fresh `Untitled-1.ml` tab ready to go.

---

## Running `.ml` files

| Method | How |
|--------|-----|
| Inside Pacer | Press **F5**, or type `/run` in the command bar |
| Terminal | `python mylang/main.py yourfile.ml` |
| After `pip install -e .` | `mylang yourfile.ml` |
| REPL | `mylang --repl` or `python mylang/main.py --repl` |
| Debug flags | `mylang --tokens yourfile.ml` dumps the token stream |
|             | `mylang --ast yourfile.ml` dumps the abstract syntax tree |

---

## Pacer Features

| Feature | Detail |
|---------|--------|
| Default new file | **Ctrl+N** always creates a `.ml` file with a starter template |
| New other types | **Ctrl+Shift+N** — pick Python, JS, HTML, etc. |
| Unsaved indicator | `●` dot in the tab name; clears on save |
| Save As default | Pre-fills with `.ml` extension; auto-appends `.ml` if forgotten |
| Save warning | Asks to save before closing a modified tab |
| Syntax highlighting | mylang, Python, JavaScript, React/JSX, HTML, XML |
| AI assistant | `/debug` `/fix` `/complete` `/explain` `/mylang <q>` |
| Model picker | Switch between Claude Haiku / Sonnet / Opus in the command bar |
| Output panel | Program output and runtime errors shown colour-coded |
| Line numbers | Gutter with current-line highlight |
| Auto-indent | Enter inside `{` blocks indents automatically |
| Documentation | **mylang menu → Open Documentation** loads `MYLANG_DOCS.md` |

---

## mylang in 60 seconds

```ml
// Variables
let name = "World";
let x    = 42;

// Print
print("Hello, " + name + "!");

// Function
fn square(n) {
    return n * n;
}
print(square(x));

// Array + loop
let nums = [1, 2, 3, 4, 5];
for (n in nums) {
    print(n * n);
}

// Hash map
let person = {"name": "Alice", "age": 30};
print(person["name"]);

// Math
print(sqrt(144));              // 12
print(sin(PI / 2));            // 1

// Statistics
let data = [10, 20, 30, 40, 50];
print(stats.mean(data));       // 30
print(stats.stdev(data));      // 15.811...

// Electrical engineering
print(ee.voltage(2, 100));     // 200 V
print(ee.parallel([100, 100]));// 50 Ω
```

---

## Language Overview

| Feature | Syntax |
|---------|--------|
| Variable | `let x = value;` |
| Function | `fn name(a, b) { return a + b; }` |
| Anonymous fn | `let f = fn(x) { return x * 2; };` |
| If/else | `if (cond) { } else if (cond) { } else { }` |
| While | `while (cond) { }` |
| For-in | `for (item in array) { }` |
| Array | `[1, 2, 3]` · `arr[0]` · `arr[1] = v` |
| Hash | `{"key": val}` · `h["key"]` · `h["k"] = v` |
| Complex | `complex(3, 4)` → `3+4j` |
| Matrix | `matrix([[1,2],[3,4]])` |
| Comment | `// single line` |
| Scientific | `1e-6`, `4.7e-12`, `1e6` |

### Standard library namespaces

| Namespace | Contents |
|-----------|----------|
| `math.*` | 40 functions — trig, log, roots, combinatorics, random, `quadratic()` |
| `stats.*` | 20 functions — mean, stdev, linreg, zscore, normal_cdf, histogram |
| `ee.*` | 35 functions — Ohm's law, impedance, RC/RL circuits, phasors, dB, Thevenin |

All functions also available as bare names: `sin(x)` = `math.sin(x)`.

Constants: `PI  E  TAU  PHI  INF  NAN`  
EE constants: `ee.EPSILON0  ee.MU0  ee.ELECTRON  ee.BOLTZMANN  ee.PLANCK  ee.C_LIGHT`

---

## Project Structure

```
mylang/
├── lexer.py        Tokeniser   — source text  → token list
├── ast_nodes.py    AST nodes   — data structures for the syntax tree
├── parser.py       Parser      — token list   → abstract syntax tree
├── interpreter.py  Interpreter — AST          → execution
├── stdlib.py       Standard library — math / stats / ee / matrix / complex
└── main.py         CLI entry point and REPL
```

---

## License

MIT — do whatever you like with it.
