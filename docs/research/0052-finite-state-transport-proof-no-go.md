# Finite No-Go: State Transport Is Not Proof-Relevant Entailment

Status: exploratory finite calibration following
[`0051-finite-context-generated-proposition-algebra.md`](0051-finite-context-generated-proposition-algebra.md).

The executable fixture is
[`tests/python/test_triadic_state_transport_no_go.py`](../../tests/python/test_triadic_state_transport_no_go.py).

The preceding note left one apparently natural next question:

> When semantic supports satisfy \(A\subseteq B\), is there an admitted
> program \(F\) that transports every realization of \(A\) into \(B\)?

For the current state-based model, this question is degenerate.  If
\(A\subseteq B\), the identity transformation already satisfies

\[
\operatorname{id}(A)\subseteq B.
\]

Conversely, a state-changing program may transport \(A\) into \(B\) even when
\(A\not\subseteq B\).  For example, the constructive flip gives

\[
\{k=1\}\xrightarrow{K}\{k=0\}
\]

and also the reverse transport.  Neither support includes the other.

Therefore the judgment

\[
F(A)\subseteq B
\]

is not proof-relevant logical entailment.  It is a deterministic Hoare or
dynamic-logic judgment:

\[
\{A\}\,F\,\{B\}.
\]

This is a useful negative result.  It prevents the sixteen-element action
monoid from being relabelled prematurely as a proof calculus.  It also
identifies the missing object: evidence or realizers must be typed separately
from world states before a construction can witness implication.

The host-side transport enumeration is research-local.  It reuses the exact
finite machine and Rust-checked scalar programs of the preceding note but adds
no stable state, action, Hoare, predicate-transformer, evidence, realizer,
proof, or logic API.  It does not modify `claims.toml` and does not change the
active `ProgramSlice` priority.

---

## 0. Executive result

Let

\[
S_0=\{0,1\}^3
\]

be the eight-state temporal-spatial-constructive core and let

\[
M=\langle T,X,K\rangle
\]

be the exact sixteen-element transformation monoid computed previously.  The
contextual Boolean envelope is

\[
\mathcal B=\mathcal P(S_0),
\qquad
|\mathcal B|=256.
\]

There are

\[
256^2=65\,536
\]

ordered proposition pairs \((A,B)\).

Define semantic entailment by support inclusion:

\[
A\models B
\quad\Longleftrightarrow\quad
A\subseteq B.
\]

Define state transport by

\[
A\xrightarrow{F}_{\mathrm{state}}B
\quad\Longleftrightarrow\quad
F(A)\subseteq B,
\qquad F\in M.
\]

Exact enumeration gives:

| relation on ordered pairs | count |
|---|---:|
| support inclusions | 6,561 |
| pairs with at least one state transporter | 37,621 |
| transported pairs that are not inclusions | 31,060 |
| pairs with no admitted transporter | 27,915 |

Every one of the 6,561 inclusions has the identity witness.  In fact,

\[
6\,561=3^8,
\]

the standard count of ordered pairs \(A\subseteq B\) on an eight-element set:
each state is outside \(B\), in \(B\setminus A\), or in \(A\).

The shortest-transporter distribution is:

| shortest context length | proposition pairs |
|---:|---:|
| 0 | 6,561 |
| 1 | 13,208 |
| 2 | 11,682 |
| 3 | 6,038 |
| 4 | 132 |

Length zero consists exactly of support inclusion, because the only
zero-length context is the identity.  Positive lengths mostly record state
change rather than proof refinement.

---

# Part I. Three judgments that must be separated

## 1. Static support inclusion

For predicates interpreted as subsets of one carrier,

\[
A\subseteq B
\]

means that every state satisfying \(A\) also satisfies \(B\).  This is an
extensional semantic relation.  It does not record:

- a program;
- a proof term;
- evidence conversion;
- execution order;
- resource cost; or
- construction history.

It is a valid finite semantic preorder, but no more.

## 2. State-changing transport

A deterministic state program \(F:S_0\to S_0\) satisfies the Hoare triple

\[
\{A\}\,F\,\{B\}
\]

when

\[
F(A)\subseteq B.
\]

This says that running \(F\) from an \(A\)-state ends in a \(B\)-state.  It
does not say that \(A\) logically implies \(B\) at the same world state.

The distinction is elementary but decisive.  A program can make a false
postcondition true by changing the world.

## 3. Evidence transformation

A proof-relevant implication needs objects of a different type.  If
\(E_A(s)\) is the evidence fibre for proposition \(A\) at state \(s\), then an
ordinary implication should act on evidence, schematically,

