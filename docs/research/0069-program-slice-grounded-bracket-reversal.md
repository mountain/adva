# A ProgramSlice-Grounded Bracket-Reversal Observer

Status: bounded checked-grounded observer calibration following
[`0060-checked-bracket-observer-bridge.md`](0060-checked-bracket-observer-bridge.md),
[`0061-lineage-aware-bracket-events.md`](0061-lineage-aware-bracket-events.md),
[`0067-circular-three-form-interface-duality.md`](0067-circular-three-form-interface-duality.md),
and
[`0068-finite-circular-overlap-transport.md`](0068-finite-circular-overlap-transport.md).

The executable fixture is
[`test_program_slice_bracket_reversal.py`][fixture].

[fixture]: ../../tests/python/test_program_slice_bracket_reversal.py

The motivating implementation conjecture is:

> Reverse every typed bracket, reverse the outer sequence, and normalize the
> outer order again.  Can this be implemented as a very small algorithm over
> `ProgramSlice`?

The bounded answer is:

\[
\boxed{\text{yes as a certificate-bound observer; no as a ProgramSlice inverse.}}
\]

For a full output-ready triadic slice, the surface algorithm is constant-size:

\[
\operatorname{SurfaceStar}_Q
=
\operatorname{Normalize}_{K<X<t}
\circ\operatorname{ReverseOuter}
\circ\operatorname{FlipPairs}
\circ\operatorname{PairBoundary}_Q.
\]

The complete exact slice remains in a residual.  The algorithm does not
reverse execution, create a new diagram, reassign identities, or claim that
noninvertible operations have acquired inverses.

---

## 0. The exact type of the algorithm

The current Rust-owned object is

\[
S=\operatorname{ProgramSlice}(P,U,V),
\qquad U\subseteq V,
\]

with certified fields:

- lower and upper causal cuts;
- interval events \(V\setminus U\);
- lower and upper changed boundaries;
- unchanged through wires;
- internal events;
- original occurrences and lineage;
- node-associated history; and
- optional compiler graft intersections.

The new research-local map has type

\[
\boxed{
\operatorname{SurfaceStar}_Q:
\operatorname{FullTriadicSlice}(P)
\longrightarrow
\operatorname{ObservedWithResidual}
(\operatorname{Raw111}^{\star}).
}
\]

It is deliberately **not** typed as

\[
\operatorname{ProgramSlice}\longrightarrow\operatorname{ProgramSlice}.
\]

The input restriction matters.  V0 requires:

1. one full slice from the initial cut to the output-ready cut;
2. three declared input roles `(t,X,K)`;
3. three declared output roles `(t,X,K)`;
4. one lower and one upper crossing for each domain; and
5. checked graph, linear-use, past, boundary, identity, and lineage
   certificates.

An arbitrary internal cut does not expose canonical `K/X/t` roles.  It is
`NotRepresentable` under this observer rather than guessed from node-port
indices.

---

## 1. One bracket is a pair of exact boundary endpoints

For every declared domain \(D\), read one exact lower crossing and one exact
upper crossing from the same checked slice:

\[
B_D=(\ell_D,u_D;+),
\]

where \(+\) records the forward slice orientation.  Each endpoint retains its
complete serialized `CutWire`: `WireRef`, source sequence, consumer, lineage,
and original IDs.

Bracket reversal is simply

\[
\boxed{
\operatorname{flip}(B_D)=(u_D,\ell_D;-).
}
\]

This is the precise implementation of “reverse each bracket.”  The glyph is
still printed as `{}`, `[]`, or `()`; its opening and closing marks are display
syntax, while the endpoint direction is carried by the typed pair.

The operation is involutive:

\[
\operatorname{flip}^2(B_D)=B_D.
\]

No `WireRef`, `SourceId`, `OccurrenceId`, or history event is changed.

---

## 2. Contravariant outer reversal

Start with the public order

\[
(B_K,B_X,B_t).
\]

