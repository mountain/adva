# Three-Layer Research Machine V0

Status: bounded executable research instrument following
[0023](0023-exact-program-slice-wp2.md),
[0024](0024-exact-program-slice-composition-wp3.md),
[0060](0060-triadic-observer-program-slice-bridge.md), and
[0073](0073-checked-boundary-return-feedback-no-go.md).

The implementation is [`adva.research`][machine] and its executable calibration
is [test_research_machine.py][fixture].

[machine]: ../../python/adva/research.py
[fixture]: ../../tests/python/test_research_machine.py

This note introduces no stable feedback, recursion, bracket normalization,
logic, topology, compiler, hardware, or universal-computation semantics.

---

## 0. The engineering question

The present global picture has three layers:

| reading | executable carrier | retained information |
|---|---|---|
| interface / three-computer | `TriadicCutObservationV0` | three opposite-pair readings, own-role complement, source-free residual |
| program space | `ProgramSlice` | exact endpoints, events, boundaries, through wires, occurrences, history, graft intersections |
| through-time | checked causal steps plus a schedule | the selected linear path through the same partial order |

The local question is whether these can form one useful machine before the
future language and feedback semantics are stable. Version zero answers yes,
provided that the result is an auditable experiment package rather than a new
semantic authority.

## 1. Interpretation cell

For nested checked cuts \(C\subseteq D\), an interpretation cell is

\[
\mathcal I(C,D;s)=
\bigl(O(C),\operatorname{Slice}(C,D),s,O(D),\tau(C,D)\bigr),
\]

where:

- \(O(C)\) and \(O(D)\) are exact triadic cut observations;
- `Slice(C,D)` is the complete canonical spatial residual;
- \(s\) is one declared linear schedule, certified step by step by Rust; and
- \(\tau(C,D)\) is the exact Rust triadic observer transition and certificate.

The machine checks

\[
\operatorname{set}(s)=
\operatorname{set}(\operatorname{events}(\operatorname{Slice}(C,D))).
\]

It deliberately does not require schedule order to equal canonical diagram
order. Independent events therefore retain their temporal distinction while
sharing one spatial cell.

## 2. Serializable research code

`ResearchCodeV0` records only replay inputs:

- one or more Lisp modules;
- an exact module and function name;
- a bijective assignment of the three inputs to construction, space, and
  time;
- an initial completed past and one finite event schedule;
- an optional global fuel bound; and
- an optional finite replay request with an explicit boundary comparison.

Its JSON decoder rejects extra or missing fields, non-string source and domain
entries, Boolean event IDs, noninteger fuel, repeated schedule events, and
malformed feedback requests. Deserialization is input validation, not semantic
authorization. Compilation, cuts, steps, slices, and observations are derived
again by Rust on every run.

## 3. Bounded replay, not semantic feedback

For `exact_frontier`, the machine first proves on one cell that

\[
F_C=F_D.
\]

It may then replay the same checked finite experiment for a declared number of
epochs. The static `NodeId` values remain unchanged. Each dynamic record is
only

\[
(\text{epoch},\text{ordinal},\text{static NodeId}),
\]

a nonsemantic coordinate inside the run artifact.

This construction establishes repeatability of an external experiment
protocol. It does not establish a feedback morphism \(D\to C\), fresh semantic
occurrences, event re-enabling, or cyclic execution.

For `exact_cut`, every nonempty finite-DAG interval is rejected. Since the
completed-past rank strictly increases,

\[
C\subsetneq D \Longrightarrow |C|<|D|,
\]

the only literal endocut is the empty identity interval. This makes the
missing feedback operator observable rather than silently fabricating it.

## 4. Verdicts

| verdict | meaning in V0 |
|---|---|
| `supported` | every requested finite check completed and all exact residuals are retained |
| `counterexample` | reserved for a checked witness refuting a future explicit conjecture |
| `obstruction` | the supplied program, schedule, or endpoint condition fails a finite check |
| `not_representable` | the requested positive object is excluded by the declared PSC0 representation boundary |
| `fuel_exhausted` | a partial exact cell is returned; no impossibility conclusion follows |

The distinction is operationally important. Failure to finish is not a
counterexample, and failure of exact-cut return is stronger and more local
than a general no-go theorem about every future feedback calculus.

## 5. Executable calibration

The bounded fixture checks:

1. read-only Python access to Rust triadic transitions and exact composition;
2. three frontier-matched replay epochs with fifteen distinct research-event
   references and the same five retained static events;
3. strict `ResearchCodeV0` JSON round-trip and deterministic replay digest;
4. partial exact evidence under fuel exhaustion;
5. explicit `not_representable` for a positive exact-cut feedback request;
6. explicit obstruction when the frontier does not return;
7. two legal schedules with the same canonical outer observer transition but
   distinct traces and digests; and
8. rejection of repeated observer roles and repeated schedule events.

The positive fixture is the checked five-event boundary-return program of note
0073. Its three source inputs pass through unchanged while two source-free
components execute and disappear. Equality of the visible frontier is
therefore paired with a nonempty complete residual, never with erased history.

## 6. Conservative conclusion and next falsifiers

The implementation is already useful for research because it forces every
proposal to state:

- which interface equality it uses;
- which exact spatial residual it retains;
- which temporal path it selected;
- how much fuel was available; and
- whether a negative result is an obstruction, representation boundary, or
  merely exhaustion.

It does not yet make the machine universal. The next decisive experiments are
small:

1. define a Rust-owned typed boundary connector and test whether it can create
   fresh occurrences without identifying sources;
2. compare two connectors that agree on the frontier but act differently on
   the complete residual;
3. add one explicit conjecture input so `counterexample` has a checked witness
   semantics;
4. test whether bracket normalization can be expressed as a certified active
   transformation rather than a Python comparison; and
5. require any proposed logic judgement to explain exactly which residual it
   may forget and under which finite observer policy.

Until those tests pass, `FeedbackWitnessV0` should be read literally: a finite
witness that one externally declared experiment was replayed, not the missing
feedback operator itself.

