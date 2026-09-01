# Finite Circular Overlap Transport and Holonomy

Status: bounded proposal with a pure-Python calibration following
[`0043-legendre-crossing-coherence-prism.md`](0043-legendre-crossing-coherence-prism.md),
[`0053-finite-causal-presented-evidence.md`](0053-finite-causal-presented-evidence.md),
[`0054-finite-linear-synchronized-evidence-tensor.md`](0054-finite-linear-synchronized-evidence-tensor.md),
[`0057-typed-vacua-constant-boundary-braids.md`](0057-typed-vacua-constant-boundary-braids.md),
and
[`0067-circular-three-form-interface-duality.md`](0067-circular-three-form-interface-duality.md).

The executable V0 fixture is
[`test_circular_overlap_transport.py`][fixture].

[fixture]: ../../tests/python/test_circular_overlap_transport.py

Note 0067 found a circle in the incidence nerve of the three opposite-pair
readings.  This note performs the next local experiment:

> Put a finite typed fibre on each chart, a checked bijective comparison on
> each pairwise overlap, and compose the comparisons around the nerve.  A
> global section exists exactly at a fixed point of the resulting holonomy.

This produces a sharper result than the provisional flat/residual/no-go
trichotomy.  There are four distinct outcomes:

1. identity holonomy: every starting phase glues;
2. nonidentity holonomy with fixed points: some phases glue while a residual
   remains;
3. fixed-point-free holonomy: every local comparison is valid but no global
   section exists; and
4. malformed types, overlaps, versions, or transports: `NotRepresentable`.

The model is a finite local system on the **chart nerve**.  It is not a sheaf
or local system already implemented by Adva, and it does not turn the finite
domain set into a topological circle.

---

## 0. The correction inherited from 0067

Let

\[
\mathcal D=\{K,X,t\},
\qquad
U_D=\mathcal D\setminus\{D\}.
\]

Then the chart-incidence nerve is

\[
N(\{U_K,U_X,U_t\})=\partial\Delta^2.
\]

This is an exact combinatorial statement: there are three chart vertices,
three nonempty pairwise intersections, and no triple intersection.  It is not
an application of the nerve theorem.  If \(\mathcal D\) has the discrete
topology, every \(U_D\) consists of two disconnected points, so the cover is
not good and its nerve need not have the homotopy type of the base.

The object studied here is therefore explicitly

\[
\Gamma_Q=N(\{U_K,U_X,U_t\}),
\]

the chart coordination graph.  The circular topology belongs to
\(\Gamma_Q\), not to the three-element content set.

---

## 1. Typed charts and overlaps

Orient the nerve by

\[
K\longrightarrow X\longrightarrow t\longrightarrow K.
\]

The three edges are typed by the unique shared content:

| transition | overlap type |
|---|---|
| \(K\to X\) | \(U_K\cap U_X=\{t\}\) |
| \(X\to t\) | \(U_X\cap U_t=\{K\}\) |
| \(t\to K\) | \(U_t\cap U_K=\{X\}\) |

Attach a finite marked fibre

\[
F_D=\{0_D,1_D,\ldots,(n-1)_D\}
\]

to each chart.  The repeated integer labels are coordinate names only; the
three fibres remain differently typed copies.

For every oriented overlap introduce a comparison

\[
g_{DE}:F_D\longrightarrow F_E.
\]

V0 admits only bijections.  This is deliberate.  The comparison layer models
reversible re-expression of retained evidence.  A noninvertible test, update,
copy, discard, or computation gate belongs to the separately typed active
program layer and cannot be hidden inside a transition function.

Each comparison also carries:

- its source and target chart types;
- the unique overlap type;
- a finite observer-policy version; and
- a fibre-coordinate version.

The reverse comparison is derived as \(g_{ED}=g_{DE}^{-1}\).  It is not an
independent declaration that may silently disagree.

---

## 2. Holonomy around the chart nerve

At base chart \(K\), define

\[
\boxed{
H_K=g_{tK}\,g_{Xt}\,g_{KX}:F_K\longrightarrow F_K.
}
\]

The individual comparison maps may all be valid while \(H_K\ne I\).  This is
the first finite expression of openness that the circular interface can
retain: every local translation succeeds, yet the complete circuit need not
close in the chosen marking.

Changing the starting chart does not destroy the invariant.  For example,

\[
H_X=g_{KX}H_Kg_{KX}^{-1}.
\]

Thus the exact permutation depends on the basepoint calibration, while its
conjugacy class, cycle type, and number of fixed points do not.

This mirrors, without identifying:

- the full-twist residual retained by the braid lift in 0057;
- the central lift residual in the Legendre coherence prism 0043; and
- the Dehn-twist path lift in 0048.

The finite permutation here is not declared to be any of those carriers.
They become comparable only after a typed interpretation map is constructed.