Contravariant reversal first gives

\[
\operatorname{rawStar}(B_K,B_X,B_t)
=
(\operatorname{flip}B_t,
  \operatorname{flip}B_X,
  \operatorname{flip}B_K).
\]

Its raw glyph presentation is

```text
()[]{}
```

The observer calibration then sorts complete typed pairs, not their internal
evidence, back into the declared order:

\[
\operatorname{Normalize}_{K<X<t}
(\operatorname{rawStar})
=
(\operatorname{flip}B_K,
  \operatorname{flip}B_X,
  \operatorname{flip}B_t).
\]

The visible result is again

```text
{}[]()
```

while the normalization witness records the exact outer permutation

\[
(2,1,0).
\]

The algorithm moves each typed pair as one record.  It never reorders sources
or occurrences inside a crossing.

---

## 3. Executable algorithm

The V0 procedure is:

```text
input: checked function P, full ProgramSlice analysis S, observer policy Q

1. verify P and S certificates
2. require S.lower = initial causal cut
3. require S.upper = complete output-ready causal cut
4. assign lower crossings by checked input producer indices
5. assign upper crossings by checked output consumer indices
6. pair lower_D with upper_D for D in K,X,t
7. raw := reverse([flip(pair_D) for D in K,X,t])
8. normalized := stable_sort(raw, K<X<t)
9. return normalized surface, permutation witness,
   exact checked-slice snapshot, and derivation certificate
```

Steps 4--8 inspect only six boundary endpoints and three domain labels.  Once
the slice is available, the visible surface computation is constant-size for
the fixed triad.  Materializing the complete residual is
\(O(|S|)\); a future Rust-owned artifact could instead reference the existing
slice and certificate without copying it.

---

## 4. Why this is not a reversed ProgramSlice

A true reversed slice would at minimum require

\[
\operatorname{ProgramSlice}(P,V,U).
\]

For every nonidentity interval, this violates the defining condition

\[
U\subseteq V.
\]

The current Rust analyzer correctly rejects the request.

There is a second obstruction.  The checked fixtures contain:

- `copy`, whose reverse would require a checked merge or equality condition;
- `discard`, whose reverse would require creation or hidden input;
- `add` and `mul`, which are not invertible on the declared boundary; and
- `swap`, which is invertible but does not make the surrounding active program
  invertible.

Therefore swapping the two cuts and reversing the event vector cannot produce
a valid semantic inverse.  Event-vector reversal would also violate the exact
diagram order used by slice composition.

The correct separation is

\[
\boxed{
\text{simple boundary reversal}
\quad\ne\quad
\text{inverse computation}.
}
\]

---

## 5. The residual is essential

The fixture checks four Rust-validated programs:

1. identity triad: no events and three through wires;
2. swap triad: one `swap`, two changed pairs, and one through wire;
3. spatial multiplication: two `copy`, one `discard`, and one `mul` event;
4. spatial addition: the same structural pattern with `add` instead of `mul`.

All four have the same normalized dual surface:

```text
{}[]()
```

Their exact slices are different.  In particular, spatial multiplication and
spatial addition have the same bracket surface and closely matching lineage
shape, but at `(t,X,K)=(2,7,3)` their checked values are

\[
(2,6,3)
\qquad\text{and}\qquad
(2,5,3).
\]

Thus the visible algorithm is many-to-one:

\[
\boxed{
\operatorname{SurfaceStar}_Q(S_1)
=
\operatorname{SurfaceStar}_Q(S_2)
\centernot\Rightarrow
S_1=S_2.
}
\]

The residual retains the complete ProgramSlice fields, original function IR,
validation certificate, role policy, and slice or composition certificate.
No `ProvenanceHide` or forgetting authority is inferred from the flat surface.

---

## 6. Compatibility with exact slice composition

For nested cuts

\[
U\subseteq M\subseteq V,
\]

Rust already certifies that composing the two adjacent slices returns the
same canonical outer `ProgramSlice` as direct analysis:

\[
\operatorname{Compose}
(S_{U,M},S_{M,V})
=
S_{U,V}.
\]

Because the observer reads that exact result, the following bounded square
commutes:

\[
\boxed{
\operatorname{SurfaceStar}_Q
(\operatorname{Compose}(S_{U,M},S_{M,V}))
=
\operatorname{SurfaceStar}_Q(S_{U,V}).
}
\]

The direct slice certificate and composition certificate remain distinct
derivation witnesses.  This does not establish

\[
(S_2\circ S_1)^\star=S_1^\star\circ S_2^\star
\]

inside a category of reversible ProgramSlices; no such category is currently
defined.

---

## 7. Relationship to the circular overlap model

Notes 0067--0068 place the three charts on a circular coordination nerve.  The
present normalization is a gauge choice of printed basepoint and order.  It
does not delete holonomy.

If future overlap maps carry a nontrivial circuit

\[
H=g_{tK}g_{Xt}g_{KX},
\]

printing the normalized surface `{}[]()` does not imply \(H=I\).  The
holonomy, fixed-point data, or obstruction must remain in the residual beside
the exact slice evidence.

This resolves a possible ambiguity:

- outer-order normalization is a coordinate/display normalization;
- bracket flip is a boundary-pair polarity reversal;
- overlap holonomy is retained comparison history; and
- active ProgramSlice events are checked computation.

These are four different operations.

---

## 8. What the fixture checks

The native-grounded Python fixture checks:

1. Rust validation and ProgramSlice certificates before observation;
2. exact lower-input and upper-output triadic role assignment;
3. endpoint exchange inside each typed pair;
4. outer raw reversal from `K,X,t` to `t,X,K`;
5. normalization back to `K,X,t` with permutation `(2,1,0)`;
6. involutivity of pair flip plus normalized outer reversal;
7. complete preservation of crossing JSON inside each moved pair;
8. identity, through-wire, swap, copy, discard, add, and multiply cases;
9. collision of distinct exact slices at the same visible surface;
10. rejection of an incomplete internal-cut view;
11. Rust rejection of the illegal reversed interval `(V,U)`; and
12. equality of direct and composed outer observations while keeping their
    derivation certificates distinct.

This is a checked-grounded research observer.  Python does not allocate or
authorize semantic identities.

---

## 9. Nonclaims and promotion boundary

This note does not establish:

- a stable `ProgramSlice::star`, `dual`, inverse, dagger, or pullback API;
- a reversed checked diagram;
- inverses for copy, discard, add, or multiply;
- canonical domain roles for arbitrary internal cuts;
- that a flat bracket surface is quiescent, complete, or provenance-free;
- that outer sorting is braid, gauge, or equation-cell authority;
- a full 3-form logic or universal normalization machine; or
- permission to change `adva.ir` version 1.

A future Rust promotion should use a name such as
`BoundaryOppositeObservation`, not `ProgramSliceStar`, and should return:

1. a reference to the original checked slice;
2. exact paired endpoint identities;
3. the outer permutation;
4. the observer role policy and version;
5. any overlap holonomy residual; and
6. a certificate that no internal evidence was reassigned or erased.

Promotion is justified only after an internal-cut role policy and at least one
nontrivial overlap comparison are Rust-grounded.

---

## Conservative conclusion

The proposed implementation intuition is correct after one type correction.
The useful algorithm really is:

\[
\boxed{
\text{flip each bracket pair}
\;\longrightarrow\;
\text{reverse the outer sequence}
\;\longrightarrow\;
\text{normalize }K<X<t.
}
\]

It is small because it acts on the finite observer boundary.  Its output is a
dualized **surface with residual**, not a reversed computation.

`ProgramSlice` already contains everything needed to ground and audit this
observer.  The remaining engineering problem is not the normalization
algorithm itself; it is choosing a certified typed role for internal cuts and
deciding how overlap holonomy is attached without losing exact process
evidence.
