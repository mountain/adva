# A Cellular Annulus, Nodal Quotient, and Torus Dehn-Twist Calibration

Status: exploratory geometric calibration extending
[`0047-a1-nodal-through-crossing-geometry.md`](0047-a1-nodal-through-crossing-geometry.md).

The executable finite calibration is
`tests/python/test_cellular_annulus_torus_dehn_twist.py`.

The preceding `A_1` note established that a passage through a node is naturally
represented by a surgery trace and a pinch cospan rather than by one smooth
transport arrow.  Its finite complex-side model of the vanishing cycle was,
however, only a quotient set.  It did not yet provide:

- an actual two-dimensional annulus cellulation;
- an actual nodal annulus or nodal torus cellulation;
- an object-level cellular representative of the Dehn twist; or
- a direct recovery of the Picard--Lefschetz matrix from that cellular map.

This note supplies those missing objects.

The central result is:

> A finite cubical annulus admits an exact relative cellular automorphism whose
> vertex action is a shear and whose radial edges are sent to staircase paths.
> Gluing the two boundary circles produces a finite cubical torus.  The
> induced map on integral first homology is
>
> \[
> \begin{pmatrix}
> 1&1\\
> 0&1
> \end{pmatrix},
> \]
>
> the primitive Picard--Lefschetz transvection about the angular cycle.  If
> that cycle is pinched, the nodal quotient kills precisely this added
> direction.  A marked outgoing pinch makes the Dehn twist an exact resolution
> of the through-cospan.

The finite model also exposes a useful lifting phenomenon.  After `n` twists,
the permutation of the finite vertex set has returned to the identity, but
the cellular edge paths have accumulated `n` windings.  Thus

\[
D_0^n=I
\qquad\text{while}\qquad
D_1^n\ne I,
\]

and the induced homology action is

\[
\begin{pmatrix}
1&n\\
0&1
\end{pmatrix}.
\]

A finite vertex observer therefore sees a periodic action, whereas the lifted
cellular-path observer retains the infinite-order Dehn twist.

This remains research-local.  It introduces no stable annulus, torus, node,
cellular map, chain complex, pinch, normalization, Dehn twist, monodromy, or
through-crossing API.  It does not modify `claims.toml`, and it does not change
the active `ProgramSlice` priority or Rust semantic authority.

---

## 0. Executive diagram

The completed finite geometry is:

\[
\boxed{
\begin{CD}
A_- @>{D}>> A_+\\
@V{q_-}VV @VV{q_+}V\\
N @= N,
\end{CD}
}
\]

where:

- `A_-` and `A_+` are genuine finite annulus cellulations;
- `N` is a genuine finite nodal-annulus cellulation;
- `D` is the primitive cellular Dehn twist;
- `q_-` is the incoming pinch; and
- the marked outgoing pinch is

\[
q_+=q_-\circ D^{-1}.
\]

Consequently,

\[
\boxed{
q_+\circ D=q_-.
}
\]

Gluing the two annulus boundaries gives:

\[
\boxed{
A/\partial_-\sim\partial_+
=T^2,
}
\]

and the annulus twist descends to a cellular torus automorphism.  Pinching its
angular cycle gives the nodal torus:

\[
\boxed{
T^2\xrightarrow{q}T^2/a.
}
\]

At the homology level:

\[
H_1(T^2;\mathbf Z)
=\mathbf Za\oplus\mathbf Zb,
\]

\[
D_*(a)=a,
\qquad
D_*(b)=b+a,
\]

and

\[
q_*(a)=0,
\qquad
q_*(b)=c.
\]

Therefore:

\[
\boxed{
q_*D_*=q_*.
}
\]

Specialization forgets exactly the vanishing-cycle contribution that
distinguishes the two smooth resolutions.

---

# Part I. The genuine finite annulus

## 1. Cubical cellulation

Fix an integer

\[
n\ge3.
\]

For the exact finite shear used below, take `n` angular subdivisions and `n`
radial subdivisions.  The annulus has vertices

\[
v_{i,j},
\qquad
i\in\mathbf Z/n\mathbf Z,
\quad
0\le j\le n.
\]

Its oriented one-cells are:

\[
h_{i,j}:v_{i,j}\longrightarrow v_{i+1,j},
\]

and

\[
r_{i,j}:v_{i,j}\longrightarrow v_{i,j+1}.
\]

