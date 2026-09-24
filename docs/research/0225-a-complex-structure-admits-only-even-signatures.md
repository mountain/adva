# A complex structure admits only even signatures: what that costs a four-dimensional carrier

**Date**: 2026-09-24 · **Checker**: `experiments/iota_frame_signature/checker.py` ·
**Contract**: `experiments/iota_frame_signature/contract.json` ·
**Evidence**: `experiments/iota_frame_signature/evidence.json` ·
**Paired test**: `tests/python/test_iota_frame_signature.py`

**Status**: one bounded external exact experiment. No Rust witness, no stable API
change, no library admission, no Seal, no transport, and no physical claim.

Authored and checked by deepseek-v4-flash-vision-exp (DeepSeek Harness),
submitted through Mingli Yuan's authorized account proxy. Account use is not his
authorship, review, endorsement or correctness guarantee. One agent wrote the
contract, the checker and this note; there is no independent reviewer.

中文摘要：在接收的 `{e, i, iota}` 框架自己的搬移义务下，与复结构 `J`（`J²=−I`）相容的度量 `G`（`JᵀGJ=G`）**正负惯性指数都是偶数**；因此在四维载体上可达的号差只有 `(4,0)`、`(2,2)`、`(0,4)`，**恰好一个负方向不可达**。若保留 `J` 而改用 Lorentz 度量，框架的恒等式在**一阶就失败**（残差已保留）。而把结构换成对合 `K`（`K²=I`）后，同一个 `(3,1)` 度量**是相容的**——所以这是「结构换号差」的取舍，不是 Lorentz 号差本身不可达。**本笔记同时保留一条更正**：先前把分裂路线读成必然给出 `(2,2)` 是错的。

---

## 1. Question and fixed sources

The received frame binds a complex structure `J` with `J² = −I`, a cut operator
`H0 = L/(2 d_max)` with `H = diag(H0, H0)`, initially `G = O = I`, and a
transport rule under which `J`, `H`, `G` and `O` travel **together**. The
question is which metric signatures a carrier can carry while `J` stays
compatible with the metric, meaning `JᵀGJ = G`.

The frame operators are quoted from the received frame profile; the received
process `chain-and-single` supplies the frame's own instance from the received
family data. Both files are pinned by SHA-256, and the pins are cross-checked
against the receiver's own records: `interpretations.json` against the previous
materials record, and `frame.md` against the delivery receipt. A pin that agrees
only with this contract and not with the received record fails the run. No
external corpus is opened.

## 2. The frame's own instance

Rebuilt from the received process: six cuts, seven cut-graph edges, degrees
`(2,3,2,2,3,2)`, `d_max = 3`, so `H0 = L/6` and the carrier has dimension twelve.
`J² = −I`, `H` is symmetric, `H J = J H` and `A = −J H` is skew all hold, and the
frame's initial metric `G = I` is `J`-compatible with inertia **(12, 0)**.

## 3. The compatibility system, solved exactly

Solving `JᵀGJ = G` over the rationals in all `4n²` entries of `G`:

| n | carrier | unknowns | general solution | symmetric solutions |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 2 | 4 | 2 (= 2n²) | 1 (= n²) |
| 2 | 4 | 16 | 8 (= 2n²) | 4 (= n²) |
| 3 | 6 | 36 | 18 (= 2n²) | 9 (= n²) |

The general solution has the block shape `G = [[P, Q], [−Q, P]]` with `P, Q`
arbitrary, from which `G J = J G` follows immediately; the checker verifies that
**every basis solution commutes with `J`**. The symmetric solutions are exactly
`[[A, B], [−B, A]]` with `A` symmetric and `B` antisymmetric.

## 4. Exhaustively, both inertia indices are even

Every symmetric nondegenerate member of each declared finite integer family was
built and its inertia computed by exact congruence reduction, with no eigenvalue
approximated:

| n | entry range | members | degenerate | signatures seen |
| ---: | --- | ---: | ---: | --- |
| 1 | −3…3 | 7 | 1 | (2,0) ×3, (0,2) ×3 |
| 2 | −3…3 | 2401 | 53 | (4,0) ×105, (2,2) ×2138, (0,4) ×105 |
| 3 | −1…1 | 19683 | 2843 | (6,0) ×1, (4,2) ×8419, (2,4) ×8419, (0,6) ×1 |

**No member has an odd index.** The structural reason is that a symmetric `G`
commuting with `J` is complex-linear, so its real eigenvalues have even
multiplicity; the exhaustion is what the run checks, and the argument is
elementary, not a proof-assistant certificate.

## 5. The four-dimensional conclusion

On a carrier of dimension four, the signatures with both indices even are
exactly **(4,0)**, **(2,2)** and **(0,4)**. The signatures **(3,1)** and **(1,3)**
do not occur. **Exactly one negative direction is unreachable while the complex
structure stays metric-compatible.**

## 6. What a Lorentzian metric costs

On the smallest four-dimensional instance the frame admits — two cuts joined by
one edge, so `d_max = 1`, `H0 = L/2` — with `A = −J H`:

| metric | signature | `J` orthogonal | `A` skew | residual `JᵀGJ − G` | residual `AᵀG + G A` |
| --- | --- | --- | --- | --- | --- |
| `G = I` | (4,0) | yes | yes, exactly zero | zero | zero |
| `G = diag(1,1,1,−1)` | (3,1) | **no** | **no** | `diag(0,−2,0,2)`, absolute sum 4 | absolute sum 4 |

So the frame identity the run checks under `G = I` **fails at first order** under
a Lorentzian metric. Keeping the complex structure and asking for `(3,1)` means
giving up metric compatibility, hence the unitarity-type identity that the frame
checks through degree twelve.

## 7. The route that does reach (3,1)

On the same four-dimensional carrier and for the same Lorentzian metric, the
declared involution `K = diag(1,1,−1,−1)` satisfies `K² = I` and
**`KᵀG K = G`**. `K` is neither `J` nor `−J`, and `JᵀG J ≠ G`. Hence **a
signature with exactly one negative direction is reachable on a four-dimensional
carrier exactly when the structure is an involution rather than a complex
structure.** This is a trade of structure for signature, not an impossibility of
Lorentzian signature.

What the frame's other obligations become under `K` — in particular what happens
to the exponential reading and to the Wick coefficient identity
`(−J)^k A^k/k! = (−H)^k/k!` — is **not decided here**.

## 8. A retained correction

An earlier reading in this exploration held that replacing the complex structure
by a split structure on a four-dimensional carrier must give two positives and
two negatives. **That reading is wrong.** The arithmetical reason is that a
metric compatible with an involution is only required to be block diagonal in the
involution's eigenspaces, and those two ranks need not be equal: with
`K = diag(1,1,−1,−1)` the ranks are three and one, so `(3,1)` is compatible.

That earlier reading was **never published**: it appeared in working discussion
and in no contract, note, claim or evidence file. It is recorded here anyway,
because the mechanism is only worth trusting while its errors stay on the record,
and because the corrected statement is a different and more useful one.

## 9. Executed result and reproduction

The frozen run returned `ExternalExactPass`: **87 assertions in seven sections**,
in 1.258 seconds wall time. No failed check and no corrective replay. The
retained evidence carries the frame instance, the solved solution spaces, every
family's counts and signature census, the four-dimensional conclusion, both exact
residuals of the Lorentzian case and the involution's compatibility.

From a checkout with Python 3.11 or later, choosing an output path that does not
already exist:

```sh
python3 -S experiments/iota_frame_signature/checker.py --output /tmp/iota-frame-signature-fresh.json
```

The contract enforces one route, 180 wall seconds, 240 CPU seconds, 256 MiB of
declared address space, 200,000 assertions, a 4 MiB output ceiling and one
correction replay. `RLIMIT_CPU`, `RLIMIT_FSIZE` and the wall alarm are installed;
no address-space ceiling is installed because no child process is launched. An
existing output is refused. A pin mismatch yields `Failed`; a missing input or an
exhausted budget yields `Unknown`.

## 10. Repository scope and next boundary

This result belongs to research in `adva`. The received bytes, the machine
specifications and the library catalogue are unchanged, and no transport, receipt
or exchange is executed. Native admission `NotGranted`, native execution
`NotRun`, new transport `NotRun`. The functions named `inertia` and
`solution_basis` in the checker are finite exact computations, not Adva
operations.

The four towers of note 0224 are cited, not recomputed: their carriers have
dimension two, twelve, twenty-two and thirty-two, so none of them is even a
four-dimensional carrier, and none is the object the Lorentzian question was
asked about here.

The next boundary is **not decided, checked or claimed here**: whether a
`K`-compatible carrier keeps any of the frame's other obligations, what the frame's
exponential and Wick identity become under `K`, whether a carrier can be given a
causal order, an observer or a clock, and whether the complex structure could be
kept while metric compatibility is weakened by a declared factor rather than
abandoned. **No computation outside a contract counts as a result of this
repository.**

## Residual

What is established is a set of exact statements about declared finite rational
matrices: the solutions of `JᵀGJ = G` form a space of dimension `2n²` whose
symmetric part has dimension `n²`, and every solution commutes with `J`; over the
declared finite integer families every symmetric nondegenerate solution has both
inertia indices even, including three families of seven, two thousand four
hundred one and nineteen thousand six hundred eighty-three members; on a
four-dimensional carrier that leaves exactly `(4,0)`, `(2,2)` and `(0,4)`, so
exactly one negative direction is unreachable while `J` stays metric-compatible;
the frame's own metric makes the generator skew exactly while a Lorentzian metric
does not, with both exact residuals retained; and the same Lorentzian metric is
compatible with the declared involution, so `(3,1)` is reachable once the
structure is an involution.

What is not established: whether a `K`-compatible carrier keeps any other frame
obligation; what the exponential and Wick readings become under `K`; whether any
carrier can be given a causal order, an observer, a clock or a dynamics; whether
the frame's carriers admit a manifold structure at all; whether the complex
structure could be retained under a weakened compatibility; and **anything about
physical spacetime** — a signature is a property of a declared rational form on a
declared finite carrier, and no claim is made that any carrier here is, or could
be, a spacetime. The retained correction in §8 is part of the result. The
exhaustive families are finite and declared: their ranges are part of the claim,
and a different range is a different run.
