# Re-receiving the frozen bounded-interpreter archive on a second host

Status: completed receiving-only reproduction on a different host and a different
Rust toolchain, 2026-09-16. No new research question, campaign or claim. Base:
`e75398b8de468d3e3efe2e2837b4c289ec63b754`.

Direction: Mingli Yuan. Reproduction, checks and record:
deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted through Mingli Yuan's
GitHub account (`mountain`) as an authorized proxy; not his authorship, review,
endorsement or guarantee. No independent human review. The machine under test is
the one recorded in
[the interpreter report](bounded-native-data-interpreter.md); this note writes no
new instruction, profile or campaign.

## Question

The report claims its checkpoints, source snapshots and CLI bytes are retained
"for historical replay". Can that archive actually be re-received from its own
bytes on a host and a toolchain other than the ones that produced it, and do the
recorded numbers reappear? A receiving-only call grants no object-execution
quantum, so this is a retention and portability check on retained evidence, not
another research run.

## Host pair

| Coordinate | Frozen campaign | This reproduction |
| --- | --- | --- |
| Host | Linux workspace `/workspace/scratch/530db4618454/adva` | macOS 26.6.2 (25G83), arm64, Darwin 25.6.0 |
| `adva` binary SHA-256 | `fff178de94592ffe41e21dd99fda8c29fee3ab9cc21ed563f6f44db2251ff9e8` | `87828c72929d5de285cbabe6ba716691285d53190c1ae4411e50070dc816cb8c` |
| Compiler | Rust 1.98.1, as recorded for the build-environment repair | cargo/rustc 1.96.1 (2026-06-26) |
| Snapshot `rust-toolchain.toml` | `channel = "stable"`, clippy and rustfmt, minimal profile | byte-identical to the snapshot copy |

Build: `cargo build --locked -p adva-witness --bin adva`, exit 0. The two
binaries are different files; only the profile digest below is equal.

## The documented sample and its controls

Run into fresh output paths, exactly as
[the program instructions](../../programs/bounded-interpreter/README.md) direct:

| Step | Observed | Recorded in the report |
| --- | --- | --- |
| `--fuel 2048 --quantum 17`, output a prefix | `Suspended`, exit 0, 17 trace edges, `pc` 20, segments `[{0,17,replayed 0}]` | suspension after 17 instructions |
| resume that prefix, `--quantum 2048` | `Returned`, exit 0, 134 edges, segments `[{0,17,0},{17,134,17}]`, `pc` 49 | 17 replayed checking steps inside 134 total |
| final registers of the resumed run | `temp` = 14, `left` = 14, `right` = 12, `tag` = 1 | `2 + (3 * 4)` returns 14 |
| `--quantum 0 --check` on the prefix | `Verified`, exit 0, `verified_steps` 17, `pc` 20 | receiving-only reception |

Three distinct refusals were also reproduced, because they are easy to conflate:

- resume with changed original fuel `2048 -> 2049` gives `adva: fuel exceeds
  profile`, exit 2, no output file — that is the declared lifetime cap, not the
  checkpoint comparison;
- resume with a checkpoint lineage at fuel 17 gives `FuelExhausted` with segments
  `[{0,17,0},{17,17,17}]`: the prefix is checked again and no new instruction is
  granted, so exhaustion stays exhaustion;
- resume of a lineage recorded at fuel 17 while supplying fuel 18 gives `adva:
  checkpoint context mismatch`, exit 2, no output file — this is the independent
  context comparison;
- resuming an already terminal artifact gives `adva: terminal execution cannot
  continue`, exit 2, no output file.

## Receiving the whole frozen archive

Both retained archives were unpacked to a scratch directory (836 files each) and
every checkpoint artifact in them was re-received with the locally built binary:

```sh
python3 -B experiments/bounded_native_interpreter/cross_host_replay.py \
  --binary target/debug/adva \
  --evidence experiments/bounded_native_interpreter/evidence/attempt-1 \
  --workdir /tmp/adva-cross-host-replay
```

Each call supplies the retained program, input and original fuel independently
and asks for reception only (`--quantum 0 --check`). A reception counts as
matched when it exits 0 with `Verified` and its `verified_steps`, final `state`
and `profile` equal the retained artifact.

- 150 of 151 artifacts per archive matched: **300 of 302** across the pair.
- The one skip per archive is `reception.run.adva`, itself a receiving-only record
  (`profile`, `state`, `verified_steps`) rather than a checkpoint, so it has no
  original fuel and nothing to resume.
- The retained outcome ledger reappears per archive: 136 `Returned`, 9 `Rejected`,
  4 `FuelExhausted`, 1 `Suspended`.

One reading needs stating explicitly, because it is the natural way to misread
this table: reception of a `Rejected` artifact also returns `Verified`. Admission
verifies the retained record — program, input, whole trace, final state — and does
not re-run the rejection or restate a terminal status. `Verified` therefore means
"this retained record is admissible and its execution rederives", never "the
recorded run succeeded". An earlier comparison of mine compared the reception
status against the retained terminal status and reported a spurious mismatch on
300 artifacts; that comparison was wrong, not the machine, and the corrected
comparison is the one above.

## The continuation is byte-identical, not merely re-verifiable

Resuming the retained `prefix.run.adva` with the locally built binary produced an
output byte-identical to the retained `resumed.run.adva`: 26,130 bytes, SHA-256
`145b6919aad6f85ea5163290019a07fb001c758186ce2ec58ab5b2b4b5c7d6af`, with all 134
trace edges equal on `pc`, `next_pc` and `state_digest`. The retained artifact is
reproducible from its own inputs on this host, not only checkable.

## Why a retained checkpoint travels at all

`data_machine_profile_v0()` hashes the fixed label `adva.data-machine.transition.v0\0`
together with `include_bytes!("data_machine.rs")` and
`include_bytes!("../../../Cargo.lock")` (`crates/adva-witness/src/data_machine.rs:200`).
The profile is therefore a compile-time function of declared source and lock
bytes, not of the host, the toolchain or the build artifact. Reading the source
gives the construction; an independent Python recomputation from the current
repository bytes and the digest computed by the locally built binary agree:

```text
independent recomputation from current repo bytes: 6e8427f5c1872067377a06bc5830f926e8f39c13017f902ddeb58e509466d46b
digest observed by the binary built here          : 6e8427f5c1872067377a06bc5830f926e8f39c13017f902ddeb58e509466d46b
digest recorded by the frozen campaign            : 6e8427f5c1872067377a06bc5830f926e8f39c13017f902ddeb58e509466d46b
```

The frozen `results.json` records the same digest, as do all 300 retained
artifacts. That equality is why a checkpoint outlives the machine that wrote it —
and it is also why a source edit invalidates old checkpoints, which the report
already records.

## Gates run here

- `cargo test --locked -p adva-witness --test data_machine --test data_machine_cli`
  — 12 and 4 tests passed, 0 failed. The same gate the report records, re-run on
  this host.
- `.venv/bin/python -m pytest tests/python/test_bounded_native_interpreter.py -q`
  — 4 passed, including the independent Python instruction receiver over the
  retained archive (16,911 state edges) and the profile recomputation. This test
  receives saved bytes and launches no campaign.
- The whole Python suite on this host: 2730 passed, 11 failed, 1 skipped. All 11
  failures have one host cause and are not a reading of the code under test:
  every runner that installs child limits through `preexec_fn` sets `RLIMIT_AS`,
  and on this macOS host `resource.setrlimit(RLIMIT_AS, ...)` raises
  `ValueError: current limit exceeds maximum limit`, so the preexec function
  aborts and the child reports `Exception occurred in preexec_fn.` (7 failures
  and 3 subfailures in `tests/python/test_phase_runner.py`, 1 in
  `tests/python/test_pascal_commutator_certificate.py`). Linux CI can install
  that limit. No limit was relaxed and no test was adjusted to hide this.

## What this supports

- The retention claim, in the strong form: the archive is re-receivable from its
  own bytes alone on a different host and toolchain, and one continuation
  reproduces the retained output byte for byte.
- The report's headline finite numbers reappear here: 134 instructions returning
  14, a 17-step prefix with 17 separately counted checking steps, exhaustion that
  stays exhausted, and the separation between the declared fuel cap, the
  checkpoint context comparison and runtime rejection.

## What it does not establish

- No new question is asked or answered. `adva` still does not interpret its own
  instruction language, and nothing here decides the next dependency the report
  records — a checked translation between this machine carrier and the
  program/process boundary, or a separately scoped extension admitting the
  interpreter's own instruction grammar.
- Receiving grants no quantum: no object execution was re-run, no campaign, fuel
  or search was created, and the frozen contract is untouched.
- One host pair and one compiler. Different binaries happened to agree; that is
  not a reproducible-build claim, only what the profile digest binds.
- The archive contains the implementation it exercises, so this tests the
  portability of a record, not the independence of the implementation, its
  arithmetic oracle or its review.

## Files

The reception checker is retained as
`experiments/bounded_native_interpreter/cross_host_replay.py`. It extracts the
retained archives into a scratch directory, replays checkpoints receiving-only
and compares them with the retained artifacts; it never launches an execution
quantum. No new evidence directory is added, because the inputs of this check are
the already-retained bytes. `docs/claims.toml` is unchanged: this note adds no
claim, only a re-reception of an existing one.
