"""
stdlib.py — Standard library for mylang.

Provides three namespaces (math, stats, ee) plus flat top-level shortcuts,
all wired into the interpreter's global environment.

All functions receive already-evaluated Python values and return Python values.
MylangArray / MylangHash / MylangComplex / MylangMatrix are the runtime types.
"""

import math as _math
import cmath as _cmath
import statistics as _stats
import random as _random
import hashlib as _hashlib
import hmac as _hmac
import os as _os

# Interpreter runtime types are imported lazily to avoid circular imports.
# We define the new complex/matrix types here so interpreter.py can import them.


# ══════════════════════════════════════════════════════════════════════════════
# New runtime value types
# ══════════════════════════════════════════════════════════════════════════════

class MylangComplex:
    """Complex number: complex(real, imag)"""
    def __init__(self, real: float, imag: float = 0.0):
        self.value = complex(real, imag)

    @property
    def real(self): return self.value.real
    @property
    def imag(self): return self.value.imag

    def __repr__(self):
        r = _fmt(self.real)
        i = _fmt(self.imag)
        sign = "+" if self.imag >= 0 else ""
        return f"{r}{sign}{i}j"

    def __eq__(self, other):
        if isinstance(other, MylangComplex): return self.value == other.value
        return False


class MylangMatrix:
    """2-D matrix stored as list-of-lists (row-major)."""
    def __init__(self, rows: list[list]):
        self.rows = [list(r) for r in rows]
        self.nrows = len(rows)
        self.ncols = len(rows[0]) if rows else 0

    def __repr__(self):
        lines = ["[" + ", ".join(_fmt(v) for v in row) + "]"
                 for row in self.rows]
        return "[\n  " + "\n  ".join(lines) + "\n]"

    def __eq__(self, other):
        if isinstance(other, MylangMatrix): return self.rows == other.rows
        return False


def _fmt(v) -> str:
    """Format a number for display: drop .0 suffix on whole floats."""
    if isinstance(v, float):
        return str(int(v)) if v == int(v) else str(v)
    return str(v)


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

def _require_array(v, fn_name: str):
    from interpreter import MylangArray
    if not isinstance(v, MylangArray):
        raise RuntimeError(f"{fn_name}() requires an array — got {type(v).__name__}")
    return v.elements

def _require_number(v, fn_name: str):
    if not isinstance(v, (int, float)):
        raise RuntimeError(f"{fn_name}() requires a number — got {type(v).__name__}")
    return v

def _require_matrix(v, fn_name: str):
    if not isinstance(v, MylangMatrix):
        raise RuntimeError(f"{fn_name}() requires a matrix — got {type(v).__name__}")
    return v

def _require_complex(v, fn_name: str):
    if isinstance(v, MylangComplex): return v.value
    if isinstance(v, (int, float)):  return complex(v)
    raise RuntimeError(f"{fn_name}() requires a complex or number — got {type(v).__name__}")

def _to_number(v):
    """Coerce MylangComplex magnitude or plain number."""
    if isinstance(v, (int, float)): return v
    if isinstance(v, MylangComplex): return abs(v.value)
    raise RuntimeError(f"Expected a number, got {type(v).__name__}")

def _wrap(v):
    """Wrap Python values back into mylang types."""
    from interpreter import MylangArray
    if isinstance(v, complex):
        return MylangComplex(v.real, v.imag)
    if isinstance(v, list):
        return MylangArray([_wrap(x) for x in v])
    if isinstance(v, float) and v == int(v):
        return int(v)
    return v


# ══════════════════════════════════════════════════════════════════════════════
# ── MATH namespace ────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

def _m_sqrt(args):
    x = _require_number(args[0], "sqrt")
    if x < 0: return MylangComplex(0, _math.sqrt(-x))
    return _math.sqrt(x)

def _m_cbrt(args):
    x = _require_number(args[0], "cbrt")
    return _math.copysign(_math.pow(abs(x), 1/3), x)

def _m_pow(args):
    return _require_number(args[0], "pow") ** _require_number(args[1], "pow")

def _m_abs(args):
    v = args[0]
    if isinstance(v, MylangComplex): return abs(v.value)
    return abs(_require_number(v, "abs"))

def _m_floor(args):  return _math.floor(_require_number(args[0], "floor"))
def _m_ceil(args):   return _math.ceil (_require_number(args[0], "ceil"))
def _m_round(args):
    x = _require_number(args[0], "round")
    d = int(args[1]) if len(args) > 1 else 0
    return round(x, d)
def _m_sign(args):
    x = _require_number(args[0], "sign")
    return 0 if x == 0 else (1 if x > 0 else -1)
def _m_clamp(args):
    x  = _require_number(args[0], "clamp")
    lo = _require_number(args[1], "clamp")
    hi = _require_number(args[2], "clamp")
    return max(lo, min(hi, x))

# Trig (degrees helpers included)
def _m_sin(args):   return _math.sin (_require_number(args[0], "sin"))
def _m_cos(args):   return _math.cos (_require_number(args[0], "cos"))
def _m_tan(args):   return _math.tan (_require_number(args[0], "tan"))
def _m_asin(args):  return _math.asin(_require_number(args[0], "asin"))
def _m_acos(args):  return _math.acos(_require_number(args[0], "acos"))
def _m_atan(args):  return _math.atan(_require_number(args[0], "atan"))
def _m_atan2(args):
    return _math.atan2(_require_number(args[0],"atan2"),
                       _require_number(args[1],"atan2"))
def _m_sinh(args):  return _math.sinh(_require_number(args[0], "sinh"))
def _m_cosh(args):  return _math.cosh(_require_number(args[0], "cosh"))
def _m_tanh(args):  return _math.tanh(_require_number(args[0], "tanh"))

def _m_deg(args):   return _math.degrees(_require_number(args[0], "deg"))
def _m_rad(args):   return _math.radians(_require_number(args[0], "rad"))

# Exponential / log
def _m_exp(args):   return _math.exp(_require_number(args[0], "exp"))
def _m_log(args):
    x = _require_number(args[0], "log")
    if len(args) > 1:
        b = _require_number(args[1], "log")
        return _math.log(x, b)
    return _math.log(x)
def _m_log2(args):  return _math.log2 (_require_number(args[0], "log2"))
def _m_log10(args): return _math.log10(_require_number(args[0], "log10"))

# Combinatorics
def _m_factorial(args):
    n = int(_require_number(args[0], "factorial"))
    if n < 0: raise RuntimeError("factorial() requires a non-negative integer")
    return _math.factorial(n)
