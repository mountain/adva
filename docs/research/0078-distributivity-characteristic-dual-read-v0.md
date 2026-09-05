# Distributivity Characteristic Dual Read V0

Status: bounded executable research experiment, task two of the three-task
validation plan, following
[0066](0066-self-dual-characteristic-completion-calculus.md),
[0077](0077-typed-connector-trichotomy-v0.md), and
[ADR 0015](../adr/0015-distributivity-characteristic-dual-read.md).

The implementation is
`adva.characteristic_research.DistributivityCharacteristicMachineV0`; the
fixture is `tests/python/test_distributivity_characteristic.py`.

This note introduces no stable polynomial semantics, proof judgment, equation
cell, right-to-forget rule, complete learning/proof duality, logic,
specializer, interpreter, or universality result.

---

## 0. The second validation task

Compare two separately compiled programs

\[
P=a(x+y),
\qquad
Q=ax+ay.
\]

Their scalar polynomials agree, but their checked processes do not.  The
expanded program explicitly copies `a`; its fixture also contains an
independent source-free constant--discard component.  The two functions have
different diagrams, events, occurrences, histories, and graft frames.

The intended IR shape is not three mutable program copies.  For each program
the experiment retains one Rust-owned core and derives a bounded atlas

\[
\mathcal A(P)=
\bigl(P_{\rm core};B_P,W_P,M_P;\chi_P,R_P\bigr).
\]

Here:

- \(B_P\) is the fixed `{}[]()` boundary and exact triadic observer view;
- \(W_P\) is the tuple of three exact opposite-pair transition relations;
- \(M_P\) is the compiler graft presentation plus complete `ProgramSlice`;
- \(\chi_P\) records the checked correspondences and the task feature; and
- \(R_P\) retains every process distinction omitted from the visible feature.

No round trip between presentations is required.  Reliability comes from a
common checked core, exact local composition certificates, and retained
residuals.

## 1. The exact finite characteristic

The declared feature carrier is the degree-bounded rational polynomial ring

\[
\mathbb Q[a,x,y]_{\le 2}.
\]

After Rust compilation and validation, the existing SymPy adapter reads the
one scalar output.  The research machine expands it and records a canonical
tuple of rational coefficients and exponent vectors.  For both positive
programs it obtains

\[
N=ax+ay.
\]

The computation is exact in the declared polynomial fragment.  It does not
derive a stable feature object inside Rust, and it does not turn equality of
the coefficient tuples into equality of the two programs.

The V0 operation boundary admits only `add`, `mul`, `copy`, `discard`,
`constant`, and `id`.  A nonpolynomial operation, a non-scalar output, an
undeclared symbol, or a polynomial above the requested degree returns
`NotRepresentable`.

## 2. One core, three presentations

Each `ProgramAtlasV0` contains:

| layer | checked input | derived presentation |
|---|---|---|
| boundary | one exact triadic observer transition | `{}[]()` plus three opposite-pair views |
| through | Rust lineage links and opposite-pair transitions | three relation-valued crossing forms |
| multi-hole | compiler `GraftTrace` and complete slice | ordered call holes, events, and residual |
| feature | checked scalar core through the SymPy adapter | canonical rational polynomial |
| correspondence | Rust slice and observer certificates | direct/composed equality flags |

For a nontrivial intermediate causal cut, Rust separately checks

\[
M(P_2\circ P_1)=M(P_2)\circ M(P_1)
\]

and exact triadic observer composition.  The Python report compares those
certified results with the direct outer views.  It never submits a
Python-created slice, transition, occurrence, or identity to the kernel.

## 3. Learning and proof readouts

Both directions invoke the same characteristic extractor.

### Learning

The learning readout returns

\[
P\mapsto N,
\qquad
Q\mapsto N,
\]

and classifies the pair as
`ObservationallyEqual(residuals)`.  The visible feature agrees, while
\(R_P\) and \(R_Q\) remain unequal and attached.

