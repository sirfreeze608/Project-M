// closures.ml — demonstrates closures and lexical scoping
fn make_counter(start) {
    let count = start;
    fn increment() {
        count = count + 1;
        return count;
    }
    return increment;
}

// String concatenation
fn greet(name) {
    return "Hello, " + name + "!";
}

print(greet("Alice"));
print(greet("Bob"));

// Nested function calls
fn square(x) { return x * x; }
fn sum_of_squares(a, b) { return square(a) + square(b); }
print(sum_of_squares(3, 4));
