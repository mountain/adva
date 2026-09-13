# Arakelov geometry, stability, Monge–Ampère and mirror symmetry: a ladder, and its first rung built

Date: 2026-09-11. Direction and question: Mingli Yuan. Reading, model, execution
and writing: assistant (DeepSeek Harness), submitted through his account as an
authorized proxy.

Status: **research plan plus one bounded external experiment**. It introduces no
stable API, no native admission, no library admission and no Seal. Rust remains
the sole semantic authority, and nothing here changes it.

Base: `9aaba3257e21`. The bounded experiment is
[`experiments/hns_stability_chamber_roundtrip/`](../../experiments/hns_stability_chamber_roundtrip/).

## 0. Why this note exists

The question was whether Arakelov geometry and the HNS equation have a potential
connection, and whether that can be organized in an ordered way that reaches
complex Monge–Ampère and mirror symmetry. The first finding is negative and worth
recording before anything else: **neither `Arakelov` nor `HNS` occurs anywhere in
this repository.** The only `Hns` in the tree is a function name in a third-party
test fixture. So this is new ground, and no existing record can be extended to
reach it.

The second finding is that the far end of the requested ladder **is** already
occupied, and carefully:

| Existing record | What it decides |
|---|---|
| [`lattice-polar-and-mirror-boundary.md`](lattice-polar-and-mirror-boundary.md) | TO24 cannot be reflexive for any compatible full-rank lattice; "Hodge matching with full mirror symmetry" is forbidden |
| [`reflexive-lattice-gate.md`](reflexive-lattice-gate.md) and its contract | an iff criterion for the reflexive-lattice question, the minimal witness lattice and its index, and the TO24 failure read as the scale-invariant denominator pair (2,3) |
| [`cube-root-conjugation-and-polar-covariance.md`](cube-root-conjugation-and-polar-covariance.md) | involutive aspects do not identify the operations; reflexivity is a lattice property, not geometric reflection |
| [`adva-library/meaning-yau-calabi-mapping-v0.md`](../../adva-library/meaning-yau-calabi-mapping-v0.md) | a proposed mapping whose anchors are exact fractions, explicitly not verified prose |

So the ordered organization does not start from nothing: it attaches two new
rungs below an existing, executable one.

## 1. What `HNS` is taken to mean, and the fork

**"HNS equation" is not a name I can confirm.** Two readings fit the requested
destination, and they are not equivalent:

| Reading | Evidence | Its metric partner |
|---|---|---|
| **Harder–Narasimhan–Seshadri** (the HN filtration and NS-type stability) | `Gr^{HNS}` is the associated graded of the Harder–Narasimhan filtration, and appears in Hermitian–Yang–Mills contexts | the Hermitian–Yang–Mills equation (Donaldson–Uhlenbeck–Yau) |
| **k-Hessian type equations** | the top case k = n of the complex Hessian equations **is** complex Monge–Ampère | complex Monge–Ampère directly |

This note proceeds under the first reading, because under the second the rung
would coincide with the endpoint and the ladder would collapse. **The fork is
unresolved and is recorded as open.** The structure below changes only in its
middle rung if the reading is the other one.

## 2. The ladder

Each rung states its object, what exists today, whether it is executable here, and
what must be imported or refused at its seam.

| Rung | Object | Exists today | Executable here |
|---|---|---|---|
| **R0** exact arithmetic carrier | exact fields, exact rationals, matrix powers, integer data | yes, this is the repository's strength | yes |
| **R1** finite stability (the HNS rung) | a slope function and a Harder–Narasimhan filtration on a declared finite carrier | **no** | **yes, and now built** — see section 3 |
| **R2** lattice and polytope (the combinatorial mirror rung) | existence of a reflexive lattice polytope, its minimal witness lattice, its obstructions | yes, `reflexive_lattice_gate` | yes |
| **R3a** bundle metric | the Hermitian–Yang–Mills equation | no | **no**; DUY must be imported |
| **R3b** Kähler metric | **complex Monge–Ampère** | only exact algebraic shadows, in the Yau–Calabi mapping | **only as an algebraic shadow** |
| **R4** Arakelov | arithmetic intersection numbers, Green's functions, arithmetic metrics | no | intersection numbers as exact shadows; the Green's-function equation only imported or refused |
| **R5a** combinatorial mirror | Hodge-number mirror symmetry on reflexive polytopes | the criterion is at R2 | yes |
| **R5b** metric mirror | SYZ and special Lagrangian fibrations | no | **no — the ladder ends in a refusal** |

