// sudoku.ml — a full Sudoku solver/printer in mylang
// Demonstrates: 2D arrays, recursion via closures-as-functions,
// nested loops, early return, and the math/array stdlib.

fn make_board(rows) {
    return rows;
}

fn print_board(board) {
    let r = 0;
    while (r < 9) {
        if (r % 3 == 0 && r != 0) {
            print("------+-------+------");
        }
        let line = "";
        let c = 0;
        while (c < 9) {
            if (c % 3 == 0 && c != 0) {
                line = line + "| ";
            }
            let v = board[r][c];
            if (v == 0) {
                line = line + ". ";
            } else {
                line = line + str(v) + " ";
            }
            c = c + 1;
        }
        print(line);
        r = r + 1;
    }
}

fn is_valid(board, row, col, num) {
    // Row check
    let i = 0;
    while (i < 9) {
        if (board[row][i] == num) { return false; }
        i = i + 1;
    }
    // Column check
    i = 0;
    while (i < 9) {
        if (board[i][col] == num) { return false; }
        i = i + 1;
    }
    // 3x3 box check
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
            if (board[r][c] == 0) {
                return [r, c];
            }
            c = c + 1;
        }
        r = r + 1;
    }
    return null;
}

fn solve(board) {
    let empty = find_empty(board);
    if (empty == null) {
        return true;  // solved
    }
    let row = empty[0];
    let col = empty[1];

    let num = 1;
    while (num <= 9) {
        if (is_valid(board, row, col, num)) {
            board[row][col] = num;
            if (solve(board)) {
                return true;
            }
            board[row][col] = 0;  // backtrack
        }
        num = num + 1;
    }
    return false;
}

// ── A real, known-solvable Sudoku puzzle (0 = empty cell) ──────────────────
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

print("=== PUZZLE ===");
print_board(puzzle);
print("");

let solved = solve(puzzle);

if (solved) {
    print("=== SOLVED ===");
    print_board(puzzle);
} else {
    print("No solution exists.");
}
