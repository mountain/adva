# Research 0142: question-indexed evidence and finite distinction

Status: completed finite external calibration; native formation/transport obligations remain open.
Base: main `24d7275971cfd61fabc3270ac2a71b79df377598`, after merging #130--#141.

## Origin and the corrected question

Mingli Yuan asked how different judgments should be distinguished within
Adva's three-computation framework, and whether the vocabulary to express
distinction already exists. On 2026-09-06 he authorized the proposed next
step: let one finite instance carry explicitly different judgments and
check that evidence cannot silently answer a different question.

This is a continuation of Research 0141, not a rerun of its eight-case
floating-point experiment or its unresolved native k28 bit-pattern audit.
Research 0131 supplies `interpret-question-form`, `observe`, `verify`, and
`judge` as working responsibilities. Research 0132 keeps judgment separate
from `switch`, `reorganize`, and `revise`. We reuse these distinctions.
Research 0123's arithmetic-universality and hypothesized-arithmetic-truth
remain Proposed. The full 0090 coverage and 0092 promotion obligations are
not discharged, and unknown-syntax-building remains paused.

The assistant's earlier transition from "a scalar result of one" to "a
multiplicative-unity witness" needed a sharper correction. Research 0107
already says that the final value and execution transport residual are
different objects. Even exact scalar unity is not native transport unity.

| Judgment | Question and carrier | Evidence boundary |
|---|---|---|
| Binary64 point equality | Do the two ordered evaluations produce the same finite binary64 scalar at this input? | External recomputation, plus a separately bound historical native observation for k27 |
| Rational point equality | Are the exact rational results equal at the declared input? | External exact arithmetic and a replayable difference |
| Native formation A0 | Does the actual signed formation boundary equal the declared boundary? | Requires a bound native formation carrier; a well-formed external AST does not provide it |
| Native transport M1 | Does the declared transition have unit exact transport and satisfy its guards? | Requires the native transition/proof carrier and verification; neither scalar equality nor a stored evaluation report provides it |

There is no contradiction between binary64 point equality being accepted
and rational point equality being refuted. They ask different questions.
For the proposed product-to-one change, the exact counterexample already
refutes exact value preservation at the declared input. Native witness
availability remains Unknown separately; missing evidence must not hide
a counterexample that has already been obtained.

## Three readings of every judgment

The same judgment keeps all three readings rather than assigning one
judgment kind to each of three machines:

- Construction K: ordered expression pair, exact inputs, admitted grammar,
  declared types, and relation obligations.
- Time t: the ordered external evaluation trace, verification work, and
  explicit references to the retained native run history where available.
- Space X: observation rule, the finite point being observed, which
  distinctions the observation loses, and the retained residual.

These are an external organization of the question. No native SourceId,
OccurrenceId, ProgramSlice, or certificate is created by Python. Native
TriadicObserverTransitionV0 is not invoked. That API uses declared policies
over checked source fibres; K/t/X labels are not intrinsic wire types.
Syntax, semantics, and pragmatics also remain cross-cutting responsibilities,
not a bijective renaming of the three readings.

The missing native questions use descriptive research domain labels for
signed formation boundaries and exact polynomial transport. Their domains
and quantifiers are not inherited from scalar rational equality. The attached
expression pair only proposes a source for a future carrier; it does not
instantiate a native template or declare new Rust types.

## Frozen finite family and imported assumptions

The pre-execution contract is
[`0142-distinguish-run-contract.json`](0142-distinguish-run-contract.json).
It permits exactly three instances and one route, with no candidate search.
For k=27 and the fresh reuse k=29, compare

```
P_k = mul(x,y),  x = 1 + 2^-k,  y = 1 - 2^-k
R_k = constant 1
```

The mathematical reference is the elementary identity
`(1+a)(1-a) = 1-a^2`. The two intended exact residuals are `-2^-54` and
`-2^-58`. Both factors are nonzero and exactly binary64-representable at
these k. The frozen observation is ordinary separate binary64 operations,
not exact rational arithmetic or a general floating-point theorem.