### Two collapses this ladder must forbid

These are the two places where the ladder would otherwise short-circuit, and both
are classical errors:

1. **Hermitian–Yang–Mills is not complex Monge–Ampère.** For a line bundle the
   HYM equation `F_h = lambda omega` becomes *linear* in the potential once
   `h = h_0 exp(-phi)`. Complex Monge–Ampère is the **Kähler–Einstein /
   Calabi–Yau** rung: `Ric(omega) = lambda omega`, that is
   `(omega + i dd^c phi)^n = e^f omega^n`, which Yau's theorem solves. The ladder
   therefore has **two** metric rungs, **R3a** with slope stability as its
   partner and **R3b** with K-stability, and slope stability is not K-stability.
2. **Combinatorial mirror is not metric mirror.** The reflexive-lattice
   criterion decides a Hodge-number statement. SYZ is a different and far less
   settled level, and this repository already forbids treating Hodge matching as
   full mirror symmetry.

## 3. The first rung, built and run

R1 was the only rung with nothing in it, and the only one executable with exact
arithmetic, so it is the rung to build first.

### The model

Carrier: an **injective representation of the A2 quiver** `(1 -> 2)` over a prime
field, realized as a subspace pair `V1 subset V2` inside `F_p^d`. Every object,
subobject and quotient is a finite set of vectors, and every slope is an exact
`Fraction`. Two things are declared at the outset:

- an injective A2 representation is classified by its dimension pair, so the
  **isomorphism class is the dimension vector**; and
- the slope is `mu(U) = (theta1 dim U1 + theta2 dim U2) / (dim U1 + dim U2)` for
  an exact integer parameter `theta = (theta1, theta2)`.

**Forward**: at a parameter, compute the Harder–Narasimhan filtration by the
iterated maximal-slope rule. **Backward**: from the graded data alone, recover
what produced it — both the object and the parameter.

### Results

The run covers both prime fields, ambient dimensions two and three, every
subspace and every subobject pair, eleven parameters in the declared sweep, and
two degenerate parameters. **18 isomorphism classes, 256 filtrations, 12,300
assertions, 0.9 seconds.**

| What was checked | Result |
|---|---|
| The filtration exists and terminates | yes, at every instance |
| Successive quotient slopes strictly decrease | yes, as exact rationals |
| Each step is the maximal-slope subobject | yes, and the maximal-slope class is closed under sum, so its sum is the maximal member |
| Exact slope conservation, `sum_i (dim_i/dim E) mu_i = mu(E)` | holds exactly at every instance |
| Degenerate parameter `theta = (1,1)` | one piece, the object is semistable — 36 instances, so the test is not vacuous in that direction |
| **Object direction** | **injective**: for a fixed parameter the graded data determines the isomorphism class, verified over all 18 classes |
| **Parameter direction** | **many-to-one**: the graded data is produced by a set of parameters, not by one |

The parameter direction is where the experiment has real content:

- **Witness of parameter forgetting.** Over `F_2`, the object of dimension pair
  `(1,1)` has graded data `[[[1,1], 1/2]]` at `theta = (1,0)` **and** at
  `theta = (2,-1)`. Two different stability parameters, one graded shadow.
  24 such witnesses were found, all non-degenerate.
- **Chamber sizes.** Per field, 72 distinct graded data arise from 11 parameters
  per object, and the largest chamber holds 6 of them.
- **A full chamber partition, retained.** For one object the eleven parameters
  fall into nine chambers, including a genuine chamber of two:
  `{(1,0), (2,-1)}` and another `{(1,1), (3,-1)}`.
- **Walls exist inside the declared grid.** 8 adjacent parameter pairs in the
  sweep change the graded data, so the backward image is a proper part of the
  grid and the chamber structure is not trivial.

### One spurious result, found and removed rather than kept

The first version of the model enumerated carriers as **embeddings**, so the same
abstract object appeared once per embedding, and it reported an "object
forgetting" witness: dimension pair `(1,1)` in ambient dimension two and in
ambient dimension three sharing one graded data. Those are the same isomorphism
class. The direction is now deduplicated by isomorphism class, and the object
direction is asserted injective instead. **The claim was wrong, and the control
that exposed it is the one that matters**: a finite model that counts embeddings
as objects will manufacture a forgetting that does not exist.

## 4. Conclusions

