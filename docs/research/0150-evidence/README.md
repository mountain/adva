# Research 0150 — executed library change

One standalone workflow completed locally on 2026-09-06 under the frozen
[contract](../0150-persistent-library-epochs.md). It bootstrapped/rechecked
the old proposal, published epoch 0, loaded that file into fresh Rust state,
performed exactly one new epoch, published epoch 1, dropped the in-memory
handles, reloaded epoch 1 and reused its native witness. No trial retry or
extra learning round ran. Code and contract were not edited after execution.

## Observed change

| Reading | Epoch 0 | New epoch before added observation | Epoch 1 |
| --- | --- | --- | --- |
| Retained catalogue size | 4 | 5 | 5 |
| Active ordinals | [1,2] | [1,2,4] | [1,2] |
| Polynomial question | FeatureClosed: 2x | Open: 2x or 2x^2 | FeatureClosed: 2x |
| History length | 5 | 5 | 6 |
| Stored native word | 2*x / x+x pair | Not published | Identical pair and node keys |

The one additional candidate is `2*x*x`. The one additional observation is the
supplied calibration assumption `f(2)=4`, not a physical measurement or a
deduction from the old catalogue. Rust computed 4, 4 and 8 for active candidates
1, 2 and 4, respectively. It retained the refutation of candidate 4 and restored
the old feature without deleting the new syntax or any old history.

The native ArithmeticTransition/Seal pair is derived with the existing
`WitnessStoreV0`, persisted in each snapshot and rebuilt on load. The root key
in both epochs is:
`blake3:a521490f03bccac1209ae92ad555ebfaf2218bb1d2ba6339a6c8307cd490426f`.
Guarded reuse after the final disk reload returned `[4,4]` at input 2. The
nonzero obligations remain stored; this is not an ExecutedCell, a new stable
operation, or program identity. No new mathematical theorem was discovered.

The [raw workflow report](run.json) confirms `same_word_content=true`,
`reload_matches=true` and `parent_bytes_unchanged=true`. Both snapshots are
actually present under [adva-library/stability](../../../adva-library/stability/README.md).
This completes the bounded check/publish/load/reuse path that 0149 lacked.

## Costs and artifact integrity

The single new workflow spent **870 / 50000** shared logical units, including
its prepaid final checkpoint, source import, ancestry replay, publication,
disk reload and guarded reuse. The previous 0149 account and its 1089 spent
units were not changed. This is the explicitly authorized 0150 allowance,
not a global resource service or an automatic refill of a running process.

[Native cost](native-cost.txt): 0.12 seconds wall time, 0.04 seconds user time,
peak RSS 6652 KiB and exit 0. This one local measurement is not a speedup claim.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| epoch-0000.json | 11968 | 27016fc510e067caa930eb4e75b0d445342d4c1bc611dcf5b2577644e96ff8bb |
| epoch-0001.json | 14529 | eafbee5a0e8d56d326088c608ee34e3f5557c55a9f1cdb40feb7aa73342013bb |
| run.json | 38815 | d858b7bc8a0c97b24a61b9ba452a167f52b141306e9811147e036f2101029f29 |

Checker source SHA-256:
`7e4c5abd0f8224cc0f7cd9092928394cc2fbc81a9b5b9b255834d04977d2b975`.

Driver source SHA-256:
`5bedf897add38b80855deaa58beec56b2190c763f8dc1fbb8e813907a173eb6f`.

Contract SHA-256:
`a7c0a63581e748ec29d5fc37d9f08443b48c3e47c5abb43e90db6ce4f5466ec7`.

Canonical snapshot BLAKE3 coordinates are distinct from hashes of pretty file
bytes: parent `4a86b8c7aaf99369254df6972e22ab20d7f433253c007f81d96acb91e9e320a9`,
successor `4480fa1e8b60ab945879f8644820ab8ef242dceaf494470bedb9b68b5fd976ee`.
They bind content but do not authenticate observations or provenance.

## Validation ledger and limits

- Targeted pass 1: standalone example built successfully under timeout 180s.
- Targeted pass 2: all 9 new integration tests passed, then the example built;
  timeout 180s. No third targeted pass was needed.
- Clippy workspace/all-targets/all-features with `-D warnings`: passed under
  timeout 180s; one pass, no repair pass.
- Full Rust workspace regression: **211 tests passed**, including the 9 new
  integration tests, under timeout 180s.
- Changed Rust files pass rustfmt and `git diff --check` passes. The unrelated
  prior prime-checker formatting mismatch and old dangling claim dependency
  remain untouched; they were documented in the 0149 evidence record.

No executed build/test command failed. Tests cover stale parent/delta,
tampered inputs/certificates/witnesses/method, zero-guard refusal, duplicate
publication, partial files, bounded input, symlink/path rejection, shared-fuel
exhaustion and Open/ModelGap refusal. They use isolated temporary fixtures,
not additional production epochs. Python and braid regressions were not rerun
for this Rust-only persistence change; existing Rust Q4/M6 tests passed as part
of the full regression.

The actual standalone invocation used timeout 20s, address-space limit
`ulimit -v 524288`, file-size limit `ulimit -f 1024` and `/usr/bin/time -v`:

```text
target/debug/examples/library_epoch
  docs/research/0149-evidence/study.json
  adva-library/stability
  docs/research/0150-evidence/run.json
```

The successful no-clobber publications removed only their own temporary hard
links after syncing the final snapshots. No prior library document, snapshot,
0149 source, contract or evidence was changed. An interrupted future workflow
could leave a staging file or committed prefix; it must not be auto-restarted.
There is no latest-pointer update, concurrency protocol, authenticated world
input, stable native learner, free operation, or open-world convergence proof.
