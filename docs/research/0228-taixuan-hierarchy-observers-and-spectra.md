# Research 0228: A Taixuan address hierarchy, its observers, and its spectra

Status: executed external finite calibration, 2026-09-24. Original mathematical
presentation and implementation by Codex (OpenAI), contributed under Unknown
v0.3 through Mingli Yuan's account as an authorized proxy. Account ownership is
not authorship, review, endorsement, or a correctness guarantee.

The two-level four-coordinate address has 6,561 points and retains 81 coarse
cells exactly. Its block address does **not** determine its next block under
unit translation. The smallest invariant refinement under all four positive
unit translations has 6,561 classes. The same 6,561 labels also support two
different Fourier analyses, depending on their declared addition and adjacency.
These are finite results, not a four-dimensional aperiodic monotile.

## 1. Inputs and the question

The question follows [0214](0214-what-a-four-trit-address-carries-and-no-shift-pairs-it.md)
and the scoped [Yi--Taixuan--Weishi packet](../../knowledge/packages/yi-taixuan-weishi-v1/materials/README.md).
The descent criterion already appears in
[0036](0036-triangular-symbolic-interpretation-learning-calculus.md): an observation
must retain every distinction needed by its declared subsequent operations.
This note supplies a finite calibration, not a new definition of that criterion.

