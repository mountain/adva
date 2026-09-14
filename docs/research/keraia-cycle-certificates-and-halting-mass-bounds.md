# Keraia cycle certificates and halting-mass bounds

Status: external bounded calibration and a conditional exact-cycle argument,
2026-09-14. Base main: `0ce30649d9343ace0085f79ed75d0198f947b1d0`.

Authored by ChatGPT (OpenAI). Mingli Yuan supplied the research direction;
his GitHub account is the authorized submission proxy, not evidence of human
authorship, review, endorsement or correctness. The assistant implemented
and reviewed both sides of the comparison. Different kernels provide a
cross-check, not independent human review or an institutional endorsement.

## Question and fixed scope

The [previous read-boundary calibration](keraia-read-boundary-and-weighted-prefix-search.md)
reduced repeated prefix execution but left the upper halting-mass bound at
one. This step asks whether finite certificates can remove an actual part
of the unresolved mass, and whether continuation still preserves cost and
probability when several reads and delayed returns are present.

We retain exactly the previous observation profile,
`keraia.appendix-b.cbn-whnf.read.v0`, and its semantic step convention.
Michael Stay's [Very Simple Chaitin Machines for Concrete AIT](https://arxiv.org/abs/cs/0508056)
is the source background, particularly sections 8–9 and Appendix B. The
previously recorded distinction between weak-head observation and full
normalization remains. The historical JavaScript is not executed here, and
optimal prefix universality is not transferred to this profile.

The [frozen contract](../../experiments/keraia_cycle_mass/contract.json)
declares all 65,535 binary words of lengths 0–15 at fuel 128; 626 distinct
complete program trees occur. Six sequence programs make two or three reads
after zero, four or twelve identity delays. Every data suffix through one
bit beyond the requested read count is checked at fuel 2, 8, 32 and 128:
552 fixture rows altogether. Seven diagnostic programs exercise cycles,
growing stacks, discarded loops, returned lambdas and a one-read selector.
The longest fixture word has 141 bits; this is not exhaustive search to 141.

The old machine, syntax compiler and named oracle are imported unchanged.
Both old and new executable sources are included in the pre-run snapshot
and source manifest. There is one primary campaign and one fresh-process
replay, with no failed attempt or correction in this round.

## A finite certificate for an entire suffix cylinder

Write an execution frame as

\[
s=(\text{control},\text{ordered stack},\text{cursor},
   \text{profile},\text{cost convention}).
\]

The candidate supplies a source prefix, a bounded trace from its independently
reconstructed initial frame, and a cycle-entry index. Each trace edge costs
one original semantic step. The receiving checker uses the string-marking
compiler, reconstructs named terms from closed de Bruijn syntax, and checks
beta contraction with capture-avoiding named substitution. It does not call
the proposer's beta or step kernel. Frame parsing refuses open terms,
incorrect field shapes and Boolean/float substitutes for integer fields.

The receiver checks a positive-length recurrence `s_j = s_k`, with `j < k`,
no read or return on the cycle, and all supplied source bits consumed by its
endpoint. Reading may occur in the finite stem before `j`. Search allowance
bounds the supplied trace, but spent fuel is not forgotten when comparing
finite executions. Fuel is omitted from the recurrence frame specifically
because this certificate concerns the underlying unbounded execution;
finite-budget exhaustion remains an observation of that execution.

**Conditional argument.** Fix a source prefix `p` with such a checked trace.
Its first complete tree and all bits read in the stem are unchanged under
any appended suffix `u`. Every internal transition in the cycle depends
only on the full frame and reads no new bit. The finite trace therefore
reaches the same recurrent frame on `pu`. Determinism repeats the same
positive-length internal cycle indefinitely, without reading or returning.
Consequently no finite extension of `p` is an accepted code. Under fair input
bits its entire cylinder has nonhalting mass `2^(-|p|)`.

