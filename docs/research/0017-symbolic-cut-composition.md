# Symbolic Backward Transport Across Nested Causal Cuts

Status: bounded Python research construction over one Rust-checked finite
diagram.  This is an exhaustive cut-composition calibration for the optical
parameter cell, not a stable contravariant functor or `D*` API.

## Why composition is the next obligation

The expression-valued backward experiment established two facts:

1. a numerical endpoint demand is the evaluation of an unsimplified
   arithmetic expression; and
2. the three root demand expressions can be emitted as a fresh checked Adva
   program.

Fresh replay proved representability, but it could not preserve semantic
identity: parsing the replay necessarily created new source and occurrence
identifiers.  A composition law should be tested before extending the term
language, and it should avoid that identity gap.

The present experiment therefore stays inside one checked composite diagram.
Every direct and staged demand is attached to exactly the same Rust endpoint,
lineage, and source records.

## Causal cuts and demand sections

Let $D$ be the finite checked diagram of the parameterized optical cell, and
let $E_D$ be its operation events.  A completed past $U\subseteq E_D$ is
required to contain the predecessor of each of its events.  Its frontier
$\partial U$ consists of the checked wire endpoints whose producer is ready
at $U$ and whose consumer still lies in the future or at the program output.

The previous expression field restricts to a cut section

$$
q_U
=
\left.
\widehat\eta
\right|_{\partial U}.
$$

Each section value retains four pieces of data:

$$
\bigl(e,Q_e,\operatorname{Lin}(e),\operatorname{Src}(e)\bigr).
$$

The endpoint and its occurrence decoration come directly from checked IR.
Only the unsimplified coefficient expression $Q_e$ is constructed by the
research transport.

## Segment transport

For nested completed pasts $U\subseteq V$, define the bounded backward
segment operation

$$
\mathcal B_{U\leftarrow V}:q_V\longmapsto q_U
$$

by traversing exactly the checked nodes in $V\setminus U$ in reverse causal
order.  Forward argument expressions are replayed once on the same original
diagram.  The local reverse rules are still the bounded
constant/copy/add/mul/scale/neg rules.

No variable-name substitution, source relabeling, program recompilation, or
coordinate array is involved.  A cut demand seeds the output endpoints of one
segment; local reverse rules propagate it to the preceding cut.

For three nested cuts $U\subseteq V\subseteq W$, the law under test is

$$
\boxed{
\mathcal B_{U\leftarrow W}
=
\mathcal B_{U\leftarrow V}
\circ
\mathcal B_{V\leftarrow W}
}.
$$

The outermost cut is allowed to be the program output and the innermost cut
the program input.

## Exhaustive finite verification

The executable witness enumerates every downward-closed event set of the
checked parameter cell.  For every nested pair $U\subseteq V$, it constructs
the full backward field in two ways.

### Direct construction

The declared output probe $\lambda=(1,2)$ is propagated through every checked
node in one uninterrupted reverse traversal.

### Three-segment construction

The same probe is propagated through:

1. the outer segment $E_D\setminus V$ to $\partial V$;
2. the middle segment $V\setminus U$ to $\partial U$; and
3. the inner segment $U$ to the input frontier.

The three resulting segment maps are assembled according to the original
producer of each checked endpoint.  The test compares the direct and staged
coefficient expressions at every endpoint.

The equality is intensional in this bounded implementation:

$$
Q_e^{\mathrm{direct}}=Q_e^{\mathrm{staged}}
$$

as unsimplified `DemandExpression` syntax, not merely after numerical
evaluation or commutative normalization.  Hence every evaluation of either
side agrees automatically within the supported arithmetic fragment.

This exact equality relies on the deterministic checked node order and the
same local constructors on both paths.  It is evidence for composition in the
fixture, not a general coherence theorem for alternative normal forms.

## The focus--drift cut

One distinguished causal cut lies after the tunable focusing stage and before
the final free-propagation stage.  Its two endpoints carry:

- the position occurrence with one source; and
- the slope expression with a merged lineage containing the three sources
  $x,s,\kappa$.

Transporting the output probe $(1,2)$ backward only through the drift exposes
the unsimplified cut demands

$$
q_{\mathrm{focus\ cut}}
=
\bigl(1,1+2\bigr).
$$

