# A Cellular Annulus, Nodal Quotient, and Torus Dehn-Twist Calibration

Status: exploratory geometric calibration extending
[`0047-a1-nodal-through-crossing-geometry.md`](0047-a1-nodal-through-crossing-geometry.md).

The executable finite calibration is
`tests/python/test_cellular_annulus_torus_dehn_twist.py`.

The preceding `A_1` note established that passage through a node is naturally
represented by a surgery trace and a pinch cospan rather than by one smooth
transport arrow. Its complex-side vanishing-cycle model was still a finite
quotient set. This note replaces that proxy by genuine two-dimensional finite
cell complexes.

The main result is:

> A finite cubical annulus admits an exact relative cellular chain
> automorphism representing the primitive Dehn twist. After gluing the two
> boundary circles, the induced torus map acts on integral first homology by
>
> \[
> \begin{pmatrix}
> 1&1\\
> 0&1
> \end{pmatrix}.
> \]
>
> Pinching the angular cycle kills precisely the added Picard--Lefschetz
> direction. A marked outgoing pinch makes the Dehn twist an exact selected
> resolution of the through-cospan.

This remains research-local. It introduces no stable annulus, torus, node,
cellular-map, chain-complex, pinch, normalization, Dehn-twist, monodromy, or
through-crossing API. It does not modify `claims.toml`, and it does not change
the active `ProgramSlice` priority or Rust semantic authority.

---

## 1. The finite annulus

Fix an integer

\[
n\ge 3.
\]

The cubical annulus has vertices

\[
v_{i,j},
\qquad
 i\in\mathbf Z/n\mathbf Z,
\qquad
0\le j\le n.
\]

Its horizontal and radial one-cells are

\[
h_{i,j}:v_{i,j}\longrightarrow v_{i+1,j},
\]

and

\[
r_{i,j}:v_{i,j}\longrightarrow v_{i,j+1}.
\]

Its square two-cells satisfy

\[
\partial f_{i,j}
=
h_{i,j}+r_{i+1,j}-h_{i,j+1}-r_{i,j}.
\]

The cell counts are

\[
|V|=n(n+1),
\qquad
|E|=n(2n+1),
\qquad
|F|=n^2,
\]

so

\[
\chi(A_n)=0.
\]

The exact boundary matrices verify

\[
\partial_1\partial_2=0,
\]

and compute

\[
(b_0,b_1,b_2)(A_n)=(1,1,0).
\]

Thus the carrier is an actual finite two-dimensional annulus, not a finite set
standing in for a circle.

---

## 2. An exact cellular Dehn twist

Define the degree-zero shear by

\[
D_0(v_{i,j})=v_{i+j,j}.
\]

Angular indices are taken modulo `n`. Since the upper row has `j=n`, both
boundary circles are fixed pointwise.

Horizontal edges map to horizontal edges:

\[
D_1(h_{i,j})=h_{i+j,j}.
\]

Radial edges map to staircase paths:

\[
\boxed{
D_1(r_{i,j})
=
h_{i+j,j}+r_{i+j+1,j}.
}
\]

Faces map by

\[
D_2(f_{i,j})=f_{i+j+1,j}.
\]

The executable fixture checks

\[
\partial D_2=D_1\partial,
\qquad
\partial D_1=D_0\partial.
\]

It also constructs the inverse shear explicitly and verifies in all three
cellular degrees that

\[
D^{-1}D=DD^{-1}=I.
\]

The map is therefore an exact invertible cellular chain representative of the
relative Dehn twist. It is not yet claimed to be a strict permutation of the
original cubical cells: radial one-cells map to edge paths. A future finite
subdivision should realize the same mapping class as a PL homeomorphism.

---

## 3. Boundary gluing and the torus

Identify the two annulus boundary circles pointwise:

\[
v_{i,n}\sim v_{i,0}.
\]

The quotient is a finite cubical torus with

\[
|V|=n^2,
\qquad
|E|=2n^2,
\qquad
|F|=n^2,
\]

and

\[
(b_0,b_1,b_2)(T_n)=(1,2,1).
\]

Let

\[
g:A_n\longrightarrow T_n
\]

be the gluing chain map. Because the annulus twist fixes both boundaries, it
descends strictly:

\[
\boxed{
gD_A=D_Tg.
}
\]

The test verifies this equality in degrees zero, one, and two.

---

## 4. Recovering the Picard--Lefschetz matrix

Choose the angular and transverse cycles

\[
a=\sum_{i=0}^{n-1}h_{i,0},
\qquad
b=\sum_{j=0}^{n-1}r_{0,j}.
\]

Two integral cellular cocycles detect their winding coordinates. They satisfy

\[
dx(a)=1,
\qquad
dy(a)=0,
\]

and

\[
dx(b)=0,
\qquad
dy(b)=1.
\]

The cellular twist fixes the angular cycle:

\[
D_*(a)=a.
\]

The transverse cycle becomes a staircase with one additional angular winding:

\[
D_*(b)=b+a.
\]

Hence the induced matrix in the ordered basis `(a,b)` is

