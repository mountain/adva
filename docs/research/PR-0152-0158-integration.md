# Integration of PR 158 and PR 152 — 2026-09-09

The user authorized merging the open PRs. The order is PR 158, then PR 152.
Neither experiment depends on the other's findings. PR 158 was already based
on current main; PR 152 required integration with later mainline claims.

## Documentary identity and historical pins

Two independently authored records used Research 0158. Cite the full title
or PR number to distinguish them:

- [PR 152: Opening equation and anchor binding](0158-opening-equation-and-anchor-binding.md),
  authored on 2026-09-07; its historical evidence is under
  `0158-evidence/run-01`, `run-02`, and the associated manifest.
- [Mainline: Downward interpretation and Mingli's drop route](0158-downward-interpretation-and-drop-route.md),
  dated 2026-09-08; its evidence is under
  `0158-evidence/downward-interpretation-v0` and
  `0158-evidence/mingli-drop-route-v0`.

The paths do not collide. Original experiment sources, contracts, witnesses,
and manifests are preserved byte-for-byte; numbering is not retroactively
rewritten inside hash-bound evidence. These studies have separate scopes.
Research 0163's description of PR 152 as an open draft records its audit-time
state, before this integration.

The PR 152 manifest's whole-file pins for claims.toml and the 0156 note belong
to original commit `ead118080f5f80c4b2a9597df1c4bee1fd1f275f`.
Research 0163's whole-file claims pin belongs to
`2b047781b848387fa186239c2ce5b30bab8f6b5e`.
Use those commits to audit those historical files. The merged claims registry
contains both additions plus all later mainline claims. Historical manifests
are not current-main checksums. The lineage implementation remains identical
to PR 152's pinned source.

## Merge validation and limitations

- PR 158 bounded replay: PassedFiniteCalibration; 7200 entries and all three
  controls retain their expected results.
- PR 152 bounded replay: CounterexampleRetained; ten controls, ten replay
  checks, 48 repository API calls.
- No archived experiment output was overwritten by either merge replay.
- CI on the reviewed heads reported failures with no runner and no execution
  steps. A log download returned BlobNotFound. The cause is not established;
  this is not a passing CI result or a full Rust/Python regression claim.
- Merge integration combines the claims and retains the mainline library
  submodule and all other mainline paths. It changes no stable semantic code.

The two proposed terms remain Proposed. Merging evidence does not establish
universal grammar, native free, or social trust.