Continuing through the focusing segment and the earlier root-copy segment
reconstructs

$$
\begin{aligned}
Q_x&=1+\bigl(-(1+2)\bigr)\kappa,\\
Q_s&=1+2,\\
Q_\kappa&=\bigl(-(1+2)\bigr)x.
\end{aligned}
$$

At three numerical inputs, every endpoint of this explicit three-stage
factorization again agrees with the independently constructed numerical
backward field.

## Causality, cut, and incision

The composition law sharpens the earlier three-way interpretation.

- **Causality** supplies the partial order that makes $U\subseteq V$ a legal
  factorization of computation.
- **Cut** supplies the spatial carrier $\partial U$ on which an intermediate
  expression-valued demand section lives.
- **Incision or sharing** supplies the occurrence refinement at explicit copy
  events, so a cut can expose distinct child demands without identifying their
  common source.

The three roles are not postulated as separate coordinate axes.  In this
fixture they arise from three readings of the same checked program and are
coupled by the cut-composition law.

## Consequence for program-like duality

The positive result is stronger than root replay.  It says that the proposed
backward object can be factorized and recomposed internally, while retaining
the program's actual occurrence identities.  The native candidate therefore
has the shape of a contravariant section transport over the finite causal-open
poset:

$$
U\longmapsto q_U,
\qquad
U\subseteq V
\longmapsto
\mathcal B_{U\leftarrow V}.
$$

Calling this a presheaf or functor would still be premature: only one bounded
diagram and one declared probe have been exhausted.  Nevertheless, the object
under test is no longer a list of derivatives.  It is an expression field
with an internal restriction and composition mechanism.

## Polynomial-like and matrix-like shadows

Composition is verified before choosing a basis or normalizing expressions.
This supports the interpretation that:

- a polynomial-like presentation forgets occurrence construction and rewrites
  the section coefficients into a chosen expression class;
- a matrix-like presentation chooses finite input and output probes and
  tabulates their pairings;
- multiplication of such tables is a coordinate shadow of cut composition,
  not the mechanism from which composition originates.

No triangular form, transpose ontology, or linear module is required by the
test.  The same statement may later acquire those shadows in a selected
commutative chart.

## Consequence for the spectral carrier

The plausible carrier now has both values and transport:

$$
\boxed{
\text{occurrence-decorated expression sections over causal cuts}
}
$$

together with their compositional backward propagation.  A program spectrum
should eventually describe invariant or recurrent behaviour of this transport
under iteration, chart change, or objectification.  Eigenvalues of a chosen
finite table may report one such behaviour, but they are not yet the carrier.

## Executable evidence

The extended optical test verifies:

1. every completed event past of the checked parameter cell is enumerated;
2. every nested pair of such pasts defines legal outer, middle, and inner
   reverse segments;
3. each cut endpoint is read from the same Rust-checked diagram;
4. upper and lower cut demands remain unchanged when used to seed the adjacent
   segment;
5. direct and three-stage fields have exactly equal unsimplified expressions at
   every checked endpoint;
6. at least one factorization has three nonempty segments;
7. the focus--drift cut exposes demands $1$ and $1+2$ on lineages of sizes one
   and three; and
8. one explicit three-stage factorization agrees endpoint-by-endpoint with the
   numerical backward witness at three inputs.

## No-go boundaries

This calibration does not establish:

- a stable cut, section, presheaf, functor, or `D*` object;
- composition for arbitrary checked diagrams or builtin operations;
- equality across distinct programs with fresh semantic identities;
- coherence between different expression normal forms or reverse schedules;
- gluing across overlapping rewrites, feedback, recursion, or forgetting;
- a canonical time--space exchange;
- an `exp`-closed polynomial-like class;
- a matrix standard form, spectrum, learning law, or physical dynamics.

## Next obligation

The non-exponential carrier has now passed the identity-preserving composition
test.  The next controlled extension should add the checked `exp` builtin with
the local expression rule

$$
Q\longmapsto Q\,\exp(A),
$$

then repeat the full cut-composition calibration on a fixture where the cut
demand genuinely depends on an exponential intermediate expression.  That is
the appropriate point to decide whether `polynomial-like` should mean an
exp-polynomial closure, or whether the two names designate different compiled
subclasses of one larger program-like transport language.
