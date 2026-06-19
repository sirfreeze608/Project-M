// complex_matrix.ml — complex numbers and matrices

print("=== Complex Numbers ===");
let z1 = complex(3, 4);
let z2 = complex(1, -2);

print(z1);                             // 3+4j
print(z2);                             // 1-2j
print(z1.real());                      // 3
print(z1.imag());                      // 4
print(z1.abs());                       // 5.0  (magnitude)
print(z1.angle());                     // 53.13°
print(z1.conj());                      // 3-4j

let zsum = ee.complex_add(z1, z2);
let zprod = ee.complex_mul(z1, z2);
let zdiv  = ee.complex_div(z1, z2);
print(zsum);                           // 4+2j
print(zprod);                          // 11-2j
print(zdiv);                           // -1+2j

print("=== Matrices ===");
let A = matrix([[1, 2], [3, 4]]);
let B = matrix([[5, 6], [7, 8]]);

print(A);
print(B);

let C = mat_add(A, B);
print("A + B =");
print(C);

let D = mat_mul(A, B);
print("A × B =");
print(D);

print("det(A) = " + str(mat_det(A)));    // -2
print("trace(A) = " + str(mat_trace(A))); // 5

let At = mat_transpose(A);
print("A^T =");
print(At);

// Method-call style
print(A.det());
print(A.trace());
print(A.transpose());

// Identity and zeros
let I3 = mat_identity(3);
let Z2 = mat_zeros(2, 3);
print("I₃ ="); print(I3);
print("0₂ₓ₃ ="); print(Z2);

// Get/set individual elements
print(mat_get(A, 0, 1));               // 2
let A2 = mat_set(A, 1, 0, 99);
print(mat_get(A2, 1, 0));              // 99

// Shape info
let sh = mat_shape(A);
print("rows: " + str(sh["rows"]) + "  cols: " + str(sh["cols"]));

print("=== Practical: Solve 2x2 system via Cramer's Rule ===");
// 2x + y = 5
// x + 3y = 10
let coeff = matrix([[2, 1], [1, 3]]);
let Dx    = matrix([[5, 1], [10, 3]]);
let Dy    = matrix([[2, 5], [1, 10]]);
let detA  = mat_det(coeff);
let x_sol = mat_det(Dx) / detA;
let y_sol = mat_det(Dy) / detA;
print("x = " + str(x_sol));           // 1.0
print("y = " + str(y_sol));           // 3.0
