# Checked Boundary Returns and the Missing Feedback Operator

Status: bounded exact research calibration following
[0023](0023-exact-program-slice-wp2.md),
[0024](0024-exact-program-slice-composition-wp3.md),
[0059](0059-tri-bracket-eigen-normalization-logic.md),
[0060](0060-triadic-observer-program-slice-bridge.md), and
[0072](0072-pq-unit-tangent-through-geometry.md).

The executable companion is
[test_checked_boundary_return_no_go.py][fixture].

[fixture]: ../../tests/python/test_checked_boundary_return_no_go.py

This note creates no stable feedback, iteration, period, normalization,
bracket, torus, orbifold, or knot semantics. Every cut and slice identity used
by the experiment is checked by Rust. Python only compares checked records and
constructs a research-local obstruction.

---

## 0. Provenance and question

Mingli Yuan proposed that two normalization returns might supply the missing
\((p,q)\) data behind the phase-torus and unit-tangent calculations of note
0072. The decisive local question is:

> Can one finite Rust-checked `ProgramSlice` produce intrinsic positive
> periods, or can it only produce equal observations at two distinct cuts?

This experiment obtains a positive finite boundary-return result and a
negative period result from the same checked history.

---

## 1. Executive result

One checked program contains two independently derived, source-free internal
components:

| component | exact operation word | least boundary-return length |
|---|---|---:|
| \(G_2\) | `constant; discard` | 2 |
| \(G_3\) | `constant; neg; discard` | 3 |

For each component, the Rust-owned frontier before and after the word is
exactly equal. The intervening `ProgramSlice` is nevertheless nonempty and
retains every event ID. Thus the experiment establishes

\[
\boxed{
B(C)=B(D),\quad C\ne D,\quad
\operatorname{Slice}(C,D)\ne 1,
}
\]

where \(B\) is the explicitly declared boundary-only observation.

The lengths \((2,3)\) therefore support a candidate finite phase reading

\[
\operatorname{lcm}(2,3)=6,
\qquad
\gcd(2,3)=1.
\]

They do **not** yet define two periods of the checked program. A finite Adva
operation DAG consumes each event once. It has no operation that feeds the
upper boundary back to the lower boundary and re-enables the same slice.

The exact verdict is

\[
\boxed{
\text{two checked boundary-return words exist,}
\qquad
\text{intrinsic periodic dynamics is NotRepresentable.}
}
\]

The missing object is now precise: a typed feedback or iteration witness, not
another numerical formula for \((p,q)\).

---

## 2. The single checked witness

The fixture compiles this program through the stable Rust boundary:

```lisp
(module checked-boundary-return
  (export witness)
  (def witness
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real)
      (frontier
        (discard 1)
        (discard (neg 1))
        (use temporal)
        (use spatial)
        (use construction)))))
```

The three typed inputs pass through unchanged. The other two components are
derived from the exact internal event graph, rather than selected by guessed
node numbers:

\[
G_2:\quad 1\longrightarrow\operatorname{discard},
\]

\[
G_3:\quad 1\longrightarrow\operatorname{neg}
\longrightarrow\operatorname{discard}.
\]

Every wire in \(G_2\) and \(G_3\) has empty source lineage. The fixture takes
connected components only after Rust has certified the complete slice and its
`internal_events`.

This is deliberately not a bracket normalizer. It is the smallest stable
kernel witness able to test the logical distinction between observed return
and exact return.

---

## 3. Exact cut, observation, and residual

For a checked causal cut \(C\), define

\[
C=(P_C,F_C),
\]

where \(P_C\) is the completed causal past and \(F_C\) is its exact frontier.
The boundary-only observer is

\[
B(C)=F_C.
\]

It forgets the completed past. This is an authorized finite abstraction only
when the forgotten interval is retained as a residual:

\[
\mathcal R_{C,D}=\operatorname{ProgramSlice}(C,D).
\]

A **boundary-return word** is a nested pair \(C\subset D\) satisfying

\[
B(C)=B(D),
\qquad
\mathcal R_{C,D}\ne 1.
\]

Its local length is the number of events in the residual. It is least along a
declared component schedule when no proper nonempty prefix has returned to the
same frontier. The fixture checks this prefix condition exactly for lengths
two and three.

This gives a clean answer to the earlier forgetting question:

> One may forget the completed past for a boundary judgement only if the
> exact slice remains attached and no claim requiring exact cut equality is
> made.

---

## 4. The finite-DAG no-go theorem

Let

\[
\rho(C)=|P_C|.
\]

For distinct nested cuts \(C\subsetneq D\),

\[
\rho(C)<\rho(D).
\]

Therefore no nonempty forward `ProgramSlice` can return to the same exact
cut. The only exact endoslice is the identity interval

\[
\operatorname{Slice}(C,C),
\]

