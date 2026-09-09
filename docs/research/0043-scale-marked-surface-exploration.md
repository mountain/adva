# Scale-marked exploration of three coupled Legendre parameters

Date: 2026-09-09. Direction: Mingli Yuan; calculation: ChatGPT/Codex.
Status: Proposed external arithmetic calibration, based on main
`7a900db49a08276d2e76a53fdb191a295ece37ac`.

## Question and prior boundary

Can a finite surface-oriented working language support both approach to a
degeneration and exploration, while three three-input expressions remain
mutually recoverable? The terms need separate carriers before computation.

Research 0041 already connects elliptic uniformization, finite kernels and
arithmetic constructions. Research 0042 already supplies the Legendre family,
three cusps, braid/transvection conventions and discriminants. Research 0043
already distinguishes actual monodromy closure from central-sign and history
residuals. Those are antecedents, not new results of this experiment. Open
drafts #161 and #163 are not assumed merged or used as native authority here.

This example is outside the mathematical library catalog. It does not add an
admitted Pascal descendant, change the Open growth obligation, issue a Seal,
introduce native source/occurrence identities, or modify claims.toml. Its
three Python expressions are external proposals, not Rust-authorized Adva
machines. No identification of arbitrary three-hole syntax with a manifold
is claimed.

## 1. Exact objects and a recoverable coupling

Use Q(i), represented by pairs of rational numbers, with epsilon a strictly
positive rational. Define three ordered, cyclic, three-input expressions:

```
M0(epsilon, z0, z1) = epsilon * (2*z0 + z1) / 3
M1(epsilon, z1, z2) = epsilon * (2*z1 + z2) / 3
M2(epsilon, z2, z0) = epsilon * (2*z2 + z0) / 3
```

The input-use ledger is explicit in these signatures: epsilon has three
uses; each z has two uses, once weighted by two and once by one. These are
research input positions, not native linear-use permissions or semantic IDs.

Let C(z0,z1,z2)=(z1,z2,z0), L=(2I+C)/3 and lambda=epsilon Lz.
Since C^3=I,

```
(2I+C)(4I-2C+C^2) = 9I,
L^-1 = (4I-2C+C^2)/3,
z_i = (4*w_i - 2*w_next + w_nextnext)/3, w=lambda/epsilon.
```

This is a symbolic algebraic proof of recoverability over Q(i), not an
inference from 200 samples. det(L)=1/3; the reciprocal of epsilon and division
by three must exist. It is not a characteristic-three construction. Epsilon
zero is refused. Neither equality nor inversion erases the input-use ledger
or the execution word. Matrix product order is retained.

A concrete input is epsilon=1/8 and
z=(1+i, 1+2i, 2+i). Its output is

```
lambda = ((3+4i)/24, (4+5i)/24, (5+3i)/24).
```

The three syntactic triangles (epsilon,z0,z1), (epsilon,z1,z2),
(epsilon,z2,z0), if realized as a simplicial complex, form a triangulated
closed disk: four vertices, six edges, three faces, Euler characteristic one.
The central vertex has circular link. They do not form three punctured
Riemann surfaces, and this combinatorial disk is not a Calabi-Yau manifold.
This is an explicit first limit on the proposed surface interpretation.

## 2. Where Teichmuller and Calabi-Yau geometry actually enter

For each output parameter, take the smooth projective completion of

```
E_lambda: y^2 = x(x-1)(x-lambda), lambda != 0,1.
Delta = 16 lambda^2 (1-lambda)^2,
j = 256 (1-lambda+lambda^2)^3 / (lambda^2 (1-lambda)^2).
```

The factor 16 distinguishes the Weierstrass discriminant from the monic
cubic polynomial discriminant. The executable checks both formulas by an
independent cubic-coefficient calculation. Parameters are in Q(i); geometric
fibres are considered over C. Enumerating rational inputs does not enumerate
all points of an elliptic curve.

A marked elliptic curve has a period parameter tau in the upper half-plane
H and is C/(Z+tau Z). Forgetting enough marking passes to a modular quotient.
The Legendre parameter base B=P^1 minus {0,1,infinity} is the level-two
modular parameter curve, with analytic uniformization H/Gamma(2), understood
through its effective action modulo the central sign. Lambda is not tau.
Three marked factors have a product parameter domain H^3, mapping to B^3.
This is the product-family parameter domain, not the full Teichmuller space
of all complex three-tori or all Calabi-Yau threefolds.

At a parameter triple, the fibre