\[
\Phi_s:E_A(s)\longrightarrow E_B(s),
\]

without silently replacing \(s\) by another world state.

The current finite machine contains state transformations

\[
F:S_0\longrightarrow S_0,
\]

but no separately typed evidence carriers \(E_A\) and no admitted grammar of
maps \(E_A\to E_B\).  It therefore cannot yet express proof-relevant
entailment.

---

# Part II. Why the proposed transporter test collapses

## 4. Identity witnesses every inclusion

Suppose

\[
A\subseteq B.
\]

For every \(s\in A\), the same state \(s\) belongs to \(B\).  Hence

\[
\operatorname{id}(s)=s\in B
\]

and therefore

\[
\operatorname{id}(A)\subseteq B.
\]

No search is needed.  The transporter-existence question adds no information
to support inclusion as long as:

1. propositions are only subsets of the same state carrier;
2. the identity state program is admitted; and
3. a transporter is required only to land in the consequent support.

This is a structural no-go, not a failure of the selected Boolean example.

## 5. Removing identity would not repair the definition

One might try to exclude the identity or require a nonempty program.  That
would be artificial and unstable:

- a longer word may still denote the identity, for example \(K^2\);
- excluding semantic identity would make the judgment depend on syntax rather
  than the declared program equality;
- logical identity should not be forbidden merely to force a nontrivial
  search; and
- state-changing witnesses would still not become evidence transformers.

The missing distinction is ontological, not a minimum-length condition.

## 6. Arbitrary functions on evidence would collapse again

Introducing evidence sets alone is also insufficient.  If every set-theoretic
function between nonempty finite evidence fibres is silently admitted, then
the host language can choose an arbitrary target witness and manufacture a
transformer.

A genuine proof-relevant experiment therefore needs both:

- separately typed evidence fibres; and
- a restricted, explicit, auditable grammar of evidence constructions.

No host callback or arbitrary finite lookup table may stand in for a proof
term.

---

# Part III. Exact direct transport table

## 7. Five context-generated predicates

Recall the five direct predicates:

\[
x,
\qquad
tk=t\wedge k,
\qquad
t\bar k=t\wedge\neg k,
\qquad
k,
\qquad
\bar k=\neg k.
\]

For each ordered pair, the following table gives one shortest context \(F\)
such that \(F(A)\subseteq B\).  A dash means that no element of the complete
sixteen-element monoid transports the row predicate into the column
predicate.

| \(A\backslash B\) | \(x\) | \(tk\) | \(t\bar k\) | \(k\) | \(\bar k\) |
|---|---:|---:|---:|---:|---:|
| \(x\) | \(\varepsilon\) | — | — | — | — |
| \(tk\) | \(X\) | \(\varepsilon\) | \(K\) | \(\varepsilon\) | \(K\) |
| \(t\bar k\) | \(KX\) | \(K\) | \(\varepsilon\) | \(K\) | \(\varepsilon\) |
| \(k\) | \(TX\) | \(T\) | \(TK\) | \(\varepsilon\) | \(K\) |
| \(\bar k\) | \(TKX\) | \(TK\) | \(T\) | \(K\) | \(\varepsilon\) |

The inclusion arrows visible in the table are:

\[
tk\subseteq k,
\qquad
t\bar k\subseteq\bar k,
\]

plus reflexivity.  All use \(\varepsilon\).

Most other entries are actions.  They change one or more coordinates before
the postcondition is tested.

## 8. The constructive flip is a decisive counterexample

Let

\[
A=\{k=1\},
\qquad
B=\{k=0\}.
\]

Then

\[
A\not\subseteq B
\quad\text{and}\quad
B\not\subseteq A.
\]

But

\[
K(A)=B,
\qquad
K(B)=A.
\]

If state transport were called implication, the machine would derive both

\[
k\vdash\neg k
\]

and

\[
\neg k\vdash k.
\]

The correct reading is simply that an involutive action flips the constructive
bit.

## 9. Some state transports do not exist

The distinction is not that every predicate can be driven into every other
predicate.  For example, no admitted transformation sends every \(x=1\) state
into \(k=1\).  The initial \(x\)-support contains both constructive bits, and
the available uniform programs cannot collapse them all to positive
construction while preserving membership in the requested target.

Thus the complete transport relation contains real reachability constraints.
They are constraints on action, not proof inhabitation.

---

# Part IV. The correct dynamic-logic reading

## 10. Weakest preconditions

For a transformation \(F\) and postcondition \(B\), define the inverse-image
predicate

\[
\operatorname{wp}_F(B)=F^{-1}(B).
\]

Then the exact equivalence is