---

## 3. Global sections are fixed points

A global marked section is a triple

\[
s=(s_K,s_X,s_t)
\]

satisfying

\[
s_X=g_{KX}(s_K),
\qquad
s_t=g_{Xt}(s_X),
\qquad
s_K=g_{tK}(s_t).
\]

Substitution gives

\[
\boxed{s_K=H_K(s_K).}
\]

Therefore global sections are in bijection with fixed points of the
holonomy:

\[
\boxed{
\operatorname{Sect}(\Gamma_Q,F,g)
\cong
\operatorname{Fix}(H_K).
}
\]

This yields three representable cases.

### Flat all-sections case

If \(H_K=I\), every element of \(F_K\) determines a global section.  The
system is flat in this finite marked sense.  Gluing is not necessarily unique:
an anchor or selected observation is still required to choose one of the
\(n\) sections.

### Residual holonomy with fixed sections

A nonidentity permutation may fix some elements.  These phases glue, but the
unselected phases still witness nontrivial holonomy.  Existence of one global
section therefore does not prove flatness.

### Holonomy obstruction

If \(H_K\) is fixed-point-free, all three overlap comparisons are individually
valid but no global marked section exists.  This is not
`NotRepresentable`: the local system is exactly represented, and its failure
to glue is a certified global result.

These cases must not be reduced to the Boolean question "did gluing work?".

---

## 4. Gauge changes and calibration independence

Let

\[
h_D:F_D\longrightarrow F_D
\]

be a local coordinate change on every chart.  The re-expressed transition is

\[
g'_{DE}=h_Eg_{DE}h_D^{-1}.
\]

The circuit transforms by

