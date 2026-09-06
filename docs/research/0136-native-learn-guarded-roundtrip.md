# Research 0136: Native learn with guarded reverse and retained history

Date: 2026-09-06. Status: native bounded experiment; proposed integration in draft PR 136.
Base: `57c1d04bcfe51b82f6e559a61ca02e668f630b5a` on main.

## Question and boundary

Mingli explicitly authorized Rust implementation after the learn-only preflight.
The repository already implements `adva` in Rust. Can one additional, bounded
method advance six native `adva learn` calls, preserve the witnesses, and close
a specified arithmetic round trip without erasing failure or history?

This branch uses main's Research 0107 witness kernel and existing learn CLI.
Draft PRs 130--135 are context, not merged dependencies or native certificates.
The paused unknown-syntax-building experiment is not resumed. This experiment
does not address universal grammar completeness or the full free objective.

The frozen contract is `0136-native-learn-roundtrip-contract.json`, SHA-256
`016cb5c2552d6716f84f9e9fa548e2f7b9220a340ed145324d52a412954e4b95`.
There is one supplied recipe, zero search candidates, and no adaptive expansion.
Inputs are three integers in [-16,16], fixed syntax p=x+y*z, q=2*p, and existing
exact integer-polynomial residual arithmetic. The concrete main input is
[2,3,4]; [5,2,3] is the reuse test, and [2,-1,2] is a zero-guard refusal test.
We test these cases; we do not claim to have enumerated all 33^3 environments.

## A=0, reverse, and M=1

In the current kernel, A is actual minus declared formation boundary. A=0 is
formation success, not a runtime zero or a reason by itself to reverse. The
forward edge p to q is formed but has nonunit transport M=q/p. The supplied
method requests reverse at this specific A=0, M!=1 stage; this is a fixed
control recipe, not discovery of an inverse from an arbitrary program.

The reverse edge is q to p, with literal endpoint correspondence checked
before native Compose. M for the composition is (q/p)*(p/q)=1. The output value
remains p (14 in the main input and 11 in reuse). All visited leaves and
intermediates must remain nonzero under the kernel's evaluate_guarded rule.

For [2,-1,2], p=0: even though symbolic M becomes one, the retained guard fails.
The fifth call records that failure, leaves one unit unspent, and refuses any
sixth successful seal. Reverse cannot make this failed history admissible.
Similarly, 1 to 2 and 6 to 3 have cancelling ratios but mismatched endpoints;
this pair is rejected as a round trip.

## Six-stage protocol and files

| Call | New action | Required distinction |
| --- | --- | --- |
| 1 | Form common boundary and Unit connector | Formation is not task success |
| 2 | Record p to q and request reverse | A=0 does not imply M=1 |
| 3 | Record q to p after checking endpoints | Matching ratios alone do not suffice |
| 4 | Compose and retain every original nonzero obligation | Symbolic closure is not concrete validity |
| 5 | Check retained obligations in the input environment | A ZeroFault persists |
| 6 | Seal and package local name learn | The interpretation free remains Proposed |

The three input files are under `programs/bootstrap-0/free-roundtrip/`.
Each output transition contains the input frontier, output frontier, stage
record, replay count and final local evidence when available. Every record is
bound to the schema, account and input values. Prior records are rebuilt with
the native WitnessStoreV0 and compared in full; their summaries are not trusted.
The final `learn.adva` is a replay recipe plus records and artifact keys, not
a standalone serialized WitnessStore. Its interpretation requires this
versioned method and source. Reproduction starts from the three initial files;
the current CLI does not load the final Transition as a new method or provide
a standalone verifier command. The boundary test also loads the saved
Transition and reconstructs it from its input history. Changing the filename
does not change its type or register a new executable method in the CLI.

The local evidence name learn records this supplied construction. Its role is
to package a bounded question, ordered actions, guards and checked result for
later readers. It is not learned syntax. free remains Proposed because a
task-relative acceptance condition and a demonstrated human use remain absent.
No source/occurrence identity, semantic program inverse, or M6 filler follows.

## Reproduction

Build with the repository's Rust toolchain and use new output paths:

```sh
cargo test -p adva-witness free_roundtrip -- --nocapture
cargo build --release -p adva-witness --bin adva
mkdir -p target/free-roundtrip
current=programs/bootstrap-0/free-roundtrip/subject.adva
for round in 1 2 3 4 5 6; do
  next=target/free-roundtrip/frontier-${round}.adva
  output=target/free-roundtrip/transition-${round}.adva
  if [ "$round" -eq 6 ]; then
    output=target/free-roundtrip/learn.adva
  fi
  timeout 30 target/release/adva learn "$current" \
    programs/bootstrap-0/free-roundtrip/method.adva \
    programs/bootstrap-0/free-roundtrip/resource.adva \
    --output "$output" --frontier-output "$next"
  current=$next
done
```