\[
\{A\}\,F\,\{B\}
\quad\Longleftrightarrow\quad
F(A)\subseteq B
\quad\Longleftrightarrow\quad
A\subseteq F^{-1}(B).
\]

The fixture checks this equivalence for:

- all sixteen transformations;
- all 256 antecedents; and
- all 256 consequents.

This is the mathematically appropriate predicate-transformer semantics of the
current finite machine.

## 11. Reinterpretation of the preceding proposition algebra

The direct propositions from the preceding note were defined by

\[
P_C=C^{-1}(A_X),
\]

where \(A_X=\{x=1\}\).  They are exactly the distinct weakest preconditions

\[
\operatorname{wp}_C(A_X)
\]

generated by the finite action monoid.

Therefore the result of note 0051 can now be stated more precisely:

> It computes a finite dynamic proposition algebra generated by the weakest
> preconditions of one spatial observation under every admitted action.

That is already useful.  It is simply not yet a natural-deduction calculus.

## 12. Identity and composition are not diagnostic by themselves

State transports have identity:

\[
\{A\}\,\operatorname{id}\,\{A\}.
\]

They also compose.  If

\[
F(A)\subseteq B
\]

and

\[
G(B)\subseteq C,
\]

then

\[
(G\circ F)(A)\subseteq C.
\]

The fixture checks composition for every direct predicate triple and every
admitted pair of transformations.

Identity and composition resemble proof identity and cut, but they occur in
many categories of actions.  Their presence alone does not establish a proof
theory or cut elimination.

## 13. The existential transport relation is a reachability preorder

Write

\[
A\leadsto B
\quad\Longleftrightarrow\quad
\exists F\in M,\;F(A)\subseteq B.
\]

Because the identity is in \(M\) and \(M\) is closed under composition,
\(\leadsto\) is reflexive and transitive.  It is not antisymmetric:

\[
k\leadsto\neg k
\quad\text{and}\quad
\neg k\leadsto k.
\]

This is a program-reachability preorder.  Quotienting by mutual reachability
would classify dynamical communication, not logical equivalence.

## 14. Empty antecedents expose ordinary Hoare vacuity

For the empty predicate,

\[
F(\varnothing)=\varnothing\subseteq B
\]

for every \(F\) and \(B\).  Hence every program satisfies

\[
\{\bot\}\,F\,\{B\}.
\]

This resembles ex falso extensionally, but no evidence object is created.  It
is the ordinary vacuity of a partial-correctness precondition with no initial
states.

No admitted total transformation sends the whole state space into the empty
postcondition.

---

# Part V. What proof relevance now requires

## 15. A two-sorted carrier

The next model must separate world states from evidence.  For every
proposition \(A\), introduce a typed evidence carrier with projection

\[
\pi_A:E_A\longrightarrow S_0.
\]

An element \(e\in E_A\) records not only that \(A\) holds at
\(\pi_A(e)\), but also how it is supported: context, construction, source,
occurrence, checked history, or another declared witness.

The support is recovered as

\[
|A|
=
\{s\in S_0\mid E_A(s)\ne\varnothing\}.
\]

Equal supports need not imply equal evidence carriers.

## 16. Ordinary implication versus action-indexed transport

An ordinary proof transformer should lie over the same world state:

\[
\Phi:E_A\longrightarrow E_B,
\qquad
\pi_B\circ\Phi=\pi_A.
\]

An action-indexed evidence transformer may instead lie over a declared state
program \(F\):

\[
\Phi_F:E_A\longrightarrow E_B,
\qquad
\pi_B\circ\Phi_F=F\circ\pi_A.
\]

These are different judgments:

\[
A\vdash^{\Phi}B
\]

versus

\[
\{A\}\,F\,\{B\}
\quad\text{with evidence lift }\Phi_F.
\]

The first transforms evidence without changing the base state.  The second
certifies an action and its evidence transport.

## 17. The proof grammar must be explicit

The carriers \(E_A\) do not authorize every host-language function.  A finite
proof experiment needs an admitted typed grammar, for example:

- identity evidence;
- checked context composition;
- explicit pairing and projections when their resource rules permit them;
- explicit injections or case analysis for declared sums;
- program-history transport supplied by the Rust kernel; and
- failure or `Unknown` when no checked construction is found.

Copy, discard, exchange, and witness choice must remain explicit.  Otherwise
the host language would silently restore contraction, weakening, or choice.

## 18. The first genuine separation target

Only after evidence fibres and a restricted proof grammar exist does the
following test become meaningful:

1. find \(A\subseteq B\) extensionally;
2. enumerate every admitted evidence transformer from \(E_A\) to \(E_B\);
3. either return a checked transformer;
4. or, after proving the finite grammar closed, return a counterexample showing
   that support inclusion does not lift to proof transport;
