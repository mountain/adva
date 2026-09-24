#!/usr/bin/env python3
"""When can one shell's radial density exceed that shell's own electron count?

THE QUESTION
------------
For an atom of nuclear charge Z, let D(r) be the radial density of one shell
(D = 4 pi r^2 rho, so that the integral of D over r is that shell's electron
count).  In the figures of the atomic line the density of some shells visibly
rose above Z itself -- "the probability density exceeds the number of
electrons".  That is legitimate for a density, and it is not a classical
particle count.  But it should have a criterion, and the criterion should be
closed form rather than a scan.

WHAT IS PROVED HERE, AND WHAT IS ONLY MEASURED
----------------------------------------------
PROVED (analytic, this file recomputes it from scratch):

  x = zeta r, with zeta the shell's effective exponent.  The exact hydrogenic
  radial function factors as R_nl(r) = zeta^{3/2} Rt_nl(zeta x), so

      D(r) = zeta * sum_l N_l x^2 Rt_nl(x)^2 =: zeta * shape_{n,occ}(x)

  The shape depends on the occupancy pattern (n, {l: electrons}) and on nothing
  else.  Therefore, with c(n, occ) = max_x shape(x) and x*(n, occ) = argmax,

      D_shell,max = c * zeta            and
      D_shell,max > Z   <=>   zeta / Z > 1 / c.

  The K shell is the check that the construction is not arbitrary: for one 1s
  electron c = 4/e^2 and for two, c = 8/e^2, both exactly, because
  Rt_10(x) = 2 exp(-x) exactly.  c is computed, never fitted.

MEASURED (retained from an external Hartree-Fock run, not recomputed here):

  Per-shell hump positions r* and hump values D_max for H, C, N, O, Si, P, S and
  for Cl, Ar.  These were produced by the workspace's own run of def2-SVP ROHF
  densities (quantum-atom-lab, out/clue4-shell-hump-criterion.json) and are
  carried here as the answers, never as inputs to the prediction.  A pure-Python
  checker cannot re-run quantum chemistry, and this file does not pretend to.

THE TEST THAT CAN FAIL
----------------------
Two channels predict the sign of (D_max - Z) for each measured shell:

  SLATER channel (no fitted parameter): the screening constant from Slater's
    rules on the retained shell occupancies gives zeta_Slater; the criterion
    then predicts the sign.  The prediction uses Z, the shell occupancies and
    the closed-form c table only.  D_max enters nowhere.

  POSITION channel: zeta = x*(pattern) / r*(measured).  This is the hump
    POSITION -- an independent measurement channel from the hump VALUE -- so the
    comparison is not a tautology either.

The third channel, the VALUE channel (zeta back-solved from D_max itself), is
recorded here only to be rejected: zeta_value = D_max / c makes the criterion
identically true, so its agreement carries no information.  The check named
`value_channel_is_information_free` demonstrates that by perturbing c and
showing the comparison still passes for every row.  The first version of this
work used that channel and reported 22 agreements that measured nothing.

WHAT IS NOT CLAIMED
-------------------
  * Not a statement about the true density of any real atom.  It is a statement
    about a one-exponent-per-shell hydrogenic model, compared against a
    finite-basis Hartree-Fock density at the measured hump.
  * The measured rows are retained evidence.  Re-running them requires PySCF,
    which this checker does not use and cannot use.
  * x*(L, 2s2 2p2) is observed to land on 3 + sqrt(3); it is recorded as an
    observation at a stated tolerance, not derived.
  * The two-shell cap says which shells CAN exceed Z in this model.  It does not
    say the excess has any physical consequence.

Run:  python3 experiments/shell_density_hump/calibration.py
Writes evidence.json beside this file.  Standard library only, no subprocess.
"""
from __future__ import annotations

import hashlib
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence.json"

EIGHT_OVER_E2 = 8.0 / math.e ** 2
FOUR_OVER_E2 = 4.0 / math.e ** 2

# Occupancy patterns that occur in this project: (n, {l: electrons}).
PATTERNS = {
    "K (1s1)": (1, {0: 1}),
    "K (1s2)": (1, {0: 2}),
    "L (2s2 2p2)": (2, {0: 2, 1: 2}),
    "L (2s2 2p3)": (2, {0: 2, 1: 3}),
    "L (2s2 2p4)": (2, {0: 2, 1: 4}),
    "L (2s2 2p6)": (2, {0: 2, 1: 6}),
    "M (3s2 3p2)": (3, {0: 2, 1: 2}),
    "M (3s2 3p3)": (3, {0: 2, 1: 3}),
    "M (3s2 3p4)": (3, {0: 2, 1: 4}),
    "M (3s2 3p5)": (3, {0: 2, 1: 5}),
    "M (3s2 3p6)": (3, {0: 2, 1: 6}),
}

# Shells whose normalisation the shape convention rests on.
NORMALISED = [(1, 0), (2, 0), (2, 1), (3, 0), (3, 1)]

