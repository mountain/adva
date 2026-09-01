# Cube-Map Equivariance and Observer-Relative Degree

Status: exploratory finite calibration extending
[`0038-triadic-characteristic-inference-calibration.md`](0038-triadic-characteristic-inference-calibration.md)
and
[`0039-square-map-branch-copy-calibration.md`](0039-square-map-branch-copy-calibration.md).

This note studies the next deliberately small pressure test for triadic
characteristic inference:

\[
C(x)=x^3.
\]

The square calibration produced an apparently harmonious coincidence:

- a generic positive real value had two preimages;
- a positive interval pulled back to two real components; and
- the checked construction used two occurrences of one source.

The cube map breaks that coincidence. Over the real line it is a monotone
bijection, so a generic value has one real preimage and every interval has one
inverse-image component. Its checked construction still needs three
occurrences. After complexification, a generic value has three algebraic
preimages.

The central conclusion is therefore:

> Algebraic degree, reverse-fibre cardinality, spatial sheet count, and
> constructive occurrence multiplicity are different typed observables. They
> may agree in a selected interpretation, but no one of them should be used as
> the definition of the others.

A second conclusion is equally important:

> A useful characteristic need not be invariant under an observer symmetry.
> It may instead be equivariant. The square is invariant under sign reversal,
> while the cube carries the sign representation.

This is a research-local note and bounded Python fixture. It does not add a
stable degree, branch, graph, correspondence, complex-number, Hopf-algebra,
characteristic, or observer-pullback API. The complex calculation is an exact
SymPy calibration outside the current real-only Adva scalar core. The active
`ProgramSlice` priority and Rust semantic authority remain unchanged.

The note follows the project research format: intuition, finite evidence and
formalization, conservative conclusion, and red-team opinion.

## 1. Intuition

### 1.1 Why the cube is a diagnostic rather than merely another power

The square map tested three phenomena at once:

\[
x\sim -x,
\]

\[
Q^{-1}(a,b)
=
(-\sqrt b,-\sqrt a)
\cup
(\sqrt a,\sqrt b),
\]

and

\[
x^2
=
\operatorname{mul}(\operatorname{copy}(x)).
\]

All three carried a visible multiplicity of two. That agreement was useful,
but it risked suggesting a false identification:

\[
\text{temporal quotient size}
=
\text{spatial branch count}
=
\text{constructive copy count}.
\]

The cube map is the smallest counter-calibration. Over `R`,

\[
C:\mathbb R\longrightarrow\mathbb R,
\qquad
C(x)=x^3,
\]

is strictly increasing and bijective. Hence:

- no two distinct real states are identified by the value map;
- a real reverse fibre is a singleton;
- the inverse image of a real interval is one interval; but
- the multiplication circuit still consumes three occurrences of its input.

The experiment is therefore designed to separate structures that happened to
coincide for `x^2`.

### 1.2 One scalar “degree” is too coarse

For a polynomial presentation one can ask for its algebraic degree. For a
typed interpretation one can also ask:

1. how many source states lie over a generic observed value;
2. how many local spatial sheets lie over a generic target neighbourhood;
3. how many explicit source occurrences are consumed by a checked
   construction; and
4. how many branches are visible to the chosen scalar domain and observer.

These are not synonyms. A provisional observer-relative profile is

\[
\mathbf d_Q(P)
=
\left(
d_{\mathrm{alg}},
d_{\mathrm{fib},Q},
d_{\mathrm{sheet},Q},
d_{\mathrm{occ},Q}
\right).
\]

For the real cube calibration,

\[
\boxed{
\mathbf d_{Q_{\mathbb R}}(C)
=
(3,1,1,3).
}
\]

For a local complex observer away from the branch values,

\[
\boxed{
\mathbf d_{Q_{\mathbb C}}(C)
=
(3,3,3,3).
}
\]

The second equality is not evidence that algebraic sheets and construction
occurrences are literally the same objects. It only records equal finite
cardinalities under that particular pair of interpretations.

### 1.3 The observer domain changes spatial multiplicity

Over the real line, every equation

\[
x^3=y
\]

has exactly one real solution. Over the complex numbers, every nonzero generic
value has three roots,

\[
z,\qquad
\omega z,\qquad
\omega^2 z,
\]

where

\[
\omega^3=1,
\qquad
\omega\ne1.
\]

Thus the same polynomial syntax has different reverse-fibre structure under
different scalar observers.

This is a direct warning against treating branch count as a syntax-only
property. Branch count is relative to at least:

- the source and target scalar domains;
- the topology or geometry used by the observer;
- the target point or neighbourhood;
- whether multiplicity is counted; and
- whether branch identity is operationally retained.

### 1.4 Invariance is only one special case of feature stability

Let sign reversal be

\[
\sigma(x)=-x.
\]

The square satisfies

\[
Q\circ\sigma=Q.
\]

It is invariant and descends to the orbit quotient

\[
\mathbb R/C_2.
\]

The cube instead satisfies

\[
C\circ\sigma
=
\sigma\circ C.
\]

It is not invariant, but it is equivariant when the target carries the same
sign action.

This is the smallest exact distinction between two kinds of characteristic
stability:

\[
\text{invariance: }
f(gx)=f(x),
\]

and

\[
\text{equivariance: }
f(gx)=\pi(g)f(x).
\]

A characteristic calculus that admits only invariant features would erase
chirality that the cube preserves. The correct general question is not
whether a feature is fixed, but how it transforms under the declared observer
symmetry.

### 1.5 Differential criticality need not create a topological split

The cube has derivative

\[
C'(x)=3x^2,
\]

so the source critical set is

\[
R_C=\{0\},
\]

and the corresponding critical value is

\[
B_C=\{0\}.
\]

Nevertheless, the real map remains a homeomorphism. An interval crossing zero
still has one connected inverse image:

\[
C^{-1}((-8,27))
=
(-2,3).
\]

Hence the following notions must remain separate:

- differential critical point;
- topological failure of local homeomorphism;
- algebraic ramification;
- splitting of an observed open set; and
- multiplicity of a reverse relation.

Over `C`, zero is ramified for `z mapsto z^3`. Over `R`, the same formula is
bijective and does not split real opens. A typed characteristic must record
which category supports each statement.

### 1.6 Constructive multiplicity belongs to the program diagram

A linear checked construction cannot use one occurrence three times
implicitly. The bounded Adva fixture constructs a three-leaf copy tree:

\[
1
\xrightarrow{\operatorname{copy}}
2
\xrightarrow{\operatorname{copy\ one\ child}}
3,
\]

then multiplies the three leaves.

Schematically,

\[
x
\xrightarrow{\Delta_3}
(x_0,x_1,x_2)
\xrightarrow{\mu_3}
x_0x_1x_2.
\]

The three leaves have distinct occurrence identities and one common source.
That fact is independent of the number of real inverse branches.

The construction degree is therefore a property of a checked presentation
relative to an operation registry and copy discipline. It is not determined
by the extensional polynomial alone.

### 1.7 Crossing laws divide into stable and expanding cases

Scaling crosses the cube by parameter transformation:

\[
D_a;C
\equiv
C;D_{a^3},
\]

because

\[
(ax)^3=a^3x^3.
\]

Sign reversal crosses without changing arity:

\[
N;C
\equiv
C;N.
\]

Translation does not stay inside a post-affine cube language:

\[
S_b;C
=
(x+b)^3
=
x^3+3bx^2+3b^2x+b^3.
\]

Moving a translation through the cube creates lower powers, coefficients,
parallel branches, and addition. The order-reduction problem therefore
cannot be a universal sorting procedure on words. Some crossings remain
word-like; others expand into a typed arithmetic DAG.

### 1.8 The binomial law is the intrinsic structure behind translation crossing

Let

\[
A=\mathbb Q[x]
\]

and define the polynomial coaction

\[
\Delta(x)=x\otimes1+1\otimes x.
\]

Then

\[
\Delta(x^3)
=
x^3\otimes1
+
3x^2\otimes x
+
3x\otimes x^2
+
1\otimes x^3.
\]

Evaluating the second factor at `b` gives

\[
(\operatorname{id}\otimes\operatorname{ev}_b)
\Delta(x^3)
=
(x+b)^3.
\]

This supplies a disciplined interpretation of the crossing:

> Translation does not merely commute with a power. It acts on the finite
> power vocabulary through the binomial coaction.

The note uses this as a calibration, not as authorization for a stable Hopf
algebra in Adva. The program-level content is the explicit copy, parallel
power terms, coefficients, and merge.

### 1.9 Compact circuits should remain compact

Repeated cubing after one translation gives

\[
P_n(x)
=
(x+1)^{3^n}.
\]

The nested circuit has one increment and `n` high-level cube calls. The fully
expanded polynomial has

\[
3^n+1
\]

nonzero monomials.

For `n=3`,

\[
P_3(x)=(x+1)^{27},
\]

so the bounded fixture retains four high-level calls while the expansion has
twenty-eight terms. This supports circuit and DAG representations over
eager polynomial expansion.

It does not imply that circuit equivalence is easy, nor that every compact
circuit has a compact canonical form.

## 2. Finite evidence and structural formalization

### 2.1 Observer contracts

The real calibration uses an observer `Q_R` with:

- exact rational probes at `-1`, `0`, `1`, and `2`;
- real open intervals whose endpoints are exact rational cubes;
- exact Rust-owned program, history, occurrence, source, and slice data;
- SymPy only as an extensional polynomial adapter; and
- finite exhaustive checks on the declared fixtures.

The complex comparison uses a separate observer `Q_C` with:

- the polynomial `z^3-1`;
- exact symbolic cube roots of unity;
- algebraic multiplicity from exact factorization; and
- no claim that the current Adva scalar core executes complex programs.

The two observers must not be silently merged. They answer different typed
questions.

### 2.2 Temporal recovery in a bounded cubic language

Let the hypothesis class be

\[
f(x)=ax^3+bx^2+cx+d.
\]

Write the observations as

\[
y_{-1}=f(-1),
\qquad
y_0=f(0),
\qquad
y_1=f(1),
\qquad
y_2=f(2).
\]

Then

\[
d=y_0,
\]

\[
b
=
\frac{(y_1-y_0)+(y_{-1}-y_0)}2,
\]

and

\[
s
=
\frac{(y_1-y_0)-(y_{-1}-y_0)}2
=
a+c.
\]

Finally,

\[
a
=
\frac{y_2-y_0-4b-2s}{6},
\]

\[
c=s-a.
\]

For the checked cube fixture, these probes recover

\[
(a,b,c,d)=(1,0,0,0).
\]

As in the affine and square calibrations, identifiability comes from the
declared hypothesis class. Four values do not identify an unrestricted
program.

### 2.3 Reflection parity

For the power family

\[
P_n(x)=x^n,
\]

one has the exact law

\[
P_n(-x)=(-1)^nP_n(x).
\]

Therefore:

- even powers carry the trivial representation of `C_2`;
- odd powers carry the sign representation of `C_2`.

For `n=2`,

\[
P_2\circ\sigma=P_2.
\]

For `n=3`,

\[
P_3\circ\sigma=\sigma\circ P_3.
\]

This suggests an equivariant characteristic judgment of the form

\[
\chi(g\cdot p)
=
\pi_Q(g)\chi(p),
\]

rather than the stronger invariant-only law

\[
\chi(g\cdot p)=\chi(p).
\]

The representation `pi_Q` is part of the observer contract. It cannot be
inferred from the group name alone.

### 2.4 Real spatial inverse image

Because the real cube is strictly increasing,

\[
C^{-1}((a,b))
=
(\sqrt[3]{a},\sqrt[3]{b}).
\]

The bounded fixture checks three intervals:

\[
(-8,-1)
\longmapsto
(-2,-1),
\]

\[
(-8,27)
\longmapsto
(-2,3),
\]

and

\[
(1,8)
\longmapsto
(1,2).
\]

All three pullbacks have one connected component. The middle interval contains
the critical value `0`, but the inverse image does not split.

The real reverse state relation is also single-valued:

\[
C^\dagger(y)
=
\{\sqrt[3]y\}.
\]

Thus a relation-valued reverse carrier is not required for this real fixture,
although the general framework may still use one.

### 2.5 Complex local sheets and ramification

For a generic nonzero complex target `w`, choose one cube root `z`. The full
fibre is

\[
\{z,\omega z,\omega^2z\},
\]

where

\[
\omega
=
-\frac12+\frac{\sqrt3}{2}i.
\]

Multiplication by `omega` cyclically permutes the three roots.

At zero,

\[
z^3=0
\]

has one root with multiplicity three. On the Riemann sphere, the map extends
to a degree-three branched covering ramified at `0` and `infinity`.

The finite test checks only:

- three exact roots of `z^3=1`;
- their cyclic `mu_3` action; and
- multiplicity three at zero.

It does not implement complex open-set pullback or monodromy in Adva.

### 2.6 Constructive copy tree

The fixture defines a checked helper with boundary

\[
(\mathrm{Real},\mathrm{Real})
\longrightarrow
(\mathrm{Real},\mathrm{Real},\mathrm{Real})
\]

by passing one input through and copying the other. The cube first copies its
single input into two occurrences and then applies this helper, producing
three leaves.

