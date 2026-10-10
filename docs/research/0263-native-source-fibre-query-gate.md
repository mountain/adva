# Research 0263: a checked source fibre does not erase occurrence identity

Status: bounded native instantiation of the Proposed `quotient-query-gate`
from [Research 0262](0262-quotient-query-gate-and-nonunique-exact-lifts.md).
This note adds no stable API and no claims-registry entry.

The executable witness is
[`quotient_query_gate_native.rs`](../../crates/adva-lisp/tests/quotient_query_gate_native.rs).

## 0. Frozen question

Research 0259 left a precise obligation: use a Rust-checked
`ProgramSlice`, preserve its source, occurrence, path and history
coordinates, and test an actually identity-sensitive proposition rather than
reconstructing semantic identities in Python.

This round freezes:

| field | value |
|---|---|
| objects | two compiled and validated Adva functions, one copying one input and one copying two inputs |
| exact carrier | the upper-cut `TriadicCutIncidenceV0` values embedded in each checked `ProgramSlice` |
| quotient | `q(o) = o.source : Occurrence -> SourceId` |
| proposition sort | finite subsets of upper-cut incidence indices |
| accepted form | a union of complete source fibres |
| rejected form | a set whose membership differs inside one source fibre |
| result grammar | `Descends(T)` or `NonSaturated(left,right)` |
| arithmetic domain | none; exact Rust identifiers and finite sets only |
| search budget | zero candidates; two declared fixtures; at most five incidences |
| verification budget | one full ordered-pair scan per query, below 100,000 units and 30 seconds |

The source quotient is an observation map. It is not an equality rule for
occurrences.

## 1. The finite criterion

For a finite occurrence carrier (C), source set (S), quotient
(q:C	o S), and proposition (Psubseteq C), the gate checks

[
q(c)=q(c') Longrightarrow
igl(cin P Longleftrightarrow c'in Pigr).
]

When this holds, the test constructs

[
T={q(c)mid cin P}
]

and independently checks the exact pullback equation
(P=q^{-1}(T)). It returns `Descends(T)`. Otherwise it retains the first
pair ((c,c')) with equal source and unequal membership as
`NonSaturated(c,c')`.

The implementation scans every ordered pair even after finding an
obstruction, so the counted finite cost is independent of witness order.

## 2. Native construction

Rust performs every semantic step:

1. parse, link and compile each module;
2. validate the resulting shared program diagram;
3. construct the transition from the empty completed past to the full checked
   cut;
4. certify the embedded complete `ProgramSlice`;
5. read `SourceId`, `OccurrenceId` and `OccurrencePath` directly from
   its upper incidences; and
6. retain and count the checked `HistoryEvent::Copy` records.

No Python adapter creates, renames or reconstructs an identity.

The first fixture has four upper incidences with source multiplicities
(2,1,1) and one copy-history event. The reuse fixture has five incidences
with multiplicities (2,2,1) and two copy-history events.

## 3. Result

Three copied source fibres are tested in total: one in the first fixture and
two independent fibres in the reuse fixture.

For every copied fibre:

- selecting the whole fibre returns `Descends({source})`;
- pulling that quotient singleton back recovers exactly the selected
  incidences;
- selecting only one copied occurrence returns `NonSaturated(left,right)`;
- the retained pair has the same exact `SourceId`;
- its two `OccurrenceId` values differ; and
- its two `OccurrencePath` values differ.

Thus a source-level proposition may descend while an occurrence-level
singleton cannot. The failure is not a tool error or a negative mathematical
fact about the occurrence. It is a type-correct refusal to answer that
identity-sensitive question on the coarser source carrier.

## 4. Counted cost and replay

The one-copy fixture performs 20 units for the accepted query and 16 for the
rejected query, for 36 units. Each of the two copied fibres in the reuse
fixture performs 30 accepted-query units and 25 rejected-query units, for 110
units. The total is therefore **146 finite comparison/pullback units**, with
zero search candidates. The first CI launch stopped at `rustfmt --check`
before compiling or executing the test. The single permitted correction
applied only the formatter's mechanical diff; the frozen objects, queries and
counts did not change.

Replay:

```sh
cargo test -p adva-lisp --test quotient_query_gate_native
```

The repository workflows additionally run formatting, clippy and the whole
workspace test suite. Wall time, CPU time and peak RSS are not measured by this
test and must not be inferred from repository size or CI duration.

## 5. Vocabulary and boundary

No new word is introduced. This is a native source-fibre instance of the
already Proposed `quotient-query-gate`; it does not revise that definition or
promote it to a stable term.

In particular, the result does **not**:

- identify two occurrences that share a source;
- authorize contraction, forgetting, a quotient program or a rewrite;
- test the event-ideal projection from Research 0259;
- turn local image equality into an M6 filler;
- prove native `free`, Close, arithmetic universality, hypothesized
  arithmetic truth, or universal grammar; or
- establish practical value for Jiamin.

It helps Mingli and later agents carry one precise question through an
observer change: source-saturated questions survive; occurrence-sensitive
questions stop with an exact native counter-pair instead of silently changing
meaning.

The remaining 0259 obligation is narrower, not discharged: repeat the same
test for the **existing event-ideal projection**, if the current Rust boundary
exposes two legal inputs with one event image and different exact identity or
history. If it does not, the correct next result is `Unknown` with that
missing native projection recorded.