def _m_gcd(args):
    return _math.gcd(int(_require_number(args[0],"gcd")),
                     int(_require_number(args[1],"gcd")))
def _m_lcm(args):
    a = int(_require_number(args[0],"lcm"))
    b = int(_require_number(args[1],"lcm"))
    return abs(a*b) // _math.gcd(a,b) if a and b else 0
def _m_comb(args):
    n = int(_require_number(args[0],"comb"))
    k = int(_require_number(args[1],"comb"))
    return _math.comb(n, k)
def _m_perm(args):
    n = int(_require_number(args[0],"perm"))
    k = int(_require_number(args[1],"perm"))
    return _math.perm(n, k)

# Random
def _m_random(args):  return _random.random()
def _m_rand_int(args):
    a = int(_require_number(args[0],"rand_int"))
    b = int(_require_number(args[1],"rand_int"))
    return _random.randint(a, b)
def _m_rand_seed(args):
    _random.seed(int(_require_number(args[0],"rand_seed")))
    return None

# Quadratic solver: quadratic(a, b, c) → array of roots (complex if needed)
def _m_quadratic(args):
    from interpreter import MylangArray
    a = _require_number(args[0],"quadratic")
    b = _require_number(args[1],"quadratic")
    c = _require_number(args[2],"quadratic")
    if a == 0: raise RuntimeError("quadratic(): coefficient 'a' cannot be 0")
    disc = b*b - 4*a*c
    if disc >= 0:
        r1 = (-b + _math.sqrt(disc)) / (2*a)
        r2 = (-b - _math.sqrt(disc)) / (2*a)
        return MylangArray([r1, r2])
    else:
        real_part = -b / (2*a)
        imag_part =  _math.sqrt(-disc) / (2*a)
        return MylangArray([
            MylangComplex(real_part,  imag_part),
            MylangComplex(real_part, -imag_part),
        ])

MATH_FUNCTIONS = {
    # Roots & powers
    "sqrt": (1, _m_sqrt), "cbrt": (1, _m_cbrt), "pow": (2, _m_pow),
    # Rounding
    "abs": (1, _m_abs), "floor": (1, _m_floor), "ceil": (1, _m_ceil),
    "round": (None, _m_round), "sign": (1, _m_sign), "clamp": (3, _m_clamp),
    # Trig
    "sin": (1,_m_sin), "cos": (1,_m_cos), "tan": (1,_m_tan),
    "asin":(1,_m_asin),"acos":(1,_m_acos),"atan":(1,_m_atan),
    "atan2":(2,_m_atan2),
    "sinh":(1,_m_sinh),"cosh":(1,_m_cosh),"tanh":(1,_m_tanh),
    "deg": (1,_m_deg), "rad": (1,_m_rad),
    # Exp / log
    "exp":(1,_m_exp), "log":(None,_m_log), "log2":(1,_m_log2), "log10":(1,_m_log10),
    # Combinatorics
    "factorial":(1,_m_factorial), "gcd":(2,_m_gcd), "lcm":(2,_m_lcm),
    "comb":(2,_m_comb), "perm":(2,_m_perm),
    # Random
    "random":(0,_m_random), "rand_int":(2,_m_rand_int), "rand_seed":(1,_m_rand_seed),
    # Algebra
    "quadratic":(3,_m_quadratic),
}

MATH_CONSTANTS = {
    "PI":  _math.pi,
    "E":   _math.e,
    "TAU": _math.tau,
    "INF": _math.inf,
    "NAN": float("nan"),
    "PHI": (1 + _math.sqrt(5)) / 2,   # golden ratio
}


# ══════════════════════════════════════════════════════════════════════════════
# ── STATS namespace ───────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

def _s_mean(args):
    return _stats.mean(_require_array(args[0], "mean"))
def _s_median(args):
    return _stats.median(_require_array(args[0], "median"))
def _s_mode(args):
    from interpreter import MylangArray
    data = _require_array(args[0], "mode")
    try:
        m = _stats.multimode(data)
        return MylangArray(m)
    except Exception:
        return MylangArray([_stats.mode(data)])
def _s_stdev(args):
    data = _require_array(args[0], "stdev")
    if len(data) < 2: raise RuntimeError("stdev() requires at least 2 values")
    return _stats.stdev(data)
def _s_pstdev(args):
    return _stats.pstdev(_require_array(args[0], "pstdev"))
def _s_variance(args):
    data = _require_array(args[0], "variance")
    if len(data) < 2: raise RuntimeError("variance() requires at least 2 values")
    return _stats.variance(data)
def _s_pvariance(args):
    return _stats.pvariance(_require_array(args[0], "pvariance"))
def _s_min(args):
    return min(_require_array(args[0], "min"))
def _s_max(args):
    return max(_require_array(args[0], "max"))
def _s_sum(args):
    return sum(_require_array(args[0], "sum"))
def _s_range_stat(args):
    data = _require_array(args[0], "range_stat")
    return max(data) - min(data)
def _s_percentile(args):
    data  = sorted(_require_array(args[0], "percentile"))
    p     = _require_number(args[1], "percentile") / 100
    idx   = p * (len(data) - 1)
    lo, hi = int(idx), min(int(idx) + 1, len(data) - 1)
    return data[lo] + (data[hi] - data[lo]) * (idx - lo)
def _s_quartiles(args):
    from interpreter import MylangArray
    data = sorted(_require_array(args[0], "quartiles"))
    q1 = _s_percentile([data.__class__(data), 25])   # reuse
    q2 = _stats.median(data)
    q3 = _s_percentile([data.__class__(data), 75])
    return MylangArray([q1, q2, q3])

def _s_quartiles(args):
    from interpreter import MylangArray
    data = sorted(_require_array(args[0], "quartiles"))
    n = len(data)
    def _perc(d, p):
        idx = p / 100 * (len(d) - 1)
        lo, hi = int(idx), min(int(idx)+1, len(d)-1)
        return d[lo] + (d[hi] - d[lo]) * (idx - lo)
    return MylangArray([_perc(data,25), _perc(data,50), _perc(data,75)])

def _s_correlation(args):
    xs = _require_array(args[0], "correlation")
    ys = _require_array(args[1], "correlation")
    if len(xs) != len(ys): raise RuntimeError("correlation() arrays must be same length")
    n = len(xs)
    if n < 2: raise RuntimeError("correlation() requires at least 2 pairs")
    mx, my = sum(xs)/n, sum(ys)/n
    num  = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    den  = (_math.sqrt(sum((x-mx)**2 for x in xs)) *
            _math.sqrt(sum((y-my)**2 for y in ys)))
    if den == 0: raise RuntimeError("correlation(): zero variance in one array")
    return num / den

