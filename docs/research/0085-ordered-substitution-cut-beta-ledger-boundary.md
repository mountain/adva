# Ordered Substitution, Fresh-Cut Admissibility, and the Beta Ledger Boundary

Status: research-local proof-transformation theorem, executable substitution
certificate, and normalization boundary following
[0084](0084-threaded-natural-deduction-entailment-cell.md).

No stable Adva proof term, cut node, substitution event, beta event, ledger
transport, logical symbol, or Rust API is introduced here. The executable
companion imports and reuses the research-local proof fixture of 0084.

Follow-up status: note
[0086](0086-contextual-beta-ledger-transport-strong-normalization.md) now
supplies the research-local beta-ledger transport anticipated here, lifts it
to arbitrary proof positions, proves transport-indexed preservation, and
establishes beta-only strong normalization for finite `TND0` derivations.
This note remains the substitution theorem and dependency boundary. Note
[0093](0093-beta-history-local-confluence-audit-2-cells.md) subsequently proves
local and global confluence of the beta-only proof-tree relation and a unique
beta normal form for each fixed finite starting derivation. It keeps competing
audit histories distinct and does not install a proof-coherence quotient.

This note follows a Gentzen/Prawitz-style dependency discipline:

1. strengthen substitution to an ordered one-hole lemma;
2. derive conditional admissibility of the corresponding V0 fresh-cut rule;
3. derive boundary-sequent preservation for implication detour contraction;
   and
4. only then ask for normalization.

The order matters. Even full subject reduction would not imply normalization,
and normalization is not established by calling two proofs equal. In the
threaded setting a proof transformation must also explain what happens to
resource identity, ordering, and history.

---

## 0. Executive result

Let

\[
\pi:\Gamma_L\circ x:A\circ\Gamma_R
\vdash_K B\blacktriangleright\Lambda_\pi,
\qquad
\sigma:\Delta\vdash_K A\blacktriangleright\Lambda_\sigma
\]

be checked derivations in the ordered implicational calculus
\(\mathrm{TND}_0\). Under the strict V0 freshness conditions below, there is
a checked proof-tree graft

\[
\boxed{
\operatorname{Sub}_x(\pi,\sigma):
\Gamma_L\circ\Delta\circ\Gamma_R
\vdash_K B
\blacktriangleright
\operatorname{splice}_x(\Lambda_\pi,\Lambda_\sigma).
}
\tag{Sub}
\]

If the unique open target occurs at ledger position \(i\), then

\[
\operatorname{splice}_x(\Lambda_\pi,\Lambda_\sigma)
=
\Lambda_\pi[:i]
\circ\Lambda_\sigma
\circ\Lambda_\pi[i+1:].
\tag{L}
\]

This is an exact ordered splice. It is neither append, sorting, exchange, nor
a multiset union. The previously proposed right-boundary statement is only
the corollary \(\Gamma_R=\epsilon\). It is too weak to serve directly as the
induction hypothesis, because implication introduction temporarily puts its
principal occurrence to the right of \(x\).

The executable result is a replayable `OrderedOneHoleSubstitutionCertificate`
that retains the input proofs, consumed target, context and ledger splits,
recursive path, exact output proof, and expected splices.

The theorem makes the conditional one-hole fresh-cut rule admissible. It does
not yet prove an unrestricted cut rule admissible, or a general cut-
elimination theorem for an explicit sequent calculus.

For a checked implication detour,

\[
\operatorname{E}
\bigl(\operatorname{I}^{b}_{x}(\pi),\sigma\bigr),
\]

the contractum \(\operatorname{Sub}_x(\pi,\sigma)\) has the same conclusion
and ordered open context. Its raw full ledger is generally not equal to the
redex ledger. If

\[
\Lambda_\pi=L\circ[x^{\mathrm{open}}]\circ R,
\]

then the exact boundary is

\[
L\circ[x^{\mathrm{discharged},b}]\circ R\circ\Lambda_\sigma
\quad\Longrightarrow_\beta\quad
L\circ\Lambda_\sigma\circ R.
\tag{B}
\]

The suffix \(R\) contains no open occurrence but may contain discharged audit
records. Thus beta contraction deletes the retired target from the current
proof and transports the replacement ledger leftward across \(R\). This must
be recorded by a beta transport cell; it cannot be silently declared to be
ledger equality.  Note 0086 subsequently realizes this requirement at the
research-local level.

---

## 1. Why the theorem must use an ordered context hole

Suppose one tried to prove only

\[
\Gamma\circ x:A\vdash B,
\quad
\Delta\vdash A
\quad\Longrightarrow\quad
\Gamma\circ\Delta\vdash B
\]