1. **The forward direction is canonical.** The Harder–Narasimhan filtration exists,
   is unique, and is computed exactly; its graded quotient slopes strictly
   decrease, and its slope weight is conserved exactly. This is the finite,
   checkable form of the HNS rung.
2. **Inside the injective model the backward direction loses only the
   parameter.** What the graded data forgets is **which member of the chamber one
   was in**, and the residual is the chamber partition and its walls.
   **Correction, 2026-09-11:** the object half of this claim does **not** survive
   dropping injectivity, and section 7 reports the test that refutes it. The
   original wording stands in the commit `c67c33b`; section 7 gives the corrected
   scope. The correction is the point rather than an erratum, because section 6
   named this test in advance.
3. **That asymmetry is the shape of the ladder.** A combinatorial stability rung
   is lossless toward the object and lossy toward the parameter. So the ladder's
   seams are not about recovering objects from shadows; they are about **which
   parameter region a shadow belongs to**, which is exactly the structure a
   stability manifold has.
4. **The ladder reaches complex Monge–Ampère only through R3b, and only by
   import.** Nothing here computes a metric, a curvature, or a solution of any
   PDE, and section 2 fixes the two collapses that would make it look otherwise.
5. **The honest endpoint is a refusal.** R5b is not reachable in this repository,
   and the value of the organization is that it says so in the same place where it
   says what is reachable.

## 5. What this does not establish

- **No Arakelov content.** No height, no Green's function, no arithmetic
  intersection number, no arithmetic surface. The word appears only in the plan.
- **No Monge–Ampère content.** No metric, no Kähler class, no curvature, no PDE,
  no numerical solution, and no algebraic shadow is computed either.
- **No mirror symmetry.** No polytope is identified with this model, and no Hodge
  number is computed here.
- **Characteristic p only.** The model is over `F_2` and `F_3`. Nothing is claimed
  for characteristic zero, for coherent sheaves, or for an arithmetic base.
- **Injective representations only.** Non-injective A2 representations are
  excluded, and that exclusion is exactly where the object direction might stop
  being injective — see section 6.
- **A finite parameter grid.** Walls are detected only inside the eleven declared
  parameters; the real walls are not located.
- No native Rust witness, no claim beyond the bounded entry registered for this
  experiment, no library admission and no Seal.

## 6. The next minimum step that was named in advance, and then taken

The model's one structural simplification is injectivity. For a non-injective A2
representation the isomorphism class is `(dim V1, dim V2, rank of the arrow)` —
three numbers, not two — while the graded data still records only dimension pairs
and slopes. **So the object direction may stop being injective exactly when the
arrow fails to be injective, and that is where a genuine object forgetting would
live.** Stating and testing that is the sharpest next experiment this plan
produces: it is finite, exact, and it decides whether the asymmetry of section 4
is a property of stability theory or an artifact of the injective model.

**This was tested, and the answer is that the asymmetry is an artefact of the
injective model.** Section 7 reports it.

Two further steps follow it: refine the parameter sweep to locate the walls
exactly rather than between adjacent grid points, and ask whether the chamber data
can be fed to the reflexive-lattice criterion at R2 — which is seam S1 and the
only place where this ladder could connect the stability rung to the mirror rung
with a checkable statement rather than an analogy.

## 7. The injective-model claim, tested and refuted

Section 6 said the object direction might stop being injective exactly when the
arrow may fold, and that this would decide whether the asymmetry of section 4 is a
property of stability theory or an artefact of the injective model. Mingli Yuan
stated the answer as a claim on 2026-09-11: **it is an artefact of the injective
model.** The claim was tested rather than accepted, and it holds.

### The model, widened

`experiments/hns_object_forgetting/` drops injectivity. The isomorphism class is
now the triple `(dim V1, dim V2, rank of the arrow)`, one canonical representative
per class, over `F_2` and `F_3` with total dimension at most four, the same eleven
parameters, and every subspace pair `(U1, U2)` with `phi(U1) subset U2`. Forward and
backward are the same as before, with one addition: each graded piece now carries
its own rank, so two keys can be compared — dimension pairs with slopes, and
dimension pairs with slopes plus the rank of the piece.

### Result

38 objects, 429 filtrations, 13,200 assertions, 0.6 seconds.

| Key | Distinct shadows per field | Colliding shadows | Most classes on one shadow |
|---|---:|---:|---:|
| dimension pairs and slopes | 130 | **72** | 3 |
| plus the rank of the piece | 137 | **60** | 3 |

