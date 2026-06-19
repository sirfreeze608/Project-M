// new_features.ml — showcases all 23 newly added features

// ── 1. Complex literal syntax  (3+4j) ─────────────────────────────────────────
print("=== Complex Literals & Native Arithmetic ===");

let z1 = 3 + 4j;          // literal j suffix
let z2 = 1 - 2j;

print(z1);                 // 3+4j
print(z2);                 // 1-2j
print(z1 + z2);            // 4+2j  (native +)
print(z1 - z2);            // 2+6j  (native -)
print(z1 * z2);            // 11-2j (native *)
print(z1 / z2);            // -1+2j (native /)
print(z1 == z1);           // true
print(z1.abs());           // 5.0
print(z1.angle());         // 53.13...°
print(z1.conj());          // 3-4j

// phasor using literal syntax
let V = 10 + 0j;
let I = 2 - 1j;
let Z = V / I;             // impedance = V/I
print("Z = " + str(Z));

// ── 2. crypto namespace ────────────────────────────────────────────────────────
print("");
print("=== Crypto ===");

let hash = crypto.sha256("hello world");
print("SHA256: " + hash);
print("length: " + str(len(hash)));   // 64 hex chars

let mac = crypto.hmac("message", "secret-key");
print("HMAC:   " + mac.slice(0, 16) + "...");

let key = crypto.pbkdf2("my-password", "random-salt", 50000);
print("PBKDF2: " + key.slice(0, 16) + "...");

let enc = crypto.encrypt_aes("Sensitive data!", "my-aes-key");
let dec = crypto.decrypt_aes(enc, "my-aes-key");
print("AES round-trip: " + dec);

// Secure in-memory vault
crypto.secure_store("api_token", "sk-abc123");
let tok = crypto.secure_retrieve("api_token");
print("Token retrieved: " + tok);
crypto.secure_wipe("api_token");
print("Token wiped from vault.");

// ── 3. csv namespace ──────────────────────────────────────────────────────────
print("");
print("=== CSV ===");

let csv_text = "name,age,score\nAlice,30,95.5\nBob,25,87\nCarol,35,91";
let rows = csv.parse(csv_text);

// First row is the header
let header = rows[0];
print("Columns: " + str(header));

// Data rows (auto-coerced to numbers where possible)
let scores = [];
let i = 1;
while (i < rows[0].len() + 2) {
    i = i + 1;
}
// Simpler: iterate all rows, skip header
let score_vals = [];
for (row in rows) {
    if (row[0] != "name") {
        push(score_vals, row[2]);
        print(row[0] + " scored " + str(row[2]));
    }
}
print("Average score: " + str(round(stats.mean(score_vals), 2)));

// Stringify back to CSV
let out_data = [["name", "grade"], ["Alice", "A"], ["Bob", "B"], ["Carol", "A"]];
let output_csv = csv.stringify(out_data);
print("Generated CSV:");
print(output_csv);

// ── 4. image namespace ────────────────────────────────────────────────────────
print("");
print("=== Image / Canvas ===");

// Create a 400×300 canvas and draw a simple circuit diagram
image.blank(400, 300, "#1e1e1e");

// Background label
image.text("RC Low-Pass Filter", 120, 30, 16, "#4EC9B0");

// Resistor (drawn as a rectangle)
image.rect(80, 130, 80, 30, "#CE9178");
image.text("R = 1kΩ", 90, 150, 11, "#1e1e1e");

// Wire left
image.line(20, 145, 80, 145, "#D4D4D4", 2);

// Wire between R and C
image.line(160, 145, 220, 145, "#D4D4D4", 2);

// Capacitor (two vertical lines)
image.line(220, 115, 220, 175, "#569CD6", 3);
image.line(240, 115, 240, 175, "#569CD6", 3);
image.text("C = 1µF", 228, 200, 11, "#569CD6");

// Wire right
image.line(240, 145, 360, 145, "#D4D4D4", 2);

// Ground lines
image.line(20,  145, 20,  230, "#D4D4D4", 2);
image.line(20,  230, 360, 230, "#D4D4D4", 2);
image.line(360, 145, 360, 230, "#D4D4D4", 2);

// Labels
image.text("Vin", 22, 135, 12, "#DCDCAA");
image.text("Vout", 330, 135, 12, "#DCDCAA");

// Cutoff frequency label
let f0 = round(ee.resonant_freq(10e-3, 1e-6), 0);
image.text("f3dB ≈ " + str(round(1/(2*PI*1000*1e-6), 1)) + " Hz", 130, 270, 12, "#6A9955");

// Show renders to Pacer's Visual Panel (or prints SVG when run from terminal)
image.show("RC Low-Pass Filter");

print("Canvas rendered.");
print("Run inside Pacer to see it in the Visual Panel →");
