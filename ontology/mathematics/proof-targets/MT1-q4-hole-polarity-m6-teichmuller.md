# MT1: Q4 with HolePolarityM6 Realizes a Teichmüller Space

Status: first principal mathematical proof target of the ontology programme;
unproved.

## Motivating statement

The motivating statement is

\[
Q_4
+
\mathcal M_6^{\mathrm{hp}}
\quad\text{is a Teichmüller space}.
\]

A finite relation machine and a Teichmüller space are not presently objects of
the same type. The theorem target must therefore identify the space of
compatible marked machine completions, rather than the current finite carrier,
with a Teichmüller space.

## Candidate machine object

Let

\[
\mathcal C^\partial
=
Q_4
\bowtie
\left(
\mathcal M_6^{\mathrm{hp}}
\right)^\partial
\]

denote a future typed juxtaposition of the open Q4 interchange boundary and
the open Three-Hole Polarity M6 boundary. The symbol \(\bowtie\) is a
construction target. It does not yet denote an implemented composition or an
existing filler.

Under the physical working hypothesis PH1, the M6 member is provisionally
annotated by the length dimension

\[
L=\mathsf{Length}.
\]

Let

\[
\mathfrak C_L^+(\mathcal C^\partial)
\]

denote the still-to-be-defined space of positive real, dimension-compatible,
marked typed fillings and certified closures of \(\mathcal C^\partial\). Let
\(\mathcal G_{\mathrm{mark}}\) denote exactly the gauge or presentation
changes proved to preserve the marked machine data.

## Strong theorem target

The first precise strong target is:

\[
\boxed{
\mathfrak C_L^+(\mathcal C^\partial)
/
\mathcal G_{\mathrm{mark}}
\;\cong\;
\mathcal T(S)
}
\tag{MT1}
\]

for one explicitly constructed marked finite-type surface \(S\).

The symbol \(\cong\) must eventually be strengthened in stages:

1. bijection of represented objects;
2. homeomorphism of topological spaces;
3. real-analytic or complex-analytic equivalence, if available; and
4. metric or symplectic compatibility only after the earlier stages.

No later strength may be inferred from the finite incidence pattern alone.

## First surface candidate

The current first candidate is

\[
S
=
\Sigma_{0,4},
\]

the four-punctured sphere.

The repository's existing finite-surface programme starts from the rigid
three-punctured sphere with the \(K,X,t\) ends and interprets one additional
Failure aperture as a move to \(\Sigma_{0,4}\). Its ordinary Teichmüller space
has real dimension two.

This candidate is provisional. MT1 must derive the genus, punctures, boundary
components, markings, and orientations from \(\mathcal C^\partial\). A shared
number four or six is not such a derivation.

## Ordinary, decorated, or augmented

The target space must be chosen by what the machine retains.

- If puncture or boundary scales, horocycles, or comparable positive
  decorations remain part of the state, the likely target is a decorated
  Teichmüller space \(\widetilde{\mathcal T}(S)\).
- If those decorations are quotiented with an explicit complete fibre, the
  likely target is the ordinary space \(\mathcal T(S)\).
- If pinching and nodal limits are admitted as completed boundary states, the
  target may require an augmented Teichmüller space.

This choice is part of the theorem statement, not a matter of notation.

## Current finite obstruction

The existing principal Q4/M6 coherence calibration has:

\[
24\ \text{states},
\qquad
36\ \text{edges},
\qquad
6\ Q_4\ \text{faces},
\qquad
8\ M_6\ \text{faces},
\]

with local face pattern \(4.6.6\). This finite TO24 envelope is a coherence
carrier. It is not itself the noncompact Teichmüller space.

Moreover, HolePolarityM6 is a nonprincipal member of the M6 relation-machine
family. Its exact six-port polarity conjugacy supplies no M6 filler and no
typed Q4 composition. MT1 cannot import the principal braid filler merely
because the two members have isomorphic six-cycle boundaries.

The plausible roles are therefore:

| Adva object | possible Teichmüller role |
|---|---|
| Q4 and HolePolarityM6 boundaries | local transition obligations |
| typed relation fillers | coordinate-transition witnesses |
| TO24-like envelope | finite coherence cell or local quotient data |
| positive marked filling space | candidate coordinate atlas |
| legal infinite development | candidate global Teichmüller carrier |
| gauge quotient | removal of presentation or decoration redundancy |

Each row requires a construction.

## Proof ladder

### MT1.1: typed juxtaposition

Construct \(Q_4\bowtie\mathcal M_6^{\mathrm{hp}}\) with common typed
boundaries, source and occurrence ledgers, polarity transport, residuals, and
explicit fillers. Prove that the construction is independent of accidental
port spelling.

### MT1.2: surface extraction

Construct a marked surface

\[
S(\mathcal C^\partial)
\]

from the completed machine. Compute its Euler characteristic, genus,
punctures, boundary components, orientation, and marking. Prove or refute

