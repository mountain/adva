# What the involution route costs: the heat sign and the invariance identity

**Date**: 2026-09-24 · **Checker**: `experiments/lorentzian_frame_reading/checker.py` ·
**Contract**: `experiments/lorentzian_frame_reading/contract.json` ·
**Evidence**: `experiments/lorentzian_frame_reading/evidence.json` ·
**Paired test**: `tests/python/test_lorentzian_frame_reading.py`

**Status**: one bounded external exact experiment. No Rust witness, no stable API
change, no library admission, no Seal, no transport. **no physical claim** is made
anywhere: a "heat reading" and its time reverse are two sign patterns of exact
matrix coefficients, not processes.

Authored and checked by deepseek-v4-flash-vision-exp (DeepSeek Harness),
submitted through Mingli Yuan's authorized account proxy. Account use is not his
authorship, review, endorsement or correctness guarantee. One agent wrote the
contract, the checker and this note; there is no independent reviewer.

中文摘要：0225 把对合 `K`（`K²=I`）与 `(3,1)` 度量相容这件事留成了一个未决边界。本实验把它算完：**指数里的符号，恰好是结构平方的符号**——`S²=σI` 时 `(−S)^k A_S^k = σ^k H^k`，`σ=−1`（复结构 `J`）给出接收框架那条热读数，`σ=+1`（对合 `K`）给出它的**时间反演**；而在四维 Lorentzian 载体上，`K` 虽与度量相容，`A_K = −KH` **不**是 `G`-斜伴随；更进一步，在框架自己的切割算子上，**同时**要求 `K`-相容与生成元斜伴随的对称度量只有退化解——没有任何非退化度量能两者兼得。

---

## 1. What was handed over, and what is answered

The received frame carries a complex structure `J` with `J² = −I`, a cut operator
`H` built from a graph Laplacian, initially `G = I`, the generator `A = −J H`, and
a checked degree of twelve for two identities: the Wick coefficient identity
`(−J)^k A^k/k! = (−H)^k/k!` and the metric invariance of `U(t) = exp(tA)`.

[0225](0225-a-complex-structure-admits-only-even-signatures.md) showed that a
metric compatible with `J` has even inertia, so a carrier with exactly one
negative direction needs `J` replaced by an involution `K`, and that such a `K` is
compatible with a Lorentzian metric. It left open what that replacement does to
the frame's reading. This note answers that, in three exact steps.

**One declared analogue, and only one:** for a structure `S` with `S² = σI` that
commutes with `H`, the frame's generator is generalised to `A_S = −S H`. This is
not an invention — it **reproduces the received frame exactly** when `S = J`, and
the checker verifies that reproduction before any structure is replaced.

## 2. The frame's own identities, reproduced first

Rebuilt from the received process `chain-and-single`: six cuts, `d_max = 3`, so
`H0 = L/6`, carrier dimension twelve. On that instance: `J² = −I` ✓,
`H J = J H` ✓, `A = −J H` skew for `G = I` ✓, the Wick identity holds with **no
mismatched degree** from zero through twelve ✓, and every coefficient of
`U(t)ᵀ G U(t)` vanishes from degree one through twelve ✓.

So the two identities the frame checks are reproduced on the received data before
the replacement is tried. Had the replacement changed the frame's own case, the
run would have failed before reaching any conclusion about it.

## 3. The sign in the exponent is the sign of the structure's square

For `S² = σI` commuting with `H` and `A_S = −S H`:

$$(-S)^k A_S^k = (-1)^k S^k \cdot (-1)^k (SH)^k = S^{2k} H^k = \sigma^k H^k$$

which is verified coefficientwise from degree zero through twelve on the frame's
own instance, for both structures:

| structure | `S²` | identity | first degrees | reading |
| --- | --- | --- | --- | --- |
| `J` | `−I` | `(−J)^k A^k = (−1)^k H^k` | odd degrees differ from `+H^k` | coefficients alternate: **the exponential of `−H`**, the received heat reading |
| `K = diag(I_6, −I_6)` | `+I` | `(−K)^k A_K^k = (+1)^k H^k` | every degree equals `+H^k` | one sign throughout: **the exponential of `+H`**, the time reverse of the heat reading |

**The sign in the exponent is exactly the sign of the structure's square.** The
received frame's heat reading is therefore not a property of the cut operator, nor
of the metric, but of `J² = −I` — and an involution, whose square is `+I`, gives
the reverse. This is the first price of the Lorentzian route.

## 4. The Lorentzian carrier: the generator is not skew

On the declared four-dimensional instance — two cuts joined by one edge, so
`d_max = 1` and `H0 = L/2` — with `G = diag(1,1,1,−1)` and `K = diag(1,1,−1,−1)`:

| statement | result |
| --- | --- |
| signature of `G` | **(3,1)**, by exact congruence reduction |
| `K² = I` | yes |
| `Kᵀ G K = G` (0225's fact, recomputed) | **yes** |
| `Jᵀ G J = G` | no |
| `A_K = −K H` skew for `G` | **no** |
| residual `A_Kᵀ G + G A_K` | `[[−1,1,0,0],[1,−1,0,0],[0,0,1,0],[0,0,0,−1]]`, absolute sum 6 |

The exact condition for skewness is that `H` anticommutes with the product `G K`,
and it **fails**. So the involution buys the signature and does not by itself buy
the frame's invariance identity.

## 5. And no metric buys both

The natural repair is to stop declaring `G` and solve for it: which symmetric
metrics are simultaneously compatible with `K` and make the generator skew?
That is the linear system `Kᵀ G K = G` together with `H (G K) + (G K) H = 0`, and
it is solved exactly here:

| instance | unknowns | rank | solution dimension | determinants of the basis | every element degenerate |
| --- | ---: | ---: | ---: | --- | --- |
| the declared four-dimensional instance | 10 | 8 | 2 | `0`, `0` | **yes** |
| the frame's own twelve-dimensional instance | 78 | 76 | 2 | `0`, `0` | **yes** |

Degeneracy is decided for the **whole** space and not only for its basis: the
determinant of `a + t b` is checked at five declared rational values of `t`, which
decides a polynomial of degree at most four identically; all five are zero.

**No nondegenerate metric of any signature keeps the involution compatible and
the generator skew at the same time** on either declared instance. The structural
reason is elementary and recorded: the cut operator is a graph Laplacian, whose
kernel on each connected component is the constants, so the metrics that survive
compatibility are scalar multiples of a rank-one matrix in each block of the
involution — and a block of rank one has zero determinant.

## 6. The trade, complete

| structure | signature available | exponential reading | invariance identity |
| --- | --- | --- | --- |
| `J`, `J² = −I` | only even inertia: `(4,0)`, `(2,2)`, … | `exp(−τH)`, coefficients alternating | holds with `G = I` and `HJ = JH` |
| `K`, `K² = +I` | `(3,1)` reachable | `exp(+τH)`, the time reverse | **not satisfiable with any nondegenerate metric** on the frame's own cut operator |

Both columns are now decided by executed checks. The frame cannot have the
Lorentzian reading and its heat reading at once; and on its own cut operator it
cannot have the Lorentzian reading and its invariance identity either.

## 7. Executed result and reproduction

The frozen run returned `ExternalExactPass`: **30 assertions in five sections**,
in 6.33 seconds wall time. No failed check and no corrective replay.

From a checkout with Python 3.11 or later, choosing an output path that does not
already exist:

```sh
python3 -S experiments/lorentzian_frame_reading/checker.py --output /tmp/lorentzian-reading-fresh.json
```

The contract enforces one route, 240 wall seconds, 300 CPU seconds, 256 MiB of
declared address space, 200,000 assertions, a 4 MiB output ceiling and one
correction replay. `RLIMIT_CPU`, `RLIMIT_FSIZE` and the wall alarm are installed;
no address-space ceiling is installed because no child process is launched. An
existing output is refused. A pin mismatch yields `Failed`.

## 8. Repository scope and next boundary

This result belongs to research in `adva`. The received bytes, the machine
specifications and the library catalogue are unchanged, and no transport, receipt
or exchange is executed. Native admission `NotGranted`, native execution
`NotRun`, new transport `NotRun`. No vocabulary word is promoted and no
terminology home is created.

This experiment is **not connected to the Kerr experiment** of note 0226: nothing
here is a spacetime, a horizon, a curvature or a solution of any field equation.

The next boundary is **not decided, checked or claimed here**: whether some other
declared analogue of the generator — other than the one that reproduces the
received frame exactly — behaves differently; whether a different cut operator or
a different involution escapes the impossibility beyond the elementary reason
recorded; and whether any carrier of the frame can carry a causal order, an
observer, a clock or a dynamics. **No computation outside a contract counts as a
result of this repository.**

## Residual

What is established is a set of exact statements about the received frame's own
construction and two declared instances of it. The frame's twelve-dimensional
instance is rebuilt from the received process and reproduces its own two
identities through degree twelve before anything is replaced. For a structure
whose square is `σI`, the coefficient identity is `(−S)^k A_S^k = σ^k H^k`: at
`σ = −1` it is the received heat reading, and at `σ = +1` every coefficient has
one sign, which is the exponential of `+H`, the time reverse; the sign in the
exponent is exactly the sign of the structure's square. On the declared
four-dimensional carrier the involution is compatible with a metric of signature
`(3,1)` and the generator is nevertheless not skew for it, with the exact residual
retained. And on both declared instances the metrics that keep the involution
compatible and the generator skew form a two-dimensional space every element of
which is degenerate, so no nondegenerate metric buys both.

What is not established: whether another declared analogue of the generator would
behave differently; whether a different cut operator, a different involution or a
larger carrier escapes the impossibility beyond the elementary reason recorded;
whether any carrier of the frame can be given a causal order, an observer, a clock
or a dynamics; and whether the exponential reading has any physical meaning,
which is **not claimed**. The declared degree of twelve bounds the coefficient
identities, and a larger degree is a different run. This run is not connected to
the Kerr experiment of note 0226.
