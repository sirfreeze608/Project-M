// math_stats.ml — math and statistics showcase

print("=== Core Math ===");
print(sqrt(144));                    // 12
print(pow(2, 10));                   // 1024
print(abs(-42));                     // 42
print(floor(3.9));                   // 3
print(ceil(3.1));                    // 4
print(round(3.14159, 2));            // 3.14
print(clamp(15, 0, 10));             // 10
print(sign(-99));                    // -1

print("=== Constants ===");
print(PI);                           // 3.141592...
print(E);                            // 2.718281...
print(PHI);                          // 1.618033... golden ratio

// Namespace style
print(math.sin(PI / 2));             // 1.0
print(math.cos(0));                  // 1.0
print(math.log(E));                  // 1.0
print(math.log(1000, 10));           // 3.0
print(math.deg(PI));                 // 180.0
print(math.rad(180));                // PI

print("=== Combinatorics ===");
print(factorial(6));                 // 720
print(comb(10, 3));                  // 120
print(perm(5, 2));                   // 20
print(gcd(48, 18));                  // 6

print("=== Quadratic solver ===");
// x² - 5x + 6 = 0  →  roots: 3, 2
let roots = quadratic(1, -5, 6);
print(roots[0]);                     // 3.0
print(roots[1]);                     // 2.0

// x² + 1 = 0  →  complex roots
let croots = quadratic(1, 0, 1);
print(croots[0]);                    // 0+1j
print(croots[1]);                    // 0-1j

print("=== Statistics ===");
let data = [4, 8, 15, 16, 23, 42, 42, 15, 4];

print(stats.mean(data));             // mean
print(stats.median(data));           // median
print(stats.mode(data));             // [4, 15, 42]
print(stats.stdev(data));            // sample std dev
print(stats.variance(data));         // sample variance
print(stats.min(data));              // 4
print(stats.max(data));              // 42
print(stats.sum(data));              // 169
print(stats.data_range(data));       // 38

print("=== Percentiles & Quartiles ===");
let scores = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100];
print(stats.percentile(scores, 25));  // 32.5
print(stats.percentile(scores, 75));  // 72.5
print(stats.quartiles(scores));       // [Q1, Q2, Q3]

print("=== Correlation & Regression ===");
let xs = [1, 2, 3, 4, 5];
let ys = [2, 4, 5, 4, 5];

print(stats.correlation(xs, ys));    // ~0.9

let model = stats.linreg(xs, ys);
print("slope:     " + str(model["slope"]));
print("intercept: " + str(model["intercept"]));
print("r²:        " + str(model["r2"]));

print("=== Z-scores & Normalise ===");
let raw = [10, 20, 30, 40, 50];
print(stats.zscore(raw));
print(stats.normalize(raw));

print("=== Normal distribution ===");
print(stats.normal_pdf(0, 0, 1));    // peak at mean (~0.3989)
print(stats.normal_cdf(0, 0, 1));    // 0.5 at mean
print(stats.normal_cdf(1.96, 0, 1)); // ~0.975
