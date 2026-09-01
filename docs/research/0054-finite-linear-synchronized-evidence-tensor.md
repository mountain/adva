# Finite Linear Synchronized Evidence Tensor

Status: exploratory finite calibration following
[`0053-finite-causal-presented-evidence.md`](0053-finite-causal-presented-evidence.md).

The executable fixture is
[`tests/python/test_triadic_linear_evidence_tensor.py`](../../tests/python/test_triadic_linear_evidence_tensor.py).

Note 0053 separated causal evidence continuation from extensional proposition
inclusion.  This note adds one composite constructor while preserving that
separation:

> Two presented evidence resources may be synchronized over the same initial
> world state.  Every admitted transformation must route each input resource
> to exactly one output resource and continue its own history forward.

The carrier is fibre-product-like, but its proof grammar is linear.  Pairing
does not silently install projection, diagonal, copy, or discard.

The result is a candidate multiplicative fragment for logic on a 3-form.  It
is not a declaration that ordinary conjunction has been recovered.

---

## 0. Executive result

Let \(M=\langle T,X,K\rangle\) be the sixteen-presentation monoid from note
0053.  The finite object family in this experiment contains:

\[
I,
\qquad
E_m,
\qquad
E_m\otimes_s E_n
\quad (m,n\in M),
\]

where \(I\) has arity zero, \(E_m\) has arity one, and the synchronized tensor
has arity two.  There are therefore

\[
1+16+16^2=273
\]

presented evidence types.

Their observed support is

\[
Q(I)=S_0,
\qquad
Q(E_m)=P_m,
\qquad
Q(E_m\otimes_s E_n)=P_m\cap P_n.
\]

For types of equal arity, a linear evidence map consists of:

1. a bijection from input resource positions to output positions; and
2. one causal suffix continuation along each routed component.

No map exists between different arities in this first grammar.

Exact enumeration gives:

| finite comparison | count |
|---|---:|
| evidence types | 273 |
| distinct observed supports | 11 |
| ordered support inclusions | 31,737 |
| inclusions admitting at least one linear map | 6,317 |
| support inclusions with no linear map | 25,420 |
| cross-arity support inclusions | 3,088 |
| same-support cross-arity pairs | 672 |
| type pairs admitting one routing | 5,373 |
| type pairs admitting two routings | 944 |
| routing-level shortest witnesses | 7,261 |

Thus support inclusion is very far from determining composite evidence.  Even
support equality does not authorize a diagonal or projection.

---

# Part I. The synchronized carrier

## 1. Atomic evidence recalled

For a presentation \(m\) and supporting initial state \(s\), note 0053 used

\[
E_m(s)
=
\{(w,\rho_w(s))\mid \llbracket w\rrbracket=m\}.
\]

A causal continuation appends a suffix \(d\):

\[
(w,\rho_w(s))
\longmapsto
(wd,\rho_{wd}(s)).
\]

The initial state is unchanged and the old trace is a literal prefix of the
new trace.

## 2. Synchronization over one base state

For two presentations define the carrier

\[
(E_m\otimes_s E_n)(s)
=
E_m(s)\times E_n(s).
\]

This is a pair of evidence histories that speak about the same initial world
state.  It is not a pair of arbitrary witnesses drawn from unrelated worlds.

The experiment rejects a pair whose components have different initial states.
The unit fibre \(I(s)\) contains the empty resource tuple at each declared
initial state.

## 3. Resource identity is additional data

Each component also carries a distinct research-local resource identifier.
The identifier is not derived from Python object identity, value equality, or
the presentation transformation.

Consequently, constructing

\[
e\otimes_s e
\]

by passing the same resource twice is rejected.  A valid

\[
e_0\otimes_s e_1
\]

requires two independently named input resources even when the two evidence
values, words, traces, and presentations are otherwise equal.

These identifiers are only a finite experimental guard.  Stable authority
would have to come from Rust `SourceId`, `OccurrenceId`, and checked lineage,
not from this Python model.

## 4. Why the support is still an intersection

A common initial state supports the synchronized pair exactly when it supports
both components.  Therefore

\[
Q(E_m\otimes_s E_n)=P_m\cap P_n.
\]

This explains why the carrier looks conjunction-like to a spatial observer.
It does not determine the constructors and eliminators of conjunction.

The support observer has forgotten:

- that there are two resources rather than one;
- which history belongs to which resource;
- the ordering of the two ports;
- which routing a transformation used; and
- whether copying or discarding was operationally available.

---

# Part II. The linear transformation grammar

## 5. One input, one output per resource

Let

\[
A=(E_{a_0},\ldots,E_{a_{r-1}})
\]

and

\[
B=(E_{b_0},\ldots,E_{b_{r-1}})
\]

have the same arity \(r\).  An admitted map \(f:A\to B\) contains a
permutation

\[
\sigma:\{0,\ldots,r-1\}\cong\{0,\ldots,r-1\}
\]

and causal continuations

