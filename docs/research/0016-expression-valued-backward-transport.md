# Expression-Valued Backward Transport and Checked Replay

Status: bounded Python research construction over Rust-checked finite diagrams.
The generated replay is a fresh checked program, not an identity-preserving
dual of the original program and not a stable `D*` operation.

## Question

The occurrence-resolved backward experiment attached numerical coefficients
to checked wire endpoints.  It left open whether those numbers were essential
or merely evaluations of a more native object.

The present experiment asks whether one declared output probe can instead be
transported as unsimplified arithmetic expressions while preserving:

1. every checked endpoint, occurrence lineage, and source decoration;
2. pointwise agreement with the numerical backward field;
3. the forward--backward pairing at more than one program input; and
4. representability of the resulting root demands by a fresh checked Adva
   program.

The distinction between preservation and representability is essential.  The
first three items concern a field over the original checked diagram.  The last
item deliberately recompiles plain Lisp expressions, so Rust allocates fresh
source and occurrence identities.

## Expression-valued carrier

For every checked endpoint $e$ of a diagram $D$, replace the numerical demand
$q_e$ by an unsimplified arithmetic term $Q_e$:

$$
\widehat\eta(e)
=
\bigl(e,Q_e,\operatorname{Lin}(e),\operatorname{Src}(e)\bigr).
$$

The term language used by this bounded witness has constants, original input
leaves, addition, multiplication, and negation.  An input leaf also records the
original root occurrence and source from which its variable name was read.
This audit decoration is not emitted when the term is later printed as Lisp.

No algebraic simplifier, polynomial normalizer, or matrix is used.  Thus the
term records the arithmetic construction by which a demand was produced, not
only the function obtained after evaluation.

## Local transport

The symbolic reverse rules have the same bounded shape as the earlier
numerical rules.  For an output demand term $Q$ and forward argument terms
$A,B$,

$$
\begin{aligned}
\operatorname{add}:&\quad Q\longmapsto(Q,Q),\\
\operatorname{mul}:&\quad Q\longmapsto(QB,QA),\\
\operatorname{neg}:&\quad Q\longmapsto-Q,\\
\operatorname{copy}:&\quad(Q_0,Q_1)\longmapsto Q_0+Q_1.
\end{aligned}
$$

The explicit copy rule retains both child endpoint records and constructs an
addition term at the certified parent.  Constants receive no input demand.
As before, `scale` is read from checked IR as a two-input product.  Operation
references, endpoints, lineages, and sources are accepted only from the
Rust-validated diagram.

## Optical result

Use the checked parameter cell

$$
p_\kappa(x,s)
=
\bigl((1-\kappa)x+s,-\kappa x+s\bigr)
$$

and the declared constant output probe $\lambda=(1,2)$.  Backward expression
transport gives the following deliberately unsimplified root terms:

$$
\begin{aligned}
Q_x&=1+\bigl(-(1+2)\bigr)\kappa,\\
Q_s&=1+2,\\
Q_\kappa&=\bigl(-(1+2)\bigr)x.
\end{aligned}
$$

Evaluation yields the familiar numerical demand

$$
\bigl(1-3\kappa,3,-3x\bigr),
$$

but the raw terms expose a crossed dependency pattern:

| demand location | input read by its coefficient term |
|---|---|
| root $x$ endpoint | $\kappa$ |
| root $s$ endpoint | none |
| root $\kappa$ endpoint | $x$ |

This is a backward dependency relation induced by the declared probe and the
local arithmetic rules.  It is not by itself a canonical time--space swap.

At three distinct values of $(x,s,\kappa)$, the experiment evaluates every
symbolic endpoint coefficient and compares it with a fresh numerical backward
traversal.  Endpoint sets, coefficients, lineages, and source decorations all
agree.  The comparison covers the whole finite endpoint field, not only the
three root values.

## Fresh checked replay

The three root terms are printed as a new binder-free Lisp function with input
ports $(x,s,\kappa)$ and three output ports.  Because $s$ is not read by any
coefficient term, the generated function consumes it through an explicit
`discard`.  The bounded generator refuses repeated input uses rather than
silently inventing a `copy`.

