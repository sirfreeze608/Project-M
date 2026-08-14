#!/usr/bin/env python3
"""
build_playground.py  —  generates playground/index.html

Reads the mylang engine source files and embeds them into a single
standalone HTML page that runs mylang entirely in the browser via
Pyodide (Python compiled to WebAssembly). No server needed — host it
on GitHub Pages, open it from disk, or share the single file.

Usage:  python build_playground.py
Output: playground/index.html
"""

import json
import os
import sys

HERE   = os.path.dirname(os.path.abspath(__file__))
MYLANG = os.path.join(HERE, "mylang")
OUT    = os.path.join(HERE, "playground")

ENGINE_FILES = ["lexer.py", "ast_nodes.py", "parser.py",
                "interpreter.py", "stdlib.py", "errors.py"]

EXAMPLES = {
    "Hello World": '''// Welcome to mylang! Press Run (or Ctrl+Enter).
let name = "World";
print(`Hello, ${name}!`);

let nums = [1, 2, 3, 4, 5];
let squares = nums.map(fn(n) { return n * n; });
print(`Squares: ${str(squares)}`);
''',
    "Fibonacci": '''// Generator-style Fibonacci using a closure
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
let seq = [];
let i = 0;
while (i < 12) {
    push(seq, next());
    i = i + 1;
}
print(seq);
''',
    "Statistics": '''// Real data analysis with stats.*
let readings = [22.1, 23.4, 22.9, 24.2, 31.8, 23.1, 22.7];

print(`Mean:   ${round(stats.mean(readings), 3)}`);
print(`Median: ${stats.median(readings)}`);
print(`Stdev:  ${round(stats.stdev(readings), 3)}`);

let limit = stats.mean(readings) + 2 * stats.stdev(readings);
for (r in readings) {
    if (r > limit) {
        print(`Outlier detected: ${r}`);
    }
}
''',
    "Electrical Engineering": '''// RLC resonance analysis with ee.*
let R = 50;      // ohms
let L = 10e-3;   // henries
let C = 1e-6;    // farads

let f0 = ee.resonant_freq(L, C);
let Q  = f0 * L / R;

print(`Resonant frequency: ${round(f0, 2)} Hz`);
print(`Q factor: ${round(Q, 2)}`);

// Reactance sweep
for (f in [500, 1000, 1591, 2500, 5000]) {
    let xl = ee.xl(f, L);
    let xc = ee.xc(f, C);
    print(`${f} Hz -> XL=${round(xl,1)}  XC=${round(xc,1)}`);
}
''',
    "Error Handling": '''// try / catch / throw  (v0.6.0)
fn safe_divide(a, b) {
    if (b == 0) {
        throw `Cannot divide ${a} by zero`;
    }
    return a / b;
}

try {
    print(safe_divide(10, 2));
    print(safe_divide(5, 0));
} catch(e) {
    print(`Caught: ${e}`);
}

// Try introducing a syntax error below and press Run
// to see mylang's code-frame error messages:
let x = 42;
print(`x = ${x}`);
''',
    "JSON": '''// json.* namespace  (v0.7.0)
let raw = "{\\"name\\": \\"Ada\\", \\"languages\\": [\\"mylang\\", \\"python\\"]}";
let person = json.parse(raw);

print(person["name"]);
print(person["languages"][0]);

let data = {"project": "Pacer", "version": 0.7, "tags": ["ide", "language"]};
print(json.pretty(data));
''',
    "Sudoku Solver": '''// Backtracking sudoku solver — the full algorithm in mylang
fn is_valid(b, row, col, n) {
    let i = 0;
    while (i < 9) {
        if (b[row][i] == n || b[i][col] == n) { return false; }
        i = i + 1;
    }
    let br = row - (row % 3);
    let bc = col - (col % 3);
    let r = br;
    while (r < br + 3) {
        let c = bc;
        while (c < bc + 3) {
            if (b[r][c] == n) { return false; }
            c = c + 1;
        }
        r = r + 1;
    }
    return true;
}

fn solve(b) {
    let r = 0;
    while (r < 9) {
        let c = 0;
        while (c < 9) {
            if (b[r][c] == 0) {
                let n = 1;
                while (n <= 9) {
                    if (is_valid(b, r, c, n)) {
                        b[r][c] = n;
                        if (solve(b)) { return true; }
                        b[r][c] = 0;
                    }
                    n = n + 1;
                }
                return false;
            }
            c = c + 1;
        }
        r = r + 1;
    }
    return true;
}

let puzzle = [
    [5,3,0, 0,7,0, 0,0,0],
    [6,0,0, 1,9,5, 0,0,0],
    [0,9,8, 0,0,0, 0,6,0],
    [8,0,0, 0,6,0, 0,0,3],
    [4,0,0, 8,0,3, 0,0,1],
    [7,0,0, 0,2,0, 0,0,6],
    [0,6,0, 0,0,0, 2,8,0],
    [0,0,0, 4,1,9, 0,0,5],
    [0,0,0, 0,8,0, 0,7,9]
];

solve(puzzle);
for (row in puzzle) {
    print(row.join(" "));
}
''',
}


