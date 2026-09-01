# An A1 Nodal Through-Crossing Geometry

Status: exploratory geometric calibration extending
[`0042-atiyah-legendre-triadic-crossing.md`](0042-atiyah-legendre-triadic-crossing.md)
and
[`0043-legendre-crossing-coherence-prism.md`](0043-legendre-crossing-coherence-prism.md).

The executable finite calibration is
`tests/python/test_a1_nodal_through_crossing.py`.

This note isolates the geometric problem left open by the preceding Legendre
work:

> We can describe transport around a cusp and specialization into a singular
> fibre. What is the correct object for passing through the singular value?

The main conclusion is:

> Through-crossing is not another parallel-transport map. The elementary
> geometric carrier is a surgery trace together with a pinch cospan
>
> \[
> F_-\longrightarrow F_0\longleftarrow F_+.
> \]
>
> Its fibre product is a relation, not generally a function. A deterministic
> continuation appears only after choosing a smoothing or gluing phase.
> Different choices differ by monodromy.

The note uses the ordinary node

\[
uv=s
\]

as the elementary `A1` model. It develops two complementary finite readings:

1. the real slice, where an index-one saddle changes the pairing of four
   boundary ports and can globally merge or split components; and
2. the complex slice, where two smooth annuli pinch to one nodal fibre and the
   lost gluing phase reappears as a torsor of through-resolutions.

It then proves the local analytic reduction of the Legendre cusp to

\[
UV=\lambda^2.
\]

Thus the Legendre cusp is the elementary nodal model after the quadratic base
change

\[
s=\lambda^2,
\]

which explains why the Legendre monodromy is the square of the primitive nodal
twist.

This remains research-local. It introduces no stable node, surgery, cospan,
correspondence, smoothing, cobordism, vanishing-cycle, monodromy, or
through-crossing API. It does not modify `claims.toml`, and it does not change
the active `ProgramSlice` priority or Rust semantic authority.

---

## 0. Executive diagram

The three geometric operations should be kept distinct:

\[
\boxed{
\begin{aligned}
\operatorname{around}_c
&:\text{invertible transport in the smooth locus},\\
\operatorname{specialize}_c
&:\text{pinch or quotient into the singular fibre},\\
\operatorname{through}_c
&:\text{surgery trace plus a smoothing choice}.
\end{aligned}
}
\]

For an elementary node, the complete local picture is:

\[
\boxed{
F_-
\xrightarrow{q_-}
F_0
\xleftarrow{q_+}
F_+,
}
\]

together with the relation

\[
\boxed{
R_c
=
F_-\times_{F_0}F_+.
}
\]

A through-resolution is a section or graph inside this relation:

\[
P_\theta:F_-\longrightarrow F_+,
\qquad
\Gamma(P_\theta)\subseteq R_c.
\]

Two resolutions satisfy, up to the declared orientation convention,

\[
\boxed{
(P_{\theta_2})^{-1}P_{\theta_1}
=
T_\delta^{\,\theta_1-\theta_2},
}
\]

where `T_delta` is the Dehn twist about the vanishing cycle.

This gives a structural interpretation of monodromy:

> Around-monodromy measures the difference between two admissible
> through-resolutions.

---

# Part I. Why through is not transport

## 1. Smooth transport lives in a groupoid

Let

\[
\pi:\mathcal Y\longrightarrow B
\]

be a family with discriminant

\[
\Delta\subset B.
\]

Over the regular locus

\[
B^\circ=B\setminus\Delta,
\]

parallel transport along a path

\[
\gamma:b_0\rightsquigarrow b_1
\]

gives an isomorphism

\[
P_\gamma:F_{b_0}\overset{\sim}{\longrightarrow}F_{b_1}.
\]

Reversing the path gives the inverse. Smooth transport therefore belongs to a
groupoid.

A path through

\[
c\in\Delta
\]

does not remain in this groupoid. At the singular value, the fibre may fail to
be a manifold, a cycle may collapse, and a marking may cease to be defined.

Therefore one should not introduce an unqualified arrow

\[
F_-\longrightarrow F_+
\]

and call it `cross(c)`.

The missing data are precisely the singular middle object and the loss and
reconstruction maps.

## 2. Three distinct questions

