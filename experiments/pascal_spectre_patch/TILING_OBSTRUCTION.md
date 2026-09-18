# Exact local obstruction for the learned Pascal-circle candidate

Authored by ChatGPT (OpenAI), through Mingli Yuan's account as proxy.
This is an external finite mathematical diagnosis, not native Adva admission.
Original contribution under Unknown v0.3. The exact input SHA-256 and all
fraction witnesses are in `evidence/obstruction.json`.

## Strong obstruction: the reflex corner cannot be completed

Let a compact Jordan tile have a piecewise smooth boundary, no cusps, and
interior corner angles `alpha_0,...,alpha_13`. At a smooth boundary point its
interior tangent cone has angle pi. Suppose one reflex corner has angle
`alpha_c = 2 pi - delta`, where

    0 < delta < min(pi, alpha_0,...,alpha_13).

Then congruent copies of this tile cannot tile the plane, even if reflections
are allowed and even if the proposed tiling is not edge-to-edge.

Proof. At this corner of one copy, all remaining tiles must fit inside the
complementary tangent wedge of angle delta. Some other copy must contain the
corner in its boundary and cover a sequence of points in that wedge approaching
the corner. Its local interior angle would be pi at a smooth edge point or one
of the alpha_i at a vertex; every possibility is strictly larger than delta.
The tangent cones would therefore overlap in positive angular measure, forcing
interior overlap near the corner.

The needed local finiteness does not add an assumption: copies of a fixed
compact tile of positive area, with disjoint interiors, that meet a fixed disk
are all contained in a larger disk of bounded radius. Comparing areas bounds
their number. A sequence approaching the corner therefore has a subsequence
covered by one fixed neighboring tile. This proves the contradiction.

For the learned candidate the exceptional vertex is p4. Approximate values,
provided only to explain the exact witness, are

    alpha_4 = 359.99690845397834 degrees,
    delta   =   0.00309154602166 degrees,
    min alpha_i = alpha_8 = 0.25642013561273 degrees.

The inequalities are certified without floating point. For each vertex write
v = p_i - p_(i-1), w = p_(i+1) - p_i, s = sign(signed polygon area),
c = s det(v,w), and d = v dot w. At p4, c<0 and d<0, and tan(delta)=c/d>0.
For each other corner:

* c<0 certifies a reflex corner, hence alpha_i>pi>delta;
* c>=0 and d>=0 certifies alpha_i>=pi/2>delta;
* c>=0 and d<0 certifies an acute corner, for which tan(alpha_i)=-c/d.

Every acute corner satisfies the strict rational inequality
`-c_i/d_i > c_4/d_4`; all other cases follow from their angle classes.
The exact fractions and decisions appear under `certificate` in the JSON
report. The public checker uses equivalent upper-half-plane determinant
comparisons so it also handles reflex complements greater than 90 degrees. This certificate is unchanged under any rigid motion, similarity,
or reflection of the tile.

## The proposed S-curve preserves this obstruction

For edge vector d_i=p_(i+1)-p_i, let J be rotation through pi/2 and replace the
edge by

    Gamma_i(t) = p_i + t d_i + epsilon_i f(t) J d_i,  0<=t<=1,
    f(t) = t^2 (1-t)^2 (2t-1).

Here f(0)=f(1)=f'(0)=f'(1)=0 and f(1-t)=-f(t). Thus each curve has the
original endpoints and endpoint tangent directions, and is invariant under the
half-turn about the midpoint (with parameter reversed). The boundary corner
angles are exactly unchanged. Whenever the modified boundary remains a simple
regular Jordan curve, the preceding impossibility theorem applies for any
amplitudes epsilon_i. The sign or smallness of epsilon_i is irrelevant to this
angle obstruction; smallness matters only for validating a simple boundary.

More generally, replacing every edge by the same normalized centrally symmetric
curve with the same dimensionless amplitude rotates all endpoint tangents by the
same angle, so also preserves the corner angles. Curves with deliberately changed
endpoint tangent directions require a new corner-angle audit.

## Scope of the local result

The four-copy curved patch has three exact shared seams and disjoint interiors.
It does not complete every vertex neighborhood. Every attempted full-plane
extension must encounter the unfillable corner. Other Pascal-circle candidates
and curves that change endpoint tangent angles are not excluded by this proof.
