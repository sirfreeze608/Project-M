// arrays.ml — demonstrates arrays and built-in functions

// Build a range array
fn range(n) {
    let arr = [];
    let i = 0;
    while (i < n) {
        push(arr, i);
        i = i + 1;
    }
    return arr;
}

// Sum all elements of an array
fn sum(arr) {
    let total = 0;
    let i = 0;
    while (i < len(arr)) {
        total = total + arr[i];
        i = i + 1;
    }
    return total;
}

// Reverse an array (in place)
fn reverse(arr) {
    let left = 0;
    let right = len(arr) - 1;
    while (left < right) {
        let tmp = arr[left];
        arr[left] = arr[right];
        arr[right] = tmp;
        left = left + 1;
        right = right - 1;
    }
    return arr;
}

// --- main ---

let nums = range(5);
print("range(5):  " + str(nums));
print("sum:       " + str(sum(nums)));
print("type:      " + type(nums));
print("length:    " + str(len(nums)));

let words = ["banana", "apple", "cherry"];
print("before:    " + str(words));
print("reversed:  " + str(reverse(words)));

// Nested arrays — a 2D grid
let grid = [[1, 2, 3], [4, 5, 6], [7, 8, 9]];
print("grid[1][2]: " + str(grid[1][2]));