### Proof

The proof readout compares the same two exact features.  In the named fixture
it additionally checks the bounded process profiles:

- the left core contains one `add`, one `mul`, and no `copy`; and
- the right core contains one `copy`, two `mul` operations, and one `add`.

It then returns a `DistributivityWitnessV0` whose common middle object is
\(N\).  This is a normalization span in the declared polynomial theory:

\[
P\xrightarrow{\chi_P}N\xleftarrow{\chi_Q}Q.
\]

It is not a Rust `EquationCell`, a rewrite path between the original diagrams,
or a proof that the learning transition is the full reverse dual of the proof
transition.  V0 supports only a shared kernel and two task readouts.

## 4. Task-relative forgetting

The polynomial feature hides:

- `NodeId`, `OccurrenceId`, and `OccurrencePath`;
- copy and discard ledgers;
- event order and call history; and
- compiler graft frames.

The experiment permits comparing the two polynomial features only because the
request names that observation policy and both complete residuals remain
attached.  The corresponding evidence explicitly refuses:

\[
\text{program identification},
\qquad
\text{equation-cell creation},
\qquad
\text{provenance erasure}.
\]

If residual retention is disabled, the projection returns
`NotRepresentable`.  This is the first executable candidate for a
task-relative right to abstract, not a stable or transferable right to forget.

## 5. Five result forms

The task keeps the requested outcomes distinct:

| result | finite meaning in V0 |
|---|---|
| `Proved(witness)` | equal exact features plus the bounded factored/expanded operation profiles |
| `Refuted(counterexample)` | unequal features separated by an exact finite integer assignment |
| `ObservationallyEqual(residuals)` | one feature, two retained checked processes, no requested proof witness |
| `NotRepresentable` | the program or projection lies outside the declared finite fragment |
| `FuelExhausted` | both cores were checked, but the feature budget ended before completion |

The refutation grid is \(\{0,\ldots,d\}^3\), where \(d\) is the declared
total-degree bound.  Two distinct polynomials of degree at most \(d\) cannot
agree on the whole grid, so the negative fixture

\[
a(x+y)
\quad\text{versus}\quad
ax+y
\]

produces an exact separating valuation.  Exhaustion produces no refutation or
nonexistence conclusion.

## 6. Common validation gates

The implementation specializes the shared protocol to eight ordered gates:

\[
\boxed{
\text{type}
\to\text{identity}
\to\text{presentation correspondence}
\to\text{local composition}
\to\text{residual}
\to\text{characteristic}
\to\text{dual readout}
\to\text{promotion boundary}
}
\]

The tests cover:

1. positive proof for `a(x+y)` and `ax+ay`;
2. the learning readout with unequal copy/constant/discard histories;
3. exact refutation of `a(x+y)` versus `ax+y`;
4. refusal when the degree bound is too small;
5. distinct fuel exhaustion; and
6. refusal to project when the residual would be dropped.

## 7. Conservative and red-team conclusions

The positive result is narrower than a logic theorem:

\[
\boxed{
\text{one exact characteristic kernel supports learning and proof readouts}
}
\]

for one finite distributivity fixture.  The result supports the original
intuition that feature extraction can mediate both directions while process
history remains present as a fibre.

The following stronger claims remain open:

- that the witness is invariant under arbitrary polynomial program
  presentations;
- that the proof readout reconstructs a canonical program rewrite;
- that the learning rule is contravariantly equivalent to proof search;
- that task-relative projection supplies a stable `MayForget` judgment;
- that polynomial equality induces an `EquationCell`;
- that the three presentations satisfy unrestricted composition laws; and
- that the mechanism extends to a complete logic or universal computation.

The next falsifiable upgrade is either a Rust-owned polynomial certificate or
a proof-relevant normalization trace whose steps can be reversed under the
proposed learning orientation.  Only after one of those exists should the
result be promoted from a bounded characteristic span toward the logic
language.
