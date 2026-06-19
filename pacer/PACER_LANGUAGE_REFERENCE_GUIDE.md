# PACER: The Interactive Computational Programming Language
### Complete Language Specification, Library Reference, and Compiler Switch Manual
*Written for Beginners, Researchers, and System Engineers (Version 2.4.0 Core)*

---

## Welcome to Pacer!

Pacer is a high-performance, dynamically-typed programming language designed for scientific calculations, electrical engineering simulations, cryptographic proof-of-concepts, spreadsheet parser systems, and dynamic canvas illustrations. 

Pacer compiles code into an **Abstract Syntax Tree (AST)**, runs structural sanitization checks to prevent unsafe register leakage, and executes inside an isolated, sandboxed **Virtual Machine (VM)** context. 

This guide acts as a comprehensive textbook and reference manual to teach you the syntax, functions, modules, compiler targets, and practical real-world automation scripts.

---

## Table of Contents
1. [Core Syntax & Primitive Types](#1-core-syntax--primitive-types)
2. [Control Flow & Iteration Loops](#2-control-flow--iteration-loops)
3. [Arrays & High-Order Closures](#3-arrays--high-order-closures)
4. [Hashes & Key-Value Stores](#4-hashes--key-value-stores)
5. [Special Scientific Data Types](#5-special-scientific-data-types)
   - [A. Complex Numbers](#a-complex-numbers)
   - [B. Math Matrices](#b-math-matrices)
6. [Global Namespace Libraries](#6-global-namespace-libraries)
   - [`math` Library](#a-the-math-library)
   - [`stats` Library](#b-the-stats-library)
   - [`ee` (Electrical Engineering) Library](#c-the-ee-electrical-engineering-library)
   - [`crypto` Library](#d-the-crypto-security-library)
   - [`image` (Canvas Vector Drawing) Library](#e-the-image-vector-drawing-library)
   - [`csv` Parsing Library](#f-the-csv-spreadsheet-library)
7. [Compiler Target Switches (Deployment Model)](#7-compiler-target-switches-deployment-model)
8. [Dynamic Tutorials for Beginners](#8-dynamic-tutorials-for-beginners)

---

## 1. Core Syntax & Primitive Types

Pacer is dynamically-typed. You do not need to declare types; variables will automatically accept whatever data is loaded into them. Variable bindings are block-scoped.

### Declaring Variables: `let`
Use the `let` keyword to declare or reassign variables:
```pacer
let lengthValue = 100;                 // Number (Integer)
let voltageCoefficient = 12.5e-3;      // Number (Scientific float notation)
let bannerTitle = "Solenoid RMS Calc"; // String
let isActiveGrid = true;               // Boolean
let remoteOffset = null;               // Null reference
```

### Basic Arithmetic and Logic Operators
Pacer standardizes math and boolean comparisons with consistent operator rules:
*   **Arithmetic**: `+`, `-`, `*`, `/`, `%` *(Modulo / division remainder)*
*   **Comparisons**: `==`, `!=`, `<`, `<=`, `>`, `>=`
*   **Logical Operations**: `&&` *(Logical AND)*, `||` *(Logical OR)*, `!` *(Unary NOT negation)*
```pacer
let totalVoltage = 12 + (3 * 4); // 24
let highPower = totalVoltage > 200 && isActiveGrid; // false
```

### String Interpolation and Addition
Adding a string and a variable automatically casts the variable's value to a string:
```pacer
let flowRate = 9.81;
print("Current system acceleration: " + flowRate + " m/s2");
```

### String Built-in Methods
Strings support extensive processing methods:
*   `.upper()`: Casts string to UPPERCASE.
*   `.lower()`: Casts string to lowercase.
*   `.trim()`: Trims surrounding whitespace.
*   `.split(separator)`: Splits a string into an Array of substrings. (Defaults to space `" "`).
*   `.replace(old_str, new_str)`: Replaces substrings.
*   `.contains(substring)`: Returns `true` if the string contains the target segment.
*   `.starts_with(prefix)`: Checks leading characters.
*   `.ends_with(suffix)`: Checks trailing characters.
*   `.slice(start, end)`: Extracts a substring from clean index ranges.
*   `.index_of(substring)`: Returns the first matched character index.

```pacer
let rawAddress = "  Pacer-Studio-Platform ";
let cleaned = rawAddress.trim(); // "Pacer-Studio-Platform"
let parts = cleaned.split("-");   // ["Pacer", "Studio", "Platform"]
```

---

## 2. Control Flow & Iteration Loops

Pacer compiles standard structured branch logic and iterative evaluations.

### The Conditional `if/else` Block
```pacer
let temperature = 102.5;

if (temperature > 100.0) {
  print("⚠️ COOLING COMPRESSOR ACTIVATING: OVER LIMIT!");
} else if (temperature < 15.0) {
  print("🔥 HEAT ELEMENTS ACTIVE");
} else {
  print("✅ CORE PARAMETERS STABLE");
}
```

### The `while` Loop
Pacer loops sequentially as long as a condition evaluates to `true`:
```pacer
let countdown = 5;
while (countdown > 0) {
  print("T-Minus: " + countdown);
  countdown = countdown - 1;
}
```

### The List Iteration `for` Loop
To traverse Arrays, Strings, or Hash Keys directly:
```pacer
let outputsList = [1.2, 5.4, 9.8];
for (item in outputsList) {
  print("Measured node feedback: " + item);
}
```

---

## 3. Arrays & High-Order Closures

Arrays in Pacer store collections of variables and are constructed using brackets `[...]`.

### Global Array Operations
*   `len(arr)`: Returns the count of array items.
*   `push(arr, element)`: Appends an item to the end of the array.
*   `pop(arr)`: Removes and returns the last element.

```pacer
let samples = [5, 10, 15];
print("Array Size: " + len(samples)); // 3
push(samples, 20); // samples is now [5, 10, 15, 20]
```

### Native Array Core Methods
Instead of using global wrappers, you can call array methods directly on the object:
*   `arr.len()`: Returns the size.
*   `arr.push(v)`: Appends value `v` directly.
*   `arr.pop()`: Returns the tail object.
*   `arr.contains(v)`: Returns `true` if element `v` is found inside the collection.
*   `arr.index_of(v)`: Returns item's index, or `-1` if not found.
*   `arr.join(separator)`: Merges elements into a text string.
*   `arr.reverse()`: Performs an in-memory reverse sequence array clone.
*   `arr.slice(start, end)`: Grabs partitioned slices.

```pacer
let tags = ["R1", "C2", "L5"];
if (tags.contains("C2")) {
  print("Capacitor indexed at: " + tags.index_of("C2")); // 1
}
```

### High-Order Functional Closures (`map`, `filter`, `reduce`)
Pacer allows array functional processing using inline callback functions (declarations beginning with `fn`):

```pacer
let elements = [1.2, 5.5, -3.1, 4.0, 9.2];

// 1. Filter out absolute negative values
let positiveNodes = elements.filter(fn(item) { 
  return item > 0; 
});
// result: [1.2, 5.5, 4.0, 9.2]

// 2. Map & scale remaining positives by 10
let scaledNodes = positiveNodes.map(fn(item) { 
  return item * 10.0; 
});
// result: [12, 55, 40, 92]

// 3. Sum all scaled objects using reduce
let sumTotal = scaledNodes.reduce(fn(accumulator, current) {
  return accumulator + current;
}, 0.0);
// result: 199.00
```

---

## 4. Hashes & Key-Value Stores

Hashes are key-value dictionaries created inside braces `{}`.

### Hash Operations
Keys must be primitive string labels, numbers, or booleans:
```pacer
let circuitMap = {
  "transistor": "NPN",
  "inductors": 5,
  "highPass": false
};

// Accessing values
print("Actives inductors: " + circuitMap["inductors"]); // 5

// Setting or changing values
circuitMap["highPass"] = true;
```

### Hash Methods Suite
*   `hash.len()`: Counts key-value pairs.
*   `hash.keys()`: Returns an Array of all key names.
*   `hash.values()`: Returns an Array of all element values.
*   `hash.has(key)`: Returns `true` if the key exists.
*   `hash.del(key)`: Removes the entry from the hash map.

```pacer
let testGrid = {"nodeA": 120, "nodeB": 240};
if (testGrid.has("nodeB")) {
  testGrid.del("nodeB");
}
```

---

## 5. Special Scientific Data Types

Pacer features built-in objects designed specifically to run advanced telemetry calculations without loading performance-heavy third-party libraries.

### A. Complex Numbers
Perfect for phase calculations, frequency sweeps, or electrical wave analysis.
*   **Creation**: Declared with suffix `j` format or via the `complex(real, imag)` utility function:
```pacer
let phas_a = complex(3, 4); // Creates complex number 3+4j
let phas_b = 3 - 4j;        // Alternative literal declaration format
```
*   **Addition and Vector Arithmetics**: Custom arithmetic operations on complex objects recalculate their components automatically.
```pacer
let sumComplex = phas_a + phas_b; // Result: 6+0j
```
*   **Properties & Core Methods**:
    *   `obj.real()`: Real coordinate number.
    *   `obj.imag()`: Imaginary offset multiplier.
    *   `obj.abs()`: Computes root magnitude $\sqrt{r^2 + i^2}$.
    *   `obj.conj()`: Conjugates signs (e.g. $3+4j \leftrightarrow 3-4j$).
    *   `obj.angle()`: Solves Phase angle directly in degrees.

```pacer
let pNode = complex(10, -10);
print("Phase Magnitude: " + pNode.abs());   // 14.142136
print("Phase Angle (Deg): " + pNode.angle()); // -45
```

---

### B. Math Matrices
Pacer contains a native Row-major multi-dimensional matrix layout compiler capable of solving complex linear systems.
*   **Creation**: Wrapped via the `matrix` standard function, or generated automatically as empty configurations:
```pacer
// Declaring an explicit 2x2 coordinate space matrix
let m = matrix([
  [1.0, 5.0],
  [0.0, 2.0]
]);

// Helper constructors
let zMatrix = mat_zeros(3, 4);    // Formats a 3-row, 4-column matrix containing zeros
let iMatrix = mat_identity(3);     // Solves a square 3x3 identity matrix with a diagonal of ones
```

*   **Matrix Property Methods**:
    *   `mat.shape()`: Returns Hash representation of grid counts `{"rows": r, "cols": c}`.
    *   `mat.get(row, col)`: Accesses specific element value.
    *   `mat.set(row, col, value)`: Modifies targeted coordinate cell.
    *   `mat.transpose()`: Rotates cell row values to columns.
    *   `mat.det()`: Performs recursive matrix cofactor expansion to solve determinant values (requires a square matrix layout).
    *   `mat.trace()`: Computes trace (sum of diagonal cells).
    *   `mat.scale(multiplier)`: Scales all entries uniformly.
    *   `mat.to_array()`: Outputs standard nested Pacer array lists.

```pacer
let mCoord = matrix([
  [2.0, 1.0],
  [1.0, 3.0]
]);
print("Determined volume: " + mCoord.det()); // 5
```

---

## 6. Global Namespace Libraries

Pacer structures specialized functions inside direct namespaces.

### A. The `math` Library
The standard library `math` provides algebraic constants and trigonometric processing blocks.

#### Constants
*   `math.PI`: $\pi \approx 3.14159265$
*   `math.E`: Euler's number $\approx 2.7182818$
*   `math.TAU`: $2\pi \approx 6.2831853$
*   `math.PHI`: Golden section ratio $\approx 1.618033$
*   `math.INF`, `math.NAN`: Infinite bounds and undefined metrics.

#### Core Functions
*   `math.sqrt(x)`: Square root. If negative, returns a `MylangComplex` object containing imaginary numbers.
*   `math.pow(x, y)`: Power operation ($x^y$).
*   `math.abs(x)`: Absolute scale.
*   `math.floor(x)`, `math.ceil(x)`: Rounds down or up.
*   `math.round(x, decimals)`: Precision rounding index.
*   `math.clamp(x, min, max)`: Restricts values within bounds.
*   `math.sin(x)`, `math.cos(x)`, `math.tan(x)`: Basic trigonometric functions (takes radians).
*   `math.deg(rad)`, `math.rad(deg)`: Angle conversions.
*   `math.exp(x)`: Exponential power ($e^x$).
*   `math.log(x, base)`: Evaluates log output. Defaults to natural log base.
*   `math.factorial(n)`: Factorial permutations.
*   `math.comb(n, k)`, `math.perm(n, k)`: Statistical combinations and selections.
*   `math.gcd(a, b)`, `math.lcm(a, b)`: Greatest Common Divisor and Least Common Multiple.
*   `math.random()`: Stable pseudo-random decimal selection between $0$ and $1$ (LCG-calculated).
*   `math.rand_int(min, max)`: Direct integer range randomized result.
*   `math.quadratic(a, b, c)`: Evaluates roots for $ax^2 + bx + c = 0$. Outputs an array of solved real or complex numbers.

```pacer
let solvedRoots = math.quadratic(1, -5, 6); // Solves x2 - 5x + 6 = 0
print("Roots solved: " + solvedRoots);       // [3, 2]
```

---

### B. The `stats` Library
Perfect for analyzing datasets and regression testing.

#### Core Functions
*   `stats.mean(arr)`: Computes average.
*   `stats.median(arr)`: Solves middle values.
*   `stats.variance(arr)`: Evaluates variance limits.
*   `stats.stdev(arr)`: Standard deviation.
*   `stats.normalize(arr)`: Min-Max normalizes a dataset.
*   `stats.linreg(x_arr, y_arr)`: Solves the linear equation $y = mx + b$. Plots a regression model directly in the Pacer Graphing View.
*   `stats.histogram(arr, bins)`: Generates frequency counts categorized into bin groups.

```pacer
let tempLogs = [22, 24, 23, 25, 29, 21, 24];
print("Avg temperature: " + stats.mean(tempLogs)); // 24
```

---

### C. The `ee` (Electrical Engineering) Library
Designed specifically to calculate analog circuits, impedance, and filter characteristics.

#### Core Functions
*   `ee.voltage(i, r)`: Solve potential Ohm difference: $V = I \times R$.
*   `ee.current(v, r)`: Solve energy current flow: $I = V / R$.
*   `ee.series(resistors_list)`: Combines series loads: $R_{eq} = R_1 + R_2 + \dots$
*   `ee.parallel(resistors_list)`: Combines parallel loops: $1/R_{eq} = 1/R_1 + 1/R_2 + \dots$
*   `ee.resonant_freq(inductance, capacitance)`: Solves resonant threshold: $f_0 = \frac{1}{2\pi\sqrt{LC}}$.
*   `ee.rc_charge(v0, time, resistance, capacitance)`: Solves time-domain voltage of a capacitor: $v(t) = v_0(1 - e^{-t/RC})$.
*   `ee.phasor(magnitude, angle_deg)`: Formats angular phasors into complex variables.
*   `ee.impedance_rlc(r, frequency, l, c)`: Models and plots RLC impedential components.

```pacer
let filterCap = 10e-6; // 10 microfarads
let filterInd = 0.22;  // 220 millihenries
let centerFreq = ee.resonant_freq(filterInd, filterCap);
print("Resonant f0: " + centerFreq + " Hz"); // 107.29... Hz
```

---

### D. The `crypto` Security Library
Provides tools to perform integrity checks, protect sensitive parameters, and encrypt datastreams.

#### Core Functions
*   `crypto.sha256(text)`: Computes standard SHA-256 integrity hash hexadecimal of text string.
*   `crypto.hmac(msg, key)`: Computes HMAC-SHA256 signature hashes.
*   `crypto.pbkdf2(password, salt, iterations)`: Validates PBKDF2 password keys with custom iterations.
*   `crypto.encrypt_aes(cleartext, key)`: Symmetric encryption stream (AES-equivalent hex format).
*   `crypto.decrypt_aes(hexstream, key)`: Symmetric decryption.

#### Scoped Secure Memory Vault Functionality
Avoid storing plaintext secrets (Database passwords, API credentials) in global system variables. Pacer secures sensitive data by locking values inside a dedicated secure memory vault:
*   `crypto.secure_store(key_label, text_secret)`: Encrypts and locks a raw key value inside the local system secure buffer.
*   `crypto.secure_retrieve(key_label)`: Temporary decryption stream to execute authentication processes.
*   `crypto.secure_wipe(key_label)`: Active garbage-collection step to sanitize workspace memory caches.

```pacer
// Enforcing secure vault lifetime
crypto.secure_store("ApiKey", "PACS-38491-API-KEY");
let workingCredentials = crypto.secure_retrieve("ApiKey");
// Execute remote service tasks...
crypto.secure_wipe("ApiKey"); // Memory cleared! No footprint remaining.
```

---

### E. The `image` Vector Drawing Library
The `image` library enables developers to create vector graphics, draw coordinates, and display customized interfaces inside the interactive canvas view.

#### Core Functions
*   `image.blank(width, height, background_hex)`: Initializes an asset workspace with fixed pixel configurations and a background color.
*   `image.rect(x, y, width, height, fill_color_hex)`: Renders flat rectangles.
*   `image.circle(cx, cy, radius, fill_color_hex)`: Draws custom circles.
*   `image.line(x1, y1, x2, y2, stroke_color, stroke_width)`: Draws line segments.
*   `image.text(message, x, y, size, fill)`: Draws readable labels.
*   `image.show(title)`: Renders and locks the canvas inside Pacer's Visual Panel tab.
*   `image.load(url, title)`: Loads remote images into the Visual Panel.

```pacer
// Generating a clean blueprint overlay
image.blank(400, 300, "#0d1117");
image.rect(10, 10, 380, 280, "#161b22");
image.circle(200, 150, 60, "#58a6ff40");
image.line(200, 0, 200, 300, "#8b949e", 1);
image.text("VECTOR COMPASS SCALE", 30, 260, 12, "#3fb950");
image.show("Dynamic Blueprint");
```

---

### F. The `csv` Spreadsheet Library
Provides tools to parse raw CSV data or serialize arrays back into CSV.

#### Core Functions
*   `csv.parse(csv_string)`: Converts raw comma-separated text into a nested array structure.
*   `csv.stringify(array_of_records)`: Serializes structured tables back into a CSV text string.

```pacer
let csvPayload = "Transistor,Value\nQ1,NPN\nQ2,PNP";
let dataGrid = csv.parse(csvPayload);
print("Read records count: " + len(dataGrid)); // 3 (includes header)
```

---

## 7. Compiler Target Switches (Deployment Model)

Pacer features a dynamic, multiple-target packaging compiler. Depending on your project requirements, you can build your application for different platforms:

### 📱 Android Standalone package (`apk`)
*   **Compile Switch**: Build profile target `apk`.
*   **Result**: Compiles source statements to a virtual bytecode layer and wraps them inside an Android runtime shell package.

### 🖥️ Desktop Standalone Client (`exe` / `msi`)
*   **Compile Switch**: Build profile target `nsis` (generates standard setup `.exe`) or `msi` (enterprise deployment).
*   **SmartScreen Code Signing**: To bypass Windows SmartScreen warnings on installation, set your code-signing certificate credentials dynamically inside the build terminal before calling packaging:
    *   **PowerShell Option**:
        ```powershell
        $env:CSC_LINK="C:\Certs\developer-key.pfx"
        $env:CSC_KEY_PASSWORD="SecurePassphraseHex"
        ```

### 🌐 Web Canvas Engine Deployment (`html`)
*   **Compile Switch**: Build profile target `html`.
*   **Result**: Compiles code to execute directly on the web using HTML5 Canvas drawing, perfect for direct integration into standard web app structures.

### 🐍 Python Native Interface script (`pyw`)
*   **Compile Switch**: Build profile target `pyw`.
*   **Result**: Produces an offline-first Python Tkinter application of your script that runs locally without complex external dependencies.

---

## 8. Dynamic Tutorials for Beginners

Here are three complete, ready-to-run examples to help you practice using Pacer's standard libraries. Copy and paste these directly into your Pacer editor!

### Tutorial 1: IoT Solar Power Budget Governor
Runs calculated checks on household energy storage, prioritizing solar panel inputs and managing battery levels to avoid drainage.

```pacer
print("=== SMART HOME RESILIENT ENERGY OPTIMIZER ===");

let solarInput = 1250.5;        // Real-time solar panel inflow (Watts)
let batteryRemaining = 1450.0;  // Stored reserves capacity (Watt-hours)

// Appliances load list structures
let appliances = [
  {"name": "Heat Pump", "load": 950.0, "priority": 1, "status": "active"},
  {"name": "Kitchen Fridge", "load": 180.0, "priority": 1, "status": "active"},
  {"name": "Living Room TV", "load": 300.0, "priority": 2, "status": "active"},
  {"name": "Outdoor Sprinkler", "load": 400.0, "priority": 3, "status": "active"}
];

// Calculate total active load
let totalActiveWatts = 0.0;
for (item in appliances) {
  if (item["status"] == "active") {
    totalActiveWatts = totalActiveWatts + item["load"];
  }
}
print("Total Household Power Demand: " + totalActiveWatts + " W");
print("Net Grid Intake Balance: " + (solarInput - totalActiveWatts) + " W");

// Prevent battery run-down during low solar periods
if (batteryRemaining < 1500.0) {
  print("⚠️ LOW STORAGE RESERVES: ENFORCING PRE-EMPTIVE SHUTDOWN ON LOW PRIORITY UNITS!");
  
  for (item in appliances) {
    if (item["priority"] >= 2 && item["status"] == "active") {
      item["status"] = "disabled";
      print("  [DISCONNECT] Shifting off appliance load: " + item["name"]);
    }
  }
} else {
  print("🔋 Standby battery capacity is within nominal parameters.");
}
```

---

### Tutorial 2: Secure Master Password Derivation
Applies modern cryptographic rules (using KDF derivation and HMAC hashing) to safely secure application access, then securely wipes memory layers to prevent credential leaks.

```pacer
print("=== CENTRAL SECURE VAULT ACCESS GATEWAY ===");

let rawMasterValue = "AdminMasterPassphrase2026!";
let staticEntropySalt = "sha256_vector_salt_entropy_9329";

// 1. Derive strong PBKDF2 vault key (execute 1,000 hashing rounds)
let vaultKeyToken = crypto.pbkdf2(rawMasterValue, staticEntropySalt, 1000);
print("Derivation Token solved successfully.");

// 2. Lock derived token securely inside volatile memory bounds
crypto.secure_store("active_session_token", vaultKeyToken);
print("Session Token cached inside protected vault.");

// 3. Retrieve and complete validation tests
let retrievedToken = crypto.secure_retrieve("active_session_token");
let hmacVerification = crypto.hmac("LAUNCH_TELEMETRY_PIPELINE", retrievedToken);
print("System Verification Hash: " + hmacVerification);

// 4. Critical: Explicitly wipe session variables from memory
crypto.secure_wipe("active_session_token");
print("Verification complete. Memory sanitized successfully.");
```

---

### Tutorial 3: Dynamic Circuit Schematic Illustrator
Renders an annotated electrical blueprint directly inside the Pacer Graphics Panel.

```pacer
// Renders an annotated electrical schematic diagram
image.blank(500, 300, "#080c10");

// Draw outline card
image.rect(10, 10, 480, 280, "#0d1117");

// Draw component connections (R - L - C in series)
image.line(30, 150, 100, 150, "#58a6ff", 2); // Left input lead

// Resistor symbol (zig-zag points mapped as lines)
image.line(100, 150, 115, 130, "#3fb950", 2);
image.line(115, 130, 135, 170, "#3fb950", 2);
image.line(135, 170, 155, 130, "#3fb950", 2);
image.line(155, 130, 170, 150, "#3fb950", 2);

image.line(170, 150, 240, 150, "#58a6ff", 1); // Mid connection lead

// Inductor coils
image.circle(260, 150, 15, "#a371f7");
image.circle(285, 150, 15, "#a371f7");

image.line(300, 150, 360, 150, "#58a6ff", 1); // Second connection lead

// Capacitor plate 1 and 2
image.line(360, 120, 360, 180, "#fff", 3);
image.line(380, 120, 380, 180, "#fff", 3);

image.line(380, 150, 470, 150, "#58a6ff", 2); // Ground output lead

// Text annotations
image.text("Pacer Circuit Schematic Sim", 25, 25, 14, "#ff7b72");
image.text("R = 100 Ohm", 95, 80, 11, "#3fb950");
image.text("L = 220 mH", 240, 80, 11, "#a371f7");
image.text("C = 10 uF", 350, 80, 11, "#fff");

image.show("Series RLC Blueprint");
print("Schematic vector loaded successfully into the Graphics tab!");
```