\[
E_{a_{\sigma(j)}}
\xRightarrow{d_j}_{\mathrm{ev}}
E_{b_j}
\]

for every target position \(j\).

On evidence it acts by

\[
(e_0,\ldots,e_{r-1})
\longmapsto
(e_{\sigma(0)};d_0,\ldots,e_{\sigma(r-1)};d_{r-1}).
\]

Every input resource appears once and only once in the result.

## 6. Exchange is explicit

For two resources there are at most two routings:

- identity routing \((0,1)\); and
- exchange routing \((1,0)\).

For example,

\[
E_X\otimes_s E_X
\longrightarrow
E_X\otimes_s E_X
\]

admits both.  Applied to independently named resources \((r_0,r_1)\), the
first returns \((r_0,r_1)\) and the second returns \((r_1,r_0)\).

Their extensional action on support is indistinguishable, but their resource
routings are not the same witness.

Across the finite object family, 944 ordered type pairs admit both routings.
This is a concrete proof-relevant multiplicity hidden by the support observer.

## 7. Tensoring atomic maps

If

\[
f:E_a\to E_b
\qquad\text{and}\qquad
g:E_c\to E_d
\]

are causal continuations, the experiment admits the componentwise map

\[
f\otimes_s g:
E_a\otimes_s E_c
\longrightarrow
E_b\otimes_s E_d.
\]

It retains the identity routing and appends the declared suffix independently
to each resource history.

## 8. Identity and cut

The empty permutation and empty continuation tuple give the unit identity.
At positive arity, identity routing together with empty suffixes gives the
evidence identity.

Suppose \(f:A\to B\) has routing \(\sigma\), and \(g:B\to C\) has routing
\(\tau\).  Their composite has routing

\[
(\sigma\circ\tau)(j)=\sigma(\tau(j))
\]

under the target-slot convention above, and concatenates the two suffixes on
the resource routed into target position \(j\).

The fixture checks a nontrivial tensor, exchange, and sequential continuation
example.  Direct composite application equals sequential application exactly;
the two input resource identifiers are preserved once each.

---

# Part III. Structural rules that are absent

## 9. No implicit contraction

Let \(A=E_X\).  Since intersection is idempotent,

\[
Q(A)=Q(A\otimes_s A).
\]

Nevertheless there is no admitted map

\[
A\longrightarrow A\otimes_s A.
\]

The arities differ, and the repeated routing \((0,0)\) is not a bijection.
At evidence construction time, using the same resource identifier twice is
also rejected.

Equal support therefore does not manufacture a copy operation.

## 10. No implicit weakening

For the same reason there is no admitted map

\[
A\otimes_s A\longrightarrow A.
\]

Selecting one input would leave the other resource unaccounted for.  A later
discard rule would need an explicit program event and checked lineage.

Equal support therefore does not manufacture a projection.

## 11. Cross-arity no-go

Among the 31,737 ordered support inclusions, 3,088 compare different resource
arities.  None lift in the admitted grammar.  Of these, 672 compare types with
exactly the same support.

These 672 pairs are the cleanest finite counterexamples to the inference

\[
Q(A)=Q(B)
\quad\Longrightarrow\quad
A\cong B.
\]

The observer has erased resource multiplicity.

## 12. Equal arity is not sufficient

Linearity alone does not explain all missing evidence.  At arity two there are
28,576 support inclusions but only 6,256 type pairs admitting a componentwise
causal routing.  Thus 22,320 arity-two inclusions still fail.

They fail because no permutation matches every source component to a causally
reachable target component.  This is the tensor-level propagation of the
twelve atomic failures from note 0053, combined with ordered resource
matching.

---

# Part IV. Exact finite enumeration

## 13. Object and support distribution

The 273 types have the following arities:

| arity | types |
|---:|---:|
| 0 | 1 |
| 1 | 16 |
| 2 | 256 |

Their support sizes are:

| supporting core states | types |
|---:|---:|
| 8 | 1 |
| 4 | 32 |
| 2 | 104 |
| 1 | 64 |
| 0 | 72 |

Only eleven distinct support subsets appear.  Presentation and resource shape
therefore retain much more information than extension.

## 14. Inclusion table by arity

| source arity | target arity | support inclusions | pairs with a linear map |
|---:|---:|---:|---:|
| 0 | 0 | 1 | 1 |
| 1 | 0 | 16 | 0 |
| 1 | 1 | 72 | 60 |
| 1 | 2 | 368 | 0 |
| 2 | 0 | 256 | 0 |
| 2 | 1 | 2,448 | 0 |
| 2 | 2 | 28,576 | 6,256 |
| **total** |  | **31,737** | **6,317** |

The 6,317 count is by ordered source-target type pair.  Counting distinct
admissible permutations instead gives

\[
5,373+2(944)=7,261
\]

shortest routing-level witnesses.  The suffix word inside each atomic fibre
remains open and may have longer representatives.

---

# Part V. Consequences for the research line

## 15. Relation to the unresolved \(L/R\) reduction