def build() -> str:
    sources = {}
    for fname in ENGINE_FILES:
        path = os.path.join(MYLANG, fname)
        with open(path, encoding="utf-8") as fh:
            sources[fname] = fh.read()

    engine_json   = json.dumps(sources)
    examples_json = json.dumps(EXAMPLES)

    html = HTML_TEMPLATE
    html = html.replace("__ENGINE_FILES__",  engine_json)
    html = html.replace("__EXAMPLES__",      examples_json)

    os.makedirs(OUT, exist_ok=True)
    out_path = os.path.join(OUT, "index.html")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return out_path


HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>mylang Playground</title>
<link rel="stylesheet"
      href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/javascript/javascript.min.js"></script>
<script src="https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js"></script>
<style>
:root {
  --bg:#0F1117; --surface:#1A1D27; --surface2:#21253A; --border:#2A2E42;
  --accent:#E2543C; --teal:#4EC9B0; --parchment:#F2EBDD; --muted:#7A7F9A;
  --green:#6A9955; --red:#F44747;
  --mono:'JetBrains Mono','Fira Code','Cascadia Code','Consolas',monospace;
  --sans:'Inter',-apple-system,'Segoe UI',sans-serif;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--parchment);font-family:var(--sans);
     height:100vh;display:flex;flex-direction:column;overflow:hidden;}

header{display:flex;align-items:center;justify-content:space-between;
       padding:12px 20px;border-bottom:1px solid var(--border);flex-shrink:0;}
.logo{font-family:var(--mono);font-size:15px;color:var(--teal);letter-spacing:.06em;}
.logo .dot{color:var(--accent);}
.logo .sub{color:var(--muted);font-size:11px;margin-left:10px;}
.header-right{display:flex;gap:10px;align-items:center;}
select{background:var(--surface);border:1px solid var(--border);color:var(--parchment);
       font-family:var(--mono);font-size:12px;padding:6px 10px;border-radius:3px;outline:none;cursor:pointer;}
.btn-run{background:var(--accent);border:none;color:#1a0a07;font-family:var(--mono);
         font-size:13px;font-weight:700;padding:8px 22px;border-radius:3px;cursor:pointer;
         transition:background .15s;display:flex;align-items:center;gap:7px;}