**The refuting witness, and it is the simplest one available.** Over `F_2` at the
degenerate parameter `theta = (1,1)`, the two classes `(1,1,0)` and `(1,1,1)` share
one shadow, `[[[1,1], 1]]`. The first is the zero arrow and the second is an
isomorphism. Both are semistable there, so both filtrations are trivial and the
shadow is the object's dimension vector with its slope. In the injective model the
rank was pinned to `dim V1`, which is exactly why the same key was injective there.

**And recording the rank does not repair it.** The rank-including key raises the
number of distinct shadows from 130 to 137 and lowers collisions from 72 to 60, but
60 remain, still with up to three classes on one shadow. The surviving witness is
the same pair at `theta = (0,1)`, shadow `[[[0,1], 1, 0], [[1,0], 0, 0]]`: there the
filtration itself splits off `(0, V2)` of slope 1 and leaves `(V1, 0)`, whose arrow
is zero for both objects. So the loss is not an omitted coordinate that a better key
would supply — **the filtration annihilates the rank difference**, and no per-piece
bookkeeping recovers it.

**The earlier result is recovered where it should be.** Restricting to `r = dim V1`
reproduces the section-3 chamber structure, including the two-parameter chamber
`{(1,0), (2,-1)}`, so the new model contains the old one rather than replacing it.

### What this changes

Section 4's second conclusion is now scoped. The correct statement is:

- the **parameter** direction is many-to-one in both models, and that asymmetry is
  not an artefact;
- the **object** direction is injective only while the arrow is injective, and in
  general the graded data forgets the **rank**, in the strong sense that the
  filtration destroys it rather than merely omitting it.

So the finite stability rung of section 2 is lossy in **both** directions once
injectivity is dropped. That is the honest shape of R1, and it is a better result
than the one section 4 first reported: the run produced a counterexample to its own
author's earlier conclusion, which is what section 6 was for.

### One further error, of the same family, recorded

The first version of this widened model compared a key that I described as the
quotient rank but computed as the rank of `E / F_i`, which is zero for the last
piece of every object — so it agreed across the very pair it was meant to separate,
and the experiment briefly reported no separation at all. The key is now the rank of
the graded piece `F_i / F_{i-1}` itself, computed from `phi(U1_i)` and the previous
accumulated subobject. Two errors in two rounds, and both were a quantity that was
not the one its name said: the first counted embeddings as objects, the second
counted a different quotient's rank. Each was caught by comparison against an
expectation the model could not satisfy, which is the only reason they are visible.

### What section 7 does not establish

- No characteristic-zero statement. The counterexamples live over `F_2` at declared
  parameters inside a finite range.
- Nothing about whether the forgotten rank corresponds to an extension class in a
  richer category. That is the natural question this raises, and it is not answered
  here. Section 8 takes it up, and answers it in the finite model.

## 8. Is the forgotten object an extension class, or a coordinate?

The question section 7 leaves is precise: the rank that the filtration destroys might
be a **coordinate** that better per-piece bookkeeping would record, or it might be
**extension data** that no per-piece key can carry. The two have different
consequences, and one experiment separates them.

**The key used in section 7 was already the strongest piece-level key that exists.**
For an `A2` representation the isomorphism class of an object is the triple
`(dim V1, dim V2, rank of the arrow)`. Section 7's key recorded, for each graded
piece, its dimension pair and its own arrow rank — and that is exactly the piece's
complete isomorphism type, not a partial shadow of it. So the 60 surviving collisions
were never going to be repaired by recording more about the pieces, because there was
nothing more about the pieces to record. This is a statement about the key, and it is
the first thing the new experiment checks: the same key, recomputed independently,
finds the same 137 distinct shadows per field and the same 60 colliding shadows,
verified at run time against the sibling evidence pinned by digest (`09280cf0…`). A
disagreement there would have meant one of the two keys was not what it claimed to be.

**The witness, and it is stronger than a shared shadow.** Over `F_2` at
`theta = (0,1)` the classes `(1,1,0)` and `(1,1,1)` have graded pieces

```
(1,1,0):  [(0,1) slope 1 rank 0]  then  [(1,0) slope 0 rank 0]
(1,1,1):  [(0,1) slope 1 rank 0]  then  [(1,0) slope 0 rank 0]
```