\[
\boxed{
M_D=
\begin{pmatrix}
1&1\\
0&1
\end{pmatrix}.
}
\]

For

\[
J=
\begin{pmatrix}
0&1\\
-1&0
\end{pmatrix},
\]

we have

\[
M_D^TJM_D=J.
\]

With vanishing cycle

\[
\delta=a,
\]

the action is exactly

\[
\boxed{
D_*(x)=x+\langle\delta,x\rangle\delta.
}
\]

Thus the primitive Picard--Lefschetz transvection is derived from the finite
cellular map rather than inserted as an independent matrix.

---

## 5. Finite vertices and the infinite path lift

The vertex action is finite:

\[
D_0^n=I.
\]

A vertex-only observer therefore sees a periodic transformation.

The cellular path action does not close:

\[
D_1^n\ne I.
\]

On homology,

\[
M_D^n=
\begin{pmatrix}
1&n\\
0&1
\end{pmatrix}.
\]

Therefore

\[
\boxed{
\text{finite vertex closure}
\not\Rightarrow
\text{lifted path closure}.
}
\]

No infinite cellulation is required. The unbounded winding is stored in
integer path coefficients and composition depth.

---

## 6. Nodal quotients

Collapse one angular row of the annulus to a node. The resulting finite nodal
annulus has

\[
(b_0,b_1,b_2)=(1,0,0).
\]

Its normalization is represented by two disk components:

\[
(b_0,b_1,b_2)=(2,0,0).
\]

Collapsing the corresponding angular cycle on the torus gives a nodal torus
with

\[
\boxed{
(b_0,b_1,b_2)=(1,1,1).
}
\]

Its normalization is a sphere:

\[
(b_0,b_1,b_2)=(1,0,1).
\]

Let

\[
q:T_n\longrightarrow N_T
\]

be the cellular pinch. It kills the vanishing cycle:

\[
q_*(a)=0.
\]

The transverse cycle survives as the nodal loop. Since

\[
D_*(b)=b+a,
\]

we obtain

\[
\boxed{
q_*D_*=q_*.
}
\]

Specialization forgets exactly the vanishing-cycle contribution that
distinguishes the smooth resolutions.

---

## 7. Marked through-resolutions

For a concrete distributed cellular twist, the unmarked equation

\[
qD=q
\]

is generally too strong on every cell. The outgoing smoothing must carry its
transported marking.

Take

\[
q_-=q,
\]

and define

\[
\boxed{
q_+=q_-D^{-1}.
}
\]

Then

\[
\boxed{
q_+D=q_-.
}
\]

More generally, for

\[
P_k=D^k,
\qquad
q_+^{(k)}=qD^{-k},
\]

we have

\[
q_+^{(k)}P_k=q_-.
\]

Two marked resolutions differ by

\[
P_\ell^{-1}P_k=D^{k-\ell}.
\]

The through-resolution space is therefore a torsor under the infinite cyclic
Dehn-twist group. This replaces the finite phase quotient used in the earlier
point-set model.

---

## 8. What has been established

The bounded executable model establishes:

1. genuine finite annulus and torus chain complexes;
2. exact cellular boundary maps with `d1 d2 = 0`;
3. an invertible relative cellular Dehn-twist representative;
4. strict descent through annulus-boundary gluing;
5. derivation of the primitive Picard--Lefschetz matrix from cycles and
   cocycles;
6. separation of finite vertex periodicity from infinite path winding;
7. nodal annulus and nodal torus quotient homology;
8. vanishing-cycle collapse under specialization; and
9. strict marked-cospan resolution by an outgoing transported pinch.

The model does **not** yet establish:

- a strict PL homeomorphism on the original square subdivision;
- one parameterized total-space cellulation for the analytic family `uv=s`;
- a compositional category of cellular cospans;
- Cerf or Hurwitz moves for several nodes;
- a coupling to the temporal or constructive domains;
- an irreducible triadic obstruction; or
- any `Omega` theorem.

---

## 9. Next geometric step

The immediate next task is to subdivide the annulus so that the staircase map
is realized by a strict PL homeomorphism. The PL representative should be
compared with the present chain map by explicit subdivision and chain-homotopy
certificates.

After that, two-node compositions can test whether different factorizations
are related by finite Hurwitz or Cerf moves at the object level rather than
only by homology matrices.

---

## Conservative conclusion

The geometric chain is now explicit:

\[
\boxed{
\text{annulus shear}
\longrightarrow
\text{cellular edge paths}
\longrightarrow
\text{torus gluing}
\longrightarrow
H_1\text{ action}
\longrightarrow
\text{Picard--Lefschetz matrix}.
}
\]

The nodal quotient supplies the complementary specialization map:

\[
\boxed{
q_*D_*=q_*.
}
\]

Together with the marked identity

\[
\boxed{
q_+D=q_-,
}
\]

this gives a genuine finite two-dimensional semantics for

\[
\text{around}
+
\text{specialize}
+
\text{through}.
\]

The essential new distinction is that a finite object may close on vertices
while retaining an infinite lift in cellular paths. The singular quotient
forgets exactly the vanishing direction and its gluing lift, not the entire
fibre.
