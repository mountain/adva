# Research 0170: Möbius conjugacy, observer transport, and the missing pole

Date: 2026-09-11. Direction and question: Mingli Yuan. Formalization,
implementation, execution, and writing: ChatGPT (OpenAI), submitted through
Mingli Yuan's GitHub account as an authorized proxy. Attribution and account
authorization are not evidence of correctness.

Status: **one elementary argument, one bounded external experiment, and one
Proposed research term**. There is no stable API, native admission, library
admission, free, or Seal.

Run preflight base: b15380423d2d84c901e824c26c53e19cd933e022.
Integration base, reread before saving:
6e18c9494bde2a191dd5315db8695cd71d3ad787.

## 1. State of the dependency boundary

The latest main already contains three results needed here:

1. Research 0032 distinguishes a Möbius image of the exact E0 grid from its
   cellular dual and warns that geometric routing is not a value-preserving
   interpretation.
2. Research 0118 transports local closures while preserving distinct path
   provenance.
3. The merged alternating-group observer experiment shows that a faithful
   inclusion may outgrow an old observer without losing faithfulness.

Research 0123's arithmetic-universality and hypothesized-arithmetic-truth
remain Proposed words, not theorems. Research 0090 still forbids closure from
an uncovered prefix. The latest Research 0169 is a separate bounded
stability-filtration result: after correcting rank to graded-piece rank, its
newest finite step identifies the surviving residual as extension-class data
rather than another coordinate of the graded pieces. It supplies a useful
warning about lossy shadows but no dependency or authority for the projective
calculation below.

At inspection, PR #172 was the only open PR and remained a draft with an
unmet native regression-test gate. It is unrelated and is not modified.

## 2. The statement that needs correction

Let

\[
H(z)=\frac{z+2}{z+1},
\qquad
H=\begin{pmatrix}1&2\\1&1\end{pmatrix}.
\]

On the affine complex chart, z=-1 is a pole. On the Riemann sphere the map is
total: H(-1)=infinity and H(infinity)=1.

Suppose rho:G->PGL_2(K) is a representation. In general

\[
g\longmapsto H\rho(g)
\]

is **not** a representation. It sends the identity to H, not to the identity,
and

\[
H\rho(gk) \ne H\rho(g)H\rho(k)
\]

unless extra exceptional equations hold.

The change-of-coordinates representation is

\[
\rho_H(g)=H\rho(g)H^{-1}.
\]

It is a representation into H rho(G) H^-1. Calling it a representation into
the same named subgroup additionally requires H to normalize that subgroup.
Thus “HG is invertible” does not justify “HG preserves the group
representation.” One-sided composition, conjugacy, and basis change must not
share one label.

## 3. Observer and predicate transport

Conjugating the action is not enough. If an old observer probes x and sees
rho(g)(x), the corresponding new observation is

\[
\rho_H(g)(H(x))=H(\rho(g)(x)).
\]

The probe moves by H, and the observed value moves by H; alternatively, the
receiver decodes the new value by H^-1. For a predicate P, the transported
predicate is

\[
P_H(w)=P(H^{-1}(w)).
\]

This matters to the question about the Riemann-hypothesis line. The hypothesis
itself concerns

\[
\operatorname{Re}(s)=\frac12.
\]

Writing w=H(s) gives s=(2-w)/(w-1). If w=u+iv, exact algebra carries the
critical line to

\[
3u^2-8u+5+3v^2=0,
\]

or

\[
(3u-4)^2+(3v)^2=1.
\]

So the line becomes the circle with centre (4/3,0) and radius 1/3. This is
only predicate transport. It does not transport the zeta function, locate a
zero, or test the Riemann hypothesis.

## 4. Frozen experiment

The exact contract is
experiments/mobius_conjugacy_transport/contract.json. It uses P^1(F_p) and
PSL(2,F_p) for p=5,7, with projective matrix classes normalized by their first
nonzero coordinate. Every acceptance decision is modular integer arithmetic.

The run is bounded by 15 seconds of wall time, 15 CPU seconds, 256 MiB address
space, 100000 work units/candidate nodes, and 1 MiB output. It has one primary
execution attempt and at most one correction replay. The correction allowance
was used once, as recorded below.

Two group constructors are compared:

- normalized invertible projective matrices with square determinant;
- determinant-one matrices modulo projective scalar equivalence.