# Retained measurements: (atom, Z, shell index, electrons, occupied l set or
# None when the run did not record it, pattern key, r_hump in Bohr, D_max,
# D_max / Z).  Sources: quantum-atom-lab out/clue4-shell-hump-criterion.json
# (`measured_shells` for the seven shipped atoms, `extension_cl_ar` for Cl, Ar).
RETAINED = [
    ("H", 1, 0, 1.0, (0,), "K (1s1)",
     0.9765443740152588, 0.5394541400700736),
    ("C", 6, 0, 2.0, (0,), "K (1s2)",
     0.17609420250231733, 6.030948988008869),
    ("C", 6, 1, 4.0, (0, 1), "L (2s2 2p2)",
     1.2483399767302714, 2.3298730928412565),
    ("N", 7, 0, 2.0, (0,), "K (1s2)",
     0.15004755809421444, 7.098802260446421),
    ("N", 7, 1, 5.0, (0, 1), "L (2s2 2p3)",
     1.0212541544197498, 3.438678368318129),
    ("O", 8, 0, 2.0, (0,), "K (1s2)",
     0.13071614373079887, 8.166730413874657),
    ("O", 8, 1, 6.0, (0, 1), "L (2s2 2p4)",
     0.8599166787759169, 4.69009807017408),
    ("Si", 14, 0, 2.0, (0,), "K (1s2)",
     0.07323364393414056, 14.629810202429404),
    ("Si", 14, 1, 8.0, (0, 1), "L (2s2 2p6)",
     0.4131994707980067, 14.054630682157333),
    ("Si", 14, 2, 4.0, (0, 1), "M (3s2 3p2)",
     1.9563242656278197, 1.817812389293411),
    ("P", 15, 0, 2.0, (0,), "K (1s2)",
     0.06824394149154572, 15.705871519377343),
    ("P", 15, 1, 8.0, (0, 1), "L (2s2 2p6)",
     0.37787459075174423, 15.545129203884683),
    ("P", 15, 2, 5.0, (0, 1), "M (3s2 3p3)",
     1.7210029003246756, 2.6423592541757714),
    ("S", 16, 0, 2.0, (0,), "K (1s2)",
     0.0638894633079875, 16.782609325179752),
    ("S", 16, 1, 8.0, (0, 1), "L (2s2 2p6)",
     0.34813699499718154, 17.030511109101855),
    ("S", 16, 2, 6.0, (0, 1), "M (3s2 3p4)",
     1.5322144708623253, 3.55818484582559),
    ("Cl", 17, 0, 2.0, None, "K (1s2)",
     0.06005669076928059, 17.859810302755896),
    ("Cl", 17, 1, 8.0, None, "L (2s2 2p6)",
     0.32275551029545946, 18.510708015606248),
    ("Cl", 17, 2, 7.0, None, "M (3s2 3p5)",
     1.381673709315506, 4.6203178182014675),
    ("Ar", 18, 0, 2.0, None, "K (1s2)",
     0.05665728549504635, 18.937402223250732),
    ("Ar", 18, 1, 8.0, None, "L (2s2 2p6)",
     0.3008345689948163, 19.987190555515735),
    ("Ar", 18, 2, 8.0, None, "M (3s2 3p6)",
     1.258657093832317, 5.825955413988421),
]

# Retained one-row-per-atom scan of D_max / Z (the value channel of clue 2),
# used only for the onset question.  Source: out/clue2-dmax-vs-z.json.
RETAINED_SCAN = [
    ("H", 1, 0.5394541400700736), ("He", 2, 0.8645041448570908),
    ("Li", 3, 0.9494506979267654), ("Be", 4, 1.0001210443292694),
    ("B", 5, 1.0270022442800113), ("C", 6, 1.0455964528967692),
    ("N", 7, 1.0599057529919156), ("O", 8, 1.0719960422039956),
    ("F", 9, 1.0823365737088557), ("Ne", 10, 1.091565720879356),
    ("Na", 11, 1.105771963410278), ("Mg", 12, 1.1170161208614424),
    ("Al", 13, 1.1270068991112272), ("Si", 14, 1.1359085331631593),
    ("P", 15, 1.1441692915819558), ("S", 16, 1.1525433954293607),
    ("Cl", 17, 1.1601704862158062), ("Ar", 18, 1.1676610414127807),
]

# c values recorded by the numpy/PySCF run of the same construction.  Used only
# as a cross-implementation consistency datum, never as an input.
RECORDED_C = {
    "K (1s1)": 0.5413411329464507, "K (1s2)": 1.0826822658929014,
    "L (2s2 2p2)": 0.7361101254389304, "L (2s2 2p3)": 0.9220408250973215,
    "L (2s2 2p4)": 1.1107306535103036, "L (2s2 2p6)": 1.4927403740178804,
    "M (3s2 3p2)": 0.4017764834475751, "M (3s2 3p3)": 0.5024691542667551,
    "M (3s2 3p4)": 0.6035043809292027, "M (3s2 3p5)": 0.7047433502069396,
    "M (3s2 3p6)": 0.8061130185984939,
}