.btn-run:hover{background:#ee6b53;}
.btn-run:disabled{background:var(--surface2);color:var(--muted);cursor:wait;}

main{flex:1;display:flex;overflow:hidden;}
.pane-editor{flex:1.2;display:flex;flex-direction:column;border-right:1px solid var(--border);min-width:0;}
.pane-output{flex:1;display:flex;flex-direction:column;min-width:0;}
.pane-label{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;
            color:var(--muted);padding:8px 14px;border-bottom:1px solid var(--border);
            display:flex;justify-content:space-between;align-items:center;flex-shrink:0;}
.pane-label .status{color:var(--teal);text-transform:none;letter-spacing:0;}

.CodeMirror{flex:1;height:auto !important;background:var(--bg) !important;
            color:var(--parchment) !important;font-family:var(--mono) !important;
            font-size:14px !important;line-height:1.6 !important;}
.CodeMirror-gutters{background:var(--bg) !important;border-right:1px solid var(--border) !important;}
.CodeMirror-linenumber{color:#3d4258 !important;}
.CodeMirror-cursor{border-left:2px solid var(--accent) !important;}
.CodeMirror-selected{background:rgba(78,201,176,.12) !important;}
.CodeMirror .cm-keyword{color:#C586C0;} .CodeMirror .cm-def{color:#DCDCAA;}
.CodeMirror .cm-variable{color:#9CDCFE;} .CodeMirror .cm-number{color:#B5CEA8;}
.CodeMirror .cm-string{color:#CE9178;} .CodeMirror .cm-string-2{color:#CE9178;}
.CodeMirror .cm-comment{color:#6A9955;} .CodeMirror .cm-operator{color:#D4D4D4;}
.CodeMirror .cm-property{color:#4EC9B0;}

#output{flex:1;overflow:auto;padding:14px;font-family:var(--mono);font-size:13px;
        line-height:1.55;white-space:pre-wrap;word-break:break-word;}
#output .err{color:var(--red);}
#output .ok{color:var(--green);}
#output .dim{color:var(--muted);}

footer{padding:8px 20px;border-top:1px solid var(--border);font-family:var(--mono);
       font-size:10px;color:var(--muted);display:flex;justify-content:space-between;flex-shrink:0;}
footer a{color:var(--teal);text-decoration:none;}
.spinner{display:inline-block;width:11px;height:11px;border:2px solid var(--muted);
         border-top-color:var(--teal);border-radius:50%;animation:spin .7s linear infinite;}
@keyframes spin{to{transform:rotate(360deg);}}
@media (max-width:760px){ main{flex-direction:column;}
  .pane-editor{border-right:none;border-bottom:1px solid var(--border);} }
</style>
</head>
<body>

<header>
  <div class="logo">my<span class="dot">.</span>lang
    <span class="sub">playground — the mylang language, running in your browser</span>
  </div>
  <div class="header-right">
    <select id="exampleSelect" title="Load an example"></select>
    <button class="btn-run" id="runBtn" disabled>
      <span id="runIcon">▶</span> <span id="runLabel">Loading…</span>
    </button>
  </div>
</header>

<main>
  <div class="pane-editor">
    <div class="pane-label"><span>editor · script.ml</span>
      <span style="color:var(--muted)">Ctrl+Enter to run</span></div>
    <textarea id="editor"></textarea>
  </div>
  <div class="pane-output">
    <div class="pane-label"><span>output</span><span class="status" id="statusLbl"></span></div>
    <div id="output"><span class="dim">Starting Python runtime (first load ≈ 5–10 s)…</span></div>
  </div>
</main>

<footer>
  <span>mylang v0.7.0 · Pacer Code Editor project</span>
  <span>runs fully client-side via <a href="https://pyodide.org" target="_blank">Pyodide</a> — nothing is uploaded</span>
</footer>

<script>
const ENGINE_FILES = __ENGINE_FILES__;
const EXAMPLES     = __EXAMPLES__;

// ── Editor ──────────────────────────────────────────────────────────────────
const editor = CodeMirror.fromTextArea(document.getElementById('editor'), {
  mode: 'javascript',       // closest highlighting match for mylang syntax
  lineNumbers: true,
  indentUnit: 4,
  tabSize: 4,
  indentWithTabs: false,
  autofocus: true,
  extraKeys: { 'Ctrl-Enter': runCode, 'Cmd-Enter': runCode,
               Tab: cm => cm.replaceSelection('    ') }
});

// Example picker
const sel = document.getElementById('exampleSelect');
Object.keys(EXAMPLES).forEach(name => {
  const o = document.createElement('option');
  o.value = name; o.textContent = '📄 ' + name;
  sel.appendChild(o);
});
sel.addEventListener('change', () => editor.setValue(EXAMPLES[sel.value]));
editor.setValue(EXAMPLES['Hello World']);

// ── Pyodide bootstrap ───────────────────────────────────────────────────────
const out       = document.getElementById('output');
const runBtn    = document.getElementById('runBtn');
const runLabel  = document.getElementById('runLabel');
const runIcon   = document.getElementById('runIcon');
const statusLbl = document.getElementById('statusLbl');

let pyodide = null;

async function boot() {
  try {
    pyodide = await loadPyodide();
    // Write the mylang engine into the virtual filesystem
    pyodide.FS.mkdir('/mylang');
    for (const [fname, src] of Object.entries(ENGINE_FILES)) {
      pyodide.FS.writeFile('/mylang/' + fname, src);
    }
    await pyodide.runPythonAsync(`
import sys
sys.setrecursionlimit(20000)
sys.path.insert(0, '/mylang')
from lexer import Lexer, LexerError
from parser import Parser, ParseError
from interpreter import Interpreter, RuntimeError as MLRuntimeError
from errors import format_error
import io

def run_mylang(source):
    old = sys.stdout
    sys.stdout = buf = io.StringIO()
    try:
        tokens = Lexer(source).tokenize()
        ast    = Parser(tokens).parse()
        Interpreter().run(ast)
        return {"ok": True, "output": buf.getvalue()}
    except (LexerError, ParseError, MLRuntimeError) as e:
        return {"ok": False, "output": buf.getvalue(),
                "error": format_error(source, e, filename="script.ml")}
    except Exception as e:
        import traceback
        return {"ok": False, "output": buf.getvalue(),
                "error": "InternalError: " + str(e)}
    finally:
        sys.stdout = old
`);
    out.innerHTML = '<span class="ok">✓ Runtime ready.</span> ' +
                    '<span class="dim">Press Run or Ctrl+Enter.</span>';
    runBtn.disabled = false;
    runLabel.textContent = 'Run';
    statusLbl.textContent = 'ready';
  } catch (err) {
    out.innerHTML = '<span class="err">Failed to load Python runtime:\n' +
                    err + '</span>';
  }
}
boot();

// ── Run ─────────────────────────────────────────────────────────────────────
async function runCode() {
  if (!pyodide || runBtn.disabled) return;
  runBtn.disabled = true;
  runIcon.innerHTML = '<span class="spinner"></span>';
  runLabel.textContent = 'Running';
  statusLbl.textContent = 'running…';
  const t0 = performance.now();

  try {
    pyodide.globals.set('__src__', editor.getValue());
    const result = await pyodide.runPythonAsync('run_mylang(__src__)');
    const r  = result.toJs({ dict_converter: Object.fromEntries });
    const ms = Math.round(performance.now() - t0);

    let html = '';
    if (r.output) html += escapeHtml(r.output);
    if (!r.ok)    html += '<span class="err">' + escapeHtml(r.error) + '</span>';
    if (r.ok)     html += '<span class="dim">\n─ finished in ' + ms + ' ms</span>';
    out.innerHTML = html || '<span class="dim">(no output)</span>';
    statusLbl.textContent = r.ok ? ('done · ' + ms + ' ms') : 'error';
    result.destroy();
  } catch (err) {
    out.innerHTML = '<span class="err">' + escapeHtml(String(err)) + '</span>';
    statusLbl.textContent = 'error';
  }

  runBtn.disabled = false;
  runIcon.textContent = '▶';
  runLabel.textContent = 'Run';
}
runBtn.addEventListener('click', runCode);

function escapeHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
</script>
</body>
</html>
'''


if __name__ == "__main__":
    path = build()
    size = os.path.getsize(path) // 1024
    print(f"Playground built: {path}  ({size} KB)")
