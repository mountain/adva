# Research 0264: one final event ideal does not determine a schedule word

Status: bounded native instantiation of the Proposed `quotient-query-gate`
from [Research 0262](0262-quotient-query-gate-and-nonunique-exact-lifts.md).
This note adds no stable API and no claims-registry entry.

The executable witness is
[`event_ideal_query_gate_native.rs`](../../crates/adva-lisp/tests/event_ideal_query_gate_native.rs).

## 0. Frozen question

Research 0259 found that event-membership probes separate the ideals of one
fixed carrier but collide across identity- and history-rich carriers. Research
0263 discharged the source-fibre part with exact Rust occurrence identities.
The remaining narrow question is whether the existing Rust process boundary
already exposes two legal native inputs with one event-ideal image and
different retained history.

This round freezes:

| field | value |
|---|---|
| objects | one checked three-event causal diamond and one checked three-independent-event reuse fixture |
| exact input | a certified schedule receipt `(word, cut_path, final_ideal)` beside the canonical whole `ProgramSlice` |
| quotient | `q(receipt) = receipt.final_ideal` |
| proposition sort | finite subsets of the enumerated legal schedule receipts |
| accepted form | a union of complete final-ideal fibres |
| rejected form | membership that depends on the first event of the schedule word |
| result grammar | `Descends(T)` or `NonSaturated(left,right)` |
| arithmetic domain | none; exact `NodeId` values and finite sets only |
| search budget | exhaustive declared enumeration of 2 plus 6 schedule words, below 100,000 |
| verification budget | one full ordered-pair scan per query, below 30 seconds |

A schedule word is explicit route data. It is not the canonical event vector of
a `ProgramSlice`, and `ProgramSlice.event_history` remains node-associated
structural history rather than the chosen route order.

## 1. Native construction

Rust performs every semantic step:

1. parse, link and compile each module;
2. keep the native `NodeId` values assigned by the checked diagram;
3. advance every declared word one event at a time with
   `advance_causal_cut`;
4. require every causal-step certificate to be certified;
5. retain the entire sequence of native completed cuts as `cut_path`;
6. construct and certify the canonical whole `ProgramSlice`; and
7. compare every receipt's final ideal with that exact slice's upper cut.

No Python adapter creates an event, identity, ideal or schedule receipt.

The first fixture has exactly the two legal linear extensions
`0,1,2` and `1,0,2`. The reuse fixture has three independent operations and
all six permutations are checked. Thus the finite enumeration is complete for
both declared fixtures; it is not a general schedule enumerator.

## 2. Result

All eight schedule receipts are accepted step by step. Within each fixture:

- every receipt has the same final completed event ideal;
- every receipt agrees with the certified whole slice's upper completed cut;
- at least two receipts retain different schedule words and different cut
  paths;
- selecting the entire final-ideal fibre returns
  `Descends({final_ideal})` and exact pullback; and
- selecting receipts by which native event occurs first returns
  `NonSaturated(left,right)`.

The retained obstruction pair therefore has equal event-ideal image but
different native `NodeId` order and different certified intermediate cuts.
A final-ideal observer may answer final-ideal-saturated questions, but it may
not answer a route-order question without changing that question.

This is the event-ideal instance left open by Research 0259. It does not repair
cross-carrier source or occurrence collisions; it isolates one history loss
already present inside a single checked program.

## 3. Counted cost and replay

The declared enumeration contains **8 schedule candidates**. Native receiving
performs **22 certified causal advances**: four steps across the two diamond
words and eighteen across the six reuse words. Two whole program slices are
constructed and certified.

The quotient gate performs:

| fixture | accepted-query units | rejected-query units |
|---|---:|---:|
| two schedules | 6 | 4 |
| six schedules | 42 | 36 |
| total | **48** | **40** |

The total gate cost is **88 ordered-pair/pullback units**. No candidate family
is generated beyond the eight declared schedule words.

Replay:

```sh
cargo test -p adva-lisp --test event_ideal_query_gate_native
```

The preceding Research 0263 commit made the Rust research-test boundary move
past the active symbol-surface successor base. Rust formatting, Clippy and the
whole workspace suite passed, while Python correctly refused that stale base.
This branch therefore adds `contract-v11.json` with the new Rust-boundary
commit as base; pins, execution limits and run authorization remain unchanged.
This is the one necessary correction replay, not a relaxed check or renewed
fuel.

Wall time, CPU time and peak RSS are not measured by these tests and must not
be inferred from repository size or workflow duration.

## 4. Vocabulary and boundary

No new word is introduced. This is an event-ideal/schedule-history profile of
the already Proposed `quotient-query-gate`.

The finite result does **not**:

- identify two schedules or make schedule order part of `ProgramSlice`;
- say that equal final ideals imply equal source, occurrence or history;
- authorize event contraction, a quotient program or a rewrite;
- produce a local or global M6 filler;
- prove native `free`, Close, arithmetic universality, hypothesized
  arithmetic truth, or universal grammar; or
- establish practical value for Jiamin.

It helps Mingli and later agents state one boundary without conflation:
canonical interval equality can coexist with different certified routes. The
gate permits questions invariant under that forgetting and retains a replayable
counter-pair for a route-sensitive question.

The next minimal obligation is receiver separation: serialize the two schedule
receipts with exact diagram and slice bindings, then have an independent
receiver recover `Descends` versus `NonSaturated` without recompiling the
program or minting identities.