# D_max / Z exactly as recorded by the source run, used only to check that this
# file transcribed the source correctly.  It is a transcription check, not a
# measurement, and it can fail: a mistyped ratio is caught here.
RECORDED_D_OVER_Z = {
    ("H", 0): 0.5394541400700736, ("C", 0): 1.005158164668145,
    ("C", 1): 0.3883121821402094, ("N", 0): 1.014114608635203,
    ("N", 1): 0.4912397669025898, ("O", 0): 1.020841301734332,
    ("O", 1): 0.58626225877176, ("Si", 0): 1.0449864430306717,
    ("Si", 1): 1.0039021915826667, ("Si", 2): 0.1298437420923865,
    ("P", 0): 1.047058101291823, ("P", 1): 1.0363419469256454,
    ("P", 2): 0.1761572836117181, ("S", 0): 1.0489130828237345,
    ("S", 1): 1.064406944318866, ("S", 2): 0.22238655286409936,
    ("Cl", 0): 1.0505770766326998, ("Cl", 1): 1.088865177388603,
    ("Cl", 2): 0.27178340107067456, ("Ar", 0): 1.0520779012917074,
    ("Ar", 1): 1.1103994753064297, ("Ar", 2): 0.3236641896660234,
}

NORM_TOLERANCE = 1e-9
VALUE_TOLERANCE = 1e-9
CONSISTENCY_TOLERANCE = 1e-7


# --------------------------------------------------------------------------
# The hydrogenic shape, written out rather than borrowed
# --------------------------------------------------------------------------

def laguerre(k: int, alpha: float, x: float) -> float:
    """Generalized Laguerre L_k^{(alpha)}(x) by the standard recurrence.

    L_0 = 1, L_1 = 1 + alpha - x,
    L_{k+1} = ((2k + 1 + alpha - x) L_k - (k + alpha) L_{k-1}) / (k + 1).

    The convention is written into the code because a library convention
    mismatch is exactly what broke the first version of this construction:
    scipy.special.assoc_laguerre(0, 1, 2.0) returns 3.0 where the mathematics
    says 1, which would have put a wrong constant under every number.
    `control_wrong_laguerre_convention` reproduces that failure on purpose.
    """
    if k == 0:
        return 1.0
    lm1 = 1.0
    lk = 1.0 + alpha - x
    for j in range(1, k):
        lm1, lk = lk, ((2 * j + 1 + alpha - x) * lk - (j + alpha) * lm1) / (j + 1)
    return lk


def hydrogenic_R(n: int, l: int, x: float, laguerre_fn=laguerre) -> float:
    """Rt_nl(x), the charge-free hydrogenic radial shape, R_nl(r) = zeta^{3/2} Rt(zeta r).

    The exponent is (n + l)!, not (n + l)!^3.  The first version had the cube;
    it is invisible for the 1s (1!^3 = 1!) and therefore survived the K-shell
    constant check while breaking every other shell -- the normalisation check
    caught it, which is why that check exists.
    """
    k = n - l - 1
    norm = math.sqrt((2.0 / n) ** 3 * math.factorial(k)
                     / (2.0 * n * math.factorial(n + l)))
    return norm * math.exp(-x / n) * (2.0 * x / n) ** l * laguerre_fn(
        k, 2 * l + 1, 2.0 * x / n)


def shape(n: int, occ: dict, x: float, laguerre_fn=laguerre) -> float:
    """D_shell / zeta at x = zeta r: sum_l N_l x^2 Rt_nl(x)^2."""
    total = 0.0
    for l, electrons in occ.items():
        rt = hydrogenic_R(n, l, x, laguerre_fn)
        total += electrons * x * x * rt * rt
    return total


def simpson(f, a: float, b: float, steps: int) -> float:
    """Composite Simpson on [a, b]; `steps` must be even."""
    if steps % 2:
        steps += 1
    h = (b - a) / steps
    total = f(a) + f(b)
    for i in range(1, steps):
        total += (4.0 if i % 2 else 2.0) * f(a + i * h)
    return total * h / 3.0


def normalisation_integral(n: int, l: int, laguerre_fn=laguerre) -> float:
    """int_0^inf x^2 Rt_nl(x)^2 dx by Simpson up to 60n, where the tail is dead.

    Rt_nl decays as x^(n-1) exp(-x/n), so beyond x = 60n the integrand is below
    1e-20 for every (n, l) used here; the truncation is not what limits accuracy.
    """
    top = 60.0 * n
    steps = 40000
    return simpson(lambda x: x * x * hydrogenic_R(n, l, x, laguerre_fn) ** 2,
                   0.0, top, steps)


def maximum_of_shape(n: int, occ: dict, laguerre_fn=laguerre):
    """c and x* for one occupancy pattern.

    The maximum is searched on the ANALYTIC function: a golden search on a
    piecewise-linear interpolant stalls at the grid step, and the first version
    reported x* = 1.00002 for the K shell where the exact value is 1.
    """
    top = 14.0 * n
    steps = 4000
    h = top / steps
    best_i, best_v = 0, -1.0
    for i in range(steps + 1):
        v = shape(n, occ, i * h, laguerre_fn)
        if v > best_v:
            best_i, best_v = i, v
    lo = (best_i - 4) * h
    hi = (best_i + 4) * h
    if lo < 0.0:
        lo = 0.0
    invphi = (math.sqrt(5.0) - 1.0) / 2.0
    a, b = lo, hi
    c_pt, d_pt = b - invphi * (b - a), a + invphi * (b - a)
    fc = shape(n, occ, c_pt, laguerre_fn)
    fd = shape(n, occ, d_pt, laguerre_fn)
    for _ in range(200):
        if fc > fd:
            b, d_pt, fd = d_pt, c_pt, fc
            c_pt = b - invphi * (b - a)
            fc = shape(n, occ, c_pt, laguerre_fn)
        else:
            a, c_pt, fc = c_pt, d_pt, fd
            d_pt = a + invphi * (b - a)
            fd = shape(n, occ, d_pt, laguerre_fn)
    x_star = 0.5 * (a + b)
    return shape(n, occ, x_star, laguerre_fn), x_star