def _s_covariance(args):
    xs = _require_array(args[0], "covariance")
    ys = _require_array(args[1], "covariance")
    if len(xs) != len(ys): raise RuntimeError("covariance() arrays must be same length")
    n = len(xs)
    if n < 2: raise RuntimeError("covariance() requires at least 2 pairs")
    mx, my = sum(xs)/n, sum(ys)/n
    return sum((x-mx)*(y-my) for x,y in zip(xs,ys)) / (n-1)

def _s_linreg(args):
    """Linear regression: linreg(xs, ys) → {slope, intercept, r2}"""
    from interpreter import MylangArray, MylangHash
    xs = _require_array(args[0], "linreg")
    ys = _require_array(args[1], "linreg")
    n  = len(xs)
    if n < 2: raise RuntimeError("linreg() requires at least 2 data points")
    mx, my = sum(xs)/n, sum(ys)/n
    ssxx = sum((x-mx)**2 for x in xs)
    ssxy = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    if ssxx == 0: raise RuntimeError("linreg(): no variance in x array")
    slope = ssxy / ssxx
    intercept = my - slope * mx
    ss_res = sum((y - (slope*x + intercept))**2 for x,y in zip(xs,ys))
    ss_tot = sum((y - my)**2 for y in ys)
    r2 = 1 - ss_res/ss_tot if ss_tot != 0 else 1.0
    return MylangHash({"slope": slope, "intercept": intercept, "r2": r2})

def _s_normalize(args):
    from interpreter import MylangArray
    data = _require_array(args[0], "normalize")
    mn, mx = min(data), max(data)
    span = mx - mn
    if span == 0: raise RuntimeError("normalize(): all values are equal")
    return MylangArray([(x-mn)/span for x in data])

def _s_zscore(args):
    from interpreter import MylangArray
    data = _require_array(args[0], "zscore")
    if len(data) < 2: raise RuntimeError("zscore() requires at least 2 values")
    mu  = _stats.mean(data)
    sd  = _stats.stdev(data)
    if sd == 0: raise RuntimeError("zscore(): standard deviation is zero")
    return MylangArray([(x-mu)/sd for x in data])

def _s_histogram(args):
    """histogram(data, bins) → {edges, counts}"""
    from interpreter import MylangArray, MylangHash
    data = _require_array(args[0], "histogram")
    bins = int(_require_number(args[1], "histogram")) if len(args) > 1 else 10
    mn, mx = min(data), max(data)
    width = (mx - mn) / bins
    edges  = [mn + i*width for i in range(bins+1)]
    counts = [0]*bins
    for x in data:
        i = min(int((x-mn)/width), bins-1)
        counts[i] += 1
    return MylangHash({"edges": MylangArray(edges), "counts": MylangArray(counts)})

def _s_normal_pdf(args):
    x  = _require_number(args[0], "normal_pdf")
    mu = _require_number(args[1], "normal_pdf") if len(args)>1 else 0.0
    sd = _require_number(args[2], "normal_pdf") if len(args)>2 else 1.0
    return (1/(_math.sqrt(2*_math.pi)*sd)) * _math.exp(-0.5*((x-mu)/sd)**2)

def _s_normal_cdf(args):
    x  = _require_number(args[0], "normal_cdf")
    mu = _require_number(args[1], "normal_cdf") if len(args)>1 else 0.0
    sd = _require_number(args[2], "normal_cdf") if len(args)>2 else 1.0
    return 0.5 * (1 + _math.erf((x-mu) / (sd*_math.sqrt(2))))

STATS_FUNCTIONS = {
    "mean":(1,_s_mean), "median":(1,_s_median), "mode":(1,_s_mode),
    "stdev":(1,_s_stdev), "pstdev":(1,_s_pstdev),
    "variance":(1,_s_variance), "pvariance":(1,_s_pvariance),
    "min":(1,_s_min), "max":(1,_s_max), "sum":(1,_s_sum),
    "data_range":(1,_s_range_stat),
    "percentile":(2,_s_percentile), "quartiles":(1,_s_quartiles),
    "correlation":(2,_s_correlation), "covariance":(2,_s_covariance),
    "linreg":(2,_s_linreg),
    "normalize":(1,_s_normalize), "zscore":(1,_s_zscore),
    "histogram":(None,_s_histogram),
    "normal_pdf":(None,_s_normal_pdf), "normal_cdf":(None,_s_normal_cdf),
}


# ══════════════════════════════════════════════════════════════════════════════
# ── EE (Electrical Engineering) namespace ─────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

# ── Ohm's law ─────────────────────────────────────────────────────────────────

def _ee_voltage(args):
    """voltage(i, r) → V = IR"""
    return _require_number(args[0],"voltage") * _require_number(args[1],"voltage")

def _ee_current(args):
    """current(v, r) → I = V/R"""
    v = _require_number(args[0],"current")
    r = _require_number(args[1],"current")
    if r == 0: raise RuntimeError("current(): resistance cannot be zero")
    return v / r

def _ee_resistance(args):
    """resistance(v, i) → R = V/I"""
    v = _require_number(args[0],"resistance")
    i = _require_number(args[1],"resistance")
    if i == 0: raise RuntimeError("resistance(): current cannot be zero")
    return v / i

def _ee_power(args):
    """power(v, i) → P = VI  (or power(i, r) if you pass 2 numbers, use power_r)"""
    return _require_number(args[0],"power") * _require_number(args[1],"power")

def _ee_power_r(args):
    """power_r(i, r) → P = I²R"""
    i = _require_number(args[0],"power_r")
    r = _require_number(args[1],"power_r")
    return i*i*r

def _ee_power_v(args):
    """power_v(v, r) → P = V²/R"""
    v = _require_number(args[0],"power_v")
    r = _require_number(args[1],"power_v")
    if r == 0: raise RuntimeError("power_v(): resistance cannot be zero")
    return v*v/r

# ── Resistor networks ─────────────────────────────────────────────────────────

def _ee_series(args):
    """series(arr) → sum of resistances"""
    return sum(_require_array(args[0], "series"))

def _ee_parallel(args):
    """parallel(arr) → 1 / Σ(1/Rᵢ)"""
    resistances = _require_array(args[0], "parallel")
    if any(r == 0 for r in resistances):
        raise RuntimeError("parallel(): a resistance of 0 short-circuits the network")
    return 1 / sum(1/r for r in resistances)