Its square two-cells are

\[
f_{i,j},
\qquad
0\le j<n,
\]

with cellular boundary

\[
\partial f_{i,j}
=
h_{i,j}
+r_{i+1,j}
-h_{i,j+1}
-r_{i,j}.
\]

The cell counts are:

\[
|V|=n(n+1),
\]

\[
|E|=n(n+1)+n^2=n(2n+1),
\]

and

\[
|F|=n^2.
\]

Hence:

\[
\chi(A_n)
=n(n+1)-n(2n+1)+n^2
=0.
\]

The executable boundary matrices verify:

\[
\partial_1\partial_2=0,
\]

and compute:

\[
(b_0,b_1,b_2)(A_n)=(1,1,0).
\]

This is now an actual finite two-dimensional annulus, not a quotient of a
finite set standing in for a circle.

## 2. Boundary circles

The two boundary cycles are:

\[
\partial_-A_n
=\sum_i h_{i,0},
\]

and

\[
\partial_+A_n
=\sum_i h_{i,n}.
\]

Both are fixed pointwise by the cellular twist constructed below.  The model
therefore represents a Dehn twist relative to the two annulus boundaries.

---

# Part II. An exact cellular Dehn twist

## 3. Vertex shear

Define the degree-zero action by:

\[
D_0(v_{i,j})
=v_{i+j,j}.
\]

Angular indices are read modulo `n`.  At the lower boundary:

\[
D_0(v_{i,0})=v_{i,0}.
\]

At the upper boundary:

\[
D_0(v_{i,n})
=v_{i+n,n}
=v_{i,n}.
\]

Thus the finite shear fixes both boundary vertex cycles pointwise.

## 4. Edge paths

Horizontal edges map to horizontal edges:

\[
D_1(h_{i,j})
=h_{i+j,j}.
\]

A radial edge maps to a two-edge staircase:

\[
\boxed{
D_1(r_{i,j})
=
h_{i+j,j}+r_{i+j+1,j}.
}
\]

The path starts at

\[
v_{i+j,j}.
\]

after the vertex shear and ends at

\[
v_{i+j+1,j+1},
\]

which is the image of `v_(i,j+1)`.

This is why an edge-path carrier is essential.  A strict permutation of the
finite radial edges cannot record a full twist while fixing both boundaries.

## 5. Face action

Define:

\[
D_2(f_{i,j})
=f_{i+j+1,j}.
\]

A direct boundary calculation gives:

\[
\partial D_2(f_{i,j})
=D_1\partial(f_{i,j}).
\]

Together with the vertex-edge compatibility, this proves that:

\[
D=(D_0,D_1,D_2)
\]

is a cellular chain map.

## 6. Exact inverse

The inverse shear is:

\[
D_0^{-1}(v_{i,j})
=v_{i-j,j},
\]

\[
D_1^{-1}(h_{i,j})
=h_{i-j,j},
\]

and

\[
D_1^{-1}(r_{i,j})
=-h_{i-j-1,j}+r_{i-j-1,j}.
\]

On faces:

\[
D_2^{-1}(f_{i,j})
=f_{i-j-1,j}.
\]

The executable fixture checks degree by degree that:

\[
D^{-1}D=I.
\]

Thus the model is not merely a homology endomorphism.  It is an exact
invertible cellular chain representative of the relative Dehn twist.

The note does not yet claim that this particular cellular representative has
been realized as a strict combinatorial homeomorphism of the original square
cellulation.  It is a cellular automorphism with explicit inverse; a future
subdivision can provide a PL realization.

---

# Part III. Boundary gluing and the torus

## 7. Gluing map

Identify:

\[
v_{i,n}\sim v_{i,0},
\]

and likewise identify the upper and lower horizontal boundary edges.  The
result is the finite cubical torus `T_n` with:

\[
|V|=n^2,
\qquad
|E|=2n^2,
\qquad
|F|=n^2.
\]

Hence:

\[
\chi(T_n)=0.
\]

The exact boundary matrices give:

\[
(b_0,b_1,b_2)(T_n)=(1,2,1).
\]

Let

\[
g:A_n\longrightarrow T_n
\]

be the boundary-gluing cellular map.

Because `D` fixes both annulus boundaries, the square commutes strictly:

\[
\boxed{
\begin{CD}
A_n @>{D_A}>> A_n\\
@V{g}VV @VV{g}V\\
T_n @>{D_T}>> T_n.
\end{CD}
}
\]

