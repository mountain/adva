# Research 0262: Quotient-query gating and non-unique exact lifts

Date: 2026-10-09. Status: elementary finite theorem plus bounded external
calibration. The retained campaign passed. No native quotient, identity merge,
`ProgramSlice` transformation, certificate, or stable API is introduced.

Research question, implementation, proof, and report: **Codex (OpenAI)**,
submitted through Mingli Yuan's GitHub account as an authorized proxy. Account
use is not his authorship, technical review, endorsement, or a correctness
guarantee. The project-original contribution is offered under Unknown v0.3.

Inspected base:
`mountain/adva@435f6e042f09c421234c81c7cdb994ccfacda03f`. PR #211's
Research 0259 showed that event probes separate states only relative to a fixed
identity-rich carrier. Research 0261 and its merged three-point successor then
retained the indexed trials `x=(-1,1,2)` even though `y=x*x` and the sole
observer `y>1` cannot distinguish trials 0 and 1. This round asks exactly which
positivity queries may pass through that observation quotient.

## 1. Frozen problem, types, and budget

Let `C` be a finite exact carrier, `q:C -> Q` a declared surjection, and
`S` a proposition region in `P(C)`. Define `S` to be **q-saturated** when it
is a union of whole fibres of `q`. The proposed operation is:

```text
quotient-query-gate(C, q, S)
  -> Descends(T)                 when S = q^{-1}(T), uniquely
  -> NonSaturated(c, c')         when q(c)=q(c') but membership differs
```

Malformed arity, negative labels, or a non-surjective consecutive quotient is
rejected before this judgment. A `Descends` result permits only the proposition
region to be read on `Q`; it does not identify the exact trials or construct a
quotient program.

The contract fixed two instances before execution:

1. the merged three-point square carrier with fibres `{0,1}` and `{2}`;
2. a fresh four-point reuse instance with fibres `{0,1}` and `{2,3}`.

The run allowed at most 30 seconds, 100,000 counted candidate families, three
child launches, and one MiB per output file. Child RSS was measured, but no hard
address-space cap was installed. There was no search expansion. One correction
replay removed an inaccurate 256 MiB contract claim after the publication
review found that the supervisor measured rather than enforced memory.

## 2. General finite proposition

For every surjection `q:C -> Q`, inverse image is a Boolean-algebra isomorphism

\[
q^{-1}:\mathcal P(Q)\;\cong\;\operatorname{Sat}(q),
\]

where `Sat(q)` is the subalgebra of saturated subsets of `C`.

Proof: inverse image preserves complements, inclusions, unions, and
intersections. It is injective because `q` is onto. Every saturated `S` equals
`q^{-1}(q(S))`, so it is surjective onto `Sat(q)`. The inverse is the unique
quotient mask constant on each fibre. If `S` is not saturated, two elements of
one fibre with different membership provide a finite refusal witness.

Consequently the static A1 complement rule and A2 upward-closure rule descend
exactly on this saturated proposition algebra. This theorem does **not** imply
that a full-powerset A1/A2 model on `C` is determined by its quotient
restriction. Restriction can forget identity-sensitive choices.

## 3. Exact result

The producer enumerated complementary choices and the receiver independently
enumerated all families of subsets. Both policies were checked:

- `basic`: static A1/A2 only;
- `joint`: A1/A2 plus a common exact realizer.

| Instance and policy | Exact models | Quotient models | Exact lifts over quotient class 0 / class 1 |
| --- | ---: | ---: | ---: |
| three point, basic | 4 | 2 | 3 / 1 |
| three point, joint | 3 | 2 | 2 / 1 |
| four point, basic | 12 | 2 | 6 / 6 |
| four point, joint | 4 | 2 | 2 / 2 |

For every row the saturated class-0 query is `Underdetermined` both before and
after quotienting. Thus the quotient preserves that declared query
classification. It does not preserve a unique exact explanation. In the
three-point basic case, three different exact positivity models restrict to the
same quotient model; under the joint policy, exact realizers 0 and 1 still
collapse to one quotient realizer class.

The three-point saturated masks are `{0,3,4,7}`. Singleton masks `1` and `2`
are refused with the counterexample pair `(0,1)`. The four-point saturated masks
are `{0,3,12,15}`; singleton `1` is refused by `(0,1)` and singleton `4` by
`(2,3)`. Taking the direct image of singleton `{0}` would produce quotient
class `{0}`, whose pullback is `{0,1}`: that apparently successful rewrite has
changed the question. The gate makes this failure explicit.

Six receiver controls were rejected: wrong lifted region, wrong lift
multiplicity, a singleton falsely labelled descending, an omitted exact model,
a changed classification, and a non-surjective quotient.

## 4. Working vocabulary

`quotient-query-gate` is recorded as a **Proposed** working term, not learned
native vocabulary. Its input/output boundary, applicability conditions,
witnesses, refusals, replay, and residual are in
`docs/terminology/quotient-query-gate-v0.json`.

The comparison is semantic rather than a speed claim. On the same singleton
input, an unchecked direct-image rewrite returns a quotient region but fails
the round trip `q^{-1}(q(S))=S`; the gate instead returns `NonSaturated` with the
specific fibre pair. The four-point instance exercises the same operation on a
new carrier. No claim of asymptotic or measured solver-cost reduction is made.

## 5. Execution, evidence, and residual

The retained campaign reports:

- 280 producer candidate families;
- 65,824 receiver candidate families;
- 24 query-gate checks;
- **66,128 counted work units** total, below the 100,000 limit;
- three child launches;
- 0.92155568 seconds wall and 0.919793 seconds child CPU for the accepted replay;
- 14,720 KiB maximum child RSS;
- zero search candidates and one correction replay.

Ordinary and optimized producer outputs are byte-identical. The independent
receiver returned `Verified` and rejected all six controls. Reproduce into a new
directory:

```sh
python3 experiments/quotient_query_gate/run_campaign.py /tmp/adva-quotient-gate-NEW
python3 tests/python/test_quotient_query_gate.py
```

The contract, producer, receiver, supervisor, retained result, receipt, and
telemetry are under
[`experiments/quotient_query_gate/`](../../experiments/quotient_query_gate/).

This helps Mingli and later agents distinguish two permissions: a proposition
may descend through an observer, while the exact carrier still may not be
contracted. It also prevents a human/AI handoff from converting an
identity-sensitive question into a saturated one without recording the change.

The calibration remains external finite set theory. Its carrier indices are
not Rust `SourceId`, `OccurrenceId`, or `History` values. It does not supply the
still-open native `ProgramSlice` pair requested by Research 0259, nor a quotient
program, loss certificate, observer specializer, M6 filler, arithmetic
universality, hypothesized arithmetic truth, or demonstrated value in Jiamin's
actual task.

The next minimum step is to expose one existing Rust-checked `ProgramSlice`
observation as a finite surjection and run the same gate on one native
source-, occurrence-, or history-sensitive proposition. If the current JSON
boundary cannot express that proposition without reconstructing identity in
Python, the correct result is `Unknown` with the missing field named.