```
X_lambda = E_lambda0 x E_lambda1 x E_lambda2
Omega = (dx0/y0) wedge (dx1/y1) wedge (dx2/y2)
```

is a compact complex three-torus with a nowhere-zero holomorphic volume
form and a flat Kahler metric. The invariant differentials extend across
the apparent poles of these affine formulas. Thus it is Calabi-Yau under
the broad trivial-canonical/Ricci-flat convention. It is not an irreducible
SU(3)-holonomy Calabi-Yau threefold: its flat holonomy is trivial and
h^(1,0)=3. These geometric conclusions use classical complex uniformization
and the product construction; the Python program does not prove analytic
uniformization or construct a Ricci-flat metric.

Consequently the simultaneous appearance is a **parameter-space/fibre
relationship**. The two spaces are not identified, even though H^3 and each
X_lambda have the same real dimension six. The total family has complex
dimension six. Coordinate coupling through L does not make the product
geometrically nonfactorizable, supply a force, or identify the syntax disk
with the fibre. A literal three-punctured sphere itself has no Teichmuller
deformation parameter; its moduli are fixed by normalizing three points.
Variable geodesic boundary lengths would be a different problem.

Relevant existing literature explicitly studies Teichmuller and moduli spaces
of Calabi-Yau manifolds; their coexistence is not new. References below do
not establish the proposed Adva interpretation.

## 3. Approach versus exploration

A sequence converging to a point cannot be dense in a positive-dimensional
manifold: outside any neighborhood of its limit it has only finitely many
terms, leaving some open set unvisited. A finite prefix cannot certify
whole-space density either.

Instead retain two separate coordinates:

```
epsilon_n = 2^(-n-3)        # scale
z in D subset [1,2]^6      # rescaled working window in C^3
lambda = epsilon_n Lz.
```

Every real and imaginary coordinate of Lz lies in [1,2]. Hence each
|lambda_i| <= 2*sqrt(2)*epsilon_n and is nonzero with positive imaginary
part. Each finite fibre is regular, while the parameter triple approaches
(0,0,0). At lambda=0 the individual cubic has a node at (x,y)=(0,0).
The singular point of the fibre, degeneration locus of the family, and a
syntactic open hole remain different objects.

The executable uses all 64 binary coordinate corners D={1,2}^6 at scales
1/8,1/16,1/32. A Gray ordering visits adjacent corners by changing one real
coordinate at a time. It covers this finite grid, not a continuous region.
Eight fresh interior direction triples test reuse at 1/64.

One could separately prove density of nested rational grids in the rescaled
window and give each finite grid its own resource contract. No such infinite
execution is requested or run here. The rescaled window retains amplitude as
well as direction; it is not a unit tangent sphere or a constructed algebraic
blow-up. No period lift tau, loop continuation or metric traversal of H^3
is computed in this experiment.

Retaining epsilon is necessary: (epsilon,z) and (epsilon/2,2z) have identical
lambda. Forgetting scale therefore destroys recovery on the broader declared
domain. The checker retains a concrete witness of this ambiguity.

## 4. Switching requires transport of the operation

If P swaps two input positions, the corresponding operation on output
coordinates is

```
T_P = L P L^-1.
```

Swapping lambda positions directly generally gives a different answer.
The required commuting equation is T_P L = L P. It preserves the *meaning
of the declared input operation*, not the original elliptic fibre's j-values:
this operation can change the curve parameters.

The two adjacent transported swaps obey T0*T1*T0=T1*T0*T1 and T_i^2=I.
Thus this action factors through S3. The braid relation alone does not prove
faithful braiding, nontrivial twists, or a mapping-class action of the three
syntax faces. Equal resulting coordinates retain different operation words.

To keep the distinction visible, the report includes a small existing 0043
monodromy regression:

```
A=((1,2),(0,1)), B=((1,0),(-2,1)), U=((-1,2),(-2,3))
A B U = -I; A B (-U) = I; A B != B A.
```

These are cusp-loop matrix conventions, not the transported input swaps and
not three newly derived machine boundaries. Their connection to the new
input graph remains an open interpretation obligation. Old monodromy checks
are not counted as new geometric findings.

## 5. Working vocabulary and refusal conditions

No new stable language primitive is added. The minimal proposed composite
policy is `scale-marked-explore`:

| operation | input/output and obligation |
| --- | --- |
| mark | Retain nonzero scale, ordered inputs, domain, finite coverage scope and fuel. |
| couple | Apply the three fixed expressions, preserving their input-use ledger. |
| interpret | Decode with L^-1 and the retained scale; refuse zero scale. |
| switch / transport | Apply L P L^-1; retain P and its ordered word. A raw output swap is not presumed correct. |
| refine | Select a separately bounded smaller scale or finer direction grid; retain old evidence. |
| verify | Check round-trip, discriminants, intended operation transport and exact finite coverage. |

