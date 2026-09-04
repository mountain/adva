# Research 0117: Obligation refinement and the verification boundary

## Question

Can the persistent inquiry chain distinguish genuine progress from merely
accumulating prose, and can it eventually close a finite scope without letting
the installed checker silently redefine truth?

The required shape remains one mechanism with three inputs and three outputs:

\[
(\text{frontier},\text{verifier},\text{packet})
\longrightarrow
(\text{decision trace},\text{scoped result},\text{residual frontier}).
\]

## Additive boundary

The two committed inquiry frontiers are immutable. The experiment therefore
does not add variants to `InquiryObligationStateV0`. It creates a
`VerificationFrontierV0` whose origin is the complete sequence-two frontier
and whose first five nodes exactly reproduce its five typed questions.

The method is a separate `verification.adva` file. Each transition stores its
digest. An installed CLI update cannot reinterpret the edge without producing
a different method coordinate or an explicit migration.

## First refinement

The `custody` hypothesis names six required observations. Type elaboration
splits the characteristic-adapter requirement into one leaf for each domain,
so the first packet produces eight leaves:

| Class | Typed leaf | Parent |
| --- | --- | --- |
| semantic | time characteristic adapter | time characteristic |
| semantic | space characteristic adapter | space characteristic |
| semantic | construction characteristic adapter | construction characteristic |
| semantic | ordered holonomy replay | multiplicative holonomy |
| semantic | concrete external coordinate | common truth coordinate |
| semantic | independent measurements | common truth coordinate |
| semantic | shared-coordinate transport | common truth coordinate |
| custody | recovery, rotation, and fork drills | orthogonal preservation ledger |

Thus the broad count changes from five open semantic roots to seven open
semantic leaves plus one custody leaf. This is not evidence of either progress
or regression by itself. The gain is that each remaining demand now has a
typed coordinate and explicit ancestry.

## State and closure

The finite state vocabulary is:

```text
Open
Refined { children, basis_digest }
Discharged { witness_digest, verifier_digest, scope_digest }
Reopened { prior_witness_digest, counterevidence_digest }
```

For a verification frontier \(F\), the implemented closure predicate is:

\[
\operatorname{Closed}(F;S)
\iff
\operatorname{OpenSemanticLeaves}(F)=\varnothing
\land
\operatorname{UnresolvedForks}(F)=\varnothing.
\]

Custody leaves are counted separately: a semantically closed statement can be
poorly preserved, while a perfectly preserved record can be false. A scoped
certificate records the method and discharge-witness coordinates. It is not an
eternal theorem; counterevidence appends `Reopened` without erasing the earlier
certificate.

## First method boundary

Version zero has no typed discharge predicate. It accepts refinements, retains
forks, and can represent reopening, but a discharge request containing only
witness and scope digests is emitted as a rejected decision. This is a
substantive negative result: content addressing can secure lineage but cannot
decide any of the five arithmetic questions.

The first run is:

```console
cargo run -p adva-witness --bin adva -- \
  verify \
  programs/bootstrap-0/frontier-2.adva \
  programs/bootstrap-0/verification.adva \
  programs/bootstrap-0/refinement-1.adva \
  --output programs/bootstrap-0/verification-1.adva \
  --frontier-output programs/bootstrap-0/verification-frontier-1.adva
```

The emitted transition must report semantic leaves `5 -> 7`, custody leaves
`0 -> 1`, no certificate, and an open residual frontier. CI repeats the run and
requires byte equality with the committed artifacts.

## First recorded result

The first bounded verification run completed with the origin inquiry frontier
unchanged:

| Artifact | BLAKE3 coordinate |
| --- | --- |
| origin `frontier-2.adva` | `ae23c007227cf0665fd2928dfb5adb41c2d23923649f867b128bdd6533deb39c` |
| verification method | `fd0e40317c10bc3d95183b3a84efa9405ef7f1199bdbf38f6d4efb1de6b48861` |
| refinement packet | `6d0386047a38dab275a677d653f316a046a1c504e74d680aa015483ca19b30fb` |
| verification transition | `ca98f26cfcd80375d26e2372bfd37417d70e563ad7747adc00a093647e5e79dc` |
| residual verification frontier | `bf0bfc721c7beea6e20d240846f390404ca9b4dc26158027cd95aa9d3484db91` |

The transition contains one applied refinement outcome, thirteen total nodes
(five refined roots plus eight open leaves), no unresolved fork, and no scoped
certificate. The parent list is deliberately sorted by stable artifact
coordinate in the decision trace; each child retains its specific parent and
the packet digest that caused the refinement.

## Falsification boundary

This experiment does not supply \(\chi_T\), \(\chi_S\), \(\chi_C\), ordered
holonomy one, or a shared external truth coordinate. It performs no physical
measurement, signature verification, independent observation, reconstruction,
or governance operation. The state machine can expose and preserve claimed
discharges; only a later versioned method with a typed, replayable predicate may
authorize them.