5. otherwise return `Unknown`.

The direct inclusion

\[
t\wedge k\subseteq k
\]

is a natural first calibration, but it is not yet a counterexample.  Whether
its temporal-spatial evidence can be converted into constructive evidence
depends on the evidence types and admitted constructors, which have not yet
been defined.

---

# Part VI. Consequences for the larger programme

## 19. Consequence for 3-form logic

The current finite structure supplies:

- actions on triadic states;
- order-sensitive context composition;
- weakest-precondition propositions;
- a contextual quotient;
- a Boolean extensional envelope; and
- exact Hoare transport.

It does not yet supply proofs as constructions between proposition-specific
evidence types.  The proposed logic on a 3-form therefore remains a proposal,
now with a sharper interface boundary.

## 20. Consequence for the \(L/R\) problem

The equations

\[
TK=KT,
\qquad
TX\ne XT,
\qquad
KX\ne XK
\]

continue to govern action order.  They may help derive schedule normal forms
without forcing a global \(L\mid R\) order.

They do not determine logical exchange.  Logical exchange concerns the order
of assumptions or evidence resources, which requires the missing evidence
grammar.  Action commutation and proof-context exchange must not be identified.

## 21. Consequence for startup calibration

Startup steps may be treated as state actions and checked with Hoare
preconditions and postconditions.  This can answer whether a sequence reaches
a calibrated region and whether calibration steps commute.

It cannot by itself prove that one calibration certificate transforms into
another.  Certificate transport again belongs to the evidence layer.

## 22. Consequence for finite representation

The preceding note showed that the Boolean language is complete for the
contextual state quotient.  The present note shows that extensional
completeness does not imply proof relevance.

There are therefore at least three finite-completeness questions:

1. **state separation:** does the proposition family distinguish every
   contextual state class?
2. **extensional expression:** does its Boolean envelope express every subset
   of the quotient?
3. **constructive completeness:** does every valid semantic judgment have an
   admitted evidence transformer?

The fixture answers the first two positively on the selected quotient.  It
does not yet formulate the third.

---

# Part VII. Verification and limits

## 23. What the fixture establishes

Within the declared finite machine, the fixture establishes:

1. the five direct propositions are exactly the weakest preconditions of the
   spatial atom under the sixteen-element action monoid;
2. weakest-precondition equivalence for all \(16\times256\times256\) declared
   transformation/antecedent/consequent triples;
3. exactly 6,561 support inclusions in the 256-element Boolean envelope;
4. the identity transformation witnesses every inclusion;
5. exactly 37,621 ordered proposition pairs admit a state transporter;
6. 31,060 of those transported pairs are not support inclusions;
7. 27,915 pairs admit no transformation from the complete monoid;
8. the exact shortest-transporter length distribution;
9. the complete shortest-witness table for the five direct predicates;
10. the bidirectional constructive-flip counterexample;
11. identity and exhaustive composition for direct Hoare transports; and
12. vacuous transport from the empty antecedent but no transport from the
    whole carrier into the empty consequent.

## 24. What it does not establish

The fixture does not establish:

- a stable Hoare or dynamic-logic API;
- that the selected action monoid is canonical;
- proof-relevant implication;
- proposition-specific evidence types;
- an admitted proof-term grammar;
- natural deduction or sequent calculus;
- cut elimination;
- logical exchange, contraction, or weakening;
- constructive completeness;
- a general decision procedure beyond the finite carrier;
- a solution to the global \(L/R\) problem; or
- mathematical novelty of the finite Hoare and weakest-precondition facts.

The no-go claim is narrow: state transport of supports cannot serve as the
missing proof-relevant entailment in this model.

## 25. Conservative conclusion

The attempted bridge from support inclusion to program-witnessed implication
fails for a precise reason:

> State programs act on the world.  Proof terms must act on evidence.

Every support inclusion already has the identity state transporter, while many
non-entailments have state-changing transporters.  The sixteen-element monoid
therefore supports a finite dynamic or Hoare logic, not yet a natural-deduction
system.

The next legitimate construction is a two-sorted finite model with world
states, proposition-indexed evidence fibres, and an explicit restricted grammar
of evidence transformations.  Only there can semantic inclusion and
constructive entailment be compared without collapsing one into the other.

The first such calibration is carried out in
[`0053-finite-causal-presented-evidence.md`](0053-finite-causal-presented-evidence.md).
It uses presentation-indexed run evidence and permits only causal suffix
continuations, producing the first exact support inclusions that do not lift to
the admitted evidence grammar.