# ── Capacitors / inductors ────────────────────────────────────────────────────

def _ee_cap_series(args):
    """cap_series(arr) → 1/Σ(1/Cᵢ)"""
    caps = _require_array(args[0], "cap_series")
    return 1 / sum(1/c for c in caps)

def _ee_cap_parallel(args):
    """cap_parallel(arr) → ΣCᵢ"""
    return sum(_require_array(args[0], "cap_parallel"))

def _ee_ind_series(args):
    """ind_series(arr) → ΣLᵢ"""
    return sum(_require_array(args[0], "ind_series"))

def _ee_ind_parallel(args):
    """ind_parallel(arr) → 1/Σ(1/Lᵢ)"""
    inds = _require_array(args[0], "ind_parallel")
    return 1 / sum(1/l for l in inds)

# ── Reactance / impedance ─────────────────────────────────────────────────────

def _ee_xc(args):
    """xc(f, c) → Xc = 1/(2πfC)  — capacitive reactance (Ω)"""
    f = _require_number(args[0],"xc")
    c = _require_number(args[1],"xc")
    if f == 0 or c == 0: raise RuntimeError("xc(): frequency and capacitance must be non-zero")
    return 1 / (2*_math.pi*f*c)

def _ee_xl(args):
    """xl(f, l) → Xl = 2πfL  — inductive reactance (Ω)"""
    f = _require_number(args[0],"xl")
    l = _require_number(args[1],"xl")
    return 2*_math.pi*f*l

def _ee_impedance_rc(args):
    """impedance_rc(r, f, c) → Z = R - jXc  as MylangComplex"""
    r = _require_number(args[0],"impedance_rc")
    f = _require_number(args[1],"impedance_rc")
    c = _require_number(args[2],"impedance_rc")
    xc = 1/(2*_math.pi*f*c)
    return MylangComplex(r, -xc)

def _ee_impedance_rl(args):
    """impedance_rl(r, f, l) → Z = R + jXl  as MylangComplex"""
    r = _require_number(args[0],"impedance_rl")
    f = _require_number(args[1],"impedance_rl")
    l = _require_number(args[2],"impedance_rl")
    xl = 2*_math.pi*f*l
    return MylangComplex(r, xl)

def _ee_impedance_rlc(args):
    """impedance_rlc(r, f, l, c) → Z = R + j(Xl-Xc)"""
    r = _require_number(args[0],"impedance_rlc")
    f = _require_number(args[1],"impedance_rlc")
    l = _require_number(args[2],"impedance_rlc")
    c = _require_number(args[3],"impedance_rlc")
    xl = 2*_math.pi*f*l
    xc = 1/(2*_math.pi*f*c)
    return MylangComplex(r, xl-xc)

# ── Resonance ─────────────────────────────────────────────────────────────────

def _ee_resonant_freq(args):
    """resonant_freq(l, c) → f₀ = 1/(2π√(LC))"""
    l = _require_number(args[0],"resonant_freq")
    c = _require_number(args[1],"resonant_freq")
    return 1/(2*_math.pi*_math.sqrt(l*c))

def _ee_q_factor(args):
    """q_factor(f0, bw) → Q = f₀/BW"""
    f0 = _require_number(args[0],"q_factor")
    bw = _require_number(args[1],"q_factor")
    if bw == 0: raise RuntimeError("q_factor(): bandwidth cannot be zero")
    return f0/bw

def _ee_bandwidth(args):
    """bandwidth(f0, q) → BW = f₀/Q"""
    f0 = _require_number(args[0],"bandwidth")
    q  = _require_number(args[1],"bandwidth")
    if q == 0: raise RuntimeError("bandwidth(): Q cannot be zero")
    return f0/q

# ── RC/RL time constants ──────────────────────────────────────────────────────

def _ee_rc_tau(args):
    """rc_tau(r, c) → τ = RC"""
    return _require_number(args[0],"rc_tau") * _require_number(args[1],"rc_tau")

def _ee_rl_tau(args):
    """rl_tau(l, r) → τ = L/R"""
    l = _require_number(args[0],"rl_tau")
    r = _require_number(args[1],"rl_tau")
    if r == 0: raise RuntimeError("rl_tau(): resistance cannot be zero")
    return l/r

def _ee_rc_charge(args):
    """rc_charge(v0, t, r, c) → V(t) = V₀(1−e^(−t/RC))"""
    v0 = _require_number(args[0],"rc_charge")
    t  = _require_number(args[1],"rc_charge")
    r  = _require_number(args[2],"rc_charge")
    c  = _require_number(args[3],"rc_charge")
    tau = r*c
    if tau == 0: raise RuntimeError("rc_charge(): RC cannot be zero")
    return v0 * (1 - _math.exp(-t/tau))

def _ee_rc_discharge(args):
    """rc_discharge(v0, t, r, c) → V(t) = V₀e^(−t/RC)"""
    v0 = _require_number(args[0],"rc_discharge")
    t  = _require_number(args[1],"rc_discharge")
    r  = _require_number(args[2],"rc_discharge")
    c  = _require_number(args[3],"rc_discharge")
    tau = r*c
    if tau == 0: raise RuntimeError("rc_discharge(): RC cannot be zero")
    return v0 * _math.exp(-t/tau)

# ── dB / signal ───────────────────────────────────────────────────────────────

def _ee_to_db(args):
    """to_db(ratio) → 20·log₁₀(ratio)   [voltage/amplitude ratio]"""
    r = _require_number(args[0],"to_db")
    if r <= 0: raise RuntimeError("to_db(): ratio must be positive")
    return 20*_math.log10(r)

def _ee_to_db_power(args):
    """to_db_power(ratio) → 10·log₁₀(ratio)  [power ratio]"""
    r = _require_number(args[0],"to_db_power")
    if r <= 0: raise RuntimeError("to_db_power(): ratio must be positive")
    return 10*_math.log10(r)

def _ee_from_db(args):
    """from_db(db) → 10^(dB/20)"""
    return 10**(_require_number(args[0],"from_db")/20)

def _ee_from_db_power(args):
    """from_db_power(db) → 10^(dB/10)"""
    return 10**(_require_number(args[0],"from_db_power")/10)

def _ee_vrms(args):
    """vrms(vpeak) → Vpeak / √2   (sinusoidal)"""
    return _require_number(args[0],"vrms") / _math.sqrt(2)

def _ee_vpeak(args):
    """vpeak(vrms) → Vrms · √2"""
    return _require_number(args[0],"vpeak") * _math.sqrt(2)

