# Tri-Bracket Eigen-Normalization Logic

Status: bounded research proposal and finite executable calibration following
[`0057-typed-vacua-constant-boundary-braids.md`](0057-typed-vacua-constant-boundary-braids.md)
and
[`0058-checked-gate-braid-composition.md`](0058-checked-gate-braid-composition.md).

The checked interpretation experiment and terminology correction are in
[`0060-checked-bracket-observer-bridge.md`](0060-checked-bracket-observer-bridge.md).

The executable fixture is
[`test_tri_bracket_partial_normalization.py`][fixture].

[fixture]: ../../tests/python/test_tri_bracket_partial_normalization.py

This note tests the proposal that computation may be organized as
normalization of mixed three-bracket forms toward typed eigenforms.  Its first
bounded result is:

> In the cell containing exactly one construction bracket, one spatial
> bracket, and one temporal bracket, the seven nonempty stable faces arise
> exactly as the seven possible sets of leaf colors.  All thirty
> mixed colored-Catalan presentations reduce to the calibrated eigenform
> `{}[]()` using a containment-splitting rewrite followed by oriented boundary
> exchange.  Flat exchange cannot act until mixed nesting is removed, and the
> exact braid transport layer supplies no containment-cutting operation.

This gives a small proposed logical language for partial normalization.  It
does not establish a universal machine, a stable normalizer, a stable bracket
or logic API, or a semantic identity in Adva.  The fixture is a finite Python
research oracle and does not allocate `SourceId`, `OccurrenceId`, proof cells,
or rewrite certificates.  Rust remains the sole semantic authority, and the
active implementation priority remains exact program-process work.

---

## 0. The decisive correction

The earlier strict braid calibration admitted only the flat word

```text
{}[]()
```

and rejected every nesting.  The normalization proposal reverses the role of
that restriction:

> absence of mixed nesting is a property of the target eigenform, not a
> restriction on raw presentations.

The raw carrier must therefore contain terms such as

```text
{[()]}
{[]()}
()[{}]
```

or there is nothing to normalize.  The fixed flat boundary remains the
calibrated output, while the program presentation may begin in a mixed form.

There is a second correction.  Sorting the colors of a nesting spine, for
example changing `{[()]}` into `([{}])`, does not make the
brackets nonnested.  A braid crossing changes order; it does not cut a
containment edge.  Strong eigen-normalization therefore needs an active
operation beyond reversible braid transport.

## 1. The first finite grammar

Use three colors

\[
D ::= K \mid X \mid t
\]

with glyphs

\[
K\leftrightarrow\{\},\qquad
X\leftrightarrow[],\qquad
t\leftrightarrow().
\]

The general unbounded grammar suggested by the intuition is

```text
forest  ::= empty | bracket forest
bracket ::= "{" forest "}"
          | "[" forest "]"
          | "(" forest ")"
```

The present calibration restricts this grammar to one finite **tri-cell**:
each color occurs exactly once.  A term is consequently an ordered rooted
forest on three distinctly colored nodes.

There are five uncolored ordered-forest shapes on three nodes and six ways to
assign the three colors.  Hence the fixture exhausts

\[
5\cdot 3! = 30
\]

raw forms.  This is the complete finite carrier for the declared first cell,
not a sample.

Three sorts must remain distinct.  `Raw111` is this thirty-object mixed
forest carrier.  `Flat111` is its six-object, zero-containment subset.  The
typed `PublicBoundary` is the single calibrated interface
\(K\otimes X\otimes t\), presented by `{}[]()`.  A nested raw forest is not a
checked boundary, and its root count is not checked program arity.

The restriction to one occurrence per color matters.  It is what makes the
seven nonempty faces exact in this experiment.  No repeated-color
`Stable` predicate is defined here: whether domain stability quantifies over
all occurrences or some occurrence is deliberately deferred.

## 2. Domain eigenpredicates

For a bracket occurrence \(b\), write \(\operatorname{desc}(b)\) for the
colors of all strict descendants.  The occurrence is monochromatic when

\[
\operatorname{desc}(b)\subseteq\{\operatorname{color}(b)\}.
\]

For a raw term \(p\), define

\[
\operatorname{Stable}(p)
=
\left\{
D\;\middle|\;
\text{the }D\text{-bracket is monochromatic}
\right\}.
\]

Because the first tri-cell has only one occurrence of each color, a bracket
is monochromatic exactly when it is a leaf.  Every nonempty finite forest has
a leaf.  Therefore

\[
\operatorname{Stable}(p)\ne\varnothing.
\]

This gives the seven exact nonempty faces without adding them by hand.