The synchronized tensor does not force independent left and right programs
into one total execution order.  It separates two kinds of order:

- inside each component, causal time is the suffix order of its evidence
  history;
- between components, port routing is an explicit permutation rather than a
  hidden totalization.

Thus an expression resembling \(L\mid R\) can retain two resources and their
common base state without pretending that either \(L<R\) or \(R<L\).  When an
output reverses their roles, exchange records that fact.  When the components
must interact, a future checked program event must supply the interaction.

This does not solve the global \(L/R\) reduction problem.  It identifies one
reason the attempted reduction was too coarse: causal sequence, synchronized
co-presence, and resource routing are different relations.

## 16. Relation to startup calibration

The same distinction applies to startup calibration.  Several computers may
begin from one declared world state while retaining separate calibration
certificates.  A joint calibrated support is their support intersection, but
that intersection does not say:

- which certificate belongs to which computer;
- whether one certificate was copied;
- whether one computer was ignored;
- whether their roles were exchanged; or
- how later calibration steps extended each history.

A future three-computer certificate can therefore use an arity-three version
of the same resource-routing grammar.  Merely enumerating arity three is not
the next foundational step; first the resource identifiers must be grounded
in checked program lineage.

## 17. Relation to logic on a 3-form

The experiment supplies a candidate multiplicative rule:

\[
\frac{e:E_m(s)\qquad f:E_n(s)\qquad e\# f}
     {e\otimes_s f:(E_m\otimes_s E_n)(s)}.
\]

Here \(e\# f\) means that the resources are distinct, and the shared \(s\)
expresses synchronization over one base state.

This rule combines:

- temporal information in the two retained traces;
- spatial information in their common supporting state; and
- constructive information in distinct lineages and explicit routing.

That makes it a plausible 3-form connective proposal.  It is still not a
natural-deduction system: there is no discharge, implication, additive sum,
case analysis, normalization theorem, or general proof equality.

---

# Part VI. Verification and limits

## 18. What the fixture establishes

Within the declared finite machine, arity-zero-to-two object family, and
permutation-plus-suffix grammar, the fixture establishes:

1. 273 finite presented evidence types and eleven observed supports;
2. synchronized evidence only over one initial state;
3. rejection of duplicate resource identifiers;
4. explicit identity and exchange routings;
5. componentwise tensor of two atomic causal maps;
6. exact cut with permutation composition and suffix concatenation;
7. preservation of each resource identifier exactly once;
8. absence of all cross-arity maps;
9. equal-support counterexamples to implicit contraction and weakening;
10. the exact 31,737 / 6,317 / 25,420 inclusion split;
11. the exact 3,088 cross-arity and 672 same-support cross-arity gaps;
12. the exact 5,373 single-routing and 944 double-routing split; and
13. 7,261 routing-level shortest witnesses.

## 19. What it does not establish

The fixture does not establish:

- a stable tensor, product, conjunction, evidence, proof, or 3-form API;
- a Rust-authoritative resource identity;
- that the carrier is a categorical product;
- projection, diagonal, copy, discard, contraction, or weakening;
- associativity, symmetry, or unit coherence cells;
- equality or normalization of evidence words;
- a complete symmetric monoidal category;
- arity-unbounded or universal computation;
- a natural-deduction calculus;
- a solution to the global \(L/R\) problem;
- a complete three-computer startup certificate; or
- validity outside the finite monoid and declared suffix grammar.

The Python resource identifier prevents accidental aliasing inside this
fixture; it cannot authorize stable semantic lineage.  The experiment changes
no Rust API, no IR schema, no `claims.toml` entry, and no active `ProgramSlice`
priority.

## 20. Next gate

The highest-priority next obligation is not a larger tensor count.  It is to
ground one composite evidence resource in a Rust-checked program boundary:

1. select a small checked diagram containing explicit independent, share, and
   discard events;
2. obtain source, occurrence, history, and lineage data from Rust rather than
   inventing Python resource identity;
3. adapt that checked data read-only into the finite evidence experiment;
4. verify that independent pairing preserves two lineages;
5. verify that copy appears only after the explicit share event;
6. verify that discard remains visible in history; and
7. determine whether the current permutation-plus-suffix grammar survives or
   must be weakened.

Only after this bridge should the same constructor be lifted to three
computers or promoted toward a stable logical connective.

## 21. Conservative conclusion

The finite result is:

> A synchronized pair may share an observed base state without sharing an
> evidence resource.  Its transformations are generated by explicit resource
> routing plus causal continuation.  Support intersection forgets both
> resource multiplicity and routing, so it cannot justify contraction,
> weakening, or proof equality.

This is a small but genuine composite evidence fragment.  It says more than
ordinary proposition intersection and less than a finished logic on a
3-form—which is exactly the boundary the next experiment needs.

The first bridge from research-local resource names to Rust-checked source,
occurrence, and lineage data is carried out in
[`0055-rust-checked-structural-evidence-bridge.md`](0055-rust-checked-structural-evidence-bridge.md).