by induction on the first derivation. If its last rule is right implication
introduction, its premise has the form

\[
\Gamma\circ x:A\circ y:C\vdash D.
\]

The target \(x\) is no longer the right boundary, so the proposed induction
hypothesis cannot be applied.

The traditional repair is to prove a stronger lemma whose context contains a
distinguished hole:

\[
\Gamma_L\circ[-]\circ\Gamma_R.
\]

The suffix is not a commutative remainder. It is part of the theorem. Filling
the hole with \(\Delta\) yields exactly

\[
\Gamma_L\circ\Delta\circ\Gamma_R.
\]

No exchange rule is used or inferred.

This also identifies the proof-theoretic meaning of a hole more precisely.
Here the hole is a typed, uniquely located assumption port in a derivation,
not falsity, incomplete search, or an 0083 same-source aperture. Substitution
is the certified operation that grafts one checked derivation into that port.

---

## 2. Strict V0 interface conditions

The executable theorem requires:

1. both input derivations recursively pass the 0084 proof checker;
2. \(\sigma\) concludes the exact formula \(A\), not merely an
   \(H_7\)-equivalent formula;
3. the full target occurrence appears exactly once in the open context and
   its open `ResourceUse` appears exactly once in \(\Lambda_\pi\);
4. the two complete ledgers have disjoint scoped occurrence identities
   \((\operatorname{ScopeId},\operatorname{OccurrenceId})\);
5. their binder identities are disjoint, including binders on already
   discharged records; and
6. their resource sources are disjoint.

Write
\(\operatorname{Fresh}_{V0}(\pi,\sigma,x)\) for the exact
target/formula conditions together with the three full-ledger disjointness
conditions.

Condition 6 is deliberately stronger than the minimum required to validate
the output after deleting \(x\). It prevents a replacement from silently
claiming that it inherits the target's semantic source identity. Such an
inheritance would require an explicit `SourceTransfer` or aperture-filling
certificate, which V0 does not have.

Labels and provenance identifiers need not be disjoint. A label is display
syntax, and shared provenance does not consume one linear source twice.

The V0 identity discipline is still not a general capture-avoidance theorem.
It treats a scoped occurrence pair as nominal identity and requires global
binder freshness. Quantifiers will additionally need term variables,
eigenvariable conditions, a scope forest or equivalent binding structure,
and certified alpha-renaming or rebasing.

---

## 3. Current dependency ledger versus transformation history

One record cannot consistently play both of these roles:

1. **current derivation ledger**: every resource use that still occurs in the
   present proof tree, including its open or discharged status; and
2. **transformation history**: the consumed node, former binder, rewrite path,
   and relation between a proof before and after substitution or beta
   contraction.

In the cut-free output of substitution, the target assumption leaf no longer
exists. It must therefore disappear from the current ledger.

- Leaving it `open` would leave \(x\) in the output context.
- Marking it `discharged` would invent an implication-introduction binder.
- Adding a `substituted` status to the same proof node would retain an
  explicit cut rather than demonstrate its admissibility.

The consumed identity is instead retained in the substitution certificate.
This is controlled forgetting: the current-proof observer projects to the
new derivation, while the audit observer retains the transition cell and can
replay the projection. Nothing is identified merely because the two proofs
have the same theorem.

This corrects an ambiguity in 0084. Its ledger is complete relative to one
current proof tree. It is not an append-only archive across proof
transformations. Moreover, residual aperture data live in an
`ApertureBoundaryDiagnostic`; they are not fields of a successful
`ResourceUse` record.

The distinction gives three levels that must remain separate:

\[
\text{proof presentation}
\longrightarrow
\text{certified coherence class}
\longrightarrow
\text{verified conclusion}.
\]

The first arrow needs explicit transformation cells. The second is an
observer-relative quotient and is not installed in this note.

---

## 4. Structural proof of ordered substitution

The proof is by induction on the height of \(\pi\).

### 4.1 Assumption

If \(\pi\) is an assumption and contains the designated open target, it is
exactly

\[
x:A\vdash A.
\]

Return \(\sigma\). Both context and ledger equations reduce to identity.

### 4.2 Right implication introduction

Let

\[
\pi=
\frac{
\pi_0:
\Gamma_L\circ x:A\circ\Gamma_R\circ y:C
\vdash D
}{
\Gamma_L\circ x:A\circ\Gamma_R
\vdash C\multimap_R D
}\;\multimap_R I_y^b.
\]