| exact stable domains | number of raw forms |
|---|---:|
| \(\{K\}\) | 2 |
| \(\{X\}\) | 2 |
| \(\{t\}\) | 2 |
| \(\{K,X\}\) | 6 |
| \(\{X,t\}\) | 6 |
| \(\{t,K\}\) | 6 |
| \(\{K,X,t\}\) | 6 |

The counts sum to thirty.  The six forms in the last row are all flat
permutations; only one is already calibrated in the external order \(KXt\).

This separates two notions:

1. **eigen-normality**: every color is stable, so there is no containment;
2. **boundary calibration**: the three flat roots occur specifically as
   `{}[]()`.

Startup calibration is therefore not identical to normalization.  It is the
remaining order choice after all three domains have reached eigenform.

## 3. Surface satisfaction and open judgments

For every nonempty

\[
S\subseteq\{K,X,t\},
\]

introduce the face-satisfaction predicate

\[
\operatorname{Sat}_S(p)
\quad\Longleftrightarrow\quad
S\subseteq\operatorname{Stable}(p).
\]

It means that every requested domain in \(S\) has normalized.  These seven
predicates overlap: a completely normalized term satisfies all seven.  The
disjoint stratum is instead

\[
\operatorname{Face}^{=}_S(p)
\quad\Longleftrightarrow\quad
S=\operatorname{Stable}(p).
\]

This distinction removes an ambiguity in the original list of seven stopping
modes.  The list can name either seven surface requests or seven exact faces;
the two uses must not share a judgment symbol.

The proof-relevant open judgment proposed for the next language is

\[
\boxed{
Q;\,p
\;\vdash\;
\operatorname{Sat}_S(p)\ @\ n
\;\dashv\;
\rho_{\bar S}
}
\]

where:

- \(Q\) is the finite observer and fuel/search policy;
- \(p\) is the raw mixed presentation;
- \(S\) is the requested nonempty face;
- \(n\) is the observed normalized surface;
- \(\rho_{\bar S}\) records the unnormalized complement, enabled rewrites,
  boundary disorder, and the retained trace.

The executable surface predicate returns `satisfied` or `open`.  The active
fuel-bounded runner returns `unknown` on exhaustion; exhausted fuel does not
prove that a normal form or halt does not exist.

The basic logical rules are provisionally:

\[
\frac{S\subseteq\operatorname{Stable}(p)}{\operatorname{Sat}_S(p)}
\quad(\textsc{Face-Sat})
\]

and

