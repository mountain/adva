# Research reference identity: bounded audit and successor clarification

Authored by Codex (OpenAI), submitted through Mingli Yuan's GitHub account
as an authorized proxy. Original documentation and tests under Unknown v0.3.
Account use is not human review, endorsement, or a correctness guarantee.

Audit base: `mountain/adva@cce73004c2b4fbfb87d9ba1ccc66820423273cf6`.
Scope: Research 0258–0261, their publication records, and the research index.
No frozen note, evidence, or historical publication record is changed.

## Two properties, two separate rules

Shared display numbers are permitted by the existing index test. A display
number is not a unique citation identity. New citations should link a full
path, and version-sensitive citations should use the canonical triple
`repository@full-commit:full-path` (or its GitHub blob URL). Never resolve an
ambiguous number by directory order or by selecting the latest file.

The machine-readable companion [identity table](research-reference-identities.json)
pins all five notes in this audit by repository, path, full commit and SHA-256,
with separate introduction commits. It also records four contextual successor
resolutions, without changing the cited historical bytes. This is a bounded
documentary citation table, not a semantic identity registry or native admission.
New entries in this table must supply the same explicit identity fields; tests
reject wrong paths, malformed commits, byte substitutions and invalid locators.
There is no retrospective ban on historical bare numbers and no automatic
whole-repository prose citation linter.

## Provenance and research boundaries

| Path under `docs/research/` | Introduction commit | Scope |
| --- | --- | --- |
| `0259-henkin-witness-completion-and-process-neighborhood-duality.md` | `6704ff5d51344e18f8f903512e2595c6e81d24cf` | Conditional witness transport, collision persistence, proposed faithfulness obligations; no native duality or universality theorem. |
| `0259-event-probes-do-not-separate-identity-rich-carriers.md` | `3fa94a24b713a786f353c96ff16e616146f7ba9e` | Finite counterexample across source, occurrence and history variants; fixed-carrier separation remains intact. Integrated by PR #211 at the audit base. |

Both continue the unique 0258 finite-poset calibration. Neither is a replacement
for the other. The Henkin publication record already identifies its full path.

## Citation findings and successor resolutions

- 0258 has no reference to either later 0259. Both 0259 notes cite 0258,
  which has a unique path within this audit.
- 0260 links the Henkin full slug at line 22. Its bare `Research 0259` at
  line 100 means that same Henkin note, not the event-probe counterexample.
- 0261 lists the Henkin full path at line 235. Its bare `Research 0259` at
  line 204 means that note's outstanding projective-duality, coherence,
  faithfulness and universality obligations. Its bare 0260 references have
  a unique target in this audit and a full-path bibliography entry.
- The 0260 publication record's component label at line 80 abbreviates
  `0181/0185/0258/0259`; its 0259 means Henkin. The 0261 record's component
  label at line 105 abbreviates `0259/0260`; its 0259 also means Henkin.
  These are contextual bibliographic clarifications, not new rights reviews
  or updates to the old admission decisions or their file digests.
- The index already links both distinct files correctly. There is a concrete
  risk of misreading bare numbers, but no wrong-file link was found in this
  bounded audit. Full paths in publication file inventories remain unambiguous.

Every locator above is anchored to the audit commit and source digest in the
table. If source bytes change, re-audit rather than silently reusing line numbers.
The table does not assert that all older research numbers across repositories
are unique, or that citation uniqueness proves mathematical faithfulness.