def slater_screening(n: int, l: int, per_shell: list, same_group: float) -> float:
    """Slater's screening constant for an electron in (n, l) of this configuration.

    Implemented only for the s and p blocks used here, and only the rules that
    apply to them:
      * 1s: 0.30 for each other 1s electron.
      * n = 2 (s or p): 0.35 for each other n = 2 electron, 0.85 for each n = 1.
      * n = 3 (s or p): 0.35 for each other n = 3 electron, 1.00 for every
        electron in n = 1 and n = 2.
    `per_shell[k]` is the electron count in principal shell k + 1.
    """
    if n == 1:
        return 0.30 * (per_shell[0] - 1)
    if n == 2:
        return 0.35 * (per_shell[1] - 1) + 0.85 * per_shell[0]
    inner = sum(per_shell[:n - 1])
    return 0.35 * (per_shell[n - 1] - 1) + 1.00 * inner


def sign_of(difference: float, tolerance: float = 1e-12) -> str:
    """'>', '<' or '=' -- the '=' branch is reachable, so the test can fail."""
    if difference > tolerance:
        return ">"
    if difference < -tolerance:
        return "<"
    return "="


def body_digest(report: dict) -> str:
    """The documented digest: everything except `cost`, with indent 2 and sorted
    keys.  The paired test recomputes it by the same method, so a change to the
    method shows up as a failure rather than as a quietly different number."""
    body = json.dumps({k: v for k, v in report.items() if k != "cost"},
                      indent=2, sort_keys=True)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------

def check0_normalisation():
    values, worst = {}, 0.0
    for n, l in NORMALISED:
        value = normalisation_integral(n, l)
        values[f"{n}{'spdf'[l]}"] = value
        worst = max(worst, abs(value - 1.0))
    return {"values": values, "worst_deviation": worst,
            "tolerance": NORM_TOLERANCE, "pass": worst < NORM_TOLERANCE}


def check1_k_constant(table):
    """The K shell: Rt_10(x) = 2 exp(-x) exactly, hence c = 4/e^2 and 8/e^2."""
    deviations = {}
    for x in (0.0, 0.25, 1.0, 2.5, 6.0):
        deviations[str(x)] = hydrogenic_R(1, 0, x) - 2.0 * math.exp(-x)
    worst_pointwise = max(abs(v) for v in deviations.values())
    c1 = table["K (1s1)"]["c"]
    c2 = table["K (1s2)"]["c"]
    return {
        "rt_10_pointwise_worst_deviation_from_2exp": worst_pointwise,
        "c_two_electrons": c2, "exact_two_electrons": EIGHT_OVER_E2,
        "c_one_electron": c1, "exact_one_electron": FOUR_OVER_E2,
        "diff_two_electrons": c2 - EIGHT_OVER_E2,
        "diff_one_electron": c1 - FOUR_OVER_E2,
        "pass": (worst_pointwise < 1e-15
                 and abs(c2 - EIGHT_OVER_E2) < VALUE_TOLERANCE
                 and abs(c1 - FOUR_OVER_E2) < VALUE_TOLERANCE),
    }


def check2_argmax(table):
    """The K-shell hump sits at x = 1 exactly; the L(2s2 2p2) hump is observed
    at 3 + sqrt(3).

    The tolerance is 1e-7, not machine epsilon, and the reason is measured
    rather than convenient: near a maximum the shape is flat to second order, so
    a value resolved to 1e-16 in double precision locates the argument only to
    about sqrt(2 * eps) = 2.1e-8, and eps is 2.22e-16, not 1e-16.  The observed deviations are that size.  The
    limit is a property of the representation, not of the search: the golden
    section runs 200 iterations and its bracket is far smaller than 1e-8.
    """
    xk_1 = table["K (1s1)"]["x_star"]
    xk_2 = table["K (1s2)"]["x_star"]
    exact = 1.0
    observed = 3.0 + math.sqrt(3.0)
    xl = table["L (2s2 2p2)"]["x_star"]
    resolution = math.sqrt(2.0 * sys.float_info.epsilon)
    return {
        "k_one_electron": xk_1, "k_two_electrons": xk_2, "k_exact": exact,
        "k_worst_deviation": max(abs(xk_1 - exact), abs(xk_2 - exact)),
        "l_2s2_2p2": xl, "observed_closed_form": observed,
        "l_deviation_from_observed": xl - observed,
        "float_resolution_limit": resolution,
        "tolerance": 1e-7,
        "pass": (abs(xk_1 - exact) < 1e-7 and abs(xk_2 - exact) < 1e-7
                 and abs(xl - observed) < 1e-7),
    }


def check3_table_is_not_fitted(table):
    """Cross-implementation consistency: this pure-Python construction against
    the recorded numpy run of the same formulas."""
    deviations = {key: table[key]["c"] - value
                  for key, value in RECORDED_C.items()}
    worst = max(abs(v) for v in deviations.values())
    return {"deviations": deviations, "worst_deviation": worst,
            "tolerance": CONSISTENCY_TOLERANCE, "pass": worst < CONSISTENCY_TOLERANCE}


