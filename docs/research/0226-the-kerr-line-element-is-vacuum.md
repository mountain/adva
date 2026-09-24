# The Kerr line element is vacuum: exact symbolic curvature, signature and horizons

**Date**: 2026-09-24 · **Checker**: `experiments/kerr_vacuum/checker.py` ·
**Contract**: `experiments/kerr_vacuum/contract.json` ·
**Evidence**: `experiments/kerr_vacuum/evidence.json` ·
**Paired test**: `tests/python/test_kerr_vacuum.py`

**Status**: one bounded external exact experiment. No Rust witness, no stable API
change, no library admission, no Seal, no transport. **no physical claim** is made
anywhere: this note computes properties of one declared line element, and nothing
about any object that does or does not exist.

Authored and checked by deepseek-v4-flash-vision-exp (DeepSeek Harness),
submitted through Mingli Yuan's authorized account proxy. Account use is not his
authorship, review, endorsement or correctness guarantee. One agent wrote the
contract, the checker and this note; there is no independent reviewer.

中文摘要：用仅标准库、自写的精确符号张量演算，在 Boyer–Lindquist 坐标下计算 Kerr 线元：五个参数对（含 $A>M$）的**十六个 Ricci 分量恒为零**；Kretschmann 标量**精确等于闭式**，$A=0$ 时回到 $48M^2/r^6$；六个声明点（视界外、视界内、能层内、内视界以内）号差**恒为 $(3,1)$**，即使 $g_{rr}$ 与 $g_{tt}$ 变号；视界半径、能层、极端性界、视界面积、角速度、表面重力与 Smarr 恒等式全部精确成立。**不声称任何观测、天体物理或与 `{e,i,iota}`-frame 的关联。**

---

## 1. What was asked, and why the boundary is drawn where it is

Mingli Yuan asked on 2026-09-24, after the signature result of note
[0225](0225-a-complex-structure-admits-only-even-signatures.md), for a black hole
to be computed. The honest form of that request inside this repository is a
bounded external exact experiment on a **declared line element**, in the pattern
of note 0222's hydrogenic model: the arithmetic is exact, the object is declared,
and every claim about reality is refused in writing.

So: the Kerr metric in Boyer–Lindquist coordinates is declared in the contract as
five nonzero components, and everything below is a consequence computed from
it — not quoted, not imported, and not checked against any table.

**The Einstein equations are not derived.** What is checked is that one declared
metric has a vanishing Ricci tensor.

This experiment **is not connected to the frame** of notes 0224 and 0225. Those
notes are the reason the question was asked; no carrier of the frame is claimed
to be a spacetime, and no black hole is claimed to be a frame.

## 2. The machinery, and how it was calibrated

The whole symbolic tensor calculus is written for this experiment in the Python
standard library: bivariate polynomials over Q, a parity-split representation of
rational functions in `(r, cos θ)` that carries `sin θ` through `sin² = 1 − cos²`,
exact Christoffel symbols, Riemann tensor, Ricci tensor and Kretschmann scalar,
exact inertia by congruence reduction, and exact arithmetic in a quadratic field
for the horizon data.

Before any result is read, the machinery is calibrated three ways, and the
calibration is part of the retained evidence:

| calibration | result |
| --- | --- |
| `g` times its inverse is the identity, exactly | verified for all 16 pairs |
| the time–phi block determinant is `−Δ sin²θ` | verified exactly |
| the two symbolic derivatives against central differences at a declared point | 14 comparisons, worst relative disagreement **2.77 × 10⁻¹⁰** against a declared tolerance of 10⁻⁶ |

The floating-point arithmetic in the checker exists **only** in that third row.

## 3. The metric is vacuum

Every one of the sixteen Ricci components is computed as a rational function of
`r` and `cos θ` and is **identically zero**, for all five declared parameter
pairs — including the pair with the spin above the mass, where the metric is
still vacuum:

| pair | M | A | Christoffels | Riemann components | Ricci components | all zero |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Schwarzschild reduction | 1 | 0 | 9 | 12 | 10 | **yes** |
| slowly spinning | 1 | 1/2 | 20 | 44 | 10 | **yes** |
| the declared black hole | 1 | 3/5 | 20 | 44 | 10 | **yes** |
| no horizon, A above M | 1 | 7/5 | 20 | 44 | 10 | **yes** |
| a second mass | 2 | 3/2 | 20 | 44 | 10 | **yes** |

## 4. The Kretschmann scalar

The computed `R_{abcd} R^{abcd}` equals the declared closed form
`48 M² (r² − A²c²)((r² + A²c²)² − 16 r² A² c²) / (r² + A²c²)⁶` **identically as a
rational function**, for every declared pair; the identity is checked by exact
polynomial cross-multiplication, not at sample points. The scalar carries no
`sin θ` part, as a scalar must not.

In the Schwarzschild case the computed scalar reduces to **48 M squared over r to
the sixth** — the known value, and therefore a check on the whole chain from
metric to curvature.
The numerator has 99 terms there and 846 with spin. The numerator vanishes
exactly where `r² = A²c²`.

## 5. The signature is three plus one everywhere declared