Inputs to the composite are the marked finite grid, scale, permutation words
and budget. Outputs are the exact parameter triples, discriminants, j-values,
counterexamples and finite report. Missing coverage is Unknown; repeated or
foreign coordinates are refused; singular parameters and zero scale are
refused. Reproduction expands these names to the formulas and script below.

The word's witness is the 200-state run, the new eight-point reuse and the
counterexamples. Its residuals are analytic lifting, actual program-to-surface
construction, native arithmetic admission, nontrivial braid transport,
Calabi-Yau conventions and real task usefulness. It is Proposed, not a learned
theorem or evidence of universal grammar completeness. No speedup or increased
expressive power is claimed; no costs for forming a vocabulary entry are
hidden inside the execution timing.

## 6. Execution and evidence

Run from the repository root with Python 3.11+ on Linux:

```sh
timeout 30s python3 experiments/surface_exploration/run.py /tmp/surface-evidence.json
```

No external Python packages, native build, network call or infinite search
are used. The contract was saved before implementation and execution. The
single run completed without an implementation retry:

- 200 exact parameter triples, 600 nonzero discriminant checks;
- 64/64 directions at each of three scales, plus eight fresh interior cases;
- 400 intended swap comparisons: the naive output swap disagreed 372 times;
- correct transported swaps passed, along with inverse and braid-relation checks;
- missing coverage, duplicate/foreign labels, singular parameters and scale
  loss were distinguished;
- exact JSON replay recovered all records and recomputed all 200 outputs.

The first swap counterexample has epsilon=1/8,
z=(2+i,1+i,1+i). Swapping z0,z1 requires output
((4+3i)/24,(5+3i)/24,(3+3i)/24). A naive output swap instead
gives ((3+3i)/24,(5+3i)/24,(4+3i)/24).

The script's measured costs were construction 0.867 ms, original-scope
verification 648.453 ms, eight-case reuse 59.082 ms, controls 0.580 ms,
record serialization 2.163 ms and replay 17.059 ms. Elapsed time before final
report writing was 0.729 s; outer process wall time was 0.735 s. Sampled
process high-water RSS was 13,820 KiB on Linux (about 13.50 MiB), sampled
before final report serialization/write. Maximum stored rational component
size was 77 bits; temporary integer bit maxima were not instrumented.
Authoring, research and network time were not measured. The 4096-bit check
applies to stored rational outputs, not every temporary arithmetic value.

Precise inputs, outputs, source/contract digests, controls and measurements are
in `experiments/surface_exploration/evidence.json`. Digests bind local bytes;
they do not authenticate the author or prove semantic identity. Timing fields
will vary on replay. No complete workspace or CI success is claimed.

## 7. Next smallest obligation

Choose one contract for a genuine marked path, not just parameter endpoints:
fix a base point, one oriented loop around lambda=0 and one homology basis;
bind the existing M0 transport to that path and retain its history. Only then
ask whether a proposed surface switch denotes that continuation, a coordinate
permutation, or another operation. This targets the exact missing bridge
without attempting whole-space traversal or full Calabi-Yau reconstruction.

## References

- [0041](0041-elliptic-isogeny-triadic-characteristics.md),
  [0042](0042-atiyah-legendre-triadic-crossing.md),
  [0043](0043-legendre-crossing-coherence-prism.md): existing project boundaries.
- J. S. Milne, *Modular Functions and Modular Forms*, sections 3 and 8:
  https://www.jmilne.org/math/CourseNotes/MF.pdf
- NIST DLMF, modular lambda and modular transformations:
  https://dlmf.nist.gov/23.15 and https://dlmf.nist.gov/23.18
- Dominic Joyce, *Lectures on Calabi-Yau and special Lagrangian geometry*:
  https://arxiv.org/abs/math/0108088 . Definition conventions must be stated;
  the broad product-torus convention used here is not irreducible SU(3) holonomy.
- Kefeng Liu, Xiaofeng Sun, Shing-Tung Yau, *Recent Development on the Geometry
  of the Teichmuller and Moduli Spaces of Riemann Surfaces and Polarized
  Calabi-Yau Manifolds* (2009): https://arxiv.org/abs/0912.5471 . This supplies
  established context, not a theorem identifying Adva syntax with those spaces.
