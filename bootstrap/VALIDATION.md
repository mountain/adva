# Bootstrap runtime v0: executed validation

Date: 2026-09-09. Source base: `1037b433851392a1a9cb0f0e954757a300d6df8b`.
Library: `7496a5c893fadf5d72fd29cf7ad5a63f42586b4b`.
This is engineering validation, not a new mathematical claim or knowledge epoch.

## What was actually built

The authenticated GitHub connector supplied the source files at the pinned
commit. This execution environment had no Rust toolchain and no authenticated
Git checkout. Rust 1.94.0 was installed, and the existing native target was first
built to establish that the unchanged base could compile. Downloaded original
files were compared with their Git blob IDs. Only the intended CLI dispatcher
changed among those original files; the new library CLI is an additional file.
All existing semantic/checker sources and Cargo.lock remained byte-identical.

The packaging script then created a **63-file** source archive, including the
62 pinned inputs and the input list itself. Its SHA256 was
`f158db9cc54f18235979180771a725db0b18ebac0d4b6429157d052f4e25467e`.
It was extracted into a new directory without Git metadata. The build script
compiled from that directory with a fresh target directory, then ran the copied
binary against copied library epochs from a separate working directory. Rust
and Cargo download caches were already populated. This tests an isolated source
bundle and clean build outputs, not a newly provisioned machine or an offline
dependency bootstrap.

## Results

- Native release build from the extracted archive: passed.
- Eight saved-report acceptance conditions: passed, including exact integer
  reuse at 2, guarded refusal at 0, retained snapshot and unchanged library bytes.
- New actual library instance at -3: `ReuseChecked`, values `[-6, -6]`.
- Actual zero-fuel request: `Unknown`; wrong expected digest: `Rejected`.
- Five Rust CLI test groups: passed (exact reuse, guard/input/word/fuel/pin
  boundaries, tampered/schema-mismatched snapshots, destination/options,
  missing epoch). These construct synthetic epochs and require no private
  library access. Command: `cargo +1.94.0 test --locked -p adva-witness --test library_cli`.
- Seven existing native-run CLI regression tests: passed; raw output retained.
- Three corrupted saved-report controls: wrong values, substituted snapshot
  digest and modified library bytes all refused by the protocol checker.
- Targeted Clippy with warnings denied and workspace formatting: passed.
- Python syntax and Bash syntax checks: passed.

The new CI workflow runs the native CLI tests and build without presuming
private submodule credentials. It does not stand in for the real-library run
recorded here; remote CI status must be checked separately.

## Costs and preserved limitations

The source-archive build plus four command calls took **76.874803 seconds** wall
time. Child user/system CPU were 240.626721 / 17.647267 seconds. Linux reported
maximum child RSS of 1,075,488 KiB (about 1.026 GiB); this is not the simultaneous
aggregate memory of all build processes. Later three actual calls plus report
checks took 0.023259 seconds, with reported maximum child RSS 11,136 KiB. See
`evidence/clean-build-cost.json` and `evidence/acceptance.json`.

Toolchain installation, the earlier base build, authoring, unit-test builds,
Clippy and network time are outside those measured intervals. They were not
fully metered; these numbers are not the entire implementation cost or a
speedup claim. A preliminary `/usr/bin/time` wrapper failed with exit 127
because that tool was absent, before the build script began. Its original
diagnostic remains in `evidence/clean-build.log`; the actual measured invocation
used Python subprocess/resource APIs. No arithmetic failure was relabelled as
success and no research campaign was resumed.

The executable SHA256 is
`b77954194eaffb085d2dbf823d92b942ccf0fffcd7cb99dee8868e8ad5adc598`.
The machine-specific executable and generated archive are not committed; they
are reproducible deliverables of the retained scripts and inputs. No claim of
identical executable bytes across machines is made. `bundle.sha256` retains the
original bundle-relative paths; the equivalent reports are copied byte-for-byte
beside it. The complete input manifest and library source pins remain available.

## Remaining obligations

1. Validate additional OS/architecture/linker combinations before advertising
   support beyond the tested Linux x86_64 path.
2. Decide dependency vendoring and third-party notice packaging before an
   offline/distributable release. Existing private licenses remain in force.
3. A general catalog/import/run API needs explicit per-schema adapters. This
   version supports only the existing bounded epoch snapshot profile.
4. General self-interpretation, new arithmetic domains, native learning/free,
   historical-anchor authentication and Quine-based compiler bootstrapping
   remain outside this adapter change.

The immediate reusable outcome is a source bundle that an authorized user can
compile and use with its two fixed library epochs, without Python in the runtime
or either repository's Git metadata.