The control compares constant 2 with constant 2. Its result is two while
its external quotient is one. Native A0 and M1 remain separate obligations.
This control cannot manufacture a three-hole native template or transport.

The only native evidence imported is the unchanged saved k27 program and
its Research 0141 report, with their fixed hashes and exact embedded-program
binding. Attaching that report records an earlier native observation; it is
not a fresh execution, an independent replay of the Rust evaluator, or a
native certificate for the new question. The k29 native observation is
NotRun. The k28 parsing/reporting discrepancy remains open.

## Proposed composite word: distinguish

Purpose: construct a question-bound distinction that can be checked and
reused without transferring a verdict across an undeclared boundary.

Input: an ordered expression pair, exact environment, question/relation,
domain, observer, quantifier, finite budget, and optional historical evidence.
Output: scoped judgments, traces and values, a separating residual where
found, evidence-applicability decisions, and remaining native obligations.

The working expansion is
`interpret-question-form -> observe -> verify -> judge`.
It is implemented by this external finite runner, not by calling four
native language primitives. No new Rust builtin is added.

The scope coordinate binds the interpretation fields and ordered expressions;
the human-readable name is excluded. Renaming a presentation therefore does
not authorize extra fuel or change which question an old receipt can answer.
A scope digest is a content coordinate, not authentication or semantic identity.

Refusals include changed observer/domain/quantifier, changed inputs, an
untransported expression-history change, forged evidence, and scalar-to-native
certificate promotion. A refusal of evidence applicability does not by
itself refute the target proposition. In contrast, a checked nonzero exact
difference does refute the exact equality question at that point.

The history-binding policy is deliberately conservative. A future checked
transport could reuse extensional evidence across different expression
histories. This experiment does not prove that all equality judgments must
invalidate every syntactic change.

No distinction found under the declared point observation means only that
the observation did not separate the pair. It is not global program identity,
full-domain equality, or a coherence/M6 filler. Exhausted verification fuel
gives Unknown; missing native carriers give their own explicit Unknown.

Status: **Proposed composite working vocabulary with a finite external
calibration**. No claim of
increased expressive power, speedup, universal grammar reliability, or real
user acceptance is made.

## Validation and comparison

The evidence checker recomputes from the frozen question rather than trusting
an embedded verdict or expected-answer field. The producer and checker use
different evaluation traversals within the same Python runtime; this is not
an independent implementation of Python or a proof of the checker.

Adversarial controls cover evidence moved to another observer, domain,
quantifier, ordered AST, or input; changed verdict/residual; native A0/M1
promotion; and stale k27 evidence used for k29. Presentation-only rename
must remain admissible, while zero local verification fuel remains Unknown.

The comparison is bare-boolean forwarding versus question-indexed replay on
the same finite evidence-promotion attempts. The count measures inadmissible
reuse of support, not a count of universally false mathematical propositions.
Formation and replay costs are included. No advantage over an ordinary typed
validation envelope is claimed.

## Execution checkpoint

One supervised execution completed with exit code 0. No implementation-repair
replay or native invocation was used. The single run included construction,
validation, adversarial controls and one serialized-payload replay.

| Instance | Binary64 equality at the declared input | Exact rational equality | Exact left-minus-right residual | Native A0 / M1 |
|---|---|---|---|---|
| product-k27 versus 1 | Confirmed | Refuted | `-1/18014398509481984` = `-2^-54` | Unknown / Unknown |
| product-k29 versus 1 | Confirmed | Refuted | `-1/288230376151711744` = `-2^-58` | Unknown / Unknown |
| constant 2 versus constant 2 | Confirmed | Confirmed | 0 | Unknown / Unknown |

All six point-observation receipts passed independent recomputation.
Here **Accepted means that a receipt was validated**; a validated `Different`
receipt still gives `RefutedAtDeclaredInput` for the equality proposition.
The two product-to-one proposals are therefore refuted at their declared
inputs. The nonunit control confirms only its point equality and external
quotient one, without authorizing a native action.

