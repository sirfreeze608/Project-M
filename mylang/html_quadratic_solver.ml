// Solve ax^2 + bx + c = 0 and present the result as an HTML page.
// This is the exact use case requested: feed in a quadratic equation,
// get a nicely formatted HTML output when the script runs.

let a = 1;
let b = -5;
let c = 6;

html.page("Quadratic Equation Solver");
html.heading("Solving ax^2 + bx + c = 0", 1);
html.text("Coefficients entered:");
html.kv("a", a);
html.kv("b", b);
html.kv("c", c);

html.divider();

let discriminant = (b * b) - (4 * a * c);
html.heading("Discriminant", 2);
html.result("b^2 - 4ac", discriminant);

html.divider();

let roots = quadratic(a, b, c);
html.heading("Roots", 2);
html.table(["Root", "Value"], [
    ["x1", roots[0]],
    ["x2", roots[1]]
]);

html.divider();
html.heading("Summary", 2);
html.list([
    "Equation: " + str(a) + "x^2 + (" + str(b) + ")x + " + str(c),
    "Discriminant: " + str(discriminant) + " (real roots since >= 0)",
    "Root 1 = " + str(roots[0]),
    "Root 2 = " + str(roots[1])
]);

html.show(["file"]);
print("Done. Quadratic solved and HTML page generated.");
