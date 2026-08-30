# Surreal Cut Presentations, Objectification, and a PSP-Star No-Go

Status: bounded exact research result.  It separates finite surreal cut
presentations from the surreal numbers they objectify and records a necessary
condition for any expression-level `P S P*` factorization.  It does not expose
a stable surreal, objectification, pullback, or factorization API.

## Question

The finite E0 dual-cut calibration shows that a checked causal cut can be
encoded by a decorated dual cycle and that an enabled event is one local face
surgery.  The natural next proposal is to read the two sides of that cut as a
Conway form

\[
\{L\mid R\}
\]

and compile an arithmetic program, possibly including addition and
multiplication, to a surreal number.

This note asks whether that objectified number can itself be the carrier on
which a scope-faithful analysis `P*`, characteristic surgery `S`, and synthesis
`P` satisfy

\[
T=P_Y S_T P_X^*.
\]

The answer is no in general, already for finite dyadic cuts.  The obstruction
is not analytic or computational.  Objectification is a non-injective,
non-natural quotient of cut presentations.

## Form versus number

A finite surreal **form** retains the presented option sets `L` and `R`.
Different forms can denote the same surreal number.  In the present program
reading, the form is the relevant intensional carrier: its two sides may retain
ordered holes, scope paths, source/occurrence decorations, and the surgery
history.

The corresponding surreal **number** is obtained by choosing the simplest
surreal strictly between every left and right option.  That choice forgets the
presentation.  It is therefore an observation or objectification, not the
native program object.

## Exact non-naturality witness

Let

\[
C=(0\mid 1),\qquad \operatorname{Obj}(C)=\frac12,
\]

and let `g(z)=3z`.  Acting on the objectified result gives

\[
g(\operatorname{Obj}(C))=\frac32.
\]

Acting on the presented options first gives

\[
gC=(0\mid 3),\qquad \operatorname{Obj}(gC)=1,
\]

because `1` is the simplest surreal between `0` and `3`.  Hence

\[
\boxed{
g(\operatorname{Obj}(C))\ne \operatorname{Obj}(gC)
}.
\]

Objectification therefore does not commute even with positive integer
scaling.  Arithmetic transformation cannot in general be pushed through the
objectification map without a residual recording the failed square.

## Retraction obstruction

There is an even smaller injectivity obstruction.  The distinct finite forms

\[
C_2=(0\mid 2),\qquad C_3=(0\mid 3)
\]

both objectify to `1`.  Suppose an analysis map on cut presentations factors
through the objectified surreal number:

\[
P^*=A\circ\operatorname{Obj}.
\]

Then `P*(C_2)=P*(C_3)`.  No single-valued synthesis `P` can consequently
satisfy both

\[
PP^*(C_2)=C_2,
\qquad
PP^*(C_3)=C_3.
\]

Thus an exact retraction, and therefore an unrestricted exact PSP-star
factorization even for the identity transformation on this two-element
fragment, is impossible if `P*` sees only the surreal number.

More generally, if `q:X->Q` is any quotient and two distinct expressions
`x_0,x_1` have `q(x_0)=q(x_1)`, no analysis that factors through `q` admits a
left-inverse synthesis on both expressions.  The required residual is exactly
the information discarded by `q`.

## Ordered-hole witness in checked Adva programs

The executable calibration also compiles two binder-free two-hole programs:

```text
left-right(x,y) = add(x,y)
right-left(x,y) = add(y,x)
```

At `x=2,y=3` both realize the scalar `5`, but the Rust-checked input producer
orders are respectively `(0,1)` and `(1,0)`, and their IR values are distinct.
No equation cell identifies them.  A scalar or surreal result therefore
cannot reconstruct the ordered substitution boundary.

This is not yet variable capture: PSC0 has no local binders.  It proves the
prior obstruction that any future capture-avoiding calculus must first retain
ordered hole identity and nested frame provenance.

## Consequence for the E0 factorization

The viable characteristic carrier is not a bare terminal loop and not a
surreal number.  It must be at least a decorated surreal cut form:

\[
\mathsf{Form}_G(E)=
(L_E\mid R_E;
  \text{ordered holes},
  \text{scope path},
  \text{sources/occurrences},
  \text{surgery trace}).
\]

Objectification may then be applied as a later observation

\[
\mathsf{Form}_G(E)\longrightarrow \operatorname{Obj}_Q(E),
\]

with an explicit residual or non-naturality witness.  It cannot be inserted
before `S_T` if the factorization is required to respect expression identity,
scope, and substitution.

For distinct source and target expression objects the still well-typed target
remains

\[
T=P_Y S_T P_X^*.
\]

Here `P_X*` must analyze a checked grafted expression into the decorated form,
not quotient it to a number.  `S_T` acts on the presented cut and its surgery
history.  `P_Y` may synthesize only on a declared fragment where a replayable
retraction is certified; otherwise the factorization must expose a residual.

## What survives and what fails

The surreal interpretation survives in a precise weakened form:

- `{L|R}` is a useful geometry of expression construction when read as a
  decorated presentation;
- the E0 dual-cycle surgery can supply the local transformations of that
  presentation;
- addition and multiplication may act on forms before objectification; and
- objectified surreal values remain valid observer-relative outputs.

The stronger proposal fails:

- one cannot compile every scope-bearing program to a surreal number and then
  reconstruct the original expression exactly;
- objectification is not functorial for ordinary arithmetic substitution;
- equal objectified values do not authorize an equation cell; and
- no `P*` that factors only through the objectified number can be a retractive
  expression analysis.

## Next obligation

The active `GraftTrace` task is now more sharply specified.  Its first
two-hole nested-call fixture must preserve enough data to build
`Form_G(E)` before any objectification:

1. parent and child frame identity;
2. ordered hole-to-argument boundary maps;
3. distinct argument-producing and callee-body regions;
4. entry and exit wires with unchanged source/occurrence lineage; and
5. the corresponding call-history event.

After that structure exists, test the contravariant gluing law on decorated
forms.  The test must compare both the form and its residual under
objectification.  Failure at that point would expose a deeper obstruction
than the quotient no-go established here.

## Executable evidence and boundaries

The exact Python test uses `fractions.Fraction`, finite dyadic birthdays, and
Rust-checked Adva IR.  It verifies the scaling non-naturality equation, the two
presentation collision, and the ordered-hole program distinction.  It uses no
floating-point tolerance, symbolic simplification, matrix, spectrum, or
analytic truncation.

The result does not define full surreal recursion, proper-class cuts,
canonical E0 grids, binders, alpha equivalence, capture avoidance, a stable
objectification operation, or a stable `P`, `P*`, or `S`.  It proves a finite
no-go boundary that those future constructions must respect.