This is induction on a verified finite transition cycle, not inference from
a long unsuccessful run. The argument is conditional on the declared
interpreter semantics. Its general form is not a native Rust theorem; this
run checks its concrete premises with two implementations.

Let `Delta = lambda x. x x`. The code `111001001100100` represents
`Delta Delta`. The receiver verifies its two-edge cycle: push the argument,
then contract beta to recover the entire initial frame, including the empty
stack and cursor 15. The direct 128-step run remains `UnknownFuel`; its
separate cycle certificate supplies the stronger nonhalting conclusion.

## The resulting probability partition

At depth 15 the exhaustive direct run reports:

| Outcome | Code words |
|---|---:|
| `Halt` | 508 |
| `NeedInput` | 391 |
| `NeedSyntax` | 13,495 |
| `Overflow` | 51,140 |
| `UnknownFuel` | 1 |

The independent named oracle agrees on status, consumed length, ordered
reads and weak-head output for every word. Prefix search finds exactly the
same accepted-code ledger, visiting 14,395 nodes. Checking the one unresolved
runtime cycle yields a disjoint terminal partition:

| Cylinder class | Count | Exact mass |
|---|---:|---:|
| Accepted | 508 | `26078/32768` |
| Certified nonhalting | 1 | `1/32768` |
| Pending input | 254 | `254/32768` |
| Incomplete syntax | 6,435 | `6435/32768` |

These masses sum to one. Terminal cylinders, rather than all overlapping
incomplete words from direct enumeration, are the objects being summed.
Writing `H_profile` for eventual halting probability under this profile,

\[
\frac{13039}{16384}\le H_{\rm profile}
\le\frac{32767}{32768}.
\]

Before the cycle certificate, the same length/fuel cut gives upper bound one
and unresolved mass `6690/32768`. Certification removes exactly `1/32768`,
leaving interval width `6689/32768`, about 20.41%. This is only about 0.00305
percentage points of upper-bound improvement. The lower bound's improvement
over the earlier length-11 experiment comes from the larger enumerated
family, not from the cycle certificate.

The exhaustive rows are streamed into ordered digests; the accepted rows,
unresolved frontier states and full positive traces are retained explicitly
in [the evidence](../../experiments/keraia_cycle_mass/evidence/attempt-1/).
The finite certificate makes no claim to account for every divergent branch.

## Multiple reads, real time cuts and a conditional exact answer

Let `J = I R`, and let `B = (J I) I`. It reads one bit and returns `I`
regardless of that bit. Using `J` also avoids accidentally constructing the
reserved binder tree when composing raw Keraia trees. The two compilers and
expected read counts check the actual generated syntax.

The sequence programs are nested applications of `B`, ending in `I`, with
additional outer identity applications as delays. Complete-data costs are:

| Reads | Identity delays | Program bits | Total semantic steps |
|---:|---:|---:|---:|
| 2 | 0 | 45 | 17 |
| 2 | 4 | 69 | 25 |
| 2 | 12 | 117 | 41 |
| 3 | 0 | 65 | 25 |
| 3 | 4 | 89 | 33 |
| 3 | 12 | 137 | 49 |

Direct, checked-cache and streamed continuation rows agree for all 552
cases, including original spent/remaining fuel and ordered read traces.
Unrequested trailing data are reported as unread, not executed. Of these
rows, 342 actually exhaust their small allowance, so the time checks are
not vacuous. At fuel 128 every exact-length data word is accepted, every
shorter word is pending input, and every longer word has unread data.
The `2^n` accepted continuations preserve the entire program-cylinder mass;
equal output `I` does not justify counting only one representative.