For one singular value `c`, geometry asks three different questions.

### Around

What automorphism is produced by a loop in `B^circ` around `c`?

\[
M_c:F_b\longrightarrow F_b.
\]

### Specialize

What survives as a regular fibre approaches the singular fibre?

\[
q:F_b\longrightarrow F_c.
\]

### Through

How can incoming data on one side of `c` be related to outgoing data on the
other side?

The third question is not answered by either `M_c` or `q` alone. It requires:

- an incoming pinch;
- an outgoing smoothing;
- a surgery trace;
- a coorientation of the parameter;
- an exterior attachment;
- and, in the complex marked case, a gluing phase.

---

# Part II. The real saddle uv=s

## 3. The local family

Consider

\[
f:\mathbf R^2\longrightarrow\mathbf R,
\qquad
f(u,v)=uv.
\]

Its only critical point is the origin, and the Hessian has one positive and one
negative direction. It is a Morse critical point of index one.

For a small positive `epsilon`, inspect the fibres inside a square around the
origin.

### Negative side

For

\[
s=-\epsilon,
\]

the equation

\[
uv=-\epsilon
\]

has one branch in the second quadrant and one in the fourth quadrant. With
boundary ports labelled north, east, south, west, the induced pairing is

\[
\boxed{
(N,W),\qquad(S,E).
}
\]

### Positive side

For

\[
s=+\epsilon,
\]

the branches lie in the first and third quadrants, giving

\[
\boxed{
(N,E),\qquad(S,W).
}
\]

### Singular value

For

\[
s=0,
\]

the fibre is

\[
uv=0,
\]

the union of the two coordinate axes. In the bounded patch this is a
four-valent star.

Thus the elementary real through-crossing changes a boundary matching:

\[
\boxed{
\{NW,SE\}
\rightsquigarrow
\{NE,SW\}.
}
\]

This is an object-level topology operation. It is not merely a matrix on
homology.

## 4. A finite saddle cellulation

The executable fixture uses a disk with:

- four boundary vertices `N,E,S,W`;
- one interior critical vertex `O`;
- four boundary edges;
- four radial edges; and
- four triangular faces.

Its cell counts are

\[
V=5,\qquad E=8,\qquad F=4,
\]

so

\[
\chi(W)=V-E+F=1.
\]

The incoming fibre is two disjoint intervals:

\[
F_-=(NW)\sqcup(SE),
\]

with

\[
\chi(F_-)=2.
\]

Therefore

\[
\chi(W,F_-)
=
\chi(W)-\chi(F_-)
=
-1.
\]

For a relative Morse decomposition with one critical point, this is

\[
(-1)^1,
\]

the signature of one index-one handle.

The test also verifies the cell incidence:

- every exterior edge belongs to one face;
- every radial edge belongs to two faces.

The finite disk is not claimed to be a geometric mesh of the exact
semialgebraic region

\[
\{(u,v):-\epsilon\le uv\le\epsilon\}.
\]

It is a cellulation of the same relative saddle-cobordism type.

## 5. Specialization forgets the smoothing pairing

Both smooth matchings specialize to the same singular star.

For the negative fibre, the two regular arcs approach the paths

\[
N-O-W,
\qquad
S-O-E.
\]

For the positive fibre, they approach

\[
N-O-E,
\qquad
S-O-W.
\]

The union of edges is identical:

\[
\{ON,OE,OS,OW\}.
\]

Thus:

\[
\boxed{
\operatorname{image}(q_-)
=
\operatorname{image}(q_+),
}
\]

while the decomposition into smooth arcs differs.

The singular graph alone does not remember which ports belonged to the same
smooth component before or after the crossing.

This is the first finite geometric residual:

\[
\boxed{
\text{singular star}
+
\text{lost boundary matching}.
}
\]

A coorientation of the parameter identifies which smoothing is incoming and
which is outgoing.

## 6. Local singularity does not determine global merge or split

The same local saddle patch can have opposite global effects.

Glue the four local ports to an exterior matching.

### Merge exterior

Choose the exterior matching equal to the negative smoothing:

\[
\{NW,SE\}.
\]

Before crossing, the union of local and exterior matchings has two connected
cycles. After crossing, it has one.

