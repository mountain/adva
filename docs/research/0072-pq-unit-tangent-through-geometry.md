# Double Periods, Unit-Tangent Lifts, and Three-Dimensional Through Geometry

Status: bounded exact research calibration following
[0048](0048-cellular-annulus-nodal-torus-dehn-twist.md),
[0057](0057-typed-vacua-constant-boundary-braids.md),
[0067](0067-circular-three-form-interface-duality.md),
[0070](0070-typed-surreal-through-forms.md), and
[0071](0071-figure-eight-through-characteristic.md).

The executable finite oracle is
[test_pq_unit_tangent_through_geometry.py][fixture].

[fixture]: ../../tests/python/test_pq_unit_tangent_through_geometry.py
[aeg-q4]: https://github.com/mountain/aeg-paper/blob/master/paper-3/sections/05-q4-geodesic-knots.tex
[dehornoy]: https://hal.science/hal-00655422v2/file/GeodFlow10.pdf
[modular-knots]: https://arxiv.org/abs/2211.05957

This is a research-local arithmetic and topology interface. It creates no
stable period, orbifold, unit-tangent, torus, filling, mapping-torus, knot, or
link semantics. Rust remains authoritative for Adva program identities.

---

## 0. Research provenance and original proposal

The conjectural chain tested here arose from proposals by Mingli Yuan:

1. mixed-bracket normalization may have two visible periods \((p,q)\), with
   forward and reverse processes retaining different closure data;
2. a through strand has no automatic reason to live in an externally supplied
   Euclidean three-space;
3. the add--multiply carrier is hyperbolic, and its earlier compactification
   programme may already contain the missing three-dimensional environment;
4. feature extraction may remove the multivaluedness of boundary threads; and
5. the \((p,q)\) clue may connect normalization, torus winding, Dehn twist,
   and knot closure.

This note adds a typed separation, an exact finite experiment, and a red-team
boundary. The classical unit-tangent, Seifert, lens-space, torus-link, and
modular-knot results are imported inputs. The \(q=4\) specialization was
already audited in [AEG Paper III][aeg-q4].

---

## 1. Executive result

Ordinary compactification does not raise dimension:

\[
\overline{H^2}=H^2\cup S^1_\infty\simeq D^2.
\]

The natural three-dimensional lift is instead

\[
\mathcal O_{p,q}=\Gamma_{p,q}\backslash H^2,
\qquad
M_{p,q}=T^1\mathcal O_{p,q}.
\]

The fibre is a direction circle \(S^1\). The third dimension is therefore a
frame or direction characteristic, not an assumed Cartesian coordinate.

For the triangle orbifold of signature \((p,q,\infty)\), the two finite
orders determine cusp-filling meridians

\[
m_P=(p-1,-1),
\qquad
m_Q=(-1,q-1).
\]

Hence

\[
\boxed{
\det
\begin{pmatrix}
p-1&-1\\
-1&q-1
\end{pmatrix}
=pq-p-q.
}
\]

With the declared hyperbolic filling convention, the classical result is

\[
\boxed{
\overline{T^1\mathcal O_{p,q}}
\cong L(pq-p-q,p-1).
}
\]

Independently, two visible phase periods form

\[
\mathbb Z/p\mathbb Z\times\mathbb Z/q\mathbb Z
\]

with successor \((i,j)\mapsto(i+1,j+1)\). Its exact orbit data is

\[
\boxed{
g=\gcd(p,q),\qquad
L=\operatorname{lcm}(p,q),\qquad
w=\left(\frac qg,\frac pg\right).
}
\]

Here \(g\) is the number of orbits, \(L\) their common length, and \(w\) the
primitive lifted winding of every orbit. This matches the component
arithmetic of \(T(p,q)\), but supplies no embedding or isotopy theorem.

The conservative synthesis is:

> Double periods create a torus of visible phases. A direction lift or
> suspended return map creates a three-dimensional carrier. Orbifold orders
> determine one filling topology. Identifying the computational periods with
> the orbifold orders still requires a theorem.

---

## 2. Three typed meanings of the same numerals

