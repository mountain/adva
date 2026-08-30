# Occurrence-Resolved Backward Probe Pairing

Status: bounded Python research witness over Rust-checked finite diagrams. This
is not a stable `Probe`, `pullback`, reverse-mode, adjoint, or learning API.

## Question

The parameterized optical experiment produced a scalar sensitivity

$$
d\mathcal L
=
(1-3\kappa)\,dx+3\,ds-3x\,d\kappa.
$$

That result was computed by Rust's authoritative forward differential. It did
not answer three finer questions:

1. can a declared output demand be transported backward over the actual
   checked expression graph without treating a matrix as the program;
2. can the backward demand be paired exactly with every tested forward
   tangent;
3. does the resulting input gradient retain the program's internal sharing
   and occurrence geometry?

The third question is essential. If only the three final numbers are kept,
then a direct arithmetic expression and a factorized device history may again
become indistinguishable.

## The carrier under test

For a checked diagram $D$, let $\mathcal E_D$ be its finite set of wire
endpoints. Rust already assigns every endpoint:

- a canonical input or node-output producer;
- an output index;
- an ordered occurrence lineage;
- the source of every occurrence in that lineage.

The research witness attaches one numerical demand to this existing data:

$$
\eta(e)
=
\bigl(e,q_e,\operatorname{Lin}(e),\operatorname{Src}(e)\bigr),
\qquad e\in\mathcal E_D.
$$

No new `SourceId` or `OccurrenceId` is allocated in Python. Endpoint keys,
lineages, sources, and copy parent--child records are copied from the
Rust-validated IR. The coefficient $q_e$ is a test-local numerical field on
that checked carrier.

This distinction matters:

> The root gradient is only the boundary value of a backward demand field;
> the occurrence-decorated endpoint field is the finer candidate carrier.

It is still only a candidate. The stable ontology does not yet contain this
field or certify its transport.

## Local arithmetic transport

At one declared numerical input, the bounded witness supports only the
versioned builtin operations used by the optical fixture. If $q$ denotes an
output demand, the reverse numerical rules are

$$
\begin{aligned}
\operatorname{add}:&\quad q\longmapsto(q,q),\\
\operatorname{mul}:&\quad q\longmapsto(qb,qa),\\
\operatorname{neg}:&\quad q\longmapsto-q.
\end{aligned}
$$

For an explicit copy with branch demands $q_0,q_1$,

$$
\operatorname{copy}:\quad(q_0,q_1)\longmapsto q_0+q_1.
$$

The sum is recorded at the parent endpoint, but the two branch endpoint
records and their distinct child occurrences are not deleted. Constants
receive no input demand. `scale` is treated by its checked two-input product
rule, not as a hidden host-language parameter.

These are Python research rules over already checked operation references.
They are independently compared with Rust's forward differential and have no
semantic authority by themselves.

## The optical pairing

Use the parameter cell

$$
p_\kappa(x,s)
=
\bigl((1-\kappa)x+s,-\kappa x+s\bigr)
$$

at

$$
u=(x,s,\kappa)=(2,3,1),
$$

and declare the oriented codomain probe

$$
\lambda=(1,2).
$$

Checked execution gives

$$
p_1(2,3)=(3,1).
$$

The research backward traversal returns the domain demand

$$
\mathsf B_{p,u}(\lambda)=(-2,3,-6).
$$

For every tested tangent $\delta u$, the experiment checks

$$
\boxed{
\left\langle
\lambda,
d p_u(\delta u)
\right\rangle
=
\left\langle
\mathsf B_{p,u}(\lambda),
\delta u
\right\rangle
}.
$$

The left side is built from the Rust-returned forward Jacobian. The right side
uses the research-local backward endpoint traversal. The finite test covers
the three input basis tangents and one mixed tangent. The resulting domain
demand also agrees with the Rust gradient of the separately checked scalar
program $\ell\circ p_\kappa$.

The notation $\mathsf B$ is deliberately provisional. It is not the reserved
stable $D^*$ operation.

## What copy reveals

Two copy sites occur in the factorized parameter cell.

### Copy of the original $x$ occurrence

One branch carries $x$ directly toward the position output. The other carries
$x$ into the product $\kappa x$. At the selected input their backward demands
are

$$
(1,-3),
$$

which recombine to the root demand

$$
1+(-3)=-2.
$$

The two coefficients are attached to two distinct child occurrences of the
same source.

### Copy of the merged slope lineage

Before free propagation, the slope expression already carries the three
sources $x,s,\kappa$. Copy creates two distinct three-occurrence child
lineages. Their demands are

