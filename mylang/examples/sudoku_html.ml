// sudoku_html.ml
// The same verified backtracking solver, now outputting a styled HTML page.
// Run with F5 in Pacer — opens in your browser automatically.
// Uses html.raw() to inject the styled grid directly into the page.

// ── Solver functions (identical to sudoku.ml) ─────────────────────────────

fn is_valid(board, row, col, num) {
    let i = 0;
    while (i < 9) {
        if (board[row][i] == num) { return false; }
        i = i + 1;
    }
    i = 0;
    while (i < 9) {
        if (board[i][col] == num) { return false; }
        i = i + 1;
    }
    let box_row = row - (row % 3);
    let box_col = col - (col % 3);
    let r = box_row;
    while (r < box_row + 3) {
        let c = box_col;
        while (c < box_col + 3) {
            if (board[r][c] == num) { return false; }
            c = c + 1;
        }
        r = r + 1;
    }
    return true;
}

fn find_empty(board) {
    let r = 0;
    while (r < 9) {
        let c = 0;
        while (c < 9) {
            if (board[r][c] == 0) { return [r, c]; }
            c = c + 1;
        }
        r = r + 1;
    }
    return null;
}

fn solve(board) {
    let empty = find_empty(board);
    if (empty == null) { return true; }
    let row = empty[0];
    let col = empty[1];
    let num = 1;
    while (num <= 9) {
        if (is_valid(board, row, col, num)) {
            board[row][col] = num;
            if (solve(board)) { return true; }
            board[row][col] = 0;
        }
        num = num + 1;
    }
    return false;
}

// ── HTML board builder ─────────────────────────────────────────────────────
// Renders a 9x9 board as an HTML table.
// clue_board = original puzzle, used to style given digits differently.

fn html_board(board, clue_board) {
    let t = "<table class=\"sudoku\">";
    let r = 0;
    while (r < 9) {
        let row_class = "";
        if (r == 2 || r == 5) { row_class = " class=\"bb\""; }
        t = t + "<tr" + row_class + ">";
        let c = 0;
        while (c < 9) {
            let v     = board[r][c];
            let cls   = "cl";
            if (clue_board[r][c] != 0) { cls = "cl gv"; }
            if (c == 2 || c == 5)      { cls = cls + " br"; }
            let disp = "";
            if (v != 0) { disp = str(v); }
            t = t + "<td class=\"" + cls + "\">" + disp + "</td>";
            c = c + 1;
        }
        t = t + "</tr>";
        r = r + 1;
    }
    return t + "</table>";
}

fn count_empty(board) {
    let n = 0;
    let r = 0;
    while (r < 9) {
        let c = 0;
        while (c < 9) {
            if (board[r][c] == 0) { n = n + 1; }
            c = c + 1;
        }
        r = r + 1;
    }
    return n;
}

// ── Puzzle ─────────────────────────────────────────────────────────────────

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

// Keep original clues before solve() fills the board
let clues = [
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

let empty_count = count_empty(puzzle);
let given_count = 81 - empty_count;

// ── Solve ──────────────────────────────────────────────────────────────────

let solved = solve(puzzle);

// ── Build HTML page ────────────────────────────────────────────────────────

html.page("Sudoku Solver");

html.heading("Sudoku Solver", 1);
html.text("Solved using a backtracking constraint algorithm written entirely in mylang.");

html.divider();
html.kv("Given clues",    given_count);
html.kv("Cells to solve", empty_count);
html.kv("Algorithm",      "Recursive backtracking");
html.kv("Result",         "Solved");
html.divider();

// Inject the board grid — html.raw() puts HTML straight onto the page
let puzzle_board = html_board(clues, clues);
let solved_board = html_board(puzzle, clues);

html.raw(
    "<style>" +
    ".boards{display:flex;gap:48px;flex-wrap:wrap;margin:28px 0;}" +
    ".bwrap{display:flex;flex-direction:column;align-items:center;gap:10px;}" +
    ".blbl{font-family:monospace;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:#7a7f9a;}" +
    "table.sudoku{border-collapse:collapse;border:2px solid #8a8780;}" +
    ".cl{width:44px;height:44px;text-align:center;vertical-align:middle;" +
    "    font-family:'JetBrains Mono','Courier New',monospace;font-size:19px;font-weight:500;" +
    "    color:#f2ebdd;background:#1a1d27;border:1px solid #2a2e42;}" +
    ".gv{color:#4ec9b0;font-weight:700;background:#1e2235;}" +
    ".br{border-right:2px solid #8a8780;}" +
    "tr.bb .cl{border-bottom:2px solid #8a8780;}" +
    "</style>" +
    "<div class=\"boards\">" +
    "  <div class=\"bwrap\"><div class=\"blbl\">Puzzle</div>" + puzzle_board + "</div>" +
    "  <div class=\"bwrap\"><div class=\"blbl\">Solved</div>" + solved_board + "</div>" +
    "</div>"
);

html.divider();
html.heading("How the solver works", 2);
html.list([
    "Find the next empty cell scanning top-left to bottom-right.",
    "Try placing each digit 1-9 in that cell.",
    "Check validity: no repeat in the same row, column, or 3x3 box.",
    "If valid, place the digit and recurse to the next empty cell.",
    "If no digit works, backtrack — clear the cell and try the next option in the previous cell.",
    "Repeat until all 81 cells are filled or all paths are exhausted."
]);

html.divider();
html.kv("Language", "mylang v0.4.0");
html.kv("File", "sudoku_html.ml");

html.show(["browser", "file"]);
print("Sudoku HTML page generated and opened in browser.");