def check4_thresholds_monotone(table):
    """Within one shell, c grows with the p occupancy: more electrons in the
    same shape put more weight where the 2p/3p density is, and the s part does
    not move.  This is the structural control on the table.  Shells with no p
    occupancy (the K patterns) carry no ordering to test and are reported as
    untested rather than counted as agreeing."""
    groups, untested = {}, []
    for key, entry in table.items():
        if "1" not in entry["occupancy"]:
            untested.append({"pattern": key, "reason": "no p electrons"})
            continue
        groups.setdefault(entry["n"], []).append(
            (entry["occupancy"]["1"], entry["c"]))
    verdicts = {}
    for n, rows in sorted(groups.items()):
        rows.sort()
        verdicts[f"n={n}"] = {
            "patterns": len(rows),
            "p_occupancies": [p for p, _c in rows],
            "c": [c for _p, c in rows],
            "strictly_increasing": all(rows[i][1] < rows[i + 1][1]
                                       for i in range(len(rows) - 1)),
        }
    return {"per_shell": verdicts, "untested": untested,
            "pass": bool(verdicts) and all(v["strictly_increasing"]
                                           for v in verdicts.values())}


def check5_slater_channel(table, rows):
    """The prediction that can fail: Slater's rules plus the closed-form table.

    Nothing about D_max enters the prediction.  Inputs are Z, the shell electron
    counts, the occupancy pattern key, and the closed-form c table.
    """
    out = []
    for atom, z, shell, _electrons, _ls, key, _r_hump, _dmax in rows:
        per_shell = [r[3] for r in rows if r[0] == atom]
        n, occ = PATTERNS[key]
        l = max(occ)
        s = slater_screening(n, l, per_shell, 0.35)
        zeta = z - s
        threshold = 1.0 / table[key]["c"]
        ratio = zeta / z
        predicted = ">" if ratio > threshold else "<"
        measured_value = next(r[7] for r in rows if r[0] == atom and r[2] == shell)
        measured = sign_of(measured_value - z)
        out.append({"atom": atom, "Z": z, "shell": shell, "pattern": key,
                    "slater_screening": s, "slater_zeta": zeta,
                    "zeta_over_Z": ratio, "threshold_1_over_c": threshold,
                    "predicted": predicted, "measured": measured,
                    "agrees": predicted == measured})
    return {"rows": out, "agreements": sum(1 for r in out if r["agrees"]),
            "rows_checked": len(out),
            "pass": all(r["agrees"] for r in out)}


def check6_position_channel(table, rows):
    """The independent measurement channel: hump POSITION only.

    zeta_position = x*(pattern) / r*(measured) uses the measured position of the
    hump; the hump VALUE is used only to form the answer, never the prediction.
    """
    out = []
    for atom, z, shell, _electrons, _ls, key, r_hump, _dmax in rows:
        zeta = table[key]["x_star"] / r_hump
        ratio = zeta / z
        threshold = 1.0 / table[key]["c"]
        predicted = ">" if ratio > threshold else "<"
        measured_value = next(r[7] for r in rows if r[0] == atom and r[2] == shell)
        measured = sign_of(measured_value - z)
        out.append({"atom": atom, "Z": z, "shell": shell, "pattern": key,
                    "r_hump": r_hump, "zeta_from_position": zeta,
                    "zeta_over_Z": ratio, "threshold_1_over_c": threshold,
                    "predicted": predicted, "measured": measured,
                    "agrees": predicted == measured})
    return {"rows": out, "agreements": sum(1 for r in out if r["agrees"]),
            "rows_checked": len(out),
            "pass": all(r["agrees"] for r in out)}


def check7_value_channel_is_information_free(table, rows, perturbation=1e-3):
    """The channel that carries no information, shown to be insensitive.

    zeta_value = D_max / c makes `zeta/Z > 1/c` the same statement as `D_max > Z`.
    Perturbing c by a relative 1e-3 in the back-solution must therefore leave
    every verdict unchanged -- if it ever changed one, the channel would be
    carrying something after all.  The first version of this work reported 22
    agreements from this channel and they measured nothing.
    """
    unchanged, changed = 0, []
    for atom, z, _shell, _electrons, _ls, key, _r, dmax in rows:
        c = table[key]["c"]
        for factor in (1.0 - perturbation, 1.0 + perturbation):
            zeta = dmax / (c * factor)
            verdict = ">" if zeta / z > 1.0 / c else "<"
            reference = sign_of(dmax - z)
            if verdict == reference:
                unchanged += 1
            else:
                changed.append({"atom": atom, "pattern": key, "factor": factor})
    return {"perturbation": perturbation, "comparisons": 2 * len(rows),
            "unchanged": unchanged, "changed": changed,
            "is_information_free": not changed,
            "pass": not changed}