| type | meaning | carrier |
|---|---|---|
| **PhasePeriods** | two visible clocks | \(\mathbb Z/p\times\mathbb Z/q\) |
| **OrbifoldOrders** | two isotropy orders | \((p,q,\infty)\) orbifold |
| **TorusSlope** | one homology class | \(m\mu+n\lambda\in H_1(T^2)\) |

Equal numerals do not identify these types. The pair \((3,4)\) is the
decisive negative control:

\[
\gcd(3,4)=1,
\qquad
\operatorname{lcm}(3,4)=12,
\qquad
3\cdot4-3-4=5.
\]

One pair yields three distinct exact features. The fixture represents the
three roles by distinct data classes.

---

## 3. Finite double-period experiment

Let

\[
P_{p,q}=\mathbb Z/p\mathbb Z\times\mathbb Z/q\mathbb Z,
\qquad
\tau(i,j)=(i+1,j+1).
\]

Every orbit closes after \(L=\operatorname{lcm}(p,q)\) steps. Therefore the
number of orbits is

\[
\frac{|P_{p,q}|}{L}
=
\frac{pq}{L}
=
\gcd(p,q)=g.
\]

At the first visible return, the universal-cover winding is

\[
\left(\frac Lp,\frac Lq\right)
=
\left(\frac qg,\frac pg\right),
\]

whose coordinates are coprime. Each orbit is primitive; when \(g>1\), the
complete state set is a union of \(g\) parallel primitive orbits.

The fixture exhaustively checks

\[
(2,3),\quad(2,4),\quad(3,4),\quad(3,6).
\]

This is a finite reason for several components when \(p,q\) are not coprime.
It does not yet construct a Heegaard torus in a three-manifold.

---

## 4. Unit-tangent lift and multivalued crossings

For a regular immersed path \(\gamma:I\to\mathcal O\), define

\[
\widehat\gamma(s)
=
\left(
\gamma(s),
\frac{\dot\gamma(s)}{\|\dot\gamma(s)\|}
\right)
\in T^1\mathcal O.
\]

If \(\gamma(s_1)=\gamma(s_2)\) but their unit tangents differ, then their
lifts are distinct. A projected crossing can separate in the
three-dimensional unit-tangent bundle. A primitive closed hyperbolic geodesic
lifts to an embedded periodic orbit.

Thus

\[
\boxed{
\text{two-dimensional add--multiply position}
+
\text{direction characteristic}
=
\text{three-dimensional lifted history}.
}
\]

This separates two operations:

1. the direction lift restores enough hidden data to distinguish branches;
2. feature extraction compresses the lifted history into winding, monodromy,
   or a Laurent characteristic.

The first is controlled de-forgetting; the second is residual-bearing
abstraction.

---

## 5. Orbifold periods and lifted nonclosure

Downstairs the two rotations close:

\[
x^p=y^q=1.
\]

Their unit-tangent lifts retain a central full turn:

\[
\boxed{
\widetilde x^{\,p}
=
\widetilde y^{\,q}
=h.
}
\]

This has the same form as

\[
R^3=1,\quad \widetilde R^{\,3}=\Delta^2
\]

in the braid calibration and

\[
D_0^n=I,\quad
M_D^n=
\begin{pmatrix}1&n\\0&1\end{pmatrix}
\]

in note 0048. Visible closure does not imply lifted closure.

At the cusp,

\[
m_P=(p-1,-1),\quad
m_Q=(-1,q-1),\quad
a_\infty=(1,1).
\]