The strengthened induction hypothesis applies to \(\pi_0\) with suffix
\(\Gamma_R\circ y:C\). Rebuild the original introduction using the same
principal occurrence and binder identity. Here \(y\) and \(x\) are distinct
full nominal occurrences, even if their display labels coincide. Full
occurrence, source, and binder freshness conditions make the rebuild valid.

For \(y\ne x\), discharge commutes with the target splice:

\[
D_{y,b}
\bigl(\operatorname{splice}_x(\Lambda,\Lambda_\sigma)\bigr)
=
\operatorname{splice}_x
\bigl(D_{y,b}(\Lambda),\Lambda_\sigma\bigr).
\]

This yields both the claimed context and the exact ledger.

### 4.3 Right implication elimination

Let

\[
\pi=
\frac{
\pi_f:\Gamma_f\vdash C\multimap_R B
\qquad
\pi_a:\Gamma_a\vdash C
}{
\Gamma_f\circ\Gamma_a\vdash B
}\;\multimap_R E.
\]

Linearity and the checked ledger imply that the unique open target occurs in
exactly one premise.

- If it occurs in \(\pi_f\), apply the induction hypothesis there and leave
  \(\pi_a\) unchanged.
- If it occurs in \(\pi_a\), leave \(\pi_f\) unchanged and apply the
  induction hypothesis there.

Then rebuild elimination. The concatenation laws are

\[
\operatorname{splice}_x
(\Lambda_f\circ\Lambda_a,\Lambda_\sigma)
=
\operatorname{splice}_x
(\Lambda_f,\Lambda_\sigma)\circ\Lambda_a
\]

when \(x\) occurs in \(\Lambda_f\), with the symmetric equation when it
occurs in \(\Lambda_a\). Full-ledger freshness ensures that rebuilding cannot
introduce a source aperture, occurrence alias, or binder alias.

These are all rules of \(\mathrm{TND}_0\), so theorem (Sub) follows.

---

## 5. Replayable proof transformation

The executable operation does not accept an asserted result. It computes the
unique descent spine from the checked body to the target assumption. Each
visited rule is recorded as replacement or descent through premise \(i\),
while the sibling outside that spine is reused without being mistaken for a
second target path.

The returned certificate records:

- body, target, replacement, and result proofs;
- target positions in the ordered context and ledger;
- left and right context pieces;
- left and right ledger pieces;
- the per-rule recursion trace; and
- the expected context and ledger splices.

Replay reruns every input check, freshness decision, recursive constructor,
and exact equality. A forged position, split, trace, output proof, context, or
ledger therefore fails certificate checking even if the forged result happens
to prove the same formula.

The fixture structurally identifies this local certificate by its frozen
contents. A stable promotion would additionally allocate a nominal
`SubstitutionId`, proof-node identities, input/output digests, and an explicit
leaf port path in Rust-owned IR.

---

## 6. Success, obstruction, and aperture

The total calibration API has three disjoint result classes.

| Result | Meaning and authority |
|---|---|
| `SubstitutionSucceeded` | A checked graft and replay certificate establish the result. |
| `SubstitutionRejected` | An invalid interface produces no derivation. |
| `PreGraftFreshnessAperture` | An 0083-shaped diagnostic refuses the graft. |

The success theorem applies only inside its source-disjoint domain. For an
input outside that domain, the total calibration calls the 0083 ledger merger
before deleting the target. A same-formula collision across two domains can
therefore return a **pre-graft freshness diagnostic** with the remaining
domain and orientation.

This is a conservative policy result obtained by reusing the 0083 classifier.
It does not prove that substitution itself opens a competitive-source
aperture: the target and replacement do not coexist in the contractum. Their
shared source may instead require endpoint identification or a certified
source transfer. V0 authorizes neither interpretation.

The diagnostic is not \(\Omega\). It is a finite typed refusal with two named
ports and a declared missing role. It may later be filled, rejected, or
translated by a new vocabulary constructor. None of those possibilities is
an implicit rule of substitution.

---

## 7. Conditional fresh-cut admissibility, not cut elimination

Adjoin the hypothetical one-hole cut rule

\[
\frac{
\pi:\Gamma_L\circ x:A\circ\Gamma_R
\vdash B\blacktriangleright\Lambda_\pi
\qquad
\sigma:\Delta\vdash A\blacktriangleright\Lambda_\sigma
\qquad
\operatorname{Fresh}_{V0}(\pi,\sigma,x)
}{
\Gamma_L\circ\Delta\circ\Gamma_R\vdash B
\blacktriangleright
\operatorname{splice}_x(\Lambda_\pi,\Lambda_\sigma)
}\;\operatorname{Cut}^{\mathrm{fresh}}_x.
\]