The dedicated CI workflow additionally imposes a 180-second outer CLI limit,
256 MiB virtual-memory limit and 15-minute job timeout, records GNU time
reports, and retains the binary, frontiers and transitions. The first native
CI run captured rustfmt output because no local rustfmt was available. The
committed source is corrected to that formatting and must pass the ordinary
formatting gate. Once the resulting learn.adva is committed, the workflow
validates it in the native test and skips another six-call CLI generation.

## Costs, integrity and remaining obligations

Six fuel units count new protocol stages. Replaying prior prefixes performs
0+1+2+3+4+5=15 additional stage reconstructions across the six main calls.
Replay, normalization, guards, serialization, process setup and build costs
are not six constant-time units. The first run's measured costs are below.
No speedup or increased expressiveness is claimed; there is no comparative
search experiment. File size is not a memory measurement.

Each input/output is limited to 128 KiB. Output paths must be new. Saving the
transition and next frontier is not a two-file transaction; a partial save
returns an explicit error. The file protocol has no external monotonic account
service: a copied or truncated valid old prefix can be forked. It guarantees
consistency of the submitted single history, not global prevention of replay
or resource duplication. Hashes are integrity coordinates, not authentication
or native semantic identities.

Seven targeted tests passed in the first native CI run. They cover a completed
local trace, tampering/schema rejection, fuel, A/M separation, a retained zero
failure, disconnected ratio cancellation, and reuse. The correction commit
also binds the completed-trace test to the actual saved CLI transition. Local
adva/cargo/rustc/rustfmt remain absent; a toolchain download request was
cancelled at network approval. All claimed execution happened in Rust on CI.

## Recorded native run

The first run is [Native learn roundtrip 34030868604](https://github.com/mountain/adva/actions/runs/34030868604),
job [101479989710](https://github.com/mountain/adva/actions/runs/34030868604/job/101479989710),
on source commit `209b3bfbc3cb596ce754103e8472903701d9dd93` after rustfmt.
All seven tests, release build, companion clippy and six actual CLI calls
succeeded. The initial ordinary CI formatting gate failed; the next commit
applies the captured formatting. No arithmetic implementation failure or
alternative search route was needed. The six CLI calls are not repeated for
that formatting correction; native tests validate the persisted transition.

The exact generated bytes are committed as
`programs/bootstrap-0/learn.adva` (6722 bytes), SHA-256
`b61c51dca215ce1cdfa5fcffd08f63445c943a1450ea76e40fdc411d1d8d9e5f`.
Its last record has spent=6, remaining=0, additive_zero=true,
multiplicative_one=true, passed guards, and local_close=true. The evidence
retains free_status=Proposed and the original value 14. The sealed artifact key
is `blake3:cc50914525f33c5a9fc35b4c776163a9b9aa927b78ae6de77d85f99d73246eda`.
The [run artifact](https://github.com/mountain/adva/actions/runs/34030868604/artifacts/9988577754)
contains the native executable, all intermediate files and individual time
reports; its configured expiration is 2026-09-13. Source and the final witness
remain in the branch beyond that archive's retention period.

| Measured component | Reported result |
| --- | --- |
| Test-profile compilation | 38.59 s |
| Seven targeted tests together, including reuse | 0.01 s |
| Release build | 1 min 07 s |
| Companion clippy | 13.79 s |
| Six CLI calls with replay and file writes, outer wall time | 0.02 s |
| Outer user / system time | 0.00 / 0.01 s |
| GNU time maximum resident set size for the timed command | 4208 KiB |
| Outer exit status | 0 |

These coarse timings are single CI observations. The memory figure is GNU
time's reported process/child maximum, not total CI memory or the sum of
simultaneously resident processes. Per-call reports are in the archive;
separate normalization, guard, serialization and reuse-only timings were not
instrumented. Tool/network/editing/total research wall time was not measured.
The aggregate CLI time includes construction, prefix replay and serialization;
it is not a measured pure solver time. No physical speedup follows.

This helps Mingli and a later agent inspect a small native reverse/guard
boundary. It does not yet demonstrate value on Jiamin's real task. The next
small extension would be an explicitly supplied task-relative free predicate
with one accepting and one rejecting instance; it should reuse these guards.