The determinant \(|\det(m_P,m_Q)|=pq-p-q\) is the first-homology order of
the filled lens space. The fixture recomputes this integer; the lens-space
identification remains an imported classical theorem, as in
[Dehornoy's calculation][dehornoy].

---

## 6. The \((2,3)\) and \((2,4)\) calibrations

For \((2,3)\),

\[
pq-p-q=1,
\qquad
\overline{T^1\mathcal O_{2,3}}\cong S^3.
\]

Classically,

\[
T^1\mathcal O_{2,3}\cong S^3\setminus T(2,3),
\]

and primitive hyperbolic classes lift to modular knots
[as reviewed here][modular-knots]. The phase experiment gives one component,
joint return six, and primitive winding \((3,2)\). This agreement is evidence,
not a history-to-geodesic construction.

For \((2,4)\),

\[
pq-p-q=2,
\qquad
\overline{T^1\mathcal O_{2,4}}
\cong L(2,1)\cong\mathbb{RP}^3.
\]

The audited [Paper III result][aeg-q4] extends the sign cover to

\[
S^3\longrightarrow\mathbb{RP}^3
\]

and identifies the lifted cusp core as \(T(2,4)\). It has two components with
absolute mutual linking

\[
\frac{2\cdot4}{\gcd(2,4)^2}=2.
\]

The fixture checks the index-two lattice

\[
\Lambda=\{(x,y):x+y\equiv0\pmod2\}.
\]

In the basis \((a_\infty,m_P)\), it obtains

\[
a_\infty=(1,0),\qquad
m_P=(0,1),\qquad
m_Q=(1,-2),
\]

so \(a_\infty=m_Q+2m_P\). It also recovers two phase components and linking
magnitude two.

---

## 7. The essential \(q=4\) red-team check

The presentation

\[
\langle x,y\mid x^p=y^q\rangle
\]

has abelianization

\[
\boxed{
\mathbb Z\oplus\mathbb Z/\gcd(p,q)\mathbb Z.
}
\]

For \((2,4)\), this is

\[
\mathbb Z\oplus\mathbb Z/2\mathbb Z.
\]

A two-component link complement in \(S^3\) instead has
\(H_1\cong\mathbb Z^2\). The fixture checks the mismatch. The \(q=4\) link
cannot be obtained by renaming the central-extension group; the sign cover
and peripheral lattice calculation are essential.

---

## 8. Double visible closure and the Dehn-twist lift

Let

\[
D=\begin{pmatrix}1&1\\0&1\end{pmatrix},
\qquad
L=\operatorname{lcm}(p,q).
\]

Then

\[
D^L=\begin{pmatrix}1&L\\0&1\end{pmatrix}.
\]

Modulo either visible period,

\[
D^L\equiv I\pmod p,
\qquad
D^L\equiv I\pmod q.
\]

Both finite observers see closure. Over integral homology,

\[
D^L(0,1)=(L,1),
\]

so the lifted residual is \((L,0)\). The fixture checks this for
\((2,3)\), \((2,4)\), and \((3,4)\):

\[
\boxed{
\text{double visible closure}
\not\Rightarrow
\text{lifted path closure}.
}
\]

Suspending \(D\) would form the candidate mapping torus

\[
M_D=
\frac{T^2\times[0,1]}
{(x,1)\sim(Dx,0)}.
\]

The fixture verifies return-map arithmetic, not a ProgramSlice-derived
mapping-torus construction.

---

## 9. Conditional triadic feature package

If a future certificate identifies computational periods with orbifold
orders, the same numerals would have three distinct readings:

| proposed domain | feature | meaning |
|---|---:|---|
| temporal | \(\operatorname{lcm}(p,q)\) | first joint return |
| spatial | \(\gcd(p,q)\) | phase-orbit component count |
| constructive | \(pq-p-q\) | filling-lattice index |

For \((3,4)\), the triple is \((12,1,5)\). The proposal is attractive because
the readings do not collapse, but it remains conditional. No checked Adva
artifact currently provides

\[
\operatorname{PhasePeriods}(p,q)
\rightsquigarrow
\operatorname{OrbifoldOrders}(p,q).
\]

---

## 10. Separation from the figure-eight result

Note 0071 established

\[
-D_w(t)
=
-\phi\!\left(\frac{\partial w}{\partial b}\right)
=
\det(tI-M)
=
t^2-3t+1
\]

for a special figure-eight presentation.

This experiment does not show that the word is an orbifold cutting code, a
periodic geodesic, a phase orbit, the \(q=4\) cusp core, or a knot selected by
a checked Adva history. The figure-eight complement is not identified with
the Seifert-fibred unit tangent bundle used here.

The missing chain is

\[
\boxed{
\text{checked normalization history}
\to
\text{typed double periods}
\to
\text{orbifold cutting code or return map}
\to
\text{unit-tangent orbit}
\to
\text{closure characteristic}.
}
\]

---

## 11. What the fixture establishes

The exact standard-library fixture checks:

1. the phase torus splits into \(\gcd(p,q)\) successor orbits;
2. every orbit has length \(\operatorname{lcm}(p,q)\);
3. every orbit has primitive winding \((q/g,p/g)\);
4. the orbifold meridian determinant is \(pq-p-q\);
5. \((2,3),(2,4),(3,4)\) give homology orders \(1,2,5\);
6. the \(q=4\) parity lattice has index two and the printed slopes;
7. \(T(2,4)\) has two components with linking magnitude two;
8. central-extension homology differs from two-component link homology;
9. two visible periods close while integral Dehn-twist winding survives; and
10. equal numerals remain distinct typed period, orbifold, and slope records.

It creates no semantic identity or topological proof object.

---

## 12. Supporting evidence and conservative conclusion

Four independent layers support the synthesis:

1. classical unit-tangent and cusp-filling topology;
2. the audited AEG \(q=4\) sign-cover calculation;
3. note 0048's finite cellular Dehn twist; and
4. the new exact orbit, determinant, parity, and homology checks.

They establish independently

\[
\text{double periods}
\to
\text{phase torus}
\to
\text{component and winding data}
\]

and

\[
(p,q,\infty)\text{ orbifold}
\to
T^1\mathcal O_{p,q}
\to
\text{three-dimensional filling}.
\]

The supported conclusion is:

> The double-period and hyperbolic-compactification clues have a common torus
> interface and agree on the \((2,3)\) and \((2,4)\) calibration patterns. A
> history-natural identification of their typed \((p,q)\) inputs remains
> open.

---

## 13. Red-team opinions

The proposal must be weakened if:

1. no checked normalization history produces two intrinsic periods;
2. the opposite-domain carrier does not support a hyperbolic chart;
3. the direction fibre fails to separate projected branches;
4. the return map fails to preserve torus intersection;
5. computational periods vary under harmless presentation changes;
6. no identity-preserving map reaches an orbifold cutting code;
7. a filling slope is hidden;
8. a non-coprime pair is called a knot rather than a link;
9. the central-extension group is substituted for a link-complement group;
10. the figure-eight word is identified from polynomial coincidence; or
11. \(\gcd\), \(\operatorname{lcm}\), and \(pq-p-q\) are conflated.

Further limits:

- a unit-tangent lift needs a regular direction;
- equal point and tangent may require a higher jet;
- phase orbits give link combinatorics, not ambient isotopy;
- Alexander data remains incomplete;
- lens-space topology depends on the filling convention; and
- this construction says nothing by itself about physical spatial dimension.

---

## 14. Next falsifiable gate

The next experiment should start from one Rust-checked normalization history:

1. retain its complete ProgramSlice;
2. define two observer-relative return predicates;
3. prove their least positive periods \(p,q\);
4. construct the phase relation as a companion with the slice as residual;
5. derive an intersection-preserving map on \(H_1(T^2)\);
6. compare its cyclic code with one Hecke cutting code;
7. return a bridge certificate, an obstruction, or **NotRepresentable**; and
8. only then form a periodic orbit and compare its closure characteristic.

Promotion requires one positive bridge and one example where equal numeric
periods fail to determine the same orbifold or knot object.

---

## Conservative conclusion

\[
\boxed{
\text{double normalization periods}
\to
\text{finite phase torus}
\dashrightarrow
(p,q,\infty)\text{ orbifold}
\to
\text{unit-tangent lift}
\to
\text{three-dimensional knot environment}.
}
\]

The dashed arrow is the missing theorem. The experiment supports the original
intuition that the three-dimensional carrier can arise from a two-dimensional
add--multiply hyperbolic space together with the direction feature required
to retain crossing history. It does not yet identify computational periods
with orbifold orders.