def check8_two_shell_cap(table, rows):
    """Which shells can exceed Z at all, in this model.

    The M patterns have c below 1 (the largest is 0.8061...), so a hump above Z
    needs zeta_M / Z > 1.2405.  The retained M rows sit at 0.21 to 0.37, and
    zeta/Z falls with n, so at most the K and L shells can exceed Z.  The cap
    and the measurement are reported separately, and the check can fail if
    either moves.
    """
    m_rows = [(r[0], r[5], r[7] / r[1]) for r in rows if r[5].startswith("M ")]
    l_rows = [(r[0], r[5], r[7] / r[1]) for r in rows if r[5].startswith("L ")]
    k_rows = [(r[0], r[5], r[7] / r[1]) for r in rows if r[5].startswith("K ")]
    m_c = max(table[key]["c"] for key in table if key.startswith("M "))
    m_threshold = 1.0 / m_c
    worst_m_ratio = max(abs(d_over_z) for _a, _k, d_over_z in m_rows)
    k_exceed = sorted({a for a, _k, d in k_rows if d > 1.0})
    l_exceed = sorted({a for a, _k, d in l_rows if d > 1.0})
    m_exceed = sorted({a for a, _k, d in m_rows if d > 1.0})
    return {
        "largest_c_among_M_patterns": m_c,
        "M_threshold_1_over_c": m_threshold,
        "M_c_below_one": m_c < 1.0,
        "measured_shells_exceeding_Z": {"K": k_exceed, "L": l_exceed, "M": m_exceed},
        "largest_measured_M_ratio_D_over_Z": worst_m_ratio,
        "M_measured_below_Z": not m_exceed,
        "shells_that_exceed_Z_among_measured": sorted(
            set(["K"] if k_exceed else []) | set(["L"] if l_exceed else []) | set(["M"] if m_exceed else [])),
        "pass": (m_c < 1.0 and not m_exceed and worst_m_ratio < 1.0
                 and bool(k_exceed) and bool(l_exceed)),
    }


def control_mistyped_ratio():
    """Mistype one recorded ratio by 1e-6 and require check10 to catch it.

    Without this the transcription check could be vacuous in the way that
    matters most: two numbers that always agree because neither is ever wrong.
    """
    original = RECORDED_D_OVER_Z[("S", 1)]
    mutated = dict(RECORDED_D_OVER_Z)
    mutated[("S", 1)] = original + 1e-6
    globals()["RECORDED_D_OVER_Z"] = mutated
    try:
        result = check10_recorded_ratio_transcription(RETAINED)
    finally:
        globals()["RECORDED_D_OVER_Z"] = dict(RECORDED_D_OVER_Z)
        globals()["RECORDED_D_OVER_Z"][("S", 1)] = original
    caught = [row for row in result["rows"] if not row["agrees"]]
    return {"description": "one recorded D_max / Z mistyped by 1e-6 at S L shell",
            "rows": result["rows"].__len__(), "caught": len(caught),
            "example": caught[0] if caught else None,
            "detected": len(caught) == 1}

def check10_recorded_ratio_transcription(rows):
    """The recorded D_max / Z against this file's own D_max and Z.

    This is a transcription check on the retained evidence, not a measurement:
    it can only fail if the numbers carried into this file disagree with the
    ratio the source run recorded beside them.  It exists because the first
    version of this bundle dropped the ratio entirely, so the note's central
    quantity could not be traced back to anything in the evidence.
    """
    out, worst = [], 0.0
    for atom, z, shell, _e, _l, _key, _r, dmax in rows:
        recorded = RECORDED_D_OVER_Z[(atom, shell)]
        computed = dmax / z
        worst = max(worst, abs(computed - recorded))
        out.append({"atom": atom, "shell": shell, "recorded": recorded,
                    "D_max_over_Z": computed, "agrees": abs(computed - recorded) < 1e-12})
    return {"rows": out, "worst_deviation": worst, "tolerance": 1e-12,
            "pass": worst < 1e-12 and len(out) == len(RECORDED_D_OVER_Z)}


def check9_onset_from_slater():
    """Where the K-shell hump first passes Z, predicted from Slater alone.

    (Z - 0.30) / Z > 0.9236320  <=>  Z > 3.9295, so the first atom with a hump
    above Z should be Be (Z = 4).  The retained scan agrees: He 0.8645,
    Li 0.9495, Be 1.00012.  The threshold is razor thin at Be and that is
    reported rather than smoothed over.
    """
    threshold = 1.0 / EIGHT_OVER_E2
    first_by_scan = next((sym for sym, _z, ratio in RETAINED_SCAN if ratio > 1.0), None)
    predicted_z = 0.30 / (1.0 - threshold)
    z_first = next(z for sym, z, ratio in RETAINED_SCAN if ratio > 1.0)
    return {"threshold_zeta_over_Z": threshold,
            "predicted_first_Z_strictly_above": predicted_z,
            "predicted_first_atom": "Be",
            "scan_first_atom": first_by_scan,
            "scan_first_Z": z_first,
            "scan_value_at_Be": next(r for s, _z, r in RETAINED_SCAN if s == "Be"),
            "scan_value_at_Li": next(r for s, _z, r in RETAINED_SCAN if s == "Li"),
            "margin_at_Be": next(r for s, _z, r in RETAINED_SCAN if s == "Be") - 1.0,
            "pass": first_by_scan == "Be" and 3.0 < predicted_z < 4.0}


# --------------------------------------------------------------------------
# Negative controls: each of these DID happen during this work
# --------------------------------------------------------------------------

def control_wrong_laguerre_convention():
    """L_0^{(alpha)} := 1 + alpha, the library convention that returned 3.0 for
    L_0^{(1)}(2).  The normalisation check must reject it."""
    def wrong(k, alpha, x):
        if k == 0:
            return 1.0 + alpha
        return laguerre(k, alpha, x)
    value = normalisation_integral(1, 0, wrong)
    return {"description": "library Laguerre convention L_0 = 1 + alpha",
            "integral_1s": value, "deviation": value - 1.0,
            "detected": abs(value - 1.0) > NORM_TOLERANCE}


def control_cubed_factorial():
    """norm with (n + l)!^3 instead of (n + l)!.  Invisible for the 1s, so it
    must be the 2s that exposes it."""
    def wrong_R(n, l, x):
        k = n - l - 1
        norm = math.sqrt((2.0 / n) ** 3 * math.factorial(k)
                         / (2.0 * n * math.factorial(n + l) ** 3))
        return (norm * math.exp(-x / n) * (2.0 * x / n) ** l
                * laguerre(k, 2 * l + 1, 2.0 * x / n))
    one_s = simpson(lambda x: x * x * wrong_R(1, 0, x) ** 2, 0.0, 60.0, 40000)
    two_s = simpson(lambda x: x * x * wrong_R(2, 0, x) ** 2, 0.0, 120.0, 40000)
    return {"description": "normalisation with (n+l)! cubed",
            "integral_1s": one_s, "integral_2s": two_s,
            "invisible_at_1s": abs(one_s - 1.0) < NORM_TOLERANCE,
            "detected_at_2s": abs(two_s - 1.0) > NORM_TOLERANCE}


def control_criterion_as_zeta_above_Z(table, rows):
    """The criterion written as `zeta > Z` instead of `zeta / Z > 1 / c`.  This
    version reported every shell as a mismatch."""
    mismatches = []
    for atom, z, shell, _e, _l, key, _r, dmax in rows:
        per_shell = [r[3] for r in rows if r[0] == atom]
        n, occ = PATTERNS[key]
        zeta = z - slater_screening(n, max(occ), per_shell, 0.35)
        predicted = ">" if zeta > z else "<"
        measured = sign_of(dmax - z)
        if predicted != measured:
            mismatches.append({"atom": atom, "shell": shell, "pattern": key})
    return {"description": "criterion implemented as zeta > Z",
            "rows": len(rows), "mismatches": len(mismatches),
            "examples": mismatches[:4],
            "detected": len(mismatches) > 0}


def control_single_global_threshold(table, rows):
    """One threshold for every shell, taken from the largest c in the table.
    The M rows must then be predicted wrongly."""
    largest = max(entry["c"] for entry in table.values())
    threshold = 1.0 / largest
    wrong = []
    for atom, z, shell, _e, _l, key, _r, dmax in rows:
        per_shell = [r[3] for r in rows if r[0] == atom]
        n, occ = PATTERNS[key]
        zeta = z - slater_screening(n, max(occ), per_shell, 0.35)
        predicted = ">" if zeta / z > threshold else "<"
        measured = sign_of(dmax - z)
        if predicted != measured:
            wrong.append({"atom": atom, "shell": shell, "pattern": key})
    return {"description": "one global threshold from the largest c",
            "largest_c": largest, "threshold": threshold,
            "rows": len(rows), "wrong": len(wrong), "examples": wrong[:4],
            "detected": len(wrong) > 0}


def control_flipped_measurement(table, rows):
    """Flip one retained answer.  The comparison channel must notice."""
    target = ("Ar", 2)
    flipped = []
    for r in rows:
        row = list(r)
        if (row[0], row[2]) == target:
            row[7] = row[1] - 1.0 if row[7] > row[1] else row[1] + 1.0
        flipped.append(tuple(row))
    result = check5_slater_channel(table, flipped)
    return {"description": "one retained answer flipped at Ar M shell",
            "agreements_after_flip": result["agreements"],
            "rows": result["rows_checked"],
            "detected": not result["pass"]}


# --------------------------------------------------------------------------