which are the same two objects in the same order, namely `S2` followed by `S1`. The
rank-0 object is `S1 ⊕ S2` and the rank-1 object is the one whose arrow is an
isomorphism. They are not isomorphic. **So the pieces agree as objects and the objects
still differ** — which is what makes this extension data rather than a forgotten
coordinate: no function of the pieces can separate two objects whose pieces are
identical.

**And the difference is a named element of `Ext^1`.** The new experiment computes
`Ext^1` two independent ways and checks that they agree on all nine ordered pairs of
indecomposables over both fields:

- by brute force, enumerating isomorphism classes of middle terms of
  `0 → N → E → M → 0`, which is what `Ext^1` classifies and which assumes no formula;
- by the hereditary Euler form, `dim Ext^1(M,N) = dim Hom(M,N) − <dim M, dim N>`, with
  `dim Hom` itself obtained by enumerating every commuting pair of linear maps.

Exactly one pair has non-zero `Ext^1`, and it is the one the witness needs:

| quotient `M` | subobject `N` | `dim Hom` | Euler pairing | `dim Ext^1` | middle terms |
|---|---|---:|---:|---:|---|
| `S1` | `S2` | 0 | −1 | **1** | `(1,1,0)`, `(1,1,1)` |
| `S2` | `S1` | 0 | 0 | 0 | `(1,1,0)` only |

So the non-split extension exists only in the direction of the `A2` arrow, the two
middle terms of `Ext^1(S1, S2)` are exactly the two objects of the witness, and
`(1,1,0)` and `(1,1,1)` are the split and the non-split extension of the same pieces.
The reversed ordering has `Ext^1 = 0` and only the split middle term, which the same
run checks. **The thing the graded shadow forgets is the extension class, and in this
model it can be computed rather than merely named.**

**Two further checks on why the shadow is structurally blind.** First, every
isomorphism class with a fixed dimension vector has the same slope, since the slope is
a function of the dimension vector alone; the run verifies this for every pair in the
range. A quantity that is constant on all the classes a collision lumps together
cannot detect their difference, whatever else it is combined with. Second, every
collision found is the *whole* isomorphism-class set of a single dimension vector, and
its size is `min(d1,d2) + 1` — exactly the number of possible gluing ranks, that is, of
choosing how many `S1–S2` pairs are glued into `P1`. At the semistable parameter
`(1,1)` the filtration is trivial and the single piece is the object itself, so the
weakest key hides all `min(d1,d2)+1` classes while the strongest key separates them
again; the run checks both sides of that.

**The residual of `R1` therefore has a name.** Section 3 called the `R2 → R3` seam `S1`
and could only say that chamber data stops short of the metric rung. What this round
adds is a definite statement about the backward map at `R1`: its residual is the
extension class, it is not piece-level data, and the reason section 6's aspiration —
refine the parameter sweep until the shadow becomes injective — is unsatisfiable is
that the collision is not a resolution problem. This is the precise finite form of the
project's own line that a shadow is not the word it came from.

**An error in this round, recorded.** The first run of the new experiment declared a
seven-parameter sweep where the previous experiment used eleven, and reported 36
collisions against the sibling's 60. The mismatch became visible only because the
sibling's own counts were re-derived: its "137 distinct shadows" was more than the 19
classes times 7 parameters I had assumed, which is impossible and therefore meant the
sweep, not the key, was wrong. With the sweep matched, the two runs agree exactly on
both counts. The wrong reading is recorded rather than quietly replaced because it is
the third error of this series found by comparing a number against an expectation the
model could not satisfy.

### What section 8 does not establish

- `A2` is hereditary and of finite representation type, with exactly three
  indecomposables. So `Ext^2 = 0` here, every extension is assembled from
  one-dimensional `Ext^1` between simples, and "one non-split class up to isomorphism"
  is a consequence of a one-dimensional `Ext^1` over a finite field rather than a
  general fact. A coherent-sheaf or Higgs category has non-hereditary, higher, and
  longer-extension phenomena that this model cannot reach.
- The counts are finite-field counts. Over `C` the middle terms of a non-split
  extension are not a finite set, and `min(d1,d2)+1` has no characteristic-zero
  counterpart in this form.
- `Ext^1` is verified by enumeration only for the nine ordered pairs of
  indecomposables with dimensions at most `(2,2)`, over `F_2` and `F_3`. The Euler-form
  route agrees there; that agreement is a check on this model, not a derivation of the
  Euler-form identity.