The history therefore contains two copy events:

\[
o
\longrightarrow
(o_0,o_1),
\]

followed by, for one selected child,

\[
o_1
\longrightarrow
(o_{10},o_{11}).
\]

The leaf set is

\[
\{o_0,o_{10},o_{11}\}.
\]

The bounded test checks:

- all three leaves are distinct;
- all belong to one Rust-owned source partition;
- the first exact program slice has boundary arity `1 -> 2`;
- the second exact slice has boundary arity `1 -> 3`;
- the final value at `2` is `8`;
- the structural derivative at `2` is `12`; and
- the certificate names the checked `copy@1` and `mul@1` rules.

No value equality is used to create or identify occurrences.

### 2.7 The observer-relative degree profile

The calibration records four different finite counts.

For the real observer:

\[
d_{\mathrm{alg}}=3,
\]

\[
d_{\mathrm{fib},Q_{\mathbb R}}=1,
\]

\[
d_{\mathrm{sheet},Q_{\mathbb R}}=1,
\]

\[
d_{\mathrm{occ}}=3.
\]

Hence

\[
\mathbf d_{Q_{\mathbb R}}(C)=(3,1,1,3).
\]

For the local complex algebraic observer:

\[
d_{\mathrm{fib},Q_{\mathbb C}}=3,
\]

and away from the branch values the local sheet count is also three, giving

\[
\mathbf d_{Q_{\mathbb C}}(C)=(3,3,3,3).
\]

Each coordinate has its own typing and exceptional locus. A scalar degree is
therefore insufficient for the triadic inference problem.

### 2.8 Revised characteristic carrier

A conservative cube characteristic can be written schematically as

\[
\widehat C_Q
=
\left(
\Gamma_C,s,t;
G_Q,\pi_Q;
R_C,B_C;
\kappa_C;
\mathbf d_Q;
\mathcal R_Q
\right),
\]

where:

- `Gamma_C` is the extensional function graph;
- `s` and `t` are source and target projections;
- `G_Q` is a declared observer symmetry group;
- `pi_Q` is the target transformation law;
- `R_C` is the typed source critical set;
- `B_C` is the typed critical-value set;
- `kappa_C` is the checked constructive copy/multiply witness;
- `d_Q` is the observer-relative degree profile; and
- `R_Q` is the residual preserving distinctions omitted by the operational
  characteristic.

This is a research schema, not one proposed Rust struct. Some observers need
only a subset of these fields.

### 2.9 Triadic interpretations remain compatible

For the cube characteristic, define

\[
\rho_t(C)(x)=x^3.
\]

For real opens,

\[
\rho_X(C)(U)=C^{-1}(U).
\]

For construction,

\[
\rho_K(C)(e)
=
\mu_3(\Delta_3(e)).
\]

The evaluation square remains:

\[
\operatorname{eval}(\rho_K(C)(e))
=
\rho_t(C)(\operatorname{eval}(e)).
\]

The open-set square remains:

\[
x\in\rho_X(C)(U)
\Longleftrightarrow
\rho_t(C)(x)\in U.
\]

Composition still has the variance signature

\[
(+,-,+),
\]

because inverse image remains contravariant. What changed is not the variance
law, but the amount and type of structure required to describe each
interpretation.

### 2.10 Scaling and sign crossings

Let

\[
D_a(x)=ax,
\qquad
N(x)=-x.
\]

Then:

\[
D_a;C
\equiv
C;D_{a^3},
\]

and

\[
N;C
\equiv
C;N.
\]

The first is a parameter-raising crossing. The second is an equivariant
crossing retaining chirality.

The square law was instead

\[
N;Q\equiv Q,
\]

which erased the sign action extensionally. The contrast provides a finite
parity calibration for invariant versus equivariant characteristics.

### 2.11 Translation crossing and the power vocabulary

Let

\[
S_b(x)=x+b.
\]

Then

\[
S_b;C
=
C
+
3bQ
+
3b^2I
+
b^3,
\]

where `Q(x)=x^2` and `I(x)=x`.

This is not an equality of raw program histories. It is an extensional
decomposition whose checked constructive realization must declare copies,
coefficients, lower-power calls, additions, and residual provenance.

The minimal power vocabulary closed under translation through the cube is not
the singleton `{C}`. It contains at least

\[
\{1,I,Q,C\}.
\]

For a bounded degree `n`, translation acts on

\[
\{1,x,\ldots,x^n\}
\]

