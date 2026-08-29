# Occurrence-Affine Causal-Cut Lift

Status: bounded research calibration, not a stable semantic API.

## Question

Can one checked program be read through the three layers

1. relation,
2. generation, and
3. boundary,

using one affine add/multiply language whose readings are expressions rather
than numbers?

The first candidate was too strong.  A raw causal-cut wire is not always an
affine variable.  If the future contains

```text
raw hole -> copy -> multiply
```

then the ordinary residual is `h * h`, which has degree two in the single raw
hole.  Explicit sharing therefore gives a minimal counterexample to raw-cut
multi-affinity.

The corrected carrier is not the raw frontier alone.  It is an
**occurrence-affine cut lift** consisting of

\[
\mathfrak A_D(U)
=
\bigl(
  U,
  \partial_D U,
  \widetilde{\partial}_D U,
  R_U,
  \Delta_U
\bigr).
\]

Here (D) is a checked finite program diagram and (U) is a completed causal
past.

## The five pieces

### 1. Completed past (U)

The Rust-checked operation DAG gives a causal event order.  A valid cut is a
downward-closed set of completed events.  This is the relational or temporal
part of the presentation.

### 2. Raw frontier \(\partial_D U\)

The raw frontier contains the checked wires produced in (U), or supplied as
inputs, and still demanded by the future.  Each wire retains type, occurrence
lineage, and source lineage.

### 3. Future-demand occurrence cover
\(\widetilde{\partial}_D U \to \partial_D U\)

Starting at a raw frontier wire, follow the uncompleted future.  Whenever a
checked `copy` is crossed, replace every incoming demand hole by two holes
whose labels are derived from the checked copy node and branch.  No fresh
semantic identity is allocated by Python: the lift is canonically indexed by
the raw checked producer plus a checked copy/branch path.

For the square fixture, before `copy` the raw frontier has one wire while its
future-demand cover has two holes:

\[
h \longmapsto (h_{(c,0)},h_{(c,1)}).
\]

After `copy`, the raw frontier itself already has two checked output wires, so
the cover no longer needs to expose a latent split.

This is the precise bounded sense in which choosing a cut on one temporal side
automatically lifts a dual spatial multiplicity on the other side.  The dual
side is a demand cover, not a dual vector space.

### 4. Residual expression \(R_U\)

Run only the uncompleted future symbolically over the lifted holes, preserving
the checked operation tree.  In the add/multiply fragment the result is
occurrence-wise multi-affine:

\[
\deg_{h} R_U \le 1
\qquad
\text{for every }h\in\widetilde{\partial}_D U.
\]

Multiplication is not jointly affine.  The claim is only that it is affine in
each independently lifted occurrence while the other occurrences are held
fixed.

### 5. Expression-valued diagonal \(\Delta_U\)

The completed past computes an expression (E_w) on every raw frontier wire
(w).  A lifted hole above (w) is not sent to a number and not merely to its
ultimate `SourceId`.  It is sent to the corresponding branch relabelling of
the whole boundary expression:

\[
\Delta_U(h_{w,p}) = p(E_w),
\]

where (p) is the checked future copy path carried by the lifted hole.

Consequently,

\[
\Delta_U(R_U)=\operatorname{Expr}(D),
\]

the occurrence-expanded checked expression of the whole program.  For

\[
y=x+1,\qquad \operatorname{copy}(y),\qquad y_0y_1,
\]

the boundary value at the pre-copy cut is the expression (E_w=x+1).  The
lifted residual is (h_0h_1), and the diagonal returns

\[
(x_0+1)(x_1+1),
\]

not the incorrect source-only substitution (x^2).  Identifying the two
source occurrences only afterwards gives the ordinary polynomial
((x+1)^2).

## Relation, generation, and boundary

The calibration supports a more precise version of the proposed three-layer
reading.

| Layer | Checked or derived datum | Meaning |
|---|---|---|
| Relation | causal order and completed past (U) | which construction events may already have occurred |
| Generation | advance (U\mapsto U\cup\{e\}) and move one operation through the cut | expression substitution and frontier transport |
| Boundary | raw frontier, occurrence cover, and expression diagonal | the presently available carriers and the future demands made of them |

The three layers are not literally one ordinary affine map.  They are three
readings of the richer object

\[
(\text{causal relation},\text{occurrence cover},
  \text{multi-affine residual},\text{expression diagonal}).
\]

Moving an enabled event from future to past changes the factorization between
(R_U) and \(\Delta_U\), while their composite remains the whole checked
expression.  Independent event orders reach the same endpoint presentation,
but their transport traces remain distinct.  Thus construction is not erased
by extensional equality.

## Polynomial-like and matrix-like

No triangular matrix is needed in this presentation.

The **polynomial-like** view expands (R_U) simultaneously over all lifted
holes.  It is multi-affine before diagonals.  Powers arise when a diagonal
identifies several lifted demands with branch relabellings of one boundary
expression or, later, when an input-chart observer forgets distinct occurrences
and whole-program source identity.

For any selected hole (h), multi-affinity gives a canonical local split

\[
R_U=A_h+B_hh,
\]

where (A_h) and (B_h) remain expressions in the other holes.  This is the
bounded **matrix-like** reading: it is a one-fibre coefficient action or local
affine decomposition, not an assertion that a numerical matrix is the
program's ontology.  Choosing many holes and a numerical observer can package
these coefficient actions as a matrix, but that is a later chart-dependent
objectification.

In this sense polynomial-like and matrix-like can be two orientations of the
same expression-valued occurrence-affine cell:

- simultaneous expansion gives the polynomial-like face;
- selection of one input occurrence and its output coefficient action gives
  the matrix-like face.

They need not be identical after an observer, normalization, or source
diagonal has forgotten construction data.

## Bounded evidence

`tests/python/test_occurrence_affine_cut_presentation.py` derives every object
from Rust-checked IR and checks four claims.

1. **Raw-frontier no-go.**  At the pre-copy cut of `square`, one raw hole occurs
   twice in the residual, so raw multi-affinity is false.
2. **Occurrence-lift recovery.**  The checked copy branches derive two lifted
   holes; the residual is multi-affine, and the expression diagonal agrees
   before and after executing `copy`.
3. **All-cut calibration.**  Every completed causal past of the branching
   `fork-recombine-expanded` fixture has a multi-affine lift and reconstructs
   the same whole occurrence-expanded expression.  Independent `neg` and
   `copy` orders have distinct traces and the same endpoint presentation.
4. **Forgetting no-go.**  `shared-double` and `scale-double` have distinct
   expression, occurrence, and whole-program `SourceId` presentations, but
   their commutative named-input polynomial shadows are both (2x).

The named-input polynomial computation is explicitly a derived Real-valued
chart.  It is used to demonstrate loss of occurrence and source information,
not as the semantic carrier.  A `SourceId`-preserving polynomial correctly
keeps the two whole programs distinct.

## Candidate structural theorem

The experiment suggests the following theorem for a deliberately restricted
fragment.

> **Occurrence-affine cut-lift theorem (candidate).**  Every Rust-checked,
> finite, binder-free program generated by typed inputs, exact constants,
> `id`, explicit `copy`, `add`, `neg`, and `mul` admits, at every completed
> causal past, a canonically derived future-demand occurrence cover and an
> expression-valued residual that is affine in every lifted hole separately.
> Its checked expression diagonal reconstructs the whole
> occurrence-expanded program expression.

The expected induction is short but has not yet been installed as a Rust
certificate.

- Inputs and constants establish the base cases.
- `id`, `add`, and `neg` preserve degree at most one because checked linear use
  keeps their live occurrence supports disjoint.
- `mul` adds degrees, but its two checked inputs have disjoint live occurrence
  identities before any later diagonal.
- `copy` preserves multi-affinity by branch relabelling instead of duplicating
  an unchanged hole identity.
- Advancing a causal cut transfers one of these constructors between residual
  expression and boundary expression without changing their composite.

## Complexification hypothesis

The occurrence-affine construction itself does not require a numerical field.
Before observation it lives in a free typed expression language with explicit
copy and lineage.  Therefore changing the foundational program carrier from
the reals to a complex vector space would be premature.

The spectral observation layer is different.  There are three related reasons
to expect its natural scalar closure to be complex.

1. A transport mode can carry both dilation and oriented phase:
   \[
   e^{(\alpha+i\omega)t}=e^{\alpha t}e^{i\omega t}.
   \]
   The real part reports scale while the imaginary part reports rotation or
   phase.  Treating them separately loses the multiplicative unity of the
   mode.
2. Real polynomial factors and real transport actions need not split into
   one-dimensional real observations.  Complexification is the minimal
   familiar closure in which conjugate modes can be selected separately.
3. A loop or chart transition can retain an oriented phase even when its
   ordinary real magnitude returns to one.  This makes complex characters a
   plausible observer for future holonomy experiments.

In program-geometric language, (i) should first be tested as an oriented
expression action satisfying (i^2=-1), rather than assumed to be a primitive
coordinate scalar.  A complex eigenvalue would then be the report of a
declared complex observer on transport: its modulus is multiplicative scale
and its argument is oriented phase.

This yields a sharper working hypothesis:

> The pre-spectral carrier is the field-independent expression-valued
> occurrence-affine cut lift.  Its natural split spectral observer is a
> complexification, with conjugation recording the paired orientation rather
> than erasing one side of the time-space duality.

The next calibration should compare a conjugate pair of complex expression
characters with its unsplit real two-component presentation.  It must preserve
checked occurrence, source, cut, and transport data; otherwise complexification
would be only another lossy numerical chart.

## Consequence for the spectral question

This calibration moves the likely spectral carrier one level upward.  The
carrier should not begin as a numerical vector space or matrix.  A more
faithful candidate is the expression-valued occurrence-affine cut lift,
together with its causal transport and diagonals.  A scalar eigenvalue can
appear only after a declared observer/chart turns an expression coefficient
action into multiplication by a scalar and forgets enough occurrence and
history data.

This explains why a scalar spectrum is multiplicative without treating
multiplicative scalars as primitive program geometry: the scalar is the
observer's report of how a selected coefficient action scales a chosen ray.
The intrinsic pre-observation datum is still an expression action.

No spectral theorem is claimed here.  The calibration only identifies a
carrier rich enough not to collapse the already checked sharing distinctions.

## Boundary of the result

The current evidence does not establish:

- a stable `OccurrenceAffineCut` API or Rust certificate;
- the candidate theorem for every accepted PSC0 diagram;
- exponentials, logarithms, trigonometric operations, complex observers,
  binders, recursion, or feedback;
- noncommutative coefficient actions, where left- and right-affinity must be
  separated;
- a sheaf, bundle, manifold, module, or dual-vector-space ontology;
- objectification, a general spectral carrier, eigenvalues, holonomy, or
  higher coherence.

The immediate next mathematical step is to formalize the structural induction
in the checked Rust layer.  After that, the same carrier should be tested under
a conjugation-preserving complex observer before extending from the AM fragment
to general exponential-polynomial observations.