Thus:

\[
2\longrightarrow1.
\]

The saddle merges two global components.

### Split exterior

Choose the exterior matching equal to the positive smoothing:

\[
\{NE,SW\}.
\]

Before crossing, the union has one cycle. After crossing, it has two.

Thus:

\[
1\longrightarrow2.
\]

The same saddle splits one global component.

Therefore:

\[
\boxed{
\text{local critical type}
\not\Rightarrow
\text{global topological consequence}.
}
\]

The global effect depends on exterior attachment data.

A geometric through language must therefore carry both:

\[
\text{local surgery generator}
\]

and

\[
\text{global port attachment}.
\]

---

# Part III. The complex nodal pinch

## 7. The complex local model

Now take

\[
uv=s
\]

over the complex numbers.

For

\[
s\neq0,
\]

the local Milnor fibre is an annulus. One convenient parametrization is

\[
u=re^{i\theta},
\qquad
v=\frac{|s|}{r}e^{i(\arg s-\theta)}.
\]

The vanishing cycle is represented by

\[
|u|=|v|=\sqrt{|s|}.
\]

As

\[
s\to0,
\]

this circle collapses to the node.

Two quantities behave differently:

- `|s|` controls the neck size;
- `arg(s)` controls a gluing phase or marking.

At the singular value, `arg(s)` is undefined. Specialization therefore loses
not only the circle but also its marked phase.

## 8. The pinch cospan

Let

\[
F_-,\qquad F_+
\]

be marked smooth fibres on two chosen sides or sectors, and let

\[
F_0
\]

be the nodal fibre.

There are pinch maps

\[
q_-:F_-\longrightarrow F_0,
\qquad
q_+:F_+\longrightarrow F_0.
\]

Away from the vanishing cycles, these maps identify corresponding regular
points. On the vanishing cycles,

\[
q_-(\delta_-)=*,
\qquad
q_+(\delta_+)=*,
\]

where `*` is the node.

The elementary geometric carrier is therefore the cospan

\[
\boxed{
F_-
\xrightarrow{q_-}
F_0
\xleftarrow{q_+}
F_+.
}
\]

This cospan is more primitive than a chosen continuation map.

## 9. The through relation

Take the fibre product

\[
R_c
=
F_-\times_{F_0}F_+.
\]

A pair belongs to `R_c` exactly when its two points have the same
specialization.

Away from the node, `R_c` is the graph of the canonical identification.

At the node,

\[
\delta_-\times\delta_+
\subset R_c.
\]

Thus every incoming point on the collapsed cycle is compatible with every
outgoing point on the reconstructed cycle.

Consequently:

\[
\boxed{
R_c
\text{ is functional away from the node and relational at the node.}
}
\]

This is the precise obstruction to treating through-crossing as a function.

## 10. A finite quotient model

The executable test represents each smooth fibre by:

- a finite set of regular points; and
- an `n`-point cyclic approximation to the vanishing circle.

The pinch map fixes regular points and sends all cycle points to one node.

If there are `r` regular points and `n` vanishing points, then the fibre-product
relation contains

\[
r+n^2
\]

pairs:

- one outgoing point for each regular incoming point;
- `n` outgoing choices for each vanishing incoming point.

The test uses

\[
r=3,\qquad n=8,
\]

and verifies:

\[
|R_c|=3+8^2.
\]

This is only a finite quotient model of the cospan. It is not a triangulation
of an annulus and does not by itself prove a mapping-class statement.

## 11. Through-resolutions form a phase torsor

A deterministic resolution chooses a phase

\[
\theta:\delta_-\longrightarrow\delta_+.
\]

For the finite `n`-cycle, a phase `k` gives

\[
i\longmapsto i+k\pmod n.
\]

Each phase defines a graph inside `R_c`.

All phases have the same specialization:

\[
q_+\circ P_k=q_-.
\]

Therefore the singular fibre cannot distinguish them.

The difference of two phases is a rotation:

\[
P_\ell^{-1}P_k
=
R_{k-\ell}.
\]

In the smooth annular geometry, the analogous marked resolutions form a torsor
under the relative mapping class group of the annulus:

\[
\langle T_\delta\rangle\cong\mathbf Z.
\]