through the binomial law. This is a finite algorithmic carrier for polynomial
translation, but it is observer- and degree-bounded.

### 2.12 A typed graph rewrite rather than word sorting

The direct word

\[
S_b;C
\]

is sequential. Its expanded power presentation has parallel terms:

\[
x
\longmapsto
\left(
x^3,
3bx^2,
3b^2x,
b^3
\right)
\longmapsto
x^3+3bx^2+3b^2x+b^3.
\]

Thus crossing a translation through a cube changes:

- the number of active branches;
- the operation vocabulary;
- the boundary arity inside the construction;
- the source-occurrence tree; and
- the shape of the program graph.

This reinforces the square result:

\[
\boxed{
\text{general reduction}
\ne
\text{global ordering of two word alphabets}.
}
\]

A more plausible mechanism is:

\[
\boxed{
\text{local crossing laws}
+
\text{typed graph expansion}
+
\text{shared DAG compression}
+
\text{certificate and residual}.
}
\]

### 2.13 Algorithmic consequences

#### Exact bounded identification

Four exact temporal probes recover one cubic characteristic in a fixed cubic
language. The cost is constant in the size of the candidate coefficients,
apart from exact arithmetic.

#### No real branch enumeration

For exact rational-cube interval endpoints, the real inverse image requires
two exact cube roots and produces one component. Unlike the square fixture,
there is no two-branch search.

#### Observer-dependent reverse complexity

The same syntax has one real reverse state and three complex algebraic states.
An inference engine should therefore receive the scalar observer explicitly
rather than treating branch count as global metadata.

#### Construction cannot be inferred from spatial multiplicity

The real spatial observer sees one sheet, but the checked program uses three
leaves. A solver that predicts copy arity from inverse-image component count
would fail on this example.

#### Circuit compression

For

\[
P_n(x)=(x+1)^{3^n},
\]

nested cubing has `n+1` high-level stages while full expansion has `3^n+1`
terms. The test checks

\[
(x+1)^{27}
\]

as three nested cube calls after one increment.

This is a representation advantage, not a general complexity theorem about
equivalence, minimization, or synthesis.

### 2.14 Bounded executable fixture

The research test is

[`tests/python/test_triadic_cube_characteristic.py`](../../tests/python/test_triadic_cube_characteristic.py).

It checks:

1. exact recovery of the cubic coefficients from four probes;
2. square invariance versus cube sign equivariance;
3. exact real interval pullbacks across negative, positive, and zero-crossing
   targets;
4. singleton real reverse fibres;
5. three exact complex roots and the cyclic `mu_3` action;
6. multiplicity three at the complex critical fibre;
7. two checked copy events forming three constructive leaves;
8. exact `1 -> 2` and `1 -> 3` program-slice boundaries;
9. value and derivative certificates;
10. the cross-observer cardinality readings `(1,1,3,3)` for real
    reverse fibres, real spatial components, constructive occurrences, and
    complex algebraic multiplicity;
11. scaling crossing by `a mapsto a^3`;
12. the cubic binomial translation law; and
13. compact nested representation of `(x+1)^27`.

The four readings in item 10 deliberately cross observer contracts. They are
not the observer-relative degree profile \(\mathbf d_Q(P)\): the formal real
profile remains \(\mathbf d_{Q_{\mathbb R}}(C)=(3,1,1,3)\). The executable
variable is therefore named `cross_observer_cardinality_readings`, rather
than `degree_profile`.

The interval and complex helpers are research-local mathematical fixtures.
They do not authorize stable spatial or complex semantics.

## 3. Conservative conclusion

### 3.1 What the calibration supports

Within the declared bounded observers, the cube calibration supports the
following claims.

1. The triadic compatibility equations survive a non-quadratic power map.
2. The variance signature remains `(+,-,+)`.
3. Invariant characteristics are too narrow; equivariant characteristics are
   already required by the parity difference between square and cube.
4. Algebraic degree, reverse-fibre cardinality, spatial sheet count, and
   constructive occurrence multiplicity are separate typed quantities.
5. These quantities depend on the observer domain and exceptional loci.
6. Differential criticality does not by itself imply real open-set splitting.
7. Construction provenance cannot be reconstructed from real spatial branch
   count.
8. Scaling and sign have compact crossing laws through the cube.
9. Translation crossing is governed by a finite binomial power vocabulary and
   expands a word into a DAG.
10. Nested circuits can be exponentially smaller than fully expanded
    polynomial syntax.

The revised finite pattern is