The exact inertia of the metric at six declared points, computed by congruence
reduction:

| point | r | c | signature | `g_tt > 0` | `g_rr < 0` |
| --- | --- | --- | --- | --- | --- |
| outside the horizon | 3 | 1/2 | (3,1) | no | no |
| inside the outer horizon | 1 | 1/2 | (3,1) | yes | yes |
| inside the ergosphere | 3/2 | 1/10 | (3,1) | yes | yes |
| between the horizons | 1/2 | 1/3 | (3,1) | yes | yes |
| inside the inner horizon, toward the ring | 1/10 | 1/2 | (3,1) | yes | no |
| far away | 50 | −1/3 | (3,1) | no | no |

`g_rr` changes sign twice and `g_tt` once, and **the signature never changes**:
exactly one negative direction at every declared point. The determinant is
`−Σ² sin²θ`, so the metric is degenerate exactly where `Σ` vanishes, at the ring,
or where `sin θ` vanishes, on the axis. Separately, the chart's radial component
is `Σ/Δ`, so the chart itself fails where `Δ = 0`; the checker refuses a declared
point that sits there, which is how the first draft of the declared point list
was corrected.

## 6. Horizons, ergosphere, area, angular velocity and Smarr

For the declared black hole `M = 1`, `A = 3/5`, exactly in `Q(√(M² − A²))`:

| quantity | exact value | identity checked |
| --- | --- | --- |
| discriminant | 16/25 | `Δ(r±) = 0` for both roots |
| `r±` | `1 ± 4/5` | `r₊² + A² = 2 M r₊` |
| ergosphere radius | `M + √(M² − A²c²)` | `g_tt = 0` at that radius, for four angles |
| horizon area | `4π(r₊² + A²) = 8πM r₊` | the two expressions agree |
| horizon angular velocity | `A/(r₊² + A²) = A/(2M r₊)` | the two expressions agree |
| surface gravity | `(r₊ − r₋)/(4M r₊) = √(M²−A²)/(2M r₊)` | the two expressions agree |
| Smarr | `M = κA/(4π) + 2Ω_H J`, `J = MA` | holds exactly |

π is a **symbol**: every identity is checked on the coefficient of π, and no
decimal value of π is used anywhere. The pair with `A > M` has no real horizon
radius, so the extremality bound is exactly the condition for a horizon in this
chart.

## 7. Executed result and reproduction

The frozen run returned `ExternalExactPass`: **58 assertions in six sections**,
in 5.54 seconds wall time. No failed check and no corrective replay.

From a checkout with Python 3.11 or later, choosing an output path that does not
already exist:

```sh
python3 -S experiments/kerr_vacuum/checker.py --output /tmp/kerr-vacuum-fresh.json
```

The contract enforces one route, 300 wall seconds, 360 CPU seconds, 512 MiB of
declared address space, 200,000 assertions, an 8 MiB output ceiling and one
correction replay. `RLIMIT_CPU`, `RLIMIT_FSIZE` and the wall alarm are installed;
no address-space ceiling is installed because no child process is launched. An
existing output is refused. An exhausted budget yields `Unknown`.

## 8. Repository scope and next boundary

This result belongs to research in `adva`. The received bytes, the machine
specifications and the library catalogue are unchanged, and no transport, receipt
or exchange is executed. Native admission `NotGranted`, native execution
`NotRun`, new transport `NotRun`.

The next boundary is **not decided, checked or claimed here**: whether a
Lorentzian carrier with the frame's obligations can also be a solution of this
kind; what happens to the frame's involution `K` of note 0225 on such a carrier;
whether the chart can be extended past `Δ = 0` in another chart; and everything
about dynamics, stability, radiation, thermodynamics and quantum theory. **No
computation outside a contract counts as a result of this repository.**

## Residual

What is established is a set of exact statements about one declared line element.
Its inverse metric is exact, its time–phi block determinant is `−Δ sin²θ`, its
symbolic derivatives are calibrated against central differences to 2.77 × 10⁻¹⁰,
all sixteen Ricci components vanish identically for five declared parameter pairs
including a spin above the mass, its Kretschmann scalar equals the declared closed
form identically and reduces to 48 M²/r⁶ when the spin vanishes, its signature is
three plus one at all six declared points including points inside the horizon and
inside the ergosphere, and the horizon radii, the ergosphere, the extremality
bound, the horizon area, the angular velocity, the surface gravity and the Smarr
identity hold exactly in the declared quadratic field.

What is not established: that the Einstein equations hold for any other metric or
in any other chart; that any such object **exists**, has been observed, or has a
mass, a spin, a charge or a temperature; that a horizon, an ergosphere or a ring
is anything more than a locus in a declared chart; that the vanishing Ricci tensor
has a physical explanation; whether the frame of notes 0224 and 0225 can carry a
Lorentzian carrier that is also a solution of this kind, which is a different
question and is not asked here; and every question about dynamics, stability,
radiation, thermodynamics or quantum theory. The declared parameters and points
bound every claim: a different mass, spin, chart or point is a different run, and
nothing transfers without re-running the checker.