A separate program `Q = (J (Delta Delta)) I` has exact conditional halting
probability one half, given its complete program tree. Its program code is
`11111000011100100110010011000` (29 bits). Input `0` selects the loop;
input `1` returns `I`. The receiver verifies the zero branch's eight-edge
trace, with its sole read in the stem and a two-edge input-free cycle
beginning at edge 6. The one branch returns after 7 steps. Thus the fair
continuation cylinder divides into equal accepted and certified divergent
halves, with no unresolved mass **for this fixed conditional experiment**.
The accepting code has weight `2^(-30)` in the global code distribution,
not global weight one half. This fixture lies outside depth 15 and is kept
separate from that exhaustive partition.

## Refusals and the limit of exact recurrence

The program `(lambda x.(x x) x)(lambda x.(x x) x)` returns repeatedly to the
same control expression while its argument stack grows. Its retained
head-only comparison shows an empty stack in one frame and an additional
argument in the other. There is no checked complete-frame cycle in the
128-step search, so it remains `UnknownFuel`. This is a counterexample to
the proposed shortcut of treating a repeated head alone as an exact cycle;
the run does not infer divergence from that shortcut.

Two positive-return controls also matter: `K I (Delta Delta)` discards the
loop, and `K (Delta Delta)` returns a lambda containing it. They halt after
5 and 3 steps respectively under weak-head observation. Searching for a
loop subexpression would therefore be unsound.

Fifteen altered or invalid receipts are refused: changed source/profile/cost,
Boolean or invalid cycle indices, zero-length cycles, altered initial or
final control, stack and cursor changes, float cursors, a proposed cycle
through a read, a repeated returning frame, and a different receiving
allowance. These are expected negative controls, not failed campaigns.

## Relation to Q4 and the next useful boundary

This step supplies an elementary four-corner relation that can be stated
precisely. Let `E_u` append an unconsumed suffix and let `T_internal` be one
non-reading, non-returning transition. On its declared domain,

\[
T_{\rm internal}\,E_u = E_u\,T_{\rm internal}.
\]

The extension leaves the full residual frame unchanged, and both routes
charge the same step. Composing these squares gives the internal-transition
part of the suffix-independence argument above; stem reads are handled
separately because their bits are already fixed by the supplied prefix.
The domain restriction is essential: a demanded read can distinguish an
empty input from an extension, and returning with extra data changes `Halt`
to `Overflow`. This equation does not authorize arbitrary read/return
commutation.

This is a candidate bridge to Q4-style transport questions, not an identified
native Q4/M6 cell or a commutativization of ACS. Exact-state recurrence uses
ordinary deterministic execution and does not need a new Q4 mechanism.
If a geometric quotient is to improve it, the quotient must justify future
simulation and preserve input, history and cost obligations. The growing
stack control shows why observational head equality is insufficient.

The next useful finite question is whether a separately checked invariant
can certify some growing-state branches that exact recurrence misses. That
would enlarge the class of excluded cylinders. It is not automatically
launched here and does not supply a computable general halting tail or a
convergence-rate result for Chaitin's Omega.

## Execution and retrospective

The primary and fresh process each pass 264,671 assertions and consume
5,004,990 counted host-work units, within the 20-million child limit.
Measured inner wall times are 2.80 and 2.88 seconds, with peak RSS about
20.6 and 20.8 MiB. The conditional two-process campaign permits at most
40 million child work units; Linux CPU/memory/output and outer wall limits
also bound evidence handling. The deterministic evidence, including work
counters, agrees exactly after excluding elapsed time and RSS.

The direct timing includes the independent oracle and the prefix timing
does not, so their ratio is not reported as a speedup. This implementation
certifies cycles after the bounded frontier is collected; it has not yet
measured an online cycle-pruning speed improvement. Native Rust and the
full repository suite were not run for this external-only addition.

The original acceleration intuition receives limited support: explicit
state plus a receiving proof can remove some uncertainty, beyond reducing
duplicate execution. The decisive addition is a certificate that excludes
all future suffixes, while preserving the cases where more input or a
different stack still matters. The present global reduction is small;
broader certified invariants, and the relation to a fixed optimal machine,
remain the substantive obstacles.
