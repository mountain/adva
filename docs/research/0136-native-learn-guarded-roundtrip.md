# Research 0136: Native learn with guarded reverse and retained history

Date: 2026-09-06. Status: proposed Rust implementation; native execution pending.
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
versioned method and source. Changing the filename does not change its type or
register a new executable method in the CLI.

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
reports, and retains the binary, frontiers and transitions. Initial formatting
is captured by CI because no local rustfmt is available; existing CI still
requires the committed source to pass its formatting gate.

## Costs, integrity and remaining obligations

Six fuel units count new protocol stages. Replaying prior prefixes performs
0+1+2+3+4+5=15 additional stage reconstructions across the six main calls.
Replay, normalization, guards, serialization, process setup and build costs
are not six constant-time units. Runtime and memory measurements are pending.
No speedup or increased expressiveness is claimed; there is no comparative
search experiment. File size is not a memory measurement.

Each input/output is limited to 128 KiB. Output paths must be new. Saving the
transition and next frontier is not a two-file transaction; a partial save
returns an explicit error. The file protocol has no external monotonic account
service: a copied or truncated valid old prefix can be forked. It guarantees
consistency of the submitted single history, not global prevention of replay
or resource duplication. Hashes are integrity coordinates, not authentication
or native semantic identities.

Seven targeted tests cover a completed local trace, tampering/schema rejection,
fuel, A/M separation, a retained zero failure, disconnected ratio cancellation,
and reuse. At this writing they have not run. Local adva/cargo/rustc/rustfmt are
absent; a toolchain download request was cancelled at network approval. No
external interpreter substitutes for native execution. CI results and the
actual learn.adva artifact must be recorded before claiming execution success.

This helps Mingli and a later agent inspect a small native reverse/guard
boundary. It does not yet demonstrate value on Jiamin's real task. The next
small extension would be an explicitly supplied task-relative free predicate
with one accepting and one rejecting instance; it should reuse these guards.