All twelve control expectations were met. Ten inadmissible support-reuse
attempts were rejected, including cross-observer/domain/quantifier/history
reuse, forged verdict/residual and scalar-to-native promotion. The bare
answer-forwarding control admitted all ten without an applicability check.
This is a negative control supplied by the experiment, not a bug report
against an existing native Adva checker or a new learning algorithm.
Presentation-only rename remained Accepted; zero checker fuel gave Unknown.

The saved report's `serialized_replay.coverage` uses "recomputed" broadly:
all twelve controls were **rechecked**, while arithmetic recomputation occurs
only after scope admission and with available fuel. Scope-mismatch refusals
and the zero-fuel result do not claim an arithmetic evaluation. This wording
clarification preserves the original report bytes and its payload hash.

The frozen contract SHA-256 is
`517feb7c78e5d36121fde30f8a69f0cac5e51a613dc1a827d800b015b8c446a1`.
The exact executed source SHA-256 is
`2f1c1e90e3dc1ffd11c8e6d7630eed6bdf2956df7ea3492f144631c6b5d1b842`.
See [`0142-distinguish-evidence.json`](0142-distinguish-evidence.json) for
the complete file manifest, and [`0142-evidence/report.json`](0142-evidence/report.json)
for all questions, evidence scopes, traces, judgments and control results.

## Measured cost and finite boundary

| Measurement | Actual |
|---|---:|
| Supervised process wall time, including startup and save | 133.531 ms |
| Construction, including record formation and historical binding | 5.554 ms |
| Validation and twelve controls | 16.495 ms |
| Mathematical payload serialization | 10.845 ms |
| Serialized payload verification/replay | 43.290 ms |
| Fresh k29 construction | 1.640 ms |
| Fresh k29 first verification | 2.900 ms |
| Charged work | 282 of 2,000 units |
| Construction / validation / replay work | 58 / 116 / 108 units |
| Largest supervised child RSS, including the Python runner | 15,872 KiB = 15.5 MiB |
| Python traced-allocation peak before final encoding/save | 994,034 bytes |
| Saved report size | 94,565 bytes; not a memory measurement |

Fresh-instance timings are subsets of construction/validation; do not sum
them again. Final cost-metadata encoding and disk persistence are included
in supervised wall time but not separately timed. Name-record formation is
included in construction, not isolated as a separate benchmark. Serialization
and replay are measured globally, not apportioned to k29. Research, static
review, source writing and network persistence are outside those process
timings and were not measured as a complete wall-time budget.

The process had a five-second wall/CPU limit, 256 MiB address-space limit,
128-bit rational-component cap, bounded AST and 256 KiB input/report caps.
No search candidates were generated. All verification and replay use one
shared work counter; no fuel reset or second invocation occurred. The coarse
work units are not CPU instructions, energy or a latency model. The comparison
does not establish acceleration over a conventional typed checking envelope.

## Reproduction and continuation boundary

Run from the repository root with Python 3.11 or later on Linux:

```sh
timeout 5s python3 experiments/judgment_distinction/calibration.py \
  --contract docs/research/0142-distinguish-run-contract.json \
  --repo-root . \
  --output target/judgment-distinction-report.json
```

Use a fresh output path. The executable enforces the contract's finite
grammar, arithmetic, resource and artifact limits. One complete build,
validation and serialization replay is permitted; there is no new native
invocation or automatic continuation. Hard termination may prevent saving
a partial report, which must then remain an explicit missing checkpoint.

The practical intended help is for Mingli and subsequent agents to inspect
why an observation supports one question and fails to support another,
without losing the known counterexample or pretending native evidence exists.
Jiamin's task acceptance and real-world usefulness remain unmeasured.

The next smallest language-oriented continuation is to select **one declared
observer change** and specify the preservation relation required to transport
an old judgment. The present conservative gate rejects changed scope, even
when a future independently checked transport might justify reuse. Such a
step would connect `distinguish` with the existing `switch` vocabulary without
weakening its boundary. The separate native k28 bit-pattern audit remains an
engineering task; it is not silently substituted for this language question.