\[
\boxed{
\text{characteristic}
=
\text{extensional core}
+
\text{equivariance law}
+
\text{observer-relative degree profile}
+
\text{critical data}
+
\text{constructive witness}
+
\text{residual}.
}
\]

### 3.2 What is not established

The note does not establish that:

- every Adva program has a polynomial degree;
- every characteristic admits a finite degree profile;
- algebraic degree is invariant under arbitrary program equivalence;
- complex branching is implemented by the current Adva scalar core;
- three complex sheets are identical to three construction occurrences;
- every critical point produces ramification in every category;
- the proposed graph carrier is minimal or canonical;
- the binomial coaction solves general noncommutative crossing;
- compact arithmetic circuits have efficiently decidable equivalence;
- the real and complex observers form a completed refinement system; or
- this calibration solves surreal `L/R` reduction.

### 3.3 Engineering consequence

No stable API should be added from this note alone.

A future research carrier should keep the following distinctions explicit:

- scalar domain and observer;
- source critical set and target critical values;
- generic fibre count and local sheet count;
- raw construction history and extensional function;
- source identity and occurrence multiplicity;
- invariant and equivariant transformation laws;
- direct compact circuit and expanded power presentation; and
- certified result versus incomplete search.

Rust remains the authority for program, source, occurrence, history, slice,
and certificate identities. SymPy does not create semantic equality or
program cells.

### 3.4 Next calibration

The next most diagnostic real example is

\[
T(x)=x^3-3x.
\]

It retains cubic constructive complexity while producing observer-visible real
branch changes:

- critical points at `x=+-1`;
- critical values at `-+2`;
- three real inverse branches for targets in `(-2,2)`; and
- one real inverse branch outside that interval.

This would test branch creation and merger in the real domain without changing
the scalar field, while keeping exact critical values. It would also test
whether the degree profile must become region-indexed rather than merely
observer-indexed.

## 4. Red-team opinion

### 4.1 The complex comparison is external to current execution

The current stable scalar core is real. SymPy's exact complex roots are useful
mathematical evidence, but they are not a checked complex Adva program,
complex open-set pullback, or certified monodromy calculation.

### 4.2 Constructive occurrence count depends on presentation

The fixture realizes `x^3` through two binary copies and two binary
multiplications. A future primitive cube operation, exponentiation operation,
or different operation registry could expose another internal occurrence
count.

Therefore `d_occ` is relative to the declared construction language and
normal-form policy. It is not an extensional invariant of the function alone.

### 4.3 Algebraic degree can be destroyed by cancellation

A program may contain high-degree intermediate terms that cancel
extensionally. The degree of the final polynomial does not measure raw
construction complexity, history length, or search difficulty.

### 4.4 Sheet count needs a local definition

Over the complex plane, the inverse image of an arbitrary large or
non-simply-connected open set need not decompose into three globally labelled
components. The safe claim is a generic local three-sheeted structure away
from branch values.

### 4.5 Criticality is category-dependent

The derivative of `x^3` vanishes at zero, yet the real map is a homeomorphism.
Calling zero a “branch point” without specifying real topology, smooth
structure, complex analytic structure, or algebraic multiplicity would be
ambiguous.

### 4.6 Equivariance requires a declared target action

The equation

\[
C(-x)=-C(x)
\]

uses sign reversal on both source and target. Without a target action, the
word “equivariant” is incomplete. Future observer contracts must type both
actions.

### 4.7 The degree profile may not compose componentwise

For maps `f` and `g`, algebraic degrees may multiply under suitable
hypotheses, but real fibre counts, open-component counts, and constructive
occurrence counts can behave differently under composition and critical
collision.

The profile is a diagnostic vector, not yet a semiring homomorphism.

### 4.8 Hopf language may overfit the polynomial fragment

The binomial coaction is exact and useful for translations of powers. General
programs with partiality, branching, recursion, transcendental operations, or
noncommuting effects may require another carrier. The terminology should not
outrun the finite calibration.

### 4.9 Circuit compression does not imply easy canonicalization

A nested cube circuit can be much shorter than its expanded polynomial.
Finding a smallest equivalent circuit, proving two circuits equal, or
constructing a canonical shared DAG may still be hard.

### 4.10 The most valuable possible outcome of the next test is failure

The map `x^3-3x` may show that one observer-relative degree vector is still too
coarse. Branch identities may have to vary over target regions and glue across
critical values. If so, the correct replacement would be a stratified or
region-indexed characteristic, not a forced scalar summary.