Rust parses, links, and validates the generated function.  Its output source
support has cardinalities

$$
(1,0,1),
$$

corresponding to the crossed dependency table above.  Across the three input
fixtures, checked execution returns exactly

$$
\bigl(1-3\kappa,3,-3x\bigr).
$$

This proves a bounded representability statement:

> the root boundary of this expression-valued demand field can itself be
> computed by a checked arithmetic program.

It does not prove that the replay has the same sources, occurrences, history,
or semantic identity as the original program.  Those identities are fresh by
construction.

## Pairing as one expression family

For every one of three program inputs and four tangent directions, the test
checks

$$
\left\langle\lambda,d p_u(\delta u)\right\rangle
=
\left\langle
\operatorname{eval}_u(Q_x,Q_s,Q_\kappa),
\delta u
\right\rangle.
$$

The left side uses the Rust forward differential.  The right side executes the
fresh checked replay program.  Consequently the witness is not a table of
unrelated gradients fitted at separate points: one arithmetic expression
family supplies the demands throughout the tested inputs.

## Program-like, polynomial-like, and matrix-like readings

This bounded result supports a precise part of the proposed general
mechanism.  The backward object now has a program-like shape:

- its inputs are arithmetic expressions carried by checked occurrences;
- its outputs are arithmetic demand expressions on checked endpoints;
- its computation is local expression transformation along the program's
  actual causal and copy structure.

The occurrence-decorated expression field is therefore a better native
candidate than either a coefficient vector or a matrix.  A polynomial-like
reading can be obtained by forgetting occurrence construction and normalizing
the arithmetic terms.  A matrix-like reading can be obtained after choosing
input and output probes and tabulating the resulting pairings.  In this
experiment those are two derived observations of the same transport, not two
competing ontologies.

No triangular matrix is needed.  The fixture also contains no `exp`, so it
does not decide whether `polynomial-like` and `exp-polynomial` should be the
same class.  That question should be tested only after the expression carrier
and its composition law survive the present non-exponential fragment.

## Consequence for the spectral carrier

The experiment strengthens, but does not finish, the earlier carrier answer.
The finite object preserved before choosing coordinates is

$$
\text{an occurrence-decorated expression section over checked endpoints}.
$$

Numerical covectors, derivative arrays, characteristic polynomials, and
eigenvalues arise only after evaluation, basis choice, iteration, and
forgetting.  A future program spectrum should therefore concern repeated or
composed transport of these sections, not the eigenvalues of an array inserted
as prior ontology.

## Executable evidence

The extended optical test verifies:

1. symbolic input leaves audit the original checked root occurrence and
   source;
2. the unsimplified term $Q_s$ remains `1 + 2`, rather than being collapsed to
   `3`;
3. every symbolic endpoint demand evaluates to the corresponding numerical
   endpoint demand at three inputs;
4. all endpoint lineages and sources agree in those comparisons;
5. the root dependency pattern is $x\leftarrow\kappa$, $s\leftarrow\varnothing$,
   and $\kappa\leftarrow x$;
6. a fresh three-output replay is Rust-checked and has output support
   cardinalities $(1,0,1)$;
7. checked replay agrees with the symbolic terms and the closed formula at all
   three inputs; and
8. the forward--backward pairing holds for twelve input--tangent combinations.

## No-go boundaries

This calibration does not provide:

- a Rust expression-valued probe, section, or transport certificate;
- stable `D*`, pullback, reverse mode, transpose, adjoint, or dagger;
- identity preservation between an original endpoint field and fresh replay;
- automatic insertion of `copy` for repeated variables;
- equality or canonical normalization of demand expressions;
- a composition, functoriality, or cut-gluing theorem;
- an `exp`-closed, exp-polynomial, or higher-order expression class;
- a program spectrum, eigenobject, learning rule, or physical measurement.

## Next obligation

The next target is compositional rather than more numerical.  Construct the
expression-valued demand field at an arbitrary checked frontier and test, for
two composable checked programs, whether transporting through the composite
agrees endpoint-by-endpoint with successive transport through the two pieces.
Only after that cut-composition law is established should the bounded term
language be extended with `exp` and used to compare polynomial-like and
matrix-like compiled observations.