\[
\boxed{H'_K=h_KH_Kh_K^{-1}.}
\]

Hence the following are gauge-invariant:

- identity versus nonidentity holonomy;
- cycle type;
- the number of fixed phases;
- the number of global sections; and
- the flat/residual/obstructed classification.

This is the correct relationship between startup calibration and retained
holonomy.  Calibration changes coordinates; it cannot erase a nontrivial
conjugacy class.

Likewise, moving the cut or base chart cyclically conjugates the holonomy.
The printed first bracket changes, while the global obstruction class does
not.

---

## 5. Reverse orientation and the corrected duality

Reverse the nerve orientation and replace every transition by its inverse:

\[
K\longrightarrow t\longrightarrow X\longrightarrow K.
\]

The reversed circuit satisfies

\[
\boxed{H_K^{\mathrm{rev}}=H_K^{-1}.}
\]

Its fixed-point set is identical to that of \(H_K\).  Thus reversal preserves
the existence and number of global sections while reversing the retained
transport history.

This is compatible with the corrected 0066 rule:

\[
(f:c\to c')^\star:(c')^\star\to c^\star.
\]

It is not a forward `NF/NF` identity.  Nor does it say that learning and proof
execute the same transition function.  It says that a candidate dual reading
reverses the comparison arrows and inverts the circuit holonomy.

---

## 6. The four typed outcomes

V0 returns the following classification:

| outcome | local transitions | holonomy | global sections |
|---|---|---|---|
| `Flat` | valid bijections | identity | all \(n\) phases |
| `ResidualFixed` | valid bijections | nonidentity with fixed points | a proper nonempty subset |
| `Obstructed` | valid bijections | fixed-point-free | none |
| `NotRepresentable` | malformed type, overlap, version, cycle, or map | not formed | not formed |

`Obstructed` and `NotRepresentable` are categorically different.  The first
is a result inside the finite language.  The second states that no V0 local
system was constructed.

Likewise, `ResidualFixed` prevents a common mistake: one successful glued
observation does not authorize forgetting holonomy on the rest of the fibre.

---

## 7. Relation to finite representation

The experiment now gives a more exact finite-expression pattern:

\[
\mathfrak L_Q=
\left(
\Gamma_Q,
(F_D)_D,
(g_{DE})_{DE},
(\nu_Q,\nu_F),
H,
\operatorname{Fix}(H),
R_H
\right).
\]

The record does not contain the open world.  It contains enough finite data
to answer a declared family of coordination questions:

1. are all local comparisons well typed?
2. what history remains after one circuit?
3. which marked local states admit global continuation?
4. how does the answer change under coordinate calibration?

The resulting notion of completeness is relative:

> The record is complete for this finite overlap-transport question exactly
> when every comparison, version, holonomy permutation, fixed-point witness,
> and residual needed by the declared observer is retained.

It is not an absolutely complete expression of an open interpretation.

---

## 8. Relation to logic and learned characteristics

Suppose each chart has inferred a local characteristic vocabulary.  Pairwise
agreement on overlaps is not yet a global logical vocabulary.  The chart
comparisons may accumulate holonomy.

The finite model suggests three different logical situations:

\[
\begin{array}{rcl}
H=I
&:& \text{every local marking extends around the circuit},\\
H\ne I,\ \operatorname{Fix}(H)\ne\varnothing
&:& \text{only invariant markings extend},\\
\operatorname{Fix}(H)=\varnothing
&:& \text{no single marked vocabulary closes globally}.
\end{array}
\]

This does not yet define propositions, inference rules, or truth.  It does
identify a necessary coordination layer for a future 3-form logic: local
vocabularies, overlap translations, and global closure certificates are
distinct objects.

On the learning side, nontrivial holonomy may be retained as a characteristic
of the observation cycle rather than normalized away.  On the proof side, a
flatness or fixed-point certificate may justify one global section.  Whether
these are reverse-dual readouts of one checked rule complex remains an open
interpretation problem.

---

## 9. Relationship to provenance and forgetting

A gauge change re-labels phases but preserves the holonomy conjugacy class.
It is therefore an abstraction candidate, not an erasure authority.

Forgetting the exact transitions while retaining only one glued section can
identify:

- an identity-holonomy system;
- a nonidentity system that fixes that section; and
- distinct nonidentity systems with the same fixed point.

Thus one visible global section does not determine the comparison history.
A valid `ProvenanceHide`-like operation must retain at least the complete
transition fibre or a sufficient holonomy residual under its declared policy.

The fixture intentionally supplies no `Erase` constructor.

---

## 10. What V0 checks

The pure-Python fixture checks:

1. the exact type of each pairwise overlap;
2. rejection of nonbijective comparison maps;
3. rejection of incorrect overlap labels, edge cycles, and mixed versions;
4. identity holonomy with all phases extending to global sections;
5. nonidentity holonomy with a proper nonempty fixed-section set;
6. fixed-point-free holonomy with valid local comparisons but no global
   section;
7. equality between global sections and holonomy fixed points;
8. conjugation of holonomy under local gauge changes;
9. conjugation under cyclic basepoint changes; and
10. inversion of holonomy under orientation reversal.

For the three-point fibre, all

\[
(3!)^3=216
\]

transition triples are enumerated.  They divide exactly into:

| status | number of local systems |
|---|---:|
| `Flat` | 36 |
| `ResidualFixed` | 108 |
| `Obstructed` | 72 |

Every one satisfies
\(\operatorname{Sect}\cong\operatorname{Fix}(H)\).
No floating-point, sampled geometric, or randomized oracle is used.

---

## 11. Nonclaims and falsifiers

This note does not establish:

- a Rust local-system, sheaf, descent, gauge, or holonomy API;
- a good cover or a nerve-theorem equivalence;
- that chart fibres are Adva values, sources, occurrences, or histories;
- that all useful overlap comparisons are invertible;
- a unique global section under identity holonomy;
- that one fixed section makes the circuit flat;
- that the finite permutation holonomy equals a braid full twist, Dehn twist,
  Legendre lift, or program residual;
- an observer-independent \(\Omega\), complete 3-form logic, or universal
  computation result; or
- permission to copy, discard, contract, weaken, or erase evidence.

The proposal must be revised if it ever:

1. confuses a gluing obstruction with malformed syntax;
2. treats pairwise validity as automatic global closure;
3. erases nontrivial holonomy because one fixed section exists;
4. lets a gauge change alter the holonomy conjugacy class;
5. makes orientation reversal preserve rather than invert transport; or
6. smuggles a noninvertible program gate into the comparison layer.

---

## 12. Next local gate

The next experiment should connect one chart transition to exact checked
evidence rather than enlarge the abstract fibre.

A minimal candidate is:

1. select one finite checked `ProgramSlice` with a lineage-aware observer;
2. derive two observer views whose common support is an explicit complete
   fibre, not an inferred set intersection;
3. construct one certificate-bearing comparison between those views;
4. show whether composition with a third view is flat, residual-bearing, or
   obstructed; and
5. retain exact source, occurrence, snapshot, policy, and transition evidence.

Only after such grounding should Cech or descent terminology be promoted
beyond analogy.

---

## Conservative conclusion

The circular 3-form intuition survives a stronger test.  Three local
universal readings can be coordinated by finite overlap maps, and the circuit
has a precise invariant:

\[
\boxed{H=g_{tK}g_{Xt}g_{KX}.}
\]

Finite gluing is controlled not merely by local consistency but by fixed
points of \(H\):

\[
\boxed{\operatorname{Sect}\cong\operatorname{Fix}(H).}
\]

The crucial distinction is now visible.  A finite observer can fully record a
nonclosing circuit without forcing it to close.  Openness appears as retained
holonomy or a certified absence of global sections, while malformed data
remains separately `NotRepresentable`.

The next missing piece is no longer topological vocabulary.  It is a checked
bridge from one overlap comparison to exact Adva process evidence.