The test verifies this equality in degrees zero, one, and two.

## 8. Integral homology basis

Choose the angular cycle:

\[
a
=\sum_{i=0}^{n-1}h_{i,0},
\]

and the transverse cycle:

\[
b
=\sum_{j=0}^{n-1}r_{0,j}.
\]

Two integral cellular cocycles detect their winding numbers.

The angular-cut cocycle `dx` is `1` exactly on horizontal edges crossing the
angular cut:

\[
h_{n-1,j},
\]

and zero elsewhere.

The radial-cut cocycle `dy` is `1` exactly on vertical edges crossing the
radial gluing seam:

\[
r_{i,n-1},
\]

and zero elsewhere.

They satisfy:

\[
dx(a)=1,
\qquad
dy(a)=0,
\]

\[
dx(b)=0,
\qquad
dy(b)=1.
\]

Thus `(a,b)` is an integral marked basis of the finite torus homology.

## 9. Recovered Picard--Lefschetz matrix

The cellular twist fixes `a`:

\[
D_*(a)=a.
\]

The image of `b` is the staircase path:

\[
D_*(b)
=
\sum_{j=0}^{n-1}
\left(
 h_{j,j}+r_{j+1,j}
\right).
\]

The cut cocycles evaluate it as:

\[
dx(D_*b)=1,
\qquad
dy(D_*b)=1.
\]

Therefore:

\[
D_*(b)=b+a
\]

in `H_1(T_n;Z)`, and the induced matrix in the ordered basis `(a,b)` is:

\[
\boxed{
M_D
=
\begin{pmatrix}
1&1\\
0&1
\end{pmatrix}.
}
\]

For the intersection form

\[
J=
\begin{pmatrix}
0&1\\
-1&0
\end{pmatrix},
\]

we have:

\[
M_D^TJM_D=J.
\]

Let:

\[
\delta=a.
\]

Then for every homology vector `x`:

\[
\boxed{
D_*(x)
=x+\langle\delta,x\rangle\delta.
}
\]

The Picard--Lefschetz transvection has therefore been recovered from the
object-level cellular map rather than inserted as an independent matrix.

---

# Part IV. Finite vertices versus lifted cellular paths

## 10. Apparent finite periodicity

Because angular coordinates are taken modulo `n`:

\[
D_0^n(v_{i,j})
=v_{i+nj,j}
=v_{i,j}.
\]

Thus:

\[
D_0^n=I.
\]

A vertex-only observer concludes that the finite twist has order dividing
`n`.

## 11. Infinite-order path lift

The one-cell action does not close:

\[
D_1^n\ne I.
\]

Each iteration adds another angular winding to the transverse cellular path.
On first homology:

\[
M_D^n
=
\begin{pmatrix}
1&n\\
0&1
\end{pmatrix}.
\]

Therefore the finite cellular object distinguishes:

\[
\boxed{
\text{finite vertex permutation}
\quad\text{from}\quad
\text{infinite lifted path action}.
}
\]

This is the geometric analogue of the earlier distinction between a coarse
projective observer and a lifted observer retaining central or historical
data.  No infinite number of cells is required; the unbounded information is
stored in integer edge-path coefficients and composition depth.

---

# Part V. The nodal annulus

## 12. Collapsing an interior core row

Choose an interior radial row:

\[
0<c<n.
\]

Collapse the angular cycle

\[
\{v_{i,c}\}_i
\]

and its horizontal edges to a single node.

All other vertices and cells remain.  Squares adjacent to the collapsed row
become triangular cells; squares away from it remain quadrilateral cells.

For an annulus with `n` angular intervals and `m` radial intervals, the nodal
quotient has:

\[
|V|=nm+1,
\]

\[
|E|=2nm,
\]

and

\[
|F|=nm.
\]

Thus:

\[
\chi(N_A)=1.
\]

The computed Betti numbers are:

\[
(b_0,b_1,b_2)(N_A)=(1,0,0).
\]

Topologically this is two disks meeting at one node.

## 13. Normalization

Split the node into a lower preimage and an upper preimage.  The normalized
cellulation has one additional vertex and two connected components:

\[
(b_0,b_1,b_2)(\widetilde N_A)=(2,0,0).
\]

Its Euler characteristic is:

\[
\chi(\widetilde N_A)=2.
\]

This is the finite cellular normalization of the two disk branches.

## 14. Exact pinch map

The smooth annulus maps to its nodal quotient by:

- sending every core-row vertex to the node;
- sending every core horizontal edge to zero;
- preserving every other edge; and
- sending each square to the corresponding quadrilateral or triangular
  quotient cell.

The resulting maps

\[
q_0,
\quad q_1,
\quad q_2
\]

form an exact cellular chain map.

The smooth angular generator is killed:

\[
q_*(a)=0.
\]

This is the cellular vanishing-cycle certificate.

---

# Part VI. Marked through-resolutions

## 15. Why the outgoing pinch must be marked

An unmarked statement

\[
q\circ D=q
\]

is too strong for a concrete cellular Dehn twist distributed through the
annulus.  The twist changes points and cellular paths away from the collapsed
core, even though its extra homology direction vanishes after specialization.

The correct cospan remembers the outgoing marking.

Set:

\[
q_-=q,
\]

and define the outgoing pinch associated with one positive resolution by:

\[
\boxed{
q_+=q\circ D^{-1}.
}
\]

Then:

\[
\boxed{
q_+\circ D=q_-.
}
\]

The executable test verifies this identity in every cellular degree.

Thus a deterministic through-resolution is not merely a map between two
unmarked copies of the same annulus.  It is a map between **marked
smoothings** whose pinch maps agree after continuation.

## 16. Resolution torsor

For an integer `k`, define:

\[
P_k=D^k,
\]

and:

\[
q_+^{(k)}=q\circ D^{-k}.
\]

Then:

\[
q_+^{(k)}P_k=q_-.
\]

Two resolutions differ by:

\[
P_\ell^{-1}P_k
=D^{k-\ell}.
\]

The resolution set is therefore a torsor under the infinite cyclic Dehn-twist
group, not a finite cyclic rotation set.

This corrects the bounded phase quotient used in the preceding `A_1` note.
The finite cycle model was useful for exposing relation-valued through-data,
but it could only retain phase modulo its number of sample points.  The
cellular path lift retains the full integer twist.

---

# Part VII. Pinching the torus

## 17. Nodal torus cellulation

In the cubical torus, collapse the horizontal row carrying `a` to one node.
The remaining rows form a cylinder whose two ends meet at that node.

The cell counts are:

\[
|V|=n(n-1)+1,
\]

\[
|E|=n(2n-1),
\]

and:

\[
|F|=n^2.
\]

Hence:

\[
\chi(N_T)=1.
\]

The exact Betti numbers are:

\[
\boxed{
(b_0,b_1,b_2)(N_T)=(1,1,1).
}
\]

This is the homology of:

\[
S^2\vee S^1,
\]

which is the topological nodal torus.

## 18. Torus normalization

Splitting the node into its two branch preimages caps the two ends of the
remaining cylinder separately.  The result is a finite sphere cellulation:

\[
\boxed{
(b_0,b_1,b_2)(\widetilde N_T)=(1,0,1).
}
\]

and:

\[
\chi(\widetilde N_T)=2.
\]

This verifies at the cell-complex level that the normalization of a
nonseparating nodal torus is a sphere.

## 19. Surviving cycle

The angular cycle vanishes:

\[
q_*(a)=0.
\]

The transverse cycle survives as the loop passing through the node:

\[
q_*(b)=c.
\]

A cellular cocycle on the nodal torus evaluates:

\[
\omega(c)=1.
\]

Since:

\[
D_*(b)=b+a,
\]

we obtain:

\[
q_*D_*(b)
=q_*(b+a)
=c.
\]

Together with `q_*D_*(a)=0`, this proves:

\[
\boxed{
q_*D_*=q_*
}
\]

on first homology.

The singular quotient has forgotten precisely the Dehn-twist direction.

---

# Part VIII. What has been gained

## 20. Around, specialize, and through now share one cellular carrier

The finite geometry now contains:

### Around

The cellular automorphism:

\[
D:A\to A
\]

or its descended torus map.

### Specialize

The exact cellular quotient:

\[
q:A\to N_A
\]

and:

\[
q:T^2\to N_T.
\]

### Through

The marked cospan:

\[
A_-
\xrightarrow{q_-}
N_A
\xleftarrow{q_+^{(k)}}
A_+,
\]

with chosen resolution:

\[
P_k=D^k.
\]

The structural relation is:

\[
q_+^{(k)}P_k=q_-.
\]

Monodromy is the difference between two marked through-resolutions:

\[
P_\ell^{-1}P_k=D^{k-\ell}.
\]

## 21. The matrix is now derived, not postulated

Earlier notes used Picard--Lefschetz matrices as exact classical
calibrations.  This project reconstructs the primitive matrix from:

- finite cells;
- explicit cellular boundary maps;
- an explicit invertible cellular map;
- two explicit integral cycles; and
- two explicit integral cocycles.

The chain of derivation is:

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

## 22. Finite structure can retain an infinite lift

The finite vertex set alone sees:

\[
D_0^n=I.
\]

The edge-path carrier sees:

\[
D_1^n\ne I.
\]

The homology carrier sees:

\[
M_D^n
=\begin{pmatrix}1&n\\0&1\end{pmatrix}.
\]

This demonstrates a general mechanism important to Adva:

> A finite object need not collapse an unbounded process when its arrows carry
> integer multiplicity, path, or history data.

The same principle may later support observer-relative lifts, construction
histories, and nonterminating refinement without requiring an infinite base
cellulation.

---

# Part IX. Conservative conclusion

The project establishes the following bounded facts.

1. A genuine finite cubical annulus and torus can be constructed with exact
   cellular boundary matrices.
2. A relative cellular Dehn twist exists with an explicit cellular inverse.
3. Boundary gluing transports that twist exactly from the annulus to the
   torus.
4. The induced integral homology action is the primitive
   Picard--Lefschetz transvection.
5. A genuine nodal annulus and nodal torus arise by collapsing the declared
   vanishing cycle.
6. Their normalizations have the expected disk and sphere homology.
7. Specialization kills the vanishing direction and therefore erases the
   added twist component.
8. A deterministic through-resolution requires a marked outgoing pinch.
9. Different marked resolutions form an infinite cyclic torsor.
10. Finite vertices can close while cellular paths retain an infinite lift.

The project does **not** yet establish:

- a stable geometric calculus;
- a strict PL homeomorphism on the original square subdivision;
- a general theorem for arbitrary Lefschetz singularities;
- a compositional category of cellular cospans;
- a Cerf or Hurwitz move calculus for multiple nodes;
- a coupling to temporal or constructive domains;
- an irreducible triadic obstruction; or
- any `Omega` theorem.

---

# Part X. Red-team opinion

## 23. Cellular automorphism versus combinatorial homeomorphism

The map `D` is an exact invertible cellular chain representative.  Radial
one-cells map to two-edge paths, so it is not a permutation of the original
one-cells.  Calling it a strict cubical homeomorphism would therefore be too
strong.

A future project should subdivide the annulus and realize the same map as an
explicit PL homeomorphism, then compare the PL and cellular certificates.

## 24. Homology does not determine the mapping class

Recovering:

\[
\begin{pmatrix}1&1\\0&1\end{pmatrix}
\]

is necessary but not, in arbitrary surfaces, sufficient to identify a mapping
class.  On the torus the action on `H_1` is faithful up to the familiar
`SL(2,Z)` identification, but a future higher-genus theory must retain more
than homology matrices.

## 25. The analytic family is not yet cellulated

The project models the topology expected from the analytic node `uv=s`, but it
does not construct one parameterized total-space cellulation whose level sets
are all the smooth and nodal cellulations above.

That is the next object-level strengthening of the through geometry.

## 26. Marking is structural, not cosmetic

The strict equation:

\[
q_+D=q_-
\]

holds because the outgoing pinch carries the transported marking:

\[
q_+=q_-D^{-1}.
\]

If markings are omitted, one should only claim equality up to an explicit
isotopy or chain homotopy.  The formal language must never silently identify
these two levels.

## 27. The nodal quotient does not erase all information

Pinching kills `a`, but the transverse nodal loop `c` survives.  The singular
fibre is not an information-free point.  It preserves the quotient information
compatible with specialization and forgets only the vanishing direction and
its gluing lift.

## 28. No irreducible three-domain result is present

This project is deliberately geometric.  It does not turn the new cellular
objects into a temporal--spatial--constructive coherence theorem.  That bridge
should be built only after the geometry is stable.

---

# Part XI. Next geometric projects

## 29. PL realization

Subdivide the annulus 