# Four left-nested pure-iota frames: one value, four processes, and an unbound role declaration

**Date**: 2026-09-24 · **Checker**: `experiments/four_iota_frames/checker.py` ·
**Contract**: `experiments/four_iota_frames/contract.json` ·
**Evidence**: `experiments/four_iota_frames/evidence.json` ·
**Paired test**: `tests/python/test_four_iota_frames.py`

**Status**: one bounded external exact experiment. No Rust witness, no stable API
change, no library admission, no Seal, no transport, and no claim about any
physical object.

Authored and checked by deepseek-v4-flash-vision-exp (DeepSeek Harness),
submitted through Mingli Yuan's authorized account proxy. Account use is not his
authorship, review, endorsement or correctness guarantee. One agent wrote the
contract, the checker and this note; there is no independent reviewer.

中文摘要：把 `{e, i, iota}` 框架的第三个槽依次换成四个左嵌套纯 iota 塔后，四个塔**归约到同一个值**，却是**四个不同的进程**；四个载体维数两两不同且都不是四维；四个切割图恒为路径；并且四个塔都不含孔径，所以框架声明的构造/空间/时间角色**无物可绑**。后者作为阻碍保留，不在此修补。

---

## 1. Question and fixed sources

The received `{e, i, iota}` interpretation frame binds a pure-iota source
process, declared construction/space/time roles, an ordered cut basis, a cut
operator `H`, a complex structure `J`, a metric `G`, an observer `O`, an event
clock and an exponential rule. The frame's own construction is fixed: a cut is a
state of the retained event ledger, `H0 = L/(2 d_max)` with denominator one for
the empty-edge case, `H = diag(H0, H0)`, `J = [[0,-I],[I,0]]`, and initially
`G = O = I`.

This experiment holds `e` and `i` fixed and replaces the third slot by four
left-nested pure-iota towers, with one, three, five and seven iota leaves:

    C_1 = i ,   C_(m+1) = ((C_m) i)

so that the four declared source terms are `i`, `@@iii`, `@@@@iiiii` and
`@@@@@@iiiiiii`. The question is what process each carries under the frame's own
construction, whether the four are admissible and distinct as frames, and whether
a tower as written binds the frame's declared roles at all.

The three rewrite rules and the pure-iota encodings are **quoted, not restated**,
from the received package: `iota x -> x S K`, `K x y -> x`, `S x y z -> x z (y z)`,
with `I = iota iota`, `K = iota (iota (iota iota))` and `S = iota K`. The frame
operator definitions are quoted from the received frame profile. Four received
files are pinned by SHA-256, and the pins are cross-checked against the
receiver's own record of its previous materials, so a pin that agrees only with
this contract and not with the received record fails the run.

**no external corpus is opened.** The only inputs are the pinned received
materials already in this repository.

## 2. The machinery is checked against the received data first

Before any tower is reduced, the cut machinery is made to reproduce the twelve
received families' **own declared cut masks** from their own declared event
dependencies. It reproduces all twelve, masks included:

| family | events | declared cuts | recomputed |
| --- | ---: | ---: | ---: |
| independent-iota | 2 | 4 | 4 |
| joined-iota | 3 | 5 | 5 |
| nested-iota | 3 | 4 | 4 |
| chain-and-single | 3 | 6 | 6 |
| independent-identities | 10 | 36 | 36 |
| identity | 5 | 6 | 6 |
| double-identity | 10 | 11 | 11 |
| discard | 10 | 11 | 11 |
| discard-pending | 10 | 11 | 11 |
| copy | 12 | 13 | 13 |
| copy-pending | 22 | 48 | 48 |
| changed-roles | 2 | 4 | 4 |

This is the only sense in which the run reproduces received data. Nothing else
about the received package is claimed.

## 3. The four towers: one value, four ledgers

Each tower is reduced to a normal form by a leftmost-innermost spine reducer
written for this experiment, with identity-preserving rewriting so that a redex
can be traced to the contractions that made it available.

| k | source | iota leaves | events | normal form |
| ---: | --- | ---: | ---: | --- |
| 0 | `i` | 1 | 0 | `i` |
| 1 | `@@iii` | 3 | 5 | `i` |
| 2 | `@@@@iiiii` | 5 | 10 | `i` |
| 3 | `@@@@@@iiiiiii` | 7 | 15 | `i` |

**All four normal forms are the single leaf `i`.** As *values* the four third
slots are one value written four times; as *processes* they are four, because the
ledgers differ. That distinction is the whole point of the experiment, and the
contract refuses the identification explicitly rather than leaving it to a
reader.

## 4. Cuts, cut graphs and the frame operators

| k | cuts n | carrier dim 2n | cut graph | degrees | d_max | H0 |
| ---: | ---: | ---: | --- | --- | ---: | --- |
| 0 | 1 | 2 | P_1 | (0) | 0 | L (denominator one) |
| 1 | 6 | 12 | P_6 | (1,2,2,2,2,1) | 2 | L/4 |
| 2 | 11 | 22 | P_11 | (1,2,…,2,1) | 2 | L/4 |
| 3 | 16 | 32 | P_16 | (1,2,…,2,1) | 2 | L/4 |

In every tower the cut set is exactly the set of **prefixes of a total order**,
so the induced cut graph is a **path** in every case. The tower widens the
carrier and never widens the causal geometry. In every tower `J² = -I`, `H` is
symmetric, `H` commutes with `J`, every absolute row sum of `H` is at most one,
and `A = -JH` is skew symmetric: all four are admissible under the frame's own
checks.

The four carrier dimensions are two, twelve, twenty-two and thirty-two, and are
pairwise distinct. **No member of this family has a carrier of dimension four,
and none presents a three-plus-one split.**

## 5. The unit cell: the k = 1 frame, repeated and chained

For k at least one, the ledger of the k-th tower is the ledger of the k = 1 tower
repeated k times in the same rule order:

    i , i , s , s , k     (five events, source @@iii)

and the blocks are **chained**: each block's first event is made available by the
previous block's last event. Hence `events = 5k`, `cuts = 5k + 1` and
`carrier dimension = 10k + 2`. Every two extra iota leaves buy exactly one more
five-event cell.

## 6. Equal dimension is not the same frame

The received process `chain-and-single` has the same cut count and the same
carrier dimension as the k = 1 tower, and a different operator:

| | `chain-and-single` (received) | k = 1 tower (`@@iii`) |
| --- | --- | --- |
| events | 3 | 5 |
| cuts / carrier dim | 6 / 12 | 6 / 12 |
| degrees | (2,3,2,2,3,2) | (1,2,2,2,2,1) |
| H0 | L/6 | L/4 |
| Laplacian characteristic polynomial | x (x-1) (x-2) (x-3)² (x-5) | x (x-1) (x-2) (x-3) (x²-4x+1) |
| spectrum | integral: 0, 1, 2, 3, 3, 5 | not integral: the quadratic factor has discriminant 12 |

An equal cut count and an equal carrier dimension come with different operators,
and one spectrum is integral where the other is not. The repository already
records the control that equal operators do not identify processes; this run
records the converse case, that an equal dimension certainly does not.

## 7. The role obstruction, retained

Every one of the twelve received families' sources carries at least one aperture
leaf (`a`, `b` or `c`). **None of the four towers carries any.** The received
frame derives its `{}`, `[]` and `()` roles from explicit entry and exit policies
over declared apertures, so for the four towers as written there is no port and
the role declaration is **unbound**.

The four towers are therefore **not claimed to be well-formed received source
terms**. Whether binding a tower into a term that also carries declared apertures
yields an admissible received process is a separate question, and it is retained
here as an obstruction rather than repaired by quietly adding apertures.

## 8. Executed result and reproduction

The frozen run returned `ExternalExactPass`: **50 assertions in seven sections**,
in 0.131 seconds wall time, with peak process RSS 26,705,920 bytes (about
25.5 MiB). No failed check and no corrective replay. The retained evidence
carries every tower's ledger, cut masks, cut-graph edges, operator checks and
characteristic polynomial, together with the twelve-family reproduction and the
pinned digests.

From a checkout with Python 3.11 or later, choosing an output path that does not
already exist:

```sh
python3 -S experiments/four_iota_frames/checker.py --output /tmp/four-iota-frames-fresh.json
```

The contract enforces one route, 120 wall seconds, 180 CPU seconds, 256 MiB of
declared address space, 200,000 assertions, a 4 MiB output ceiling and one
correction replay. `RLIMIT_CPU`, `RLIMIT_FSIZE` and the wall alarm are installed;
no address-space ceiling is installed because no child process is launched, so
the repository's portability inventory is unaffected. An existing output is
refused. A pin mismatch yields `Failed`; a missing input or an exhausted budget
yields `Unknown`.

## 9. Repository scope and next boundary

This result belongs to research in `adva`. The received bytes, the machine
specifications and the library catalogue are unchanged, and no transport, receipt
or exchange is executed. Native admission `NotGranted`, native execution
`NotRun`, new transport `NotRun`. The Python function named `reduce` in the
checker is a finite term rewriter, not an Adva operation.

The next boundary is **not** decided, checked or claimed here. In particular,
whether a `J`-compatible metric forces an even inertia, which would make a
three-plus-one signature unreachable on that branch, is a separate question that
this run hands over rather than answers, and **no computation outside a contract
counts as a result of this repository**.

## Residual

What is established is a set of exact statements about four declared finite
source terms and one received finite process: that the four left-nested towers
with one, three, five and seven iota leaves all reduce to the single leaf `i`, in
zero, five, ten and fifteen local contractions; that their cut sets are the
prefixes of a total order, of size one, six, eleven and sixteen, so every induced
cut graph is a path and no tower widens the causal geometry; that their carriers
have dimension two, twelve, twenty-two and thirty-two, so the family reaches no
carrier of dimension four and no three-plus-one split; that all four satisfy the
frame's own `J`, `H`, row-sum and skewness checks; that the family grows by one
five-event cell per pair of iota leaves; that the k = 1 member shares its cut
count and carrier dimension with a received process while carrying a different
operator, whose spectrum is irrational where the received one is integral; and
that the four towers as written carry no aperture leaf, so the received frame's
declared roles have nothing to bind.

What is not established: whether binding a tower into a term that carries
declared apertures yields an admissible received process; whether any tower can
be placed on a grid or a manifold; whether the tower index is a level, an energy
or a time; and anything at all about **physical spacetime**. The four towers are
**not claimed to be well-formed received source terms**, and their common normal
form is a fact about values that licenses no contraction, memoisation or reuse.