The finite model replaces this infinite twist torsor by a cyclic quotient.

---

# Part IV. Around as the difference of through-resolutions

## 12. Upper and lower bypasses

Let the incoming and outgoing parameters lie on opposite sides of the origin.
There are two paths in the punctured complex base:

\[
\gamma^\uparrow,
\qquad
\gamma^\downarrow,
\]

passing above and below the singular value.

Parallel transport gives two marked isomorphisms

\[
P^\uparrow,P^\downarrow:
F_-\longrightarrow F_+.
\]

Their difference is an automorphism of the incoming fibre:

\[
(P^\downarrow)^{-1}P^\uparrow:
F_-\longrightarrow F_-.
\]

The concatenated path is a loop around the node, so, with the orientation
convention fixed,

\[
\boxed{
(P^\downarrow)^{-1}P^\uparrow
=
T_\delta.
}
\]

Changing orientation replaces `T_delta` by its inverse.

This relation changes the conceptual order:

> Monodromy is not an unrelated effect added after through-crossing. It
> measures the ambiguity between two smooth bypass resolutions of the same
> singular cospan.

## 13. The three operations in one table

| operation | carrier | invertible? | information lost |
|---|---|---:|---|
| around | smooth path | yes | none at the declared level |
| specialize | pinch map | generally no | vanishing cycle and phase |
| through | cospan plus resolution | after a choice | hidden resolution choice |

A language that represents all three by one untyped arrow will erase the
distinction that produces monodromy.

---

# Part V. Why Legendre gives a squared monodromy

## 14. Local Legendre equation at lambda=0

Start with the Legendre family

\[
y^2=x(x-1)(x-\lambda).
\]

Near

\[
x=0,\qquad\lambda=0,
\]

rewrite it as

\[
y^2=x(1-x)(\lambda-x).
\]

Since `1-x` is a nonzero analytic unit, choose a local square root and set

\[
Y=\frac{y}{\sqrt{1-x}}.
\]

Then

\[
Y^2=x(\lambda-x).
\]

Define

\[
A=2x-\lambda.
\]

A direct calculation gives

\[
A^2+4Y^2=\lambda^2.
\]

Over the complex numbers, put

\[
U=A+2iY,
\qquad
V=A-2iY.
\]

Then

\[
\boxed{
UV=\lambda^2.
}
\]

The executable test verifies this identity symbolically.

## 15. Quadratic base change

The elementary semistable nodal parameter is

\[
s=UV.
\]

The Legendre parameter satisfies

\[
s=\lambda^2.
\]

Therefore a loop

\[
\lambda\mapsto e^{2\pi i}\lambda
\]

maps to a loop in `s` with winding number two.

If the elementary nodal monodromy is

\[
T_\delta,
\]

then the Legendre cusp monodromy is

\[
\boxed{
M_{\mathrm{Legendre}}
=
T_\delta^2.
}
\]

In the homology convention used by note 0042, for

\[
\delta=
\begin{pmatrix}
1\\
0
\end{pmatrix},
\]

the primitive twist is

\[
T_\delta=
\begin{pmatrix}
1&1\\
0&1
\end{pmatrix},
\]

while the Legendre cusp gives

\[
T_\delta^2=
\begin{pmatrix}
1&2\\
0&1
\end{pmatrix}.
\]

This recovers the squared unipotent matrix already used in the three-cusp
calibration.

## 16. What the base change explains

The earlier Legendre calculation started from:

- branch-point braid;
- vanishing cycle;
- squared cusp monodromy.

The local equation

\[
UV=\lambda^2
\]

now explains why the square occurs.

The Legendre family carries level-two branch data. Its parameter is not the
elementary semistable smoothing coordinate; it is a quadratic cover of that
coordinate near the cusp.

Thus:

\[
\boxed{
\text{primitive nodal through}
\longrightarrow
T_\delta,
}
\]

whereas:

\[
\boxed{
\text{Legendre cusp circuit}
\longrightarrow
T_\delta^2.
}
\]

This is the missing bridge between elementary through-crossing and the
previous around-monodromy fixture.

---

# Part VI. A candidate geometric data object

## 17. Minimal typed carrier

A simple nodal through-crossing should retain at least