\[
\frac{\operatorname{Sat}_S(p)\qquad\varnothing\ne S'\subseteq S}
     {\operatorname{Sat}_{S'}(p)}
\quad(\textsc{Face-Weakening}).
\]

Face weakening is observational forgetting.  It must not be confused with a
program rewrite or with deletion of proof history.

## 4. Two different normalization operations

### 4.1 Active containment split

For distinct colors \(D\ne E\), the first active rule is

\[
D\langle E\langle u\rangle, v\rangle
\longrightarrow
D\langle v\rangle\;E\langle u\rangle.
\]

In the finite fixture it is applied when the \(D\)-bracket is a root and the
\(E\)-bracket is one of its direct children.  It cuts that one parent-child
edge and promotes the child subtree to the root forest.  Repeated promotion
eventually exposes every deeper edge.

The rule preserves all three bracket occurrences.  It does not copy or erase
a bracket.  It does forget the old attachment if only the output surface is
retained, so the event `split:D>E` remains in the trace.  A future checked
version must state how source, occurrence, and payload data cross this cut;
the present abstract bracket oracle does not authorize that semantics.

### 4.2 Coxeter boundary calibration

After the roots are flat, adjacent roots are exchanged toward the declared
order

\[
K<X<t.
\]

The executable oracle uses only the unsigned Coxeter endpoint projection
\(\pi:B_3\to S_3\), and only after the term is flat.  Its steps are named
\(s_1,s_2\); they do not distinguish \(\sigma_i\) from
\(\sigma_i^{-1}\).  It has the three-root critical pair

\[
s_1s_2s_1
\quad\text{and}\quad
s_2s_1s_2.
\]

Both routes take `()[]{}` to `{}[]()`.  Their raw traces remain different;
the Coxeter braid relation compares their endpoint schedules.  A lift to an
exact signed braid coherence cell must retain the Artin history from notes
0057 and 0058; the present `s_i` trace does not supply it.

Thus the syntax already requires the repository's three-way separation:

- `split` and oriented exchange are `DirectedRewrite` candidates;
- a later assertion that two endpoints denote the same program would require
  an `EquationCell` and is not made here;
- the Yang--Baxter comparison between two rewrite decompositions is a
  `CoherenceCell` candidate.

## 5. Termination and the exchange-only no-go

For a term \(p\), let

- \(e(p)\) be the number of bracket-containment edges; and
- \(i(p)\) be the inversion count of the current root colors relative to
  \(K<X<t\).

Order pairs lexicographically:

\[
\mu(p)=(e(p),i(p)).
\]

Every split strictly decreases \(e\).  It may expose roots in a less ordered
configuration, but the first coordinate has already decreased.  Every
oriented exchange preserves \(e\) and decreases \(i\).  Hence every rewrite
strictly decreases \(\mu\), and no split-plus-exchange reduction is infinite
in the first tri-cell.

The fixture exhaustively verifies that all thirty inputs have the unique
endpoint

```text
{}[]()
```

although branching inputs can retain several distinct reduction traces.

This proof also gives an exact no-go.  Twenty-four of the thirty raw forms
have \(e>0\).  The test-local Coxeter exchange is undefined on all of them,
while the exact braid transport of note 0057 is typed only on the flat public
boundary.  Therefore neither supplies a path from a nested raw form to a flat
eigenform.  An additional block-exchange extension could preserve \(e\), but
it would be a new research operation, not the existing exact braid.  Thus

\[
\boxed{
\text{braid transport calibrates order but does not perform strong
eigen-normalization.}
}
\]

The missing operation in the previous model was not another braid relation.
It was an active change of containment topology.

## 6. Schedule convergence does not erase schedule evidence

Consider the branching form

```text
{[]()}
```

The spatial child or temporal child can be split first.  Both schedules reach
the same calibrated surface, possibly after different exchanges.  The
fixture keeps both traces and verifies that they are unequal.

This gives a finite three-level distinction:

\[
\text{raw presentation}
\longrightarrow
\text{normal surface}
\longrightarrow
\text{requested stable face}.
\]

The first arrow forgets containment and schedule unless its trace is retained.
The second forgets domains outside the observer's requested face.  A finite
decision procedure may use the last two layers, but evidence must remain
indexed by the first.

## 7. Why a normal-looking state is not yet a halt

The fixture adds one bounded active inverse-shaped gate

\[
\operatorname{inject}_{D,E}:
D\langle\rangle\;E\langle\rangle
\longrightarrow
D\langle E\langle\rangle\rangle.
\]

Starting from `{}[]()`, the gate gives

```text
{[]}()
```

and reopens the construction domain while leaving the spatial and temporal
domains stable.  A subsequent split returns to `{}[]()`, but the
`inject;split` history is not empty.

If an active program still contains another `inject`, the flat surface is not
quiescent.  The bounded machine alternates injection and splitting; after two
steps its surface and control phase repeat while its trace grows.  A
fuel-limited run therefore returns `unknown` with the pending gate and trace
as residual.

This corrects a state-only notion of halting:

\[
\boxed{
\operatorname{Halt}_{S,Q}(M)
=
\operatorname{Sat}_S(\operatorname{surface}(M))
\land
\operatorname{Quiescent}_Q(M).
}
\]

Partial normalization is a property of a surface.  Halting is a property of
the surface together with its remaining program and observation policy.

This is the first place where the normalization intuition begins to resemble
an open computation rather than a terminating sorting algorithm: active gates
may continually create redexes for other domains.  The finite example shows
the mechanism but not universal computational capacity.

## 8. Relationship to the three computers

Note 0058 has already supplied one Rust-checked noninvertible spatial gate and
verified its color-relative composition with the braid layer.  It also found
that pure-braid history is observationally inert for the current value-only
gate contexts.  The containment split in this note addresses a different
obstruction: braid cannot turn a nested raw syntax into a flat eigenform.

The two active operations must not yet be identified.  `spatial-update`
changes checked values, copy/discard history, and lineage while preserving the
public three-color boundary.  Test-local `split` changes abstract containment
topology while preserving the three bracket occurrences.  Note 0060 connects
them only through a checked-grounded observer with an explicit residual; it
refutes a Rust-owned rewrite identity and classifies plain normalization as an
observer-level presentation.

The seven faces can be read exactly as the proposed observation interfaces:

| requested face | reading |
|---|---|
| \(\{t\}\) | temporal normalization |
| \(\{X\}\) | spatial normalization |
| \(\{K\}\) | construction normalization |
| \(\{t,X\}\) | temporal-spatial normalization |
| \(\{X,K\}\) | spatial-construction normalization |
| \(\{K,t\}\) | construction-temporal normalization |
| \(\{K,X,t\}\) | full eigen-normalization |

Their requested faces need not be surface-satisfied together.  Each can
observe a face and return the complement as an open residual, while machine
stopping still requires quiescence.  The first tri-cell does not yet contain
three independently injected checked programs.  It supplies only the proposed
control language in which such a machine could later be stated.

Full startup calibration now separates into:

1. remove all mixed containment to reach a full eigenform, or return an
   earlier requested face together with its open complement;
2. for the full path, calibrate the flat roots to the shared order `{}[]()`;
   and
3. check that no enabled active program can immediately reopen the face.

The old \(L/R\) order problem consequently becomes only the second layer.
Order cannot solve mixed containment, and an ordered surface cannot determine
whether active computation has ended.

## 9. What the fixture establishes

Within the one-occurrence-per-color tri-cell, the fixture establishes:

1. a parser for mixed three-bracket forests;
2. exactly five ordered-forest shapes and thirty distinct colorings;
3. exactly seven nonempty stable-domain sets;
4. the exact distribution \(2,2,2,6,6,6,6\) over those sets;
5. overlapping target-satisfaction predicates and disjoint exact-face strata;
6. twenty-four nested forms and six flat eigenforms;
7. one calibrated eigenform among the six flat permutations;
8. strict termination of split plus oriented exchange by a lexicographic
   measure;
9. a unique calibrated endpoint for every one of the thirty inputs;
10. unavailability of Coxeter calibration outside the six flat forms;
11. absence of a transport-only path from all twenty-four nested inputs;
12. distinct normalization schedules with one endpoint;
13. the three-root Yang--Baxter critical pair;
14. explicit open residuals for a partially satisfied face; and
15. reopening of a normalized domain by a pending active injection gate.

## 10. What it does not establish

The fixture does not establish:

- that brackets are the final Adva code carrier;
- semantics for arbitrary bracket payloads;
- repeated same-color or mixed-color bracket occurrences;
- a Rust-owned rewrite identity between `split` and existing \(T/X/K\) programs;
- source, occurrence, copy, discard, or graft transport through `split`;
- a stable rewrite, equation, coherence, normal-form, or logic type;
- confluence for an unbounded grammar with arbitrary active gates;
- decidability of any unbounded normalization problem;
- that every computation is normalization;
- code-as-data, an interpreter, self-application, or reflective execution;
- a simulation of a known universal machine; or
- Turing, component, coupled, or reflective universality.

In particular, split-plus-exchange in this finite grammar always terminates
and reaches one constant boundary.  That fact is evidence against calling the
bare system universal.  Computational openness enters only when independently
specified active gates can create new mixed forms and when the retained
residual carries data not collapsed by the boundary.

## 11. Result of the next falsifiable gate

Note 0060 performs the advertised experiment against the exact checked
spatial gate.  Its bounded verdict is:

1. one elementary `split` is not checked `spatial-update`;
2. a Rust-derived source observer projects the checked gate to dependency
   activation, not split;
3. a decorated Boolean equation-defect observer makes the checked gate
   commute with a conditional split macro;
4. the complete `ProgramSlice`, source/occurrence lineage, resource ledger,
   and schedule remain in a residual; and
5. compiler graft containment is a separate immutable construction tree.

Thus the plain normalizer is an observer presentation rather than the native
program carrier.  The next authority upgrade is a lineage-aware bracket event
with an exact discharge witness, not a larger untyped grammar.

## Conservative conclusion

The normalization intuition survives its first finite test in a precise but
limited form:

> The seven stable faces are not an arbitrary enumeration.  They are the
> seven nonempty leaf-color faces of the smallest mixed three-bracket cell.
> A containment split performs the missing topological change, and Coxeter
> endpoint exchange then calibrates the resulting flat boundary.  Exact braid
> history remains a separate signed transport layer.

The test also exposes the remaining gap:

> A terminating normalizer is not yet a universal computer.  Universality can
> only become plausible when checked active programs can create new redexes,
> act on retained payloads, and support a faithful simulation theorem while
> leaving an auditable residual.

The immediate object is therefore a proposed partial-normalization logic with
open evidence, not a completed theory of universal computation.

## References

- Eugenia Cheng,
  [Iterated distributive laws](https://arxiv.org/abs/0710.1120),
  for three-way distributive composition and the Yang--Baxter compatibility
  condition.
- André Joyal and Joachim Kock,
  [Weak units and homotopy 3-types](https://arxiv.org/abs/math/0602084),
  for the free braided monoidal category on colored generators.
- Yves Lafont,
  [Interaction combinators](https://doi.org/10.1006/inco.1997.2643),
  for a universal flat local-interaction calibration that requires more than
  invertible transport.