They agree exactly in both fields. All group pairs, projective points, and
coordinate subsets through the first separating cardinality are then checked.

## 5. Results

| Check | F_5 | F_7 |
|---|---:|---:|
| PSL(2,F_p) elements | 60 | 168 |
| H belongs to this PSL | yes | no |
| one-sided outputs inside PSL | 60 | 0 |
| one-sided product-law matches | 0 / 3600 | 0 / 28224 |
| conjugation product laws | 3600 / 3600 | 28224 / 28224 |
| pointwise covariance squares | 360 / 360 | 1344 / 1344 |
| transported observer receipts | 60 / 60 | 168 / 168 |
| unchanged-probe/value mismatches | 57 | 165 |
| minimum point-image coordinates | 3 | 3 |

The two fields expose complementary failures:

- Over F_5, det(H)=4 is a square. Left translation is a bijection of the
  underlying 60-element set, yet is not a homomorphism. Set preservation is
  therefore insufficient.
- Over F_7, det(H)=6 is not a square. Left translation lands in the other
  projective coset, so it fails even before the product law. Conjugation still
  normalizes PSL and passes every declared check.

The affine-chart control is deliberately deceptive. After removing the pole,
H gives distinct returned values:

\[
F_5:\quad 0\mapsto2,\ 1\mapsto4,\ 2\mapsto3,\ 3\mapsto0.
\]

This looks injective, but input 4=-1 maps to infinity, and finite output
1=H(infinity) is missing. The same pattern appears over F_7. The gated judgment
is UnknownCoverage, not closure.

The saved accepted evidence records 57893 work units. Construction, search, and
verification took 274.177 ms; serialization replay took 0.612 ms; total before
the final report write was 274.955 ms. Peak process RSS was 12288 KiB
(12 MiB). Network, reading, mathematical formulation, code authoring, final
write, and report preparation are excluded. File size is not used as a memory
measurement.

The first execution is retained as
experiments/mobius_conjugacy_transport/evidence-initial-invalid.json with status
InvalidEvidence. Its critical-line check compared a prewritten coefficient list
with itself, so it could not witness the line-to-circle derivation. The group
and observer results were not contradicted, but the combined report was
inadmissible. The single permitted correction replay replaced that empty check
with an actual bivariate integer-polynomial expansion. No bound or expected
coefficient was weakened.

## 6. Proposed term

conjugacy-gated-transport is recorded in
docs/terminology/conjugacy-gated-transport-v0.json. Its function is:

> Transport a representation only by two-sided conjugacy, bind the transformed
> probes, values and predicates, and refuse closure when the declared carrier
> or chart coverage is incomplete.

Its inputs, outputs, applicability conditions, witnesses, F_7 reuse, refusal
conditions, replay command, formation-cost omission and residuals are explicit
in the term file. It remains Proposed. No expression-power or solving-cost
improvement is claimed.

## 7. Evidence and boundaries

Artifacts:

- experiments/mobius_conjugacy_transport/calibration.py;
- experiments/mobius_conjugacy_transport/contract.json;
- experiments/mobius_conjugacy_transport/evidence-initial-invalid.json;
- experiments/mobius_conjugacy_transport/evidence.json.

Reproduce on Linux, using a fresh output:

    timeout 15s python -B -S \
      experiments/mobius_conjugacy_transport/calibration.py \
      --contract experiments/mobius_conjugacy_transport/contract.json \
      --output /tmp/mobius-conjugacy-transport.json

This is an in-repository fixed-fixture checker, not a general validator of
untrusted evidence. Python creates no Adva identities. The run does not prove
the simplicity of these groups, a universal representation of all simple
groups, arithmetic universality, a global transport theorem, or any result
about zeta zeros. Local image equality creates no M6 filler.

## 8. Who it helps and the next obligation

For Mingli, it corrects the proposed interpretation of HG without discarding
the useful Möbius intuition: the safe form is H G H^-1, together with the
observer/predicate transport. For a receiving agent, it supplies exact positive
and negative fixtures instead of a naming analogy. Its practical value for
Jiamin is still untested.

The smallest continuation is a versioned external receipt containing: source
representation domain, target conjugate domain, H, composition convention,
probe policy, predicate transport, and projective coverage. A receiver should
reject a one-sided HG receipt before any native work. Native promotion would
then require a separate Rust checked-diagram design and certificates.