Qiong (窮), the user's specified head, is ordinal 69 with one-based address
3223 and zero-based address 2112. The address is independently visible in the
[volume-five heading](https://zh.wikisource.org/w/index.php?title=集註太玄經/卷五&oldid=1529430).
The earlier conversational token `316` was clarified to mean this head; it is
not used as a count, ordinal, or exponent. No verse or commentary is an axiom
of the experiment. Interpreting four symbolic places as four geometric
coordinates is an additional model choice, not a historical attribution.

The [contract](../../experiments/taixuan_hierarchy_spectrum_v1/contract.json)
was fixed before execution. It pins the prior research and dependency inputs,
declares the full finite family and four negative controls, and preserves the
Open library growth obligation. The experiment creates no native identities,
Rust operations, physical metric, forecast, or knowledge-exchange receipt. The
earlier paused Lorentzian files and the unexecuted observer-dynamics draft are
untouched.

## 2. Two meanings of 9^4

Write X = {0,1,2}^4 and Z = {0,...,8}^4. The map

    e(a,b)_i = 3 a_i + b_i

is a bijection X x X -> Z. Integer division and remainder give its inverse.
Thus |Z| = 9^4 = 81^2 = 6,561, with 81 points in each fixed-a fibre.

There are two interpretations of this same set bijection:

| Interpretation | First address a | Second address b |
| --- | --- | --- |
| Nested spatial addresses | coarse cell | child inside that cell |
| Ordered state relations | source state | target state |

These interpretations are not identified by counting. In the second reading,
a kernel K(b,a) has 6,561 entries, but its admissibility, weights, composition,
and learning rule remain to be supplied. A deterministic transition has only
one selected target per source; it does not permit every pair by definition.
On functions over X, the matrix units E_(b,a) satisfy
E_(b,a) E_(d,c) = delta_(a,d) E_(b,c). This elementary operator interpretation
does not turn the relation labels into geometric coordinates or a learned model.

For the first reading, Qiong has a = (2,1,1,2). Its children are exactly

    {6,7,8} x {3,4,5} x {3,4,5} x {6,7,8}.

The checker exhausts the entire encoding and this 81-point fibre. It verifies
the arithmetic ordinal 1 + 27*2 + 9*1 + 3*1 + 2 = 69; the historical naming
remains the cited input rather than an arithmetic consequence.

## 3. Recovering a parent is different from predicting it

Declare periodic boundary conditions for this **control model**: Z is the group
(Z/9Z)^4 and T_i adds one in coordinate i. The periodic boundary is chosen for
an exactly solvable comparison and does not claim to model a nonperiodic tile.

Two 81-valued observations are available:

    q_block(z) = floor(z/3), componentwise
    q_phase(z) = z mod 3, componentwise.

Exhaustion of all 26,244 point/generator pairs verifies

    q_phase(T_i z) = q_phase(z) + e_i mod 3
    q_block(T_i^3 z) = q_block(z) + e_i mod 3.

But q_block has no autonomous one-step update at all, even one different from
ordinary coarse translation. A witness inside Qiong is:

| Fine point | Its block | After T_0 | New block |
| --- | --- | --- | --- |
| (6,3,3,6) | (2,1,1,2) | (7,3,3,6) | (2,1,1,2) |
| (8,3,3,6) | (2,1,1,2) | (0,3,3,6) | (0,1,1,2) |

Equal observed inputs have different observed successors. The zero in the second
row is the declared periodic wrap. More generally a cell-interior point and a
cell-boundary point already give the obstruction on an unbounded integer grid.
There are 17,496 failures of the *particular* equation q_block T_i = T_i q_block
in the finite family. The two-point witness, rather than that count alone,
refutes every proposed deterministic update on block labels for T_0.

Starting with the block partition, repeatedly give a point the signature

    (current_class(z), current_class(T_0 z), ..., current_class(T_3 z)).

The measured class counts are

    81 -> 1296 -> 6561 -> stable.

Why is this the smallest invariant refinement? Any invariant partition finer
than the initial one must distinguish each signature: otherwise equal classes
would acquire unequal successor classes. Induction preserves that obligation
at every round; at stability the signature partition itself respects all four
generators. This proves the minimality statement for the executed finite family.
It does not say that every useful coarse model must recover every fine state.
It says that this initial observation, these exact translations, and exact
deterministic closure together require it.

Geometric subdivision and translation phase also require different maps at
greater depth. On a fixed unit box, dividing an integer address by three and
rounding down forgets the latest spatial subdivision. For the inverse system
of translation phases Z/3^nZ, the compatible map is **reduction modulo 3^n**.
The latter gives a 3-adic phase coordinate in the limit, not an automatically
constructed Euclidean or Lorentzian space. Confusing these two projections would
silently change the observer and invalidate the translation law.

## 4. Coarse fields and retained detail

For a real field f on Z, define block averaging and constant lifting by

    R f(a) = (1/81) sum_b f(3a+b)
    I g(3a+b) = g(a).

Then R I = identity and P = I R is the orthogonal projection onto block-constant
fields under the ordinary finite sum inner product. With r = f - P f,

    f = I R f + r,       R r = 0,
    ||f||^2 = 81 ||R f||^2 + ||r||^2.

The dimensions are 81 coarse plus 6,480 residual. These formulas follow directly
by summing within fibres; the cross term vanishes because every residual fibre
sum is zero. They preserve coarse data while allowing fine reconstruction.

The executed synthetic field is

    f(z) = sum_i (i+1)(z_i-4) + (z_0 mod 3 - 1)(z_1 mod 3 - 1).

Exact rational arithmetic gives:

| Quantity | Result |
| --- | ---: |
| Total sum of squares | 1,315,116 |
| Lifted coarse sum of squares | 1,180,980 |
| Residual sum of squares | 134,136 |
| Qiong block mean | 15 |
| Reconstruction and every residual fibre sum | exact |

This is an original artificial fixture with no physical units. It contains no
weather observations or learned forecasts. Removing its detail fails lossless
reconstruction, as the negative control requires. A smaller array is not by
itself a sufficient dynamical state.

## 5. The same labels have different spectra

The bijection z = 3a+b is not an additive group isomorphism between
(Z/9Z)^4 and (Z/3Z)^8. In one coordinate, 2+1 is 3 in Z/9Z, whereas digitwise
ternary addition of (0,2) and (0,1) is (0,0). The first group has exponent 9;
every nonzero element of the second has order 3.

For the explicitly declared positive, unnormalized nearest-neighbour graph
Laplacians, tensor Fourier characters give:

| Carrier and adjacency | Eigenvalues | Measured distinct values |
| --- | --- | ---: |
| Four cyclic coordinates of length 9 | sum_(i=0..3) [2 - 2 cos(2 pi k_i/9)] | 65 |
| Eight independent cyclic coordinates of length 3 | 3 j, with multiplicity C(8,j) 2^j | 9 |

Both function spaces have dimension 6,561 and a single zero mode. Their graph
degrees are respectively 8 and 16; their unnormalized traces are 52,488 and
104,976. These are different declared operators, not a claim that one spectrum
is better. A new weighting or normalization would need its own comparison.

The exact checker represents ninth roots in Z[t]/(t^6+t^3+1), verifies all
one-coordinate Fourier inner products and Laplacian eigenvector entries for
lengths 9 and 3, and enumerates all frequency tuples for both carriers. Tensor
factorization turns the one-coordinate orthogonality sums into the full Gram
identity: the inner product is the product of the four (or eight) finite sums.
Thus these characters form complete bases for the stated finite spaces. The
eigenvalue multiplicities are retained as exact cyclotomic coefficient tuples;
decimal values are display approximations only.

A separate complex-valued separable DFT and inverse on the fixed field give
relative maximum reconstruction error 8.07e-15 and relative Parseval error
1.06e-15, below the declared 1e-10 tolerance. Numerical replay supplements the
exact factor checks rather than proving an infinite spectral theorem.

For the phase observation the character embedding is also explicit:

    exp(2 pi i k . (z mod 3)/3) = exp(2 pi i (3k) . z/9).

It selects the 81 frequencies whose four indices are divisible by three. Block
averaging selects a different 81-dimensional space. Their equal ranks are not
a reason to substitute one observation for the other.

## 6. What the new three-dimensional result supplies

Tsiokos's [Chair44 preprint, v1, 16 September 2026](https://arxiv.org/abs/2609.19214v1)
reports a connected polyhedral three-dimensional monotile, with reflections
allowed, whose every tiling has finite symmetry group. Its geometric rules
enforce a unique hierarchy with inflation factor two. Section 8.2 restricts its
pure-point diffraction conclusion to the specified substitution fixed-point
label classes; passage to every legal tiling remains an explicit hull question.
Section 10 leaves extension of the mechanism to other dimensions as a question.
We read this as an external proof report and have not replayed its Lean or census.

[Goodman-Strauss, v1, 21 September 2026](https://arxiv.org/abs/2609.24779v1)
gives a simpler presentation of the construction, and
[Flicker, v1, 20 September 2026](https://arxiv.org/abs/2609.23783v1)
studies alternative face-matching rules. No paper code, diagrams, tile-coordinate
data, or transcription is incorporated here. These papers guide the question;
they are not dependencies of the finite arithmetic checker.

The four-coordinate ternary hierarchy has scale factor three, so it is a new
candidate language rather than the binary Chair44 substitution relabelled. If
one four-dimensional tile admits an exact inflation by three into congruent
unscaled copies, volume alone requires 3^4 = 81 children, and two inflations
require 6,561. This necessary count neither constructs the subdivision nor
proves that local geometry forces it. The 81 address symbols do not establish
81 tile types, let alone one geometric prototile.

## 7. A conditional route to a four-dimensional monotile

Here is the proof interface a future geometric construction would have to meet.
It is a conditional mathematical argument, not an executed existence result.

1. Specify a compact four-dimensional prototile Q and permitted congruences,
   including whether reflections are allowed. If a connected 4-ball is wanted,
   that topology is a separate obligation.
2. Prove there exists an entire-space tiling, without overlaps or gaps.
3. Prove every legal geometric tiling is registered so its translation periods
   belong to a fixed full-rank lattice, written Z^4 after choosing units.
4. Prove local geometry forces a unique parent decomposition and the parent
   obeys the same rules after scale change. This must cover all legal tilings,
   not just tilings generated by one substitution seed.
5. Extract coherent, intrinsic phases alpha_n(T) in (Z/3^nZ)^4 for every n,
   satisfying alpha_n(T+p) = alpha_n(T)+p modulo 3^n, with the same declared
   sign convention throughout.

If p is a period, T+p=T, so p belongs to 3^n Z^4 for every n. The intersection
of those lattices is {0}: any nonzero integer component fails divisibility by
a sufficiently large power of three. Therefore p=0. This proves absence of
translation periods **under the five hypotheses**.

To get the strong form excluding every infinite-order Euclidean symmetry, also
prove that the linear parts of all tiling symmetries lie in a finite group G.
The map from a symmetry to its linear part then has trivial kernel, since that
kernel consists of translation symmetries. Hence the symmetry group injects
into finite G and is finite. The phase argument alone does not establish this
extra hypothesis or eliminate every possible screw symmetry.

Two countermodels prevent shortcuts. A uniform four-dimensional cubical tiling
can be assigned an arbitrarily deep *chosen* ternary hierarchy and remains
periodic: that chosen hierarchy is not intrinsic to the undecorated tiling.
Also, if Q_3 tiles three-space, Q_3 x [0,1] admits a tiling formed by repeating
the same spatial tiling at every integer fourth coordinate. That tiling has
period (0,0,0,1), irrespective of spatial aperiodicity. Simple extrusion cannot
supply the required four-dimensional monotile property.

Even a successful Euclidean construction would not yet pick out physical time,
causality, a Lorentzian metric, a wave operator, or a weather evolution law.
Diffraction of a point set, the translation spectrum of a tiling hull, and the
spectrum of a chosen field operator are separate objects with separate inputs.

## 8. Evidence, limitations, and the next finite question

The [checker](../../experiments/taixuan_hierarchy_spectrum_v1/check.py) and
[retained evidence](../../experiments/taixuan_hierarchy_spectrum_v1/evidence.json)
report Pass for the fixed family and reject all four declared false controls.
The first run charged 544,743 finite cases/transform multiplications, took
approximately 0.59 seconds of worker wall time, and used about 30 MiB peak RSS.
These counts are not machine instruction counts. The supervisor enforces a
30-second wall limit, 25-second CPU limit, 512 MiB address-space cap, two-million
charged-case cap, one-MiB output cap, and at most two launches with no automatic
retry. Resource exhaustion would produce Unknown. Exact arithmetic and written
proofs remain open to review; neither Python nor this note is native authority.

The useful new constraint is operational: keep both the geometric block reading
and its residual, and specify a translation-compatible phase reading separately
when analysing hierarchical symmetry. A future finite tile trial should first
name its carrier, contact alphabet, allowed poses, parent recognition radius,
and coarsening law. Its first question should be whether every admissible local
configuration decodes consistently and whether decoded contacts obey the same
law. Even success would leave geometric realization, entire-space existence,
and the universal quantifier over tilings to prove.

No tile search is silently launched by this note. A successor trial needs its
own finite contract. No native library entry, source migration, or Seal is made;
the pinned Pascal-rooted growth obligation remains Open.
