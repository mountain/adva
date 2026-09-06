# ADR 0042: Math topics constrain a documentary view, not semantic authority

Status: accepted for the requested catalog engineering only, 2026-09-06.

## Motivation and attribution

Mingli Yuan proposes a `math/` directory containing arithmetic, geometry and
logic, with logic's placement understood as a **降位**: logic becomes research
content subject to explicit assumptions and calibration, rather than gaining
authority merely from its place in a knowledge hierarchy. This is an Adva
organizational interpretation, not a universal historical claim that logic
belonged to metaphysics or a proved semantic lowering operation.

Distinguish the logic being studied from the rules currently checking it.
A candidate logic cannot change the checker used to admit that candidate.
Cataloging rules does not remove the trusted checking boundary or establish
self-verification, objectification, a logic calculus or three-computation.

## Decision

Add an opt-in, version-zero documentary catalog at `adva-library/math/`.
Its manifest describes references once; each entry has exactly one home and
the arithmetic, geometry and logic indexes partition owned keys from external
references. Multiple topic views may cite the same entry without acquiring
ownership, copying, merging or creating semantic identities. A topic tree
is not the topology of knowledge, an exhaustive taxonomy, a triadic observer
policy, or a mapping to compute/verify/learn or Rust/Lean/Metamath.

Entries declare a theory/version, supplied assumptions, finite scope,
recorded status, original material, evidence, checker/version/source
references, reuse requirements, and unresolved obligations. All file
references are repository-relative with SHA256 pins. Names and digests are
documentary coordinates only. The recorded status is an author's declaration,
not a judgment produced by this catalog check.

The Python-only `adva.py math-check` adapter checks strict schemas, duplicate
keys, the fixed topic paths, cross-index coverage, required metadata, bounded
references and file integrity. It rejects unsupported admission fields and
policy changes. It never parses a referenced proof/IR, invokes a verifier,
publishes a knowledge epoch, or uses file names as semantic identities.
`CatalogConsistent` permits browsing declared references, **not** executing
them or trusting their mathematical or historical claims.

Python is appropriate here because these are documentary/transport checks,
not Rust type, program, proof, occurrence or certificate judgments. Existing
Rust loaders and external prover boundaries remain the only applicable
routes to their respective original checks. No new Rust semantic code,
registry operation, stable API, dependency or IR version is introduced.

## Limits and failure behavior

The checker admits at most 32 manifest entries, 256 reference occurrences,
96 files, 256 KiB per metadata file, 8 MiB per referenced file and 32 MiB total
read bytes, with a five-second cooperative deadline. Deadline checks occur
between reads; this is not a hard wall-time watchdog for blocked filesystem
I/O. POSIX descriptor-relative opens reject symlinks in child components and
nonregular files. The supplied root is resolved once and trusted as the
chosen checkout. Use a quiescent local checkout: this is neither an atomic
repository snapshot, authentication nor a security sandbox.

Only four catalog files, two fixed growth-checkpoint files and listed references are read. Other
files are not discovered or admitted, and referenced catalogs are not
recursively loaded. A checksum mismatch or malformed manifest gives
`InvalidCatalog`; a resource limit gives `Unknown`. No retry, repair, search,
proof replay or automatic pin update occurs. Reports always deny native
admission, even on success. Optional CLI report publication is no-clobber.

These finite engineering checks are not a breakthrough trial or a new phase
of mathematical search. The research agenda's specialization, exact-data,
open-logic and intrinsic-compilation prerequisites remain unchanged.

## Preservation and compatibility

The old documentary `index.json`, Pascal documents, epochs, recipe journals,
and Research 0149--0153 proof/checker/evidence files remain in place and
unchanged. The new catalog is not a replacement for any of their formats.
The previous physical/mathematical/logical interface hypothesis remains a
separate attributed research view; a topic index does not silently revise it.

Adding a CLI subcommand necessarily changes the outer `adva.py` source hash.
Historical Research 0153 pins must not be edited to match the new CLI.
Its recorded source remains available at commit
`5d956deaeff5f55bf5ec885a343b91877f53d8b4` (merged by `8c94621`). Use that
revision for the historical runtime envelope. This new catalog check neither
replays nor restarts its 100-round campaign.

## Pascal-rooted growth obligation

Mingli's subsequent instruction requires continuing program growth to respect
directory separation and geometry to grow from Pascal, recorded as a sealed
obligation. V0 fixes the obligation bytes and a documentary `RecordedOpen`
checkpoint under `math/constraints/`; a compiled-in pin rejects editing both
the obligation and its checkpoint to bypass the rule. It is an integrity
checkpoint, not authentication or the existing Rust `WitnessProofV0::Seal`.
The contract explicitly records native Seal NotIssued and discharge Open.

The initial eight documentary keys have fixed homes. New keys must start with
their home-topic prefix. Proposed geometry descendants cite earlier same-home
parents, all of whose paths reach the pinned Pascal root; this ordering excludes
cycles. An external reference cannot serve as a derivation parent. The root
must retain the two original Pascal files with their exact digests. Repeated
topic membership does not weaken any of these conditions.

Q4/M6 is retained as external geometric reference, not an admitted descendant.
Research 0128 already has an external Pascal calculation and exact witness;
its proposed link into this growth line stays Open pending native import and
derivation/coordinate-transport certificates. All geometry candidate entries
remain proposed documents or hypotheses even if their references contain
external proofs. Native geometry successors admitted by this checker: zero.

This enforces documentary gates in the CLI and CI, not filesystem isolation
against arbitrary code, a stable program-publishing API or a proof that all
future edits obey the obligation. Root AGENTS.md also records the constraint
for subsequent engineering. Revisions require explicit review and a new
finite/versioned contract; they cannot be invented inside a search run.

The task-loop capability audit in Research 0154 distinguishes existing finite
arithmetic search, external geometric calculations and test-local logical
procedures from the missing common task transport and native feedback. It
does not add a loop command or restart any mathematical campaign.