def run() -> dict:
    table = {}
    for key, (n, occ) in PATTERNS.items():
        c, x_star = maximum_of_shape(n, occ)
        table[key] = {"n": n, "occupancy": {str(l): e for l, e in occ.items()},
                      "c": c, "x_star": x_star, "threshold_1_over_c": 1.0 / c}

    rows = RETAINED

    checks = {
        "check0_normalisation": check0_normalisation(),
        "check1_k_constant": check1_k_constant(table),
        "check2_argmax": check2_argmax(table),
        "check3_consistency_with_recorded_run": check3_table_is_not_fitted(table),
        "check4_table_monotone_in_p_occupancy": check4_thresholds_monotone(table),
        "check5_slater_channel": check5_slater_channel(table, rows),
        "check6_position_channel": check6_position_channel(table, rows),
        "check7_value_channel_is_information_free": check7_value_channel_is_information_free(table, rows),
        "check8_two_shell_cap": check8_two_shell_cap(table, rows),
        "check9_onset_from_slater": check9_onset_from_slater(),
        "check10_recorded_ratio_transcription": check10_recorded_ratio_transcription(rows),
    }

    controls = {
        "wrong_laguerre_convention": control_wrong_laguerre_convention(),
        "cubed_factorial": control_cubed_factorial(),
        "criterion_as_zeta_above_Z": control_criterion_as_zeta_above_Z(table, rows),
        "single_global_threshold": control_single_global_threshold(table, rows),
        "flipped_measurement": control_flipped_measurement(table, rows),
        "mistyped_ratio": control_mistyped_ratio(),
    }

    every_check = all(entry["pass"] for entry in checks.values())
    every_control_detected = all(entry.get("detected") or entry.get("detected_at_2s")
                                 for entry in controls.values())

    report = {
        "status": "MatchedFiniteScope" if every_check and every_control_detected
                  else "Rejected",
        "contract": "experiments/shell_density_hump/contract.json",
        "construction": "D(r) = zeta * sum_l N_l x^2 Rt_nl(x)^2 with x = zeta r, "
                        "Rt_nl the charge-free hydrogenic radial shape",
        "constants": table,
        "checks": checks,
        "negative_controls": controls,
        "retained_measurements": {
            "provenance": "quantum-atom-lab def2-SVP ROHF densities, "
                          "out/clue4-shell-hump-criterion.json and out/clue2-dmax-vs-z.json",
            "rows": [{"atom": r[0], "Z": r[1], "shell": r[2], "electrons": r[3],
                      "ls": r[4], "pattern": r[5], "r_hump": r[6], "D_max": r[7],
                      "D_over_Z": r[7] / r[1],
                      "D_over_Z_recorded": RECORDED_D_OVER_Z[(r[0], r[2])]}
                     for r in rows],
            "scan": [{"atom": s, "Z": z, "D_max_over_Z": ratio}
                     for s, z, ratio in RETAINED_SCAN],
            "ls_not_recorded_for": sorted({r[0] for r in rows if r[4] is None}),
        },
        "channels": {
            "slater": {"agreements": checks["check5_slater_channel"]["agreements"],
                       "rows": checks["check5_slater_channel"]["rows_checked"],
                       "uses_the_measured_value": False},
            "position": {"agreements": checks["check6_position_channel"]["agreements"],
                         "rows": checks["check6_position_channel"]["rows_checked"],
                         "uses_the_measured_value": False},
            "value": {"agreements": len(rows), "rows": len(rows),
                      "uses_the_measured_value": True,
                      "verdict": "information free: agreement is forced by construction"},
        },
        "not_claimed": [
            "Not the true density of any real atom: a one-exponent-per-shell "
            "hydrogenic model compared against a finite-basis Hartree-Fock density",
            "The retained measurements are not recomputed here; re-running them "
            "needs PySCF, which this checker does not use",
            "x*(L, 2s2 2p2) = 3 + sqrt(3) is an observation at 1e-8, not derived",
            "The two-shell cap says which shells can exceed Z in this model, not "
            "that the excess has any physical consequence",
            "No native certificate, no Rust witness, no Seal follows from this file",
        ],
        "tooling": {
            "external_library_used": False,
            "numpy_used": False,
            "sympy_used": False,
            "pyscf_used": False,
            "subprocesses": 0,
            "arithmetic": "double precision throughout; tolerances stated per check",
            "integration": "composite Simpson, 40000 intervals on [0, 60n]",
            "maximisation": "coarse grid of 4000 nodes then golden section, 200 iterations",
        },
        "cost": {"assertions": 0, "wall_seconds": 0.0},
    }

    report["cost"]["assertions"] = sum(
        len(entry.get("rows", [])) if isinstance(entry.get("rows"), list) else 0
        for entry in checks.values()) + len(NORMALISED) + len(PATTERNS)
    report["all_checks_pass"] = every_check
    report["all_controls_detected"] = bool(every_control_detected)
    # The digest covers everything except `cost`, and it lives inside `cost`, so
    # a replay can reproduce it: the wall time is the only field that differs
    # between two runs and it is excluded on both sides.
    report["cost"]["evidence_body_sha256_excluding_cost"] = body_digest(report)
    return report


def main(argv=None) -> int:
    import time
    start = time.time()
    report = run()
    report["cost"]["wall_seconds"] = round(time.time() - start, 3)
    EVIDENCE.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")

    failed = [name for name, entry in report["checks"].items() if not entry["pass"]]
    controls_missed = [name for name, entry in report["negative_controls"].items()
                       if not (entry.get("detected") or entry.get("detected_at_2s"))]
    print(f"status = {report['status']}")
    for name, entry in report["checks"].items():
        print(f"  {'ok  ' if entry['pass'] else 'FAIL'} {name}")
    for name, entry in report["negative_controls"].items():
        caught = entry.get("detected") or entry.get("detected_at_2s")
        print(f"  {'ok  ' if caught else 'MISS'} control {name}")
    print(f"slater channel: {report['checks']['check5_slater_channel']['agreements']}"
          f"/{report['checks']['check5_slater_channel']['rows_checked']} agree")
    print(f"position channel: {report['checks']['check6_position_channel']['agreements']}"
          f"/{report['checks']['check6_position_channel']['rows_checked']} agree")
    print("evidence body sha256 = "
          f"{report['cost']['evidence_body_sha256_excluding_cost']}")
    print(f"wall seconds = {report['cost']['wall_seconds']}")
    if failed or controls_missed:
        print(f"FAILED checks: {failed}; controls not detected: {controls_missed}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