\[
\mathsf{NodalThrough}_c
=
\left(
F_-,F_0,F_+;
q_-,q_+;
W_c;
\delta_-,\delta_+;
\mathcal P_c;
\kappa_c;
A_c;
\nu_c;
R_c
\right).
\]

The fields have distinct types.

### Smooth and singular fibres

\[
F_-,\qquad F_0,\qquad F_+.
\]

### Pinch maps

\[
q_-:F_-\to F_0,
\qquad
q_+:F_+\to F_0.
\]

### Surgery trace

\[
W_c.
\]

For the real model, this is the index-one saddle cobordism.

### Vanishing data

\[
\delta_-\subset F_-,
\qquad
\delta_+\subset F_+.
\]

### Resolution torsor

\[
\mathcal P_c.
\]

A point of this torsor selects a deterministic marked smoothing.

### Regular complement identification

\[
\kappa_c:
F_-\setminus\delta_-
\overset{\sim}{\longrightarrow}
F_+\setminus\delta_+.
\]

### Exterior attachment

\[
A_c.
\]

This determines whether the local saddle merges, splits, or only re-pairs
global components.

### Parameter coorientation

\[
\nu_c.
\]

This distinguishes incoming from outgoing smoothing.

### Residual

\[
R_c.
\]

This stores data destroyed by specialization and not restored without a
resolution choice.

## 18. Required certificates

A finite implementation should provide certificates for:

1. cell-incidence validity of the surgery trace;
2. relative Euler characteristic and handle index;
3. equality of the two specialization images;
4. inequality of the two smoothing matchings;
5. global component counts after declared exterior gluing;
6. cospan commutation;
7. relation membership of every chosen resolution;
8. the difference-of-resolutions monodromy law;
9. the local Legendre reduction to `UV=lambda^2`; and
10. the base-change monodromy exponent.

These certificates are geometric. They need not wait for the separate logical
language project.

---

# Part VII. Relation to the three-domain programme

## 19. What geometry now contributes

The preceding triadic prism used an `H1` charge as the spatial carrier. The
current project adds four structures that were absent from that linear shadow:

\[
\boxed{
\text{object-level fibre},
}
\]

\[
\boxed{
\text{singular middle fibre},
}
\]

\[
\boxed{
\text{surgery trace},
}
\]

and

\[
\boxed{
\text{resolution torsor}.
}
\]

The spatial domain can now distinguish:

- a monodromy automorphism;
- a pinch quotient;
- a through correspondence;
- a chosen smoothing;
- and a global attachment.

The temporal and constructive domains may later interpret these objects, but
their grammar is deliberately deferred.

## 20. A geometric residual before any logical quotation

There are two independent geometric losses.

### Matching loss in the real saddle

The singular star does not remember which boundary ports formed smooth arcs.

### Phase loss in the complex node

The nodal fibre does not remember the marked gluing phase of the collapsed
annulus.

Both have the same pattern:

\[
\boxed{
\text{many smooth resolutions}
\longrightarrow
\text{one singular object}.
}
\]

A through language must not erase this fibre of resolutions.

This suggests a geometric definition:

\[
\operatorname{Resolutions}(F_0)
=
\{(F,q,\text{marking}):q:F\to F_0\}.
\]

Monodromy acts on this resolution fibre.

---

# Part VIII. Conservative conclusions

## 21. What has been established

The bounded executable calibration establishes:

1. a finite real saddle cellulation with relative Euler characteristic `-1`;
2. two distinct smooth boundary matchings specializing to one singular star;
3. global merge and split outcomes from the same local saddle under different
   exterior attachments;
4. a finite pinch cospan whose fibre product is nonfunctional exactly over the
   node;
5. deterministic phase resolutions whose difference is a finite rotation;
6. the local Legendre identity
   \[
   UV=\lambda^2;
   \]
7. winding doubling under the quadratic base change; and
8. the matrix identity
   \[
   M_{\mathrm{Legendre}}=T_\delta^2.
   \]

## 22. What has not been established

The project does not yet provide:

1. a full triangulated complex Milnor fibre and nodal curve;
2. a certified mapping-class computation inside Adva;
3. a generic cospan or correspondence API;
4. a proof that every useful through-crossing is a cospan of this form;
5. a global genus-one Legendre surgery object;
6. a Cerf calculus for composing several critical events;
7. a construction-sensitive continuation theorem;
8. an irreducible triadic obstruction; or
9. any theorem relating the nodal residual to Chaitin `Omega`.

## 23. Red-team qualifications

### The endpoint complex fibres need not change abstract topology

For a simple complex node, both nonzero fibres are annuli locally. The change
is concentrated in:

- the singular middle fibre;
- the pinch map;
- the marking;
- the real locus;
- the surgery trace; and
- the gluing phase.

One must not say that the abstract complex smooth fibre necessarily changes
homeomorphism type across the node.

### The finite cycle is not the vanishing circle itself

The `n`-point cycle in the executable fixture is a quotient model used to
exhibit relation-valued through data and phase ambiguity. It is not a
simplicial annulus.

### Monodromy depends on orientation convention

The equation comparing two bypasses may yield `T_delta` or its inverse,
depending on path order and orientation. The finite test fixes one convention.

### The singular fibre permits more abstract resolutions than the family

A four-valent star has three perfect matchings of its ports. The real function
`uv` and its parameter coorientation select two as the negative and positive
smoothings. The family data are therefore part of the through object.

### Global merge and split require exterior data

The local index-one critical point does not alone determine whether a global
component count rises or falls.

---

# Part IX. Next geometric phase

## 24. Globalize the nodal patch

The next geometry project should replace the finite set quotient by an actual
finite cellulation of:

- an incoming annulus;
- a nodal pinched annulus;
- an outgoing annulus; and
- the two-dimensional surgery trace.

The cellulation should expose:

- normalization of the node;
- the two preimages of the nodal point;
- the gluing map;
- a marked vanishing circle;
- a Dehn twist on the cell complex; and
- a computable fibre-product correspondence.

## 25. Embed the patch in a genus-one fibre

The local patch should then be glued into a finite torus cellulation.

The target verification is:

\[
\text{local twist on the annulus}
\longrightarrow
\text{Picard--Lefschetz action on }H_1(T^2).
\]

This would connect object-level surgery to the matrices already used in notes
0042 and 0043.

## 26. Compose two critical events

After the `A1` generator is stable, introduce two intersecting vanishing
cycles and compare two event orders.

The geometric target is a finite version of:

- braid relation;
- Hurwitz move;
- handle slide; or
- Cerf interchange.

Only then should a general through-crossing calculus be proposed.

---

# Part X. Research judgement

## 27. Current answer to the original gap

The earlier diagnosis was:

> We implemented around and specialization, but not through.

The current answer is:

\[
\boxed{
\operatorname{through}_c
\text{ is a surgery cospan, not a smooth transport arrow.}
}
\]

Its unchosen form is:

\[
\boxed{
F_-\to F_0\leftarrow F_+,
}
\]

or equivalently the correspondence:

\[
\boxed{
F_-\times_{F_0}F_+.
}
\]

Its chosen form is a marked resolution inside that relation.

The difference between choices is monodromy.

This supplies a finite geometric semantics for all three operations:

\[
\boxed{
\text{around}
+
\text{specialize}
+
\text{through}.
}
\]

## 28. The key new relation

The most important result is not a new matrix. It is the structural identity:

\[
\boxed{
\text{around monodromy}
=
\text{difference of through resolutions}.
}
\]

The real saddle shows why a singular fibre loses a smoothing matching. The
complex pinch shows why it loses a gluing phase. The Legendre base change shows
why the existing cusp monodromy is squared.

Together they fill the exact geometric gap left by the preceding line of
research while preserving a strict boundary between finite evidence and a
future general calculus.

---

## References

Classical background for the geometric interpretation includes:

- J. Milnor, *Morse Theory*.
- J. Milnor, *Singular Points of Complex Hypersurfaces*.
- A. Dimca, *Singularities and Topology of Hypersurfaces*.
- R. Gompf and A. Stipsicz, *4-Manifolds and Kirby Calculus*.
- Standard Picard--Lefschetz accounts of vanishing cycles and Dehn twists.

These references motivate the local model and terminology. The finite
cellulation, quotient relation, observer boundary, and Adva research
interfaces remain the responsibility of the present calibration.