Theorem (Sub) gives a cut-free derivation of every conclusion produced by one
such rule. Therefore this conditional fresh-cut rule is admissible in
\(\mathrm{TND}_0\). No alpha-renaming theorem currently converts an arbitrary
nominally colliding cut into this fresh form.

This statement should not be inflated into a general cut-elimination theorem.
The present calculus has no explicit cut proof node and hence no complete
family of principal and commuting cut reductions. A future sequent
presentation would need those reductions, a decreasing measure, and their
resource/audit transports.

Natural-deduction substitution and sequent-calculus cut reduction are closely
related proof transformations. They are not definitionally the same proof
object.

---

## 8. Implication detours and boundary-sequent preservation

Consider a checked maximal implication detour

\[
R=
\operatorname{E}
\bigl(\operatorname{I}^{b}_{x}(\pi),\sigma\bigr).
\]

Because the elimination was accepted, the abstraction and argument ledgers
already satisfy the strict disjointness conditions. Ordered substitution
therefore constructs

\[
C=\operatorname{Sub}_x(\pi,\sigma).
\]

Define the ledger-erased boundary projection

\[
U(D)=
\bigl(\operatorname{OpenContext}(D),
\operatorname{conclusion}(D)\bigr).
\]

The substitution theorem yields

\[
\operatorname{conclusion}(R)
=
\operatorname{conclusion}(C),
\qquad
\operatorname{OpenContext}(R)
=
\operatorname{OpenContext}(C).
\tag{SP}
\]

Equivalently, \(U(R)=U(C)\).

Thus contraction of this proof-level beta detour preserves the conclusion and
ordered open boundary. It does not preserve the complete ledger-indexed
judgment by equality. The fixture also has no term AST, so (SP) is not yet a
theorem about term syntax or runtime evaluation.

Full ledger equality is false. Since \(x\) is the rightmost open assumption
of \(\pi\), the suffix \(R_0\) in

\[
\Lambda_\pi=L\circ[x^{\mathrm{open}}]\circ R_0
\]

contains only discharged records. Introduction and subsequent elimination
produce

\[
\Lambda_{\mathrm{redex}}
=
L\circ[x^{\mathrm{discharged},b}]
\circ R_0\circ\Lambda_\sigma,
\]

whereas substitution produces

\[
\Lambda_{\mathrm{contractum}}
=
L\circ\Lambda_\sigma\circ R_0.
\]

Even after deleting the retired target, the tuple orders differ whenever both
\(R_0\) and \(\Lambda_\sigma\) are nonempty. The executable counterexample is

\[
[x^b,h^c,r]
\quad\Longrightarrow_\beta\quad
[r,h^c].
\]

Deleting \(x^b\) from the left gives \([h^c,r]\), not \([r,h^c]\).
The resource multiset of surviving uses agrees, but multiset agreement forgets
the very order that the threaded grammar asks us to retain.

This note therefore required a future `BetaLedgerTransport` to record at
least:

- the redex and contractum roots;
- the consumed target/binder pair;
- the argument proof and graft site;
- embeddings of all surviving occurrence identities;
- the movement of \(\Lambda_\sigma\) across the discharged suffix;
- any certified alpha-renaming or scope rebasing; and
- the open-context and conclusion preservation checks.

If this movement later has geometric content, it may have a braid-like
survivor component or form part of a transport cell; it is not an invisible
permutation.  The entire beta event is directed and retires one record, so it
is not itself a braid.

Note 0086 now implements the corresponding checked transport as a directed
survivor span: it retires exactly the target record, preserves
the identities and complete records of every survivor, retains the internal
orders of \(L\), \(R_0\), and \(\Lambda_\sigma\), and records the prescribed
cross-block movement.  It remains a directed audit cell, not a proved braid
or an authorized proof-coherence quotient.

---

## 9. Halting and normalization

The proof-theoretic words now have distinct meanings.

- The project-local **beta success** supplied by note 0086 is one certified
  detour contraction at a declared proof position.
- A **beta normal form** has no beta detour at any proof position.
- **Weak normalization** says that some reduction sequence reaches a normal
  form.
- **Strong normalization** says that every reduction sequence terminates.
- **Confluence** says that divergent reductions can be joined.

The substitution theorem in this note proves none of the last three by
itself. Boundary-sequent preservation also does not prove termination.