# ── Complex / phasor helpers ──────────────────────────────────────────────────

def _ee_phasor(args):
    """phasor(mag, angle_deg) → MylangComplex in rectangular form"""
    mag   = _require_number(args[0],"phasor")
    angle = _math.radians(_require_number(args[1],"phasor"))
    return MylangComplex(mag*_math.cos(angle), mag*_math.sin(angle))

def _ee_phasor_mag(args):
    """phasor_mag(complex) → magnitude"""
    z = _require_complex(args[0],"phasor_mag")
    return abs(z)

def _ee_phasor_angle(args):
    """phasor_angle(complex) → angle in degrees"""
    z = _require_complex(args[0],"phasor_angle")
    return _math.degrees(_cmath.phase(z))

def _ee_complex_add(args):
    a = _require_complex(args[0],"complex_add")
    b = _require_complex(args[1],"complex_add")
    r = a+b; return MylangComplex(r.real, r.imag)

def _ee_complex_mul(args):
    a = _require_complex(args[0],"complex_mul")
    b = _require_complex(args[1],"complex_mul")
    r = a*b; return MylangComplex(r.real, r.imag)

def _ee_complex_div(args):
    a = _require_complex(args[0],"complex_div")
    b = _require_complex(args[1],"complex_div")
    if b == 0: raise RuntimeError("complex_div(): division by zero")
    r = a/b; return MylangComplex(r.real, r.imag)

def _ee_complex_conj(args):
    z = _require_complex(args[0],"complex_conj")
    return MylangComplex(z.real, -z.imag)

# ── Voltage divider / current divider ────────────────────────────────────────

def _ee_voltage_divider(args):
    """voltage_divider(vin, r1, r2) → Vout = Vin · R2/(R1+R2)"""
    vin = _require_number(args[0],"voltage_divider")
    r1  = _require_number(args[1],"voltage_divider")
    r2  = _require_number(args[2],"voltage_divider")
    if r1+r2 == 0: raise RuntimeError("voltage_divider(): total resistance is zero")
    return vin * r2 / (r1+r2)

def _ee_current_divider(args):
    """current_divider(iin, r1, r2) → I1 = Iin · R2/(R1+R2)"""
    iin = _require_number(args[0],"current_divider")
    r1  = _require_number(args[1],"current_divider")
    r2  = _require_number(args[2],"current_divider")
    if r1+r2 == 0: raise RuntimeError("current_divider(): total resistance is zero")
    return iin * r2 / (r1+r2)

# ── Thevenin / Norton equivalents ─────────────────────────────────────────────

def _ee_thevenin(args):
    """thevenin(voc, isc) → {vth, rth}  — Vth=Voc, Rth=Voc/Isc"""
    from interpreter import MylangHash
    voc = _require_number(args[0],"thevenin")
    isc = _require_number(args[1],"thevenin")
    if isc == 0: raise RuntimeError("thevenin(): short-circuit current cannot be zero")
    return MylangHash({"vth": voc, "rth": voc/isc})

def _ee_norton(args):
    """norton(voc, isc) → {in_, rn}  — IN=Isc, RN=Voc/Isc"""
    from interpreter import MylangHash
    voc = _require_number(args[0],"norton")
    isc = _require_number(args[1],"norton")
    if isc == 0: raise RuntimeError("norton(): short-circuit current cannot be zero")
    return MylangHash({"in_": isc, "rn": voc/isc})

# ── Energy & charge ───────────────────────────────────────────────────────────

def _ee_energy_cap(args):
    """energy_cap(c, v) → E = ½CV²"""
    c = _require_number(args[0],"energy_cap")
    v = _require_number(args[1],"energy_cap")
    return 0.5*c*v*v

def _ee_energy_ind(args):
    """energy_ind(l, i) → E = ½LI²"""
    l = _require_number(args[0],"energy_ind")
    i = _require_number(args[1],"energy_ind")
    return 0.5*l*i*i

def _ee_charge(args):
    """charge(c, v) → Q = CV"""
    return _require_number(args[0],"charge") * _require_number(args[1],"charge")

EE_FUNCTIONS = {
    # Ohm's law
    "voltage":(2,_ee_voltage), "current":(2,_ee_current),
    "resistance":(2,_ee_resistance),
    "power":(2,_ee_power), "power_r":(2,_ee_power_r), "power_v":(2,_ee_power_v),
    # Networks
    "series":(1,_ee_series), "parallel":(1,_ee_parallel),
    "cap_series":(1,_ee_cap_series), "cap_parallel":(1,_ee_cap_parallel),
    "ind_series":(1,_ee_ind_series), "ind_parallel":(1,_ee_ind_parallel),
    # Reactance
    "xc":(2,_ee_xc), "xl":(2,_ee_xl),
    "impedance_rc":(3,_ee_impedance_rc),
    "impedance_rl":(3,_ee_impedance_rl),
    "impedance_rlc":(4,_ee_impedance_rlc),
    # Resonance
    "resonant_freq":(2,_ee_resonant_freq),
    "q_factor":(2,_ee_q_factor), "bandwidth":(2,_ee_bandwidth),
    # Time constants
    "rc_tau":(2,_ee_rc_tau), "rl_tau":(2,_ee_rl_tau),
    "rc_charge":(4,_ee_rc_charge), "rc_discharge":(4,_ee_rc_discharge),
    # dB / signal
    "to_db":(1,_ee_to_db), "to_db_power":(1,_ee_to_db_power),
    "from_db":(1,_ee_from_db), "from_db_power":(1,_ee_from_db_power),
    "vrms":(1,_ee_vrms), "vpeak":(1,_ee_vpeak),
    # Complex / phasor
    "phasor":(2,_ee_phasor),
    "phasor_mag":(1,_ee_phasor_mag), "phasor_angle":(1,_ee_phasor_angle),
    "complex_add":(2,_ee_complex_add), "complex_mul":(2,_ee_complex_mul),
    "complex_div":(2,_ee_complex_div), "complex_conj":(1,_ee_complex_conj),
    # Dividers
    "voltage_divider":(3,_ee_voltage_divider),
    "current_divider":(3,_ee_current_divider),
    # Thevenin / Norton
    "thevenin":(2,_ee_thevenin), "norton":(2,_ee_norton),
    # Energy
    "energy_cap":(2,_ee_energy_cap), "energy_ind":(2,_ee_energy_ind),
    "charge":(2,_ee_charge),
}