whose event set is empty.

The fixture enumerates every downward-closed cut of the five-event witness.
For every comparable strict pair it asks Rust for the interval and verifies

\[
C\ne D,
\qquad
\operatorname{events}(C,D)\ne\varnothing.
\]

This is not a limitation of the example. It follows from finite acyclicity and
the monotone completed-past rank.

---

## 5. Why \((2,3)\) is not yet `PhasePeriods(2,3)`

The candidate companion can compute

\[
L=\operatorname{lcm}(2,3)=6,
\qquad
g=\gcd(2,3)=1,
\]

but it deliberately stores

```text
feedback_witness = None
homology_return_map = None
orbifold_orders = None
status = not_representable_without_feedback
```

Three bridges remain absent:

1. **repeatability** — the checked word cannot be executed again after its
   events have entered the completed past;
2. **phase transport** — no successor on
   \(\mathbb Z/2\times\mathbb Z/3\) is induced by the slice itself; and
3. **topological return** — the program carries no torus basis, intersection
   form, or element of \(SL_2(\mathbb Z)\).

Consequently no intersection-preserving map on \(H_1(T^2)\), Hecke cutting
code, mapping torus, or orbifold order follows from this result.

---

## 6. Relation to the triadic observer

The witness exposes time, space, and construction as three checked input
sources. They survive as unchanged through wires at both endpoints. The two
return components are source-free.

This matters because the current triadic observer calibration assigns roles
through checked input-source fibres. A transient source-free wire is recorded
outside all three opposite-pair charts; once its component closes, it is absent
from both endpoint observations. The three endpoint views can therefore agree
while a nonempty internal history survives.

`ProgramSlice` already contains the required corrective information:

\[
\boxed{
\text{three agreeing projected boundaries}
+
\text{one exact internal residual}.
}
\]

This suggests that feedback, if introduced, must act on the complete residual-
decorated transition. Closing only the three projected boundaries would erase
exactly the source-free computation that created the return word.

---

## 7. What is supported

The executable fixture establishes:

1. one stable Rust compilation produces a finite five-event DAG;
2. its source-free internal graph has components of sizes two and three;
3. their exact operation words are the two words printed above;
4. each word has equal checked lower and upper frontiers;
5. no proper component prefix has the same frontier;
6. each complete interval retains its nonempty event IDs;
7. every strict nested cut pair has increasing completed-past rank;
8. only identity slices have equal exact cuts;
9. \((2,3)\) yields candidate phase arithmetic \((L,g)=(6,1)\); and
10. feedback, homology return, and orbifold fields remain explicitly absent.

The result is stronger than hand-inserting two modular counters, because the
two finite return lengths are derived from one checked operation graph. It is
weaker than periodic computation, because no repetition rule exists.

---

## 8. Red-team conclusions

The following objections remain decisive:

1. event-count length is presentation-sensitive;
2. inserting an identity or a closed detour changes length without changing
   the external boundary;
3. two independent components can be interleaved by different schedules;
4. leastness here is component-local, not a global dynamical period;
5. source-free arithmetic cells are not tri-bracket normalization steps;
6. equal frontiers do not imply equal cuts or equal histories;
7. a trace, feedback, fixpoint, or iteration operator has not been defined;
8. feedback can threaten termination and must carry its own certificate;
9. no torus intersection form is present; and
10. the same numeric pair cannot be renamed as orbifold orders.

The fixture includes a concrete refinement warning: the two checked closed
words have the same unchanged external boundary but different lengths. Hence
boundary behaviour alone does not make event count invariant.

---

## 9. Next falsifiable gate

The next experiment should add a research-local `FeedbackWitnessV0`, without
changing stable semantics. It must:

1. accept only a Rust-certified slice;
2. provide an explicit upper-to-lower boundary isomorphism;
3. preserve exact wire, source, and occurrence identities or report the
   unavoidable quotient;
4. retain the slice as the loop residual;
5. specify whether one loop re-enables fresh events or reuses old identities;
6. distinguish termination, fuel exhaustion, and genuine recurrence;
7. test invariance under identity insertion and schedule exchange;
8. derive a return action rather than assume a modular counter;
9. return `NotRepresentable` when the boundary match is insufficient; and
10. only after these checks ask whether a torus or Hecke code is induced.

The most important negative control is a pair of boundary-equal slices with
different internal histories. If the proposed feedback identifies them merely
because their frontiers match, it has forgotten too much.

---

## Conservative conclusion

\[
\boxed{
\text{checked finite history}
\to
\text{least boundary-return words }(2,3)
\dashrightarrow
\text{periodic phase torus}.
}
\]

The dashed arrow is no longer mysterious. It is the absent typed feedback
operator together with an invariance theorem for the feature extracted from
its residual-decorated loop. Until that exists, the honest word is **return**,
not **period**.