- Nothing about whether the residual admits a *canonical* representative, or whether
  an extension class is the right invariant in a category whose pieces themselves
  deform. That is now the next question rather than this one.
- No metric, Arakelov, Monge–Ampère or mirror content, exactly as in section 5.

## 9. Where the walls are, and what the backward fibre really is

Section 6 named two further steps and left both open. One bounded run takes them
up: [`experiments/hns_wall_localization/`](../../experiments/hns_wall_localization/),
under the contract frozen in that directory.

**The interface is the frozen model, re-run.** This round imports the sibling
model rather than reimplementing it and reproduces its declared counts at run
time: 38 objects, 429 filtrations, 130 distinct graded data per field, 72
colliding graded data, with `experiments/hns_object_forgetting/evidence.json`
unchanged at `09280cf0…`.

**The wall set is one line.** For this model's slope the exact identity is

\[
\mu_e(\theta) = \mu_d(\theta) \iff (e_1 d_2 - e_2 d_1)(\theta_1 - \theta_2) = 0 .
\]

Checked against the exact Fractions for every admissible dimension-vector pair at
all seventeen parameters — the declared eleven plus six off-grid — it has **0
mismatches**. So a genuine wall exists only at `theta_1 = theta_2`: the primitive
wall directions are exactly `(1, -1)` and `(-1, 1)`, and the rest are
*identically tied*, 7 pairs whose slopes agree at every parameter against 59
genuine wall pairs. **This model's stability parameter space has two chambers and
one wall.**

**Section 4's chamber reading is refuted, and the residual is larger than it
said.** The nine groups section 3 reports are not chambers: the graded data
records slopes as exact rationals, and those move continuously inside a cell.
Three claims are separated and decided:

| Claim | Outcome |
|---|---|
| a cell determines the filtration type | holds |
| the graded data is constant on a cell | **refuted**: 2080 of the 5168 class-parameter pairs are two parameters in one cell with different graded data |
| the fibre description: the key is equal exactly when the filtration type is equal and `theta - theta'` pairs to zero with every piece dimension | holds, 0 mismatches |

The simplest witness is over `F_2`: the class `(0,1,0)` at `theta = (1,-1)` and at
`theta = (1,0)` lies in the same cell, with graded data `[[(0,1), -1]]` and
`[[(0,1), 0]]`. What the backward map forgets is therefore **not only which
chamber one was in**; inside one chamber it still forgets the slope values, and
the fibre is the cell intersected with the level set of the piece slopes. A fibre
can even cross the wall: 92 pairs of parameters in different cells share one
graded data, and every one of them is an object whose filtration is trivial at
both parameters, where there is no order for the wall to change.

**Seam S1 is refused, with reasons.** Four natural constructions were attempted
and none reached the R2 criterion as a canonical polytope: the half-plane
intersection of the wall normals is an unbounded strip, since two opposite
normals do not positively span the plane; the hull of the wall normals is a
segment and not full dimensional; the weight polytope `conv(d_1 - d_2, d_1 + d_2)`
has the origin outside; and the hull of the declared grid parameters is decided —
it **fails** the criterion with the nonintegral pairing `1/5` — but is refused as
non-canonical, the grid being a declared finite sample rather than a consequence
of the stability structure. The criterion itself was validated on five fixtures
before it was applied: the square, the reflexive triangle, twice the square and
the halves triangle pass, the halves triangle passing although one of its
vertices is not integral, its witness lattice being the Z-span of `(1,0)`, `(0,1)`
and `(-1/2,-1/2)`, so the criterion is not the integrality of the vertices; and
the thirds triangle fails with the pairing `-2/3`.

**What section 9 does not establish.** The single wall is a property of *this*
slope convention on a rank-two dimension-vector space: with two parameters a wall
is a line, so two half-planes are all the chambers there can be. A quiver with
more vertices has a higher-dimensional parameter space where walls are genuine
hyperplanes, and nothing here bounds that case. The statements are over `F_2` and
`F_3`, total dimension at most four, at the declared parameters. The refusal
concerns four constructions, not the seam: another justified construction could
still exist.

**Two accounting errors were caught by the interface check and are recorded.**
Reproducing the sibling's declared counts first disagreed with them — 440
filtrations against 429, and 36 colliding graded data against 72 — because the
sibling's own regression block re-runs one injective class over the sweep, and
because its collision count is per field while the re-run had merged the fields.
Neither disagreement was adjusted away: matching them forced the accounting to be
exact, and the matched counts are what the interface check now asserts.