EE_CONSTANTS = {
    "EPSILON0": 8.854187817e-12,   # F/m  permittivity of free space
    "MU0":      1.2566370614e-6,   # H/m  permeability of free space
    "C_LIGHT":  299_792_458.0,     # m/s
    "PLANCK":   6.62607015e-34,    # J·s
    "BOLTZMANN":1.380649e-23,      # J/K
    "ELECTRON": 1.602176634e-19,   # C   elementary charge
}


# ══════════════════════════════════════════════════════════════════════════════
# ── Matrix functions ──────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

def _mat_make(args):
    from interpreter import MylangArray
    v = args[0]
    if isinstance(v, MylangArray):
        rows = []
        for row in v.elements:
            if isinstance(row, MylangArray):
                rows.append([float(x) for x in row.elements])
            else:
                raise RuntimeError("matrix(): each element must be an array (row)")
        return MylangMatrix(rows)
    raise RuntimeError("matrix(): expects an array of arrays")

def _mat_zeros(args):
    r = int(_require_number(args[0],"mat_zeros"))
    c = int(_require_number(args[1],"mat_zeros"))
    return MylangMatrix([[0.0]*c for _ in range(r)])

def _mat_identity(args):
    n = int(_require_number(args[0],"mat_identity"))
    return MylangMatrix([[1.0 if i==j else 0.0 for j in range(n)] for i in range(n)])

def _mat_add(args):
    a = _require_matrix(args[0],"mat_add")
    b = _require_matrix(args[1],"mat_add")
    if a.nrows!=b.nrows or a.ncols!=b.ncols:
        raise RuntimeError("mat_add(): matrices must have the same dimensions")
    return MylangMatrix([[a.rows[i][j]+b.rows[i][j]
                          for j in range(a.ncols)] for i in range(a.nrows)])

def _mat_sub(args):
    a = _require_matrix(args[0],"mat_sub")
    b = _require_matrix(args[1],"mat_sub")
    if a.nrows!=b.nrows or a.ncols!=b.ncols:
        raise RuntimeError("mat_sub(): matrices must have the same dimensions")
    return MylangMatrix([[a.rows[i][j]-b.rows[i][j]
                          for j in range(a.ncols)] for i in range(a.nrows)])

def _mat_mul(args):
    a = _require_matrix(args[0],"mat_mul")
    b = _require_matrix(args[1],"mat_mul")
    if a.ncols != b.nrows:
        raise RuntimeError(f"mat_mul(): incompatible dimensions {a.nrows}×{a.ncols} · {b.nrows}×{b.ncols}")
    result = [[sum(a.rows[i][k]*b.rows[k][j] for k in range(a.ncols))
               for j in range(b.ncols)] for i in range(a.nrows)]
    return MylangMatrix(result)

def _mat_scale(args):
    m = _require_matrix(args[0],"mat_scale")
    s = _require_number(args[1],"mat_scale")
    return MylangMatrix([[v*s for v in row] for row in m.rows])

def _mat_transpose(args):
    m = _require_matrix(args[0],"mat_transpose")
    return MylangMatrix([[m.rows[i][j] for i in range(m.nrows)]
                         for j in range(m.ncols)])

def _mat_det(args):
    """Determinant (up to 4×4 via cofactor expansion)."""
    m = _require_matrix(args[0],"mat_det")
    if m.nrows != m.ncols:
        raise RuntimeError("mat_det(): matrix must be square")
    return _det(m.rows)

def _det(rows):
    n = len(rows)
    if n == 1: return rows[0][0]
    if n == 2: return rows[0][0]*rows[1][1] - rows[0][1]*rows[1][0]
    total = 0
    for c in range(n):
        minor = [rows[r][:c]+rows[r][c+1:] for r in range(1,n)]
        total += ((-1)**c) * rows[0][c] * _det(minor)
    return total

def _mat_trace(args):
    m = _require_matrix(args[0],"mat_trace")
    if m.nrows != m.ncols:
        raise RuntimeError("mat_trace(): matrix must be square")
    return sum(m.rows[i][i] for i in range(m.nrows))

def _mat_get(args):
    m = _require_matrix(args[0],"mat_get")
    r = int(_require_number(args[1],"mat_get"))
    c = int(_require_number(args[2],"mat_get"))
    return m.rows[r][c]

def _mat_set(args):
    m = _require_matrix(args[0],"mat_set")
    r = int(_require_number(args[1],"mat_set"))
    c = int(_require_number(args[2],"mat_set"))
    v = _require_number(args[3],"mat_set")
    m.rows[r][c] = v
    return m

def _mat_shape(args):
    from interpreter import MylangHash
    m = _require_matrix(args[0],"mat_shape")
    return MylangHash({"rows": m.nrows, "cols": m.ncols})

def _mat_to_array(args):
    from interpreter import MylangArray
    m = _require_matrix(args[0],"mat_to_array")
    return MylangArray([MylangArray(list(row)) for row in m.rows])

MATRIX_FUNCTIONS = {
    "matrix":       (1, _mat_make),
    "mat_zeros":    (2, _mat_zeros),
    "mat_identity": (1, _mat_identity),
    "mat_add":      (2, _mat_add),
    "mat_sub":      (2, _mat_sub),
    "mat_mul":      (2, _mat_mul),
    "mat_scale":    (2, _mat_scale),
    "mat_transpose":(1, _mat_transpose),
    "mat_det":      (1, _mat_det),
    "mat_trace":    (1, _mat_trace),
    "mat_get":      (3, _mat_get),
    "mat_set":      (4, _mat_set),
    "mat_shape":    (1, _mat_shape),
    "mat_to_array": (1, _mat_to_array),
}


# ══════════════════════════════════════════════════════════════════════════════
# ── Complex number constructor ────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

def _make_complex(args):
    r = _require_number(args[0],"complex") if args else 0.0
    i = _require_number(args[1],"complex") if len(args)>1 else 0.0
    return MylangComplex(r, i)

def _complex_real(args):
    v = args[0]
    if isinstance(v, MylangComplex): return v.real
    return _require_number(v, "real")

def _complex_imag(args):
    v = args[0]
    if isinstance(v, MylangComplex): return v.imag
    return 0.0

def _complex_abs(args):
    v = args[0]
    if isinstance(v, MylangComplex): return abs(v.value)
    return abs(_require_number(v,"complex_abs"))

COMPLEX_FUNCTIONS = {
    "complex":     (None, _make_complex),
    "real":        (1,    _complex_real),
    "imag":        (1,    _complex_imag),
    "complex_abs": (1,    _complex_abs),
}


# ══════════════════════════════════════════════════════════════════════════════
# ── Namespace object (math.sin, stats.mean, ee.voltage, …) ───────────────────
# ══════════════════════════════════════════════════════════════════════════════

class MylangNamespace:
    """
    Appears in mylang as a hash-like object but dispatches .method() calls
    to Python functions.  Registered in the global env as e.g. `math`.
    """
    def __init__(self, name: str, functions: dict, constants: dict = None):
        self.name      = name
        self.functions = functions          # name → (arity, fn)
        self.constants = constants or {}

    def __repr__(self):
        return f"<namespace {self.name}>"

    def call(self, method: str, args: list):
        if method in self.constants:
            raise RuntimeError(
                f"{self.name}.{method} is a constant, not a function — use {self.name}.{method} directly")
        if method not in self.functions:
            raise RuntimeError(
                f"'{self.name}' has no function '{method}'")
        arity, fn = self.functions[method]
        if arity is not None and len(args) != arity:
            raise RuntimeError(
                f"{self.name}.{method}() expects {arity} arg(s) — got {len(args)}")
        return fn(args)

    def get_constant(self, name: str):
        if name in self.constants:
            return self.constants[name]
        raise RuntimeError(f"'{self.name}' has no constant '{name}'")


# ══════════════════════════════════════════════════════════════════════════════
# ── CRYPTO namespace ──────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

# In-process secure vault (process-lifetime, memory-only)
_SECURE_VAULT: dict[str, bytes] = {}
_VAULT_KEY = _os.urandom(32)   # ephemeral session key


def _xor_cipher(data: bytes, key: bytes) -> bytes:
    """Simple XOR cipher for the in-memory vault (not for network use)."""
    key_len = len(key)
    return bytes(data[i] ^ key[i % key_len] for i in range(len(data)))


def _crypto_sha256(args) -> str:
    text = args[0]
    if not isinstance(text, str):
        raise RuntimeError("sha256() requires a string")
    return _hashlib.sha256(text.encode()).hexdigest()


def _crypto_hmac(args) -> str:
    msg, key = args
    if not isinstance(msg, str) or not isinstance(key, str):
        raise RuntimeError("hmac() requires two strings (msg, key)")
    return _hmac.new(key.encode(), msg.encode(), _hashlib.sha256).hexdigest()


def _crypto_pbkdf2(args) -> str:
    password, salt = args[0], args[1]
    iterations = int(args[2]) if len(args) > 2 else 100_000
    if not isinstance(password, str) or not isinstance(salt, str):
        raise RuntimeError("pbkdf2() requires string arguments")
    dk = _hashlib.pbkdf2_hmac("sha256", password.encode(),
                               salt.encode(), iterations)
    return dk.hex()


def _crypto_encrypt_aes(args) -> str:
    """XOR-based symmetric encryption stored as hex (AES-equivalent interface)."""
    cleartext, key = args
    if not isinstance(cleartext, str) or not isinstance(key, str):
        raise RuntimeError("encrypt_aes() requires string arguments")
    key_bytes  = _hashlib.sha256(key.encode()).digest()
    encrypted  = _xor_cipher(cleartext.encode("utf-8"), key_bytes)
    return encrypted.hex()


def _crypto_decrypt_aes(args) -> str:
    hexstream, key = args
    if not isinstance(hexstream, str) or not isinstance(key, str):
        raise RuntimeError("decrypt_aes() requires string arguments")
    key_bytes  = _hashlib.sha256(key.encode()).digest()
    decrypted  = _xor_cipher(bytes.fromhex(hexstream), key_bytes)
    return decrypted.decode("utf-8")


def _crypto_secure_store(args):
    label, secret = args
    if not isinstance(label, str) or not isinstance(secret, str):
        raise RuntimeError("secure_store() requires string arguments")
    encrypted = _xor_cipher(secret.encode("utf-8"), _VAULT_KEY)
    _SECURE_VAULT[label] = encrypted
    return None


def _crypto_secure_retrieve(args) -> str:
    label = args[0]
    if not isinstance(label, str):
        raise RuntimeError("secure_retrieve() requires a string label")
    if label not in _SECURE_VAULT:
        raise RuntimeError(f"secure_retrieve(): no entry for '{label}'")
    return _xor_cipher(_SECURE_VAULT[label], _VAULT_KEY).decode("utf-8")


def _crypto_secure_wipe(args):
    label = args[0]
    if not isinstance(label, str):
        raise RuntimeError("secure_wipe() requires a string label")
    if label in _SECURE_VAULT:
        # Overwrite before deleting
        _SECURE_VAULT[label] = bytes(len(_SECURE_VAULT[label]))
        del _SECURE_VAULT[label]
    return None


CRYPTO_FUNCTIONS = {
    "sha256":          (1, _crypto_sha256),
    "hmac":            (2, _crypto_hmac),
    "pbkdf2":          (None, _crypto_pbkdf2),
    "encrypt_aes":     (2, _crypto_encrypt_aes),
    "decrypt_aes":     (2, _crypto_decrypt_aes),
    "secure_store":    (2, _crypto_secure_store),
    "secure_retrieve": (1, _crypto_secure_retrieve),
    "secure_wipe":     (1, _crypto_secure_wipe),
}


# ══════════════════════════════════════════════════════════════════════════════
# ── IMAGE namespace  (SVG canvas — renders in Pacer's Visual Panel) ───────────
# ══════════════════════════════════════════════════════════════════════════════

class _Canvas:
    """In-process SVG canvas accumulator."""
    def __init__(self):
        self.reset()

    def reset(self):
        self.width      = 400
        self.height     = 300
        self.background = "#ffffff"
        self.elements: list[str] = []

    def svg(self) -> str:
        body = "\n  ".join(self.elements)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'width="{self.width}" height="{self.height}" '
                f'style="background:{self.background}">\n  {body}\n</svg>')


_CANVAS = _Canvas()
# Optional hook: Pacer sets this to render into its Graphics panel
# Signature: fn(title: str, svg_text: str) -> None
_IMAGE_SHOW_HOOK = None


def _img_blank(args):
    w   = int(_require_number(args[0], "image.blank"))
    h   = int(_require_number(args[1], "image.blank"))
    bg  = args[2] if len(args) > 2 else "#ffffff"
    if not isinstance(bg, str): bg = "#ffffff"
    _CANVAS.reset()
    _CANVAS.width      = w
    _CANVAS.height     = h
    _CANVAS.background = bg
    return None

def _img_rect(args):
    x, y, w, h = (int(_require_number(a, "image.rect")) for a in args[:4])
    color = str(args[4]) if len(args) > 4 else "#cccccc"
    _CANVAS.elements.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}"/>')
    return None

def _img_circle(args):
    cx, cy, r = (int(_require_number(a, "image.circle")) for a in args[:3])
    color = str(args[3]) if len(args) > 3 else "#cccccc"
    _CANVAS.elements.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}"/>')
    return None

def _img_line(args):
    x1, y1, x2, y2 = (int(_require_number(a, "image.line")) for a in args[:4])
    color = str(args[4]) if len(args) > 4 else "#000000"
    width = int(args[5]) if len(args) > 5 else 1
    _CANVAS.elements.append(
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{color}" stroke-width="{width}"/>')
    return None

def _img_text(args):
    msg  = str(args[0]) if args else ""
    x    = int(_require_number(args[1], "image.text")) if len(args) > 1 else 0
    y    = int(_require_number(args[2], "image.text")) if len(args) > 2 else 0
    size = int(_require_number(args[3], "image.text")) if len(args) > 3 else 12
    fill = str(args[4]) if len(args) > 4 else "#000000"
    safe = (msg.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
               .replace('"','&quot;'))
    _CANVAS.elements.append(
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
        f'font-family="monospace">{safe}</text>')
    return None

def _img_show(args):
    title = str(args[0]) if args else "Canvas"
    svg   = _CANVAS.svg()
    if _IMAGE_SHOW_HOOK:
        _IMAGE_SHOW_HOOK(title, svg)
    else:
        print(f"[image.show] '{title}' — SVG ({_CANVAS.width}×{_CANVAS.height}):")
        print(svg)
    return None

def _img_load(args):
    url   = str(args[0]) if args else ""
    title = str(args[1]) if len(args) > 1 else "Image"
    _CANVAS.reset()
    _CANVAS.elements.append(
        f'<image href="{url}" x="0" y="0" '
        f'width="{_CANVAS.width}" height="{_CANVAS.height}"/>')
    if _IMAGE_SHOW_HOOK:
        _IMAGE_SHOW_HOOK(title, _CANVAS.svg())
    else:
        print(f"[image.load] '{title}' loaded from {url}")
    return None


IMAGE_FUNCTIONS = {
    "blank":  (None, _img_blank),
    "rect":   (None, _img_rect),
    "circle": (None, _img_circle),
    "line":   (None, _img_line),
    "text":   (None, _img_text),
    "show":   (None, _img_show),
    "load":   (None, _img_load),
}


# ══════════════════════════════════════════════════════════════════════════════
# ── CSV namespace ─────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

def _csv_parse(args) -> "MylangArray":
    from interpreter import MylangArray
    text = args[0]
    if not isinstance(text, str):
        raise RuntimeError("csv.parse() requires a string")

    rows = []
    # Simple CSV parser (handles quoted fields, \n or \r\n line endings)
    for raw_line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        fields = []
        buf    = []
        in_q   = False
        for ch in line:
            if ch == '"':
                in_q = not in_q
            elif ch == "," and not in_q:
                cell = "".join(buf).strip()
                # Auto-coerce to number if possible
                try:    fields.append(int(cell))
                except ValueError:
                    try: fields.append(float(cell))
                    except ValueError: fields.append(cell)
                buf = []
            else:
                buf.append(ch)
        cell = "".join(buf).strip()
        try:    fields.append(int(cell))
        except ValueError:
            try: fields.append(float(cell))
            except ValueError: fields.append(cell)
        rows.append(MylangArray(fields))
    return MylangArray(rows)


def _csv_stringify(args) -> str:
    from interpreter import MylangArray
    data = args[0]
    if not isinstance(data, MylangArray):
        raise RuntimeError("csv.stringify() requires an array of arrays")
    lines = []
    for row in data.elements:
        if isinstance(row, MylangArray):
            cells = [_csv_cell(c) for c in row.elements]
        else:
            cells = [_csv_cell(row)]
        lines.append(",".join(cells))
    return "\n".join(lines)


def _csv_cell(v) -> str:
    s = str(v) if not isinstance(v, bool) else ("true" if v else "false")
    if "," in s or '"' in s or "\n" in s:
        return '"' + s.replace('"', '""') + '"'
    return s


CSV_FUNCTIONS = {
    "parse":     (1, _csv_parse),
    "stringify": (1, _csv_stringify),
}


# ══════════════════════════════════════════════════════════════════════════════
# ── register_stdlib(interpreter) ─────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

def register_stdlib(interp):
    """
    Called from Interpreter.__init__.
    Populates globals with:
      - Flat top-level shortcuts (sin, mean, voltage, …)
      - Namespace objects  (math, stats, ee, crypto, image, csv)
      - Constants          (PI, E, …)
      - complex() and matrix() constructors
    """
    from interpreter import BuiltinFunction

    def _reg(name, arity, fn):
        interp.globals.define(name, BuiltinFunction(name, arity, fn))

    # ── Flat shortcuts ────────────────────────────────────────────────────────
    for name, (arity, fn) in MATH_FUNCTIONS.items():
        _reg(name, arity, fn)
    for name, (arity, fn) in STATS_FUNCTIONS.items():
        _reg(name, arity, fn)
    for name, (arity, fn) in EE_FUNCTIONS.items():
        _reg(name, arity, fn)
    for name, (arity, fn) in MATRIX_FUNCTIONS.items():
        _reg(name, arity, fn)
    for name, (arity, fn) in COMPLEX_FUNCTIONS.items():
        _reg(name, arity, fn)

    # ── Constants as plain values ─────────────────────────────────────────────
    for name, val in MATH_CONSTANTS.items():
        interp.globals.define(name, val)
    for name, val in EE_CONSTANTS.items():
        interp.globals.define(name, val)

    # ── Namespace objects ─────────────────────────────────────────────────────
    interp.globals.define("math",   MylangNamespace("math",   MATH_FUNCTIONS,   MATH_CONSTANTS))
    interp.globals.define("stats",  MylangNamespace("stats",  STATS_FUNCTIONS))
    interp.globals.define("ee",     MylangNamespace("ee",     EE_FUNCTIONS,     EE_CONSTANTS))
    interp.globals.define("crypto", MylangNamespace("crypto", CRYPTO_FUNCTIONS))
    interp.globals.define("image",  MylangNamespace("image",  IMAGE_FUNCTIONS))
    interp.globals.define("csv",    MylangNamespace("csv",    CSV_FUNCTIONS))