\[
S(\mathcal C^\partial)
\cong
\Sigma_{0,4}.
\]

### MT1.3: parameter and dimension count

Define the positive filling parameters and the gauge action. Prove that the
ordinary quotient has the real dimension required by \(\mathcal T(S)\). For
the \(\Sigma_{0,4}\) candidate this first target is

\[
\dim_{\mathbb R}
\left(
\mathfrak C_L^+/\mathcal G_{\mathrm{mark}}
\right)
=
2.
\]

If decorations are retained, state and verify the corresponding larger
dimension instead of silently discarding them.

### MT1.4: coordinate atlas

Choose one explicit coordinate system, such as positive lambda lengths, shear
coordinates, or a cross-ratio presentation. Define both directions:

\[
\operatorname{Encode}:
\mathcal T(S)
\longrightarrow
\mathfrak C_L^+/\mathcal G_{\mathrm{mark}},
\]

\[
\operatorname{Decode}:
\mathfrak C_L^+/\mathcal G_{\mathrm{mark}}
\longrightarrow
\mathcal T(S).
\]

The selected coordinates must retain or explicitly quotient every marking,
scale, and residual.

### MT1.5: Q4 and polarized-M6 transition laws

Derive the coordinate transformations induced by Q4 and
HolePolarityM6. Compare the complete formulas, domains, orientations, and
relations with the chosen Teichmüller coordinate groupoid.

Cycle length alone is insufficient. Rank-two positive-coordinate systems may
have square, pentagon, hexagon, or octagon relations depending on their
exchange data. A four-cycle and six-cycle therefore do not identify a
Teichmüller groupoid without the corresponding transformation law.

### MT1.6: global coherence

Prove that different legal Q4/M6 paths with the same endpoints induce the same
marked Teichmüller point, or retain the exact monodromy that distinguishes
them. The present TO24 envelope is a finite test, not the global theorem.

### MT1.7: reconstruction

Prove that Encode and Decode are inverse at the declared level:

\[
\operatorname{Decode}\circ\operatorname{Encode}
=
\operatorname{id}_{\mathcal T(S)},
\]

\[
\operatorname{Encode}\circ\operatorname{Decode}
=
\operatorname{id}_{\mathfrak C_L^+/\mathcal G_{\mathrm{mark}}}.
\]

Only then may MT1 be called a realization theorem.

## Relationship to circle closure

A represented configuration enters the closed candidate space only when its
shared triadic run satisfies

\[
\mathsf{HaltSet}(r)
=
\{K,X,t\}
\]

and the global Q4/HolePolarityM6 connector and filler obligations close with a
replayable certificate. One-domain and two-domain halt words remain boundary
strata or open configurations; they are not interior points of the certified
closed space unless a later compactification theorem says otherwise.

## Decisive falsifiers

The strong target must be revised if:

1. the typed Q4/HolePolarityM6 juxtaposition cannot be formed;
2. no marked surface can be reconstructed without erasing machine identity;
3. the reconstructed surface is not \(\Sigma_{0,4}\) and no alternative
   surface is justified;
4. the positive filling quotient has the wrong dimension;
5. the quotient is non-Hausdorff or fails to parameterize the claimed marked
   structures;
6. Q4 or polarized M6 lacks the required coordinate-transition law;
7. a missing pentagon, hexagon, or other relation prevents path independence;
8. different legal machine histories collapse to one point without an
   authorized residual quotient;
9. the \(L\) annotation changes under a transition without a physical or
   mathematical transport rule; or
10. only numerical samples or visual resemblance support the identification.

A failure of the literal target may still leave a valid theorem that the
machine presents a coordinate groupoid, cell decomposition, cover, quotient,
boundary stratum, or finite coherence subcomplex associated with
Teichmüller theory.

## Verification character

MT1 is a symbolic, topological, and geometric proof target. Numerical
experiments may test formulas but cannot prove the realization.

## Internal references

- [Finite Surface, Universal Lift, and Threaded Imagination](../../../docs/research/0080-finite-surface-universal-lift-imagination.md)
- [Cell, Carrier, View, and Relation Machines](../../../docs/research/0103-cell-carrier-view-relation-machines.md)
- [Three-Hole Conjugate M6 and the Projective J-Lift](../../../docs/research/0106-three-hole-conjugate-m6-projective-lift.md)
- [PH1: HolePolarityM6 Carries the Dimension L](../../physics/working-hypotheses/PH1-hole-polarity-m6-carries-L.md)

## External calibrations

- V. Fock and A. Goncharov,
  [Cluster ensembles, quantization and the dilogarithm](https://arxiv.org/abs/math/0311245).
- S. Fomin and D. Thurston,
  [Cluster algebras and triangulated surfaces, Part II: Lambda lengths](https://arxiv.org/abs/1210.5569).
- L. Funar and R. Kashaev,
  [Centrally extended mapping class groups from quantum Teichmüller theory](https://arxiv.org/abs/1003.5365).
