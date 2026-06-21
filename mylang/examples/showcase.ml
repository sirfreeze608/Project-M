// showcase.ml — demonstrates all new features

// ── for loops ─────────────────────────────────────────────────────────────────
print("=== for loops ===");
let fruits = ["apple", "banana", "cherry"];
for (fruit in fruits) {
    print(fruit);
}

// range() built-in
for (i in range(5)) {
    print(i);
}

// ── hash maps ─────────────────────────────────────────────────────────────────
print("=== hash maps ===");
let person = {
    "name": "Alice",
    "age": 30,
    "active": true
};
print(person["name"]);
print(person["age"]);

person["age"] = 31;
print("birthday: " + str(person["age"]));

// iterate hash keys
for (key in person) {
    print(key + " => " + str(person[key]));
}

// ── string methods ─────────────────────────────────────────────────────────────
print("=== string methods ===");
let msg = "  Hello, World!  ";
print(msg.trim());
print(msg.trim().upper());
print(msg.trim().lower());
print(msg.trim().replace("World", "mylang"));

let csv = "one,two,three,four";
let parts = csv.split(",");
print(parts);
print("length: " + str(len(parts)));
print(parts.join(" | "));

print("contains 'World': " + str(msg.contains("World")));
print("starts_with '  H': " + str(msg.starts_with("  H")));
print(msg.trim().slice(0, 5));

// ── first-class functions ─────────────────────────────────────────────────────
print("=== first-class functions ===");

// Store functions in variables
let double = fn(x) { return x * 2; };
let square = fn(x) { return x * x; };
print(double(5));
print(square(5));

// Pass functions as arguments
fn apply(f, value) {
    return f(value);
}
print(apply(double, 7));
print(apply(square, 7));

// Return functions from functions (closures)
fn make_adder(n) {
    return fn(x) { return x + n; };
}
let add10 = make_adder(10);
let add100 = make_adder(100);
print(add10(5));
print(add100(5));

// ── array methods (map / filter / reduce) ─────────────────────────────────────
print("=== map / filter / reduce ===");
let nums = range(1, 6);   // [1, 2, 3, 4, 5]
print(nums);

let doubled = nums.map(fn(x) { return x * 2; });
print(doubled);

let evens = nums.filter(fn(x) { return x % 2 == 0; });
print(evens);

let total = nums.reduce(fn(acc, x) { return acc + x; }, 0);
print("sum: " + str(total));

// Chain them
let result = range(1, 11)
    .filter(fn(x) { return x % 2 == 0; })
    .map(fn(x) { return x * x; });
print(result);
