# CI checkout and historical library replay — 2026-09-15

Authored by ChatGPT (OpenAI), through Mingli Yuan's account as authorized proxy;
no human authorship, review or endorsement is implied.

CI now checks out full history and recursive pinned submodules. The preceding
run lacked library artifacts and could not check a pinned base ancestor. The
first repaired run exposed a second failure: the historical 0150 snapshots bind
checker revision 34f4d38420963c49809aa09c5fd7258f0247faaac6caba89221650356e941b27,
while the live revision is 0a040fad89315214a668440f92cdbd4e027364e353c477d29adfb3b22ddde6cb.

The five checker source files are unchanged. Commit 41fa9b6 added the macOS
PyO3 build dependency to Cargo.lock, and the entire lockfile participates in
the fingerprint. Rejecting the old snapshots is the existing boundary working.
The macOS fix and strict loader are retained.

scripts/check_frozen_library_ci.py verifies that those five sources and the
library-generation example still equal the explicitly pinned pre-change commit
caabb28b95bb7484680b8d0039fd5a571de421d6. It prepares a separate source snapshot
with that revision's Cargo manifests and dependencies, copies only the two
hash-pinned epoch files, and runs the unchanged 12 example tests there. It also
requires the live CLI to reject the old snapshots for the expected fingerprint
reason. No production snapshot is rewritten, admitted or rehashed.

This is historical receiver replay, not automatic compatibility of the live
runtime. A future source change stops this bridge until a new compatibility
assessment. Current workspace, numeric and other CI checks stay on current code.

Local preparation, exact source comparisons, both snapshot SHA-256 checks, and
Python syntax checks passed. BLAKE3 recomputation confirmed both revisions above.
Rust execution requires the CI toolchain; its result is reported by CI.

## Follow-up checks and corrections

The first isolated replay preparation omitted the labs-search workspace member;
CI caught the missing Cargo.toml before any test ran. The archive now includes
that member, and preparation checks every declared workspace member manifest.
The repeated local preparation passed.

The Python CI failures dropped to one after checkout was fixed: golden-ratio
replay required Linux's successful address-space limit installation to equal
a retained macOS refusal. The test now separately validates complete, disjoint
installed/refused limit records and each installed value against the budget,
then compares mathematical evidence independently of those host observations.
The old report is unchanged. All 11 golden-ratio tests pass locally.

CI run 34977846731 then passed the live stale-fingerprint refusal but exposed
another archive omission during historical compilation: the example embeds
research note 0151 with include_bytes!. Frozen docs and programs now accompany
the source archive. Preparation also checks literal include_bytes!/include_str!
paths in the dependency sources and selected example, so this class of missing
compile-time input is detected without a Rust compiler. These inputs come from
the same pinned commit; current documents do not reinterpret the old experiment.