$$
(1,2),
$$

which recombine to

$$
1+2=3.
$$

The test reads every parent--child occurrence assignment from checked copy
history and verifies that both branch records use exactly the certified child
lineages. It does not divide a merged scalar demand among the occurrences in
its lineage. Such a division would require additional semantics and would not
be canonical here.

## Causality, cut, and incision

This fixture gives a bounded operational reading of the earlier three-way
intuition:

- causality is the checked forward dependency order, along which values and
  tangents propagate;
- a cut exposes a frontier of endpoints on which a demand field can be read;
- incision or sharing is visible at explicit copy sites, where future demands
  remain occurrence-separated before recombining at their certified parent.

Backward traversal reverses dependency order, not physical time and not the
program itself. Its constructivity comes from visiting the actual operation
and copy records rather than an externally supplied action array.

This does not establish a global equivalence among causality, cut, and
incision. It supplies one local calculation in which the three roles are
simultaneously visible.

## Equal gradients, unequal demand fields

The previous experiment compared two scalar programs:

$$
\ell\circ P\circ L_\kappa
\qquad\text{and}\qquad
x+3s-3\kappa x.
$$

At the selected input, both have value $5$ and root demand

$$
(-2,3,-6).
$$

Their internal backward fields are nevertheless different:

- the device program has two copy sites, including one whose parent lineage
  contains all three sources;
- the direct expression has only the single-source copy needed to reuse $x$;
- their operation-demand sequences have different lengths and shapes.

Thus

$$
\text{equal root gradient}
\centernot\Longrightarrow
\text{equal occurrence demand field}
\centernot\Longrightarrow
\text{equal program}.
$$

This is the dual analogue of the earlier lineage residual: numerical
sensitivity at the boundary can agree while the construction fibre remains
distinguishable.

## Consequence for the spectral carrier

The result suggests a sharper answer to the carrier question. On the backward
or observer side, a bare covector or a list of eigenvalues is too coarse. A
more native finite carrier is an occurrence-decorated demand section over the
checked causal diagram. Repeated observer transport would act on such
sections, while a coordinate vector, action table, or spectrum would be a
compiled shadow obtained only after selecting a chart and forgetting part of
the section.

This interpretation is not yet a dual-spectrum construction. It identifies
the information that a future construction must avoid discarding too early.

## Relation to polynomial-like and matrix-like forms

At this stage the coefficients $q_e$ are numbers because the experiment is
evaluated at one input. The local rules nevertheless show the next lift:

- addition duplicates a demand expression;
- multiplication modifies each demand by the partner expression;
- copy recombines future demand expressions while retaining occurrence
  branches.

An expression-valued version would therefore output arithmetic expressions
from arithmetic expressions on the same checked graph. A matrix-like table
could then be compiled after choosing a finite chart and basis, but would no
longer be mistaken for the native mechanism. This is the promising route by
which polynomial-like and matrix-like presentations may become two readings
of one expression-level transport.

The present numerical witness does not yet construct that lift.

## Executable evidence

The extended optical test verifies:

1. every endpoint, lineage, source, and copy child is read from a
   Rust-validated diagram;
2. the bounded Python forward replay agrees with Rust execution;
3. the research backward domain demand is $(-2,3,-6)$;
4. the forward--backward pairing holds for four tangent directions;
5. the same demand agrees with the native gradient of the scalar objective;
6. the three root demand records retain three distinct source identities;
7. both copy sites use exactly their checked child occurrences;
8. branch demands $(1,-3)$ and $(1,2)$ recombine at their respective parents;
9. equal values and root gradients coexist with different internal demand
   fields for the device and direct histories.

## No-go boundaries

This calibration does not provide:

- a Rust `Probe`, `PredicateRegion`, or `pullback` value;
- a semantic certificate for the Python backward witness;
- a general reverse-mode implementation for the builtin registry;
- an unconditional transpose, inverse, dagger, or involution;
- a canonical splitting of one merged-lineage demand among its occurrences;
- an equation cell from equal values, gradients, or root demands;
- an expression-valued demand language;
- a dual spectrum, normal form, learning rule, parameter update, or physical
  measurement.

## Next obligation

The next theoretical target is to replace numerical endpoint coefficients by
checked arithmetic expressions while preserving the same occurrence carrier
and pairing law. That experiment should determine whether the native backward
object has the same input--output--computation shape as a program, and whether
polynomial-like and matrix-like forms arise only as two compiled observations
of this expression-valued transport.
