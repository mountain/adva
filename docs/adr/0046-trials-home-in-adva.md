# ADR 0046: The trials tree lives in adva, and AEG keeps only its history

- Status: accepted for the migration step; the AEG retirement step is open
- Date: 2026-09-11
- Relates to: the three-repo split proposal and the six-repo design proposal in
  the AEG repository (2026-09-08), whose decision point 1 asked whether AEG
  remains a separate trust zone

## Context

The trial tree — 397 files of trial artifacts, receipts, ledgers and the feed —
lived only in the local `AEG` repository. That repository has no remote, so the
Human-layer record had no backup, and nobody reading `adva` could see the trials
it refers to. Three shapes were measured before choosing:

| shape | main-repo growth | what it costs |
|---|---:|---|
| migrate with history (chosen) | 52.47 MiB of pack | 17 trial scripts hardcode the AEG root |
| submodule with a pin | ~0 | AEG's checkout path moves, or a second checkout is kept; needs a remote that does not exist yet |
| squashed snapshot | ~52 MiB | loses the 47-commit traceability |

The written cross-repo rule was "one home directory per entry", which a second
full copy would break, and "a repository boundary grants no authority", which
the chosen shape preserves: the trials enter the repository as evidence and
receive no identity by arriving.

## Decision

1. `trials/` at the adva repository root is the single working home of the
   trial tree. It was imported with its history by `git subtree split -P trials`
   followed by `git subtree add --prefix trials`; 47 commits, 397 files, and a
   `git ls-tree -r` comparison that matches the source repository entry for
   entry.
2. The six files that were untracked in AEG at migration time are recorded in
   this repository with their SHA-256 digests, because any git-based import
   would have dropped them silently. Their AEG copies remain untracked.
3. AEG keeps its own history and its non-trial content (`.campaign/`, the stale
   `math/`, `stability/` and `knowledge-boundary/` copies, and the two
   proposals). It is no longer the working home of the trials.
4. No checker, catalog entry, claim, or trial byte changes. `math-check` and
   `claims.toml` are untouched, and the recorded absolute AEG paths inside
   `docs/research/*-evidence/` stay exactly as recorded — those are evidence,
   not live references, and none of the 1,207 recorded references was rewritten.

## Consequences

- Reading `adva` now shows the trials; the operational record, digests and the
  inventory of what did **not** move are in [`trials/MIGRATION.md`](../../trials/MIGRATION.md).
- **Open: AEG retirement.** Seventeen trial scripts hardcode
  `/Users/mingli/Adva/AEG` as a root constant. The plan is to keep that path
  resolving to the migrated tree (a directory holding one `trials` symlink)
  rather than editing trial bytes. Until that step runs, AEG still holds a
  second copy of the working tree.
- **Open: AEG backup.** AEG still has no remote, so `.campaign/` (41,418 files,
  57.61 MiB) and the stale library copies exist on one disk only. Migrating the
  trials did not fix that.
- **Open: two third-party PDFs** inside the migrated tree (an IRS 1040
  instruction booklet and an arXiv preprint) are recorded as facts with their
  unknown parts marked Unknown; the same discipline as the Hilbert photograph
  provenance record.
- **Open: the AEG proposals themselves** still describe AEG as the Human-layer
  working repository; they are outside this checkout and were not edited here.
  They should record this decision, and the number assigned to it, on the next
  pass with access to that repository.

## Verification

- Byte identity: `git ls-tree -r main trials` in AEG versus
  `git ls-tree -r HEAD trials` in adva — 397 of 397 entries identical.
- Cost: `git rev-list --objects e18cf11 --not cb5f62d` — 522 new objects (343
  blobs, 179 trees/commits), 52.47 MiB compressed.
- Digests: the six untracked files, listed in `trials/MIGRATION.md`.
- Suite: with only `RLIMIT_AS` neutralised (see TC-010 in the toolchain watch
  for why that is required on this host), the full Python suite passes
  (2401 passed, 1 skipped, 0 failed). The trials tree is data; nothing in the
  suite reads it.
