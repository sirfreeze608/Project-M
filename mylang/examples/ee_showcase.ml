// ee_showcase.ml — Electrical Engineering built-ins

print("=== Ohm's Law ===");
let V = ee.voltage(2, 100);
let I = ee.current(12, 4);
let R = ee.resistance(9, 3);
print("V = " + str(V) + " V");
print("I = " + str(I) + " A");
print("R = " + str(R) + " Ω");

print("=== Power ===");
print(ee.power(12, 2));
print(ee.power_r(2, 10));
print(ee.power_v(10, 50));

print("=== Resistor Networks ===");
print("Series R   = " + str(ee.series([100, 200, 300])) + " Ω");
print("Parallel R = " + str(round(ee.parallel([100, 100, 100]), 4)) + " Ω");

print("=== Capacitors ===");
print("Caps series:   " + str(ee.cap_series([10e-6, 10e-6])));
print("Caps parallel: " + str(ee.cap_parallel([10e-6, 10e-6])));

print("=== RC / RL Time Constants ===");
print("RC τ = " + str(ee.rc_tau(1000, 100e-6)) + " s");
print("RL τ = " + str(ee.rl_tau(0.5, 100)) + " s");

print("=== RC Charge/Discharge ===");
let Vs = 5.0;
for (t in [0, 0.1, 0.5, 1.0, 2.0]) {
    let vc = ee.rc_charge(Vs, t, 1000, 100e-6);
    print("t=" + str(t) + "s  Vc=" + str(round(vc, 4)) + "V");
}

print("=== Reactance ===");
print("Xc = " + str(round(ee.xc(1000, 1e-6), 2)) + " Ω");
print("Xl = " + str(round(ee.xl(1000, 10e-3), 4)) + " Ω");

print("=== Impedance (complex) ===");
let Z_rlc = ee.impedance_rlc(100, 1000, 10e-3, 1e-6);
print("Z_RLC = " + str(Z_rlc));
print("Z_RLC magnitude = " + str(round(Z_rlc.abs(), 3)) + " Ω");
print("Z_RLC phase     = " + str(round(Z_rlc.angle(), 2)) + "°");

print("=== Resonance ===");
let f0 = ee.resonant_freq(10e-3, 1e-6);
print("f₀ = " + str(round(f0, 2)) + " Hz");
print("Q  = " + str(round(ee.q_factor(f0, 500), 2)));
print("BW = " + str(round(ee.bandwidth(f0, 10), 2)) + " Hz");

print("=== dB & Signal ===");
print(round(ee.to_db(2), 3));
print(ee.to_db_power(10));
print(round(ee.vrms(340), 2));
print(round(ee.vpeak(230), 2));

print("=== Phasors ===");
let V1 = ee.phasor(10, 0);
let V2 = ee.phasor(10, 90);
let Vsum = ee.complex_add(V1, V2);
print("|V1+V2| = " + str(round(ee.phasor_mag(Vsum), 4)));
print("∠(V1+V2) = " + str(round(ee.phasor_angle(Vsum), 2)) + "°");

print("=== Voltage Divider ===");
print("Vout = " + str(round(ee.voltage_divider(9, 10000, 4700), 3)) + " V");

print("=== Thevenin Equivalent ===");
let th = ee.thevenin(12, 0.5);
print("Vth = " + str(th["vth"]) + " V");
print("Rth = " + str(th["rth"]) + " Ω");

print("=== Energy Storage ===");
print("E_cap = " + str(ee.energy_cap(100e-6, 12)) + " J");
print("E_ind = " + str(ee.energy_ind(10e-3, 2)) + " J");
print("Q_cap = " + str(ee.charge(100e-6, 12)) + " C");

print("=== Physical Constants ===");
print("ε₀ = " + str(ee.EPSILON0));
print("q  = " + str(ee.ELECTRON) + " C");
