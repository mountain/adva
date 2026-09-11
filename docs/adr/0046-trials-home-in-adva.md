# ADR 0046: The trials tree lives in adva, and AEG keeps only its history

- Status: accepted for the migration step; the AEG backup is done, the
  retirement step is open
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

## Update 2026-09-11: the AEG backup, and where the Human layer goes next

**Backup done.** The retiring repository now has a private remote, because it
had none and its non-trial content exists nowhere else: 1,512 of the 2,700
unique blobs under `.campaign/` are absent from this repository, so the earlier
assumption that `docs/research/0162-evidence/` already covered the campaign was
wrong to rely on.

- Remote: `git@github.com:mountain/adva-aeg.git`, **private**, one branch.
- Tip at first push: `dc639c65e503a554e18ebe48bc65e627a0b63c01`, 56 commits,
  9,922 objects, 58.57 MiB pack. The first push includes a commit that records
  the six round-05 files, so the backup no longer depends on this repository
  for them.
- Verified: local tip equals the remote ref, the working tree is clean, and the
  repository reads back as private.

**Handover (directed by Mingli Yuan, 2026-09-11).** The Human-layer working home
moves to `~/AEG`, the 7.7 GB cluster of about thirty projects and 23 git
repositories that already holds `process-geometry`, `knot-alexander`,
`aeg-lm`, `aeg-multiplication`, `aeg-shakespeare`, `aeg-topological-order` and
the rest. This answers decision point 5 of the six-repo proposal, which asked
whether that cluster is the Surface-side source of trials and objects: it is.

The boundary that keeps the migration from unravelling: **`trials/` here stays
the record home** of the trial tree, its receipt ledger and its feed, while
`~/AEG` is where new lines are worked. Results return by the existing
cross-repository rule — a byte-pinned receipt or an evidence registration here,
catalog admission in `adva-library` when the result is knowledge.

**Still open.**

1. Retirement mechanics: move the repository directory aside, and leave a stub
   at `/Users/mingli/Adva/AEG` holding one `trials` symlink so the 17 hardcoded
   root constants keep working without editing trial bytes.
2. **Done 2026-09-11.** The cluster has a top-level index at `~/AEG/README.md`,
   byte-identical to [`docs/maintenance/aeg-cluster-index.md`](../maintenance/aeg-cluster-index.md)
   here, and the two split proposals are copied to `~/AEG/_adva-bridge/`. The
   originals stay in the retiring repository until its retirement step runs; that
   repository owns a private backup, so the map is no longer single-copy.
3. Risk items measured in `~/AEG` before it becomes the working home: `brain`
   has no remote, no commits at all and a detached HEAD with 15 uncommitted
   files; `optaeg` (28), `cayley` (28) and `autoresearch2` (34) carry
   uncommitted work; `dags`, `gru`, `moc` and `thermal` are not repositories at
   all. The index records each of them rather than implying they are managed.