Note 0086 subsequently defines a typed reduction relation on derivation trees,
lifts checked beta transport through implication introduction and both
elimination premises, and proves transport-indexed preservation at arbitrary
proof positions.  In this linear one-hole fragment no argument proof is
duplicated: every beta-only step decreases the complete current ledger length
and discharged-record count by exactly one and the derivation-tree node count
by exactly three.  Hence every beta-only reduction sequence from a finite
`TND0` derivation terminates; its length is bounded by the initial number of
discharged records.  This is strong normalization for that declared
derivation reduction, not a theorem about a runtime term language.  It still
does not by itself imply confluence, coherence of different audit paths, or
uniqueness of beta normal forms. Note
[0093](0093-beta-history-local-confluence-audit-2-cells.md) adds local
confluence and uses this strong-normalization result to prove global
confluence and a unique beta normal form for each fixed finite starting proof.
It does not identify arbitrary proofs of the same sequent or make their audit
histories equal.

A normal form may forget administrative detours only through a declared
observer quotient whose invariants have been proved to descend.  That
quotient is not installed by notes 0085, 0086, and 0093.

This also constrains exploration and compactification. A finite vocabulary
does not by itself imply termination or compactness.  Conversely, beta-only
strong normalization means that the reduction tree of one fixed finite
`TND0` proof has no infinite beta ray and supplies no \(\Omega\)-boundary.
Only an actually infinite, scheduler-stable family of unclosed histories in a
future recursive or open-search extension, or a compatible size-unbounded
family of finite proofs, could supply rays for a future boundary. Any such
compactification must preserve typed open ports, thread identity, and the
declared transport cells until a controlled quotient names exactly which
variation history is forgotten.

Consequently,

\[
\text{normal form}
\ne
\text{semantic truth}
\ne
\text{search exhaustion}
\ne
\Omega.
\]

---

## 10. Executable calibration

The companion
**tests/python/test_threaded_substitution_calibration.py** checks:

1. the assumption base case;
2. ordered insertion of a multi-source replacement;
3. the general one-hole case with nonempty left and right context pieces;
4. descent through implication introduction, where the target becomes an
   interior premise occurrence;
5. descent through both function and argument sides of elimination;
6. exact context and ledger splices without append, sorting, or exchange;
7. rejection of wrong formula, wrong right boundary, occurrence alias, source
   formula mismatch, and binder collision;
8. a conservative pre-graft third-domain freshness diagnostic for a shared
   source;
9. deterministic rejection of a forged substitution certificate;
10. the identity beta ledger comparison boundary; and
11. a nontrivial beta example in which deleting the retired target still does
    not make the two raw ledger orders equal.

The substitution result is also passed back through the recursive 0084 proof
checker and its finite Boolean rule-soundness cell.

---

## 11. Proven, calibrated, and deferred

### Proven in the mathematical fragment

- ordered one-hole proof substitution under strict global freshness;
- exact context and current-ledger splice equations;
- the right-boundary substitution corollary;
- conditional admissibility of the corresponding V0 fresh-cut rule; and
- boundary-sequent preservation for one implication detour contraction.

### Executably calibrated

- recursive proof-tree grafting through all three `TND0` rules;
- a replayable substitution certificate with exact split data;
- strict separation of success, obstruction, and a pre-graft aperture-shaped
  diagnostic;
- preservation of the checked conclusion and ordered open context; and
- failure of raw full-ledger equality under general beta contraction.

### Established by the research-local continuation in note 0086

- a standalone beta-ledger transport record and replay checker;
- a path-indexed beta-only reduction relation at arbitrary proof positions;
- transport-indexed preservation of conclusion and ordered open context;
- exact survivor identity and ledger-order accounting; and
- beta-only strong normalization of every finite `TND0` derivation.

### Established by the research-local continuation in note 0093

- explicit separation of endpoint proof equality, transport summaries,
  histories, and history 2-cells;
- local confluence for independent and nested beta peaks;
- global confluence of the beta-only proof-tree relation; and
- one beta normal form, under strict proof-tree equality, for every fixed
  finite starting derivation.

### Deferred

- a stable nominal substitution or cut-event identity;
- source-transfer and 0083 aperture-filling rules for substitution;
- term syntax and capture-avoiding term substitution;
- a stable promoted beta event, transport identity, or Rust API;
- stable promoted history, residual, and 2-cell identities or APIs;
- equality or a quotient of distinct audit histories;
- uniqueness of history 2-cells and higher coherence laws;
- eta conversion and any beta-eta or eta-long normalization claim;
- a sequent calculus with explicit cuts and cut elimination;
- proof-relevant quantifier rules and eigenvariable transport;
- a justified proof-coherence quotient; and
- any compactification or \(\Omega\) claim for reduction histories.

Note 0093 discharges the beta-only proof-tree confluence target without
collapsing distinct normalization histories. A promoted history API, an
observer-relative coherence quotient, and higher coherence remain separate.
Quantifier rules still wait for the separate term-substitution and scope
theorem.
