# Research 0153: policy comparison followed by 100 frozen-policy rounds

Status: pre-execution contract, 2026-09-06. Research only. The user authorized
comparison, selection of the best measured policy, and then 100 rounds while
away. This contract does not authorize indefinite continuation or new stable
semantics. Read with Research 0126, 0127, 0129, 0152, ADR 0041, and the agenda.

## Question and trusted interface

Does finite exact-syntax visit memory repair the observed zero-gain zigzag,
and does a fixed residual/exploration mixture improve this bounded search?
After a fixed pilot, how do the selected policies behave on 100 new seeded
rounds without further tuning?

The arithmetic grammar, ordered rewrite neighborhood, exact witness checker,
proof exporters, target family, residual, nonzero guard distinction and
external theory interpretations are exactly those of Research 0152. These
are research arithmetic trees, not ProgramTerm, native occurrences, sharing,
or history equality. Lean Int and Metamath complex-class interpretations are
explicit scoped interpretations, not an established foundational equivalence.
Three verifier implementations still do not establish the T/X/K constraint.

Freeze the prior Rust verifier example (SHA256
`ee938cb0589c16cb0765e5c2d9a992e51c9106d59790d2a3bd1c3a461f7b04ca`),
the prior Python verification module (SHA256
`388553cd6293576b5b449ecafe7fba50c2cb8bf6bc93a459a42de110febab6a3`),
Cargo.lock, all old library/checker sources, both epochs and recipe journals.
Do not edit them. The new Rust example retains byte-identical blocks for
arithmetic syntax, rewriting, proof export, task generation, PRNG and negative
calibration. A runtime preflight and tests compare those blocks against the
frozen source. This explicit duplication is a temporary research adapter to
its private example-local functions, not a second definition of semantic
rules. Drift blocks execution. The old module supplies the Python Lean/MM
log-admission functions unchanged.

Use the same pinned Lean 4.24.0 installation and Metamath 0.199.pre binary,
and set.mm SHA256
`cf534eb74bd665c41a3ba8867296ad969e80834c750eea2094f6428e9af1f931`.
Recheck all 47,670 base proofs once in this invocation; 3,008 axioms/syntax
rules remain imported. Repeat all old positive/negative controls, including
false equalities, sorryAx, invalid position, nonduplicate contraction and
guarded zero refusal. Every selected edge is externally verified; no sampling
of proof obligations. The sole outer entry is `adva.py search-campaign`.

## Fixed policies and memory

Each arm has at most 48 selected steps. All policies enumerate and Rust-check
the same neighborhood and retain every selected traversal and candidate score.

1. `random`: the original seeded uniform neighbor choice, without filtering.
2. `tabu`: prefer neighbors whose literal arithmetic tree has not appeared in
   the arm's retained path; choose uniformly among them. If none are fresh,
   relax the filter, record this event and choose among all neighbors.
3. `hybrid`: use the same freshness preference; normally choose minimum old
   residual with seeded tie-breaking. Every fourth selected step (4,8,...,48)
   instead chooses uniformly from the eligible set, regardless of residual.
   Thus at most 12 scheduled exploration steps occur; this number never adapts.

Visit memory contains at most 49 trees, compared by exact arithmetic syntax,
not normalized polynomial, hashing, native identity or observation equality.
No tree or path is deleted. Freshness is a proposal preference, not proof of
irrelevance of a visited state. Forced revisits and uphill/equal-residual moves
remain permitted and recorded. All arm exhaustion is Unknown. This is not
SGD, learned parameters, a shortest-path theorem or a convergence guarantee.

## Pilot, selection and conditional continuation

Run exactly three pilot batches at depths 2,3,4, each containing expansion
and contraction tasks, seeds 1,7,19 and all three policies: 54 arms total.
These are known diagnostic tasks, not a new held-out theorem family. The
random policy's paths must match the corresponding retained Research 0152
paths; changed policy instrumentation is not counted as a new baseline.

Only after all pilot batches pass Rust replay and both external checks,
select one policy **per direction**, ordered lexicographically by:

1. most Reached targets among that direction's nine pilot arms;
2. least declared work: enumerated candidates + witness checks + memory-tree
   comparisons + policy-selection scans;
3. fewest selected steps, including exhausted paths;
4. fixed tie order random, tabu, hybrid.

Each tree comparison/scan is a bounded primitive in this explicit logical
cost model; it is not a measured CPU instruction or latency estimate. Memory
and filter costs are not free. Export/replay and external batch timings are
also reported, but common external batches cannot identify per-policy total
wall cost. Selection is therefore best only under this declared pilot ranking.
Require at least one Reached pilot case for each selected direction; otherwise
retain an insufficient-comparison result and do not launch the continuation.
Do not choose by names or conceal a result favoring the random baseline.

After selection, freeze both winners and perform **exactly 100 rounds**,
numbered 1..100. Round r uses depth `2 + ((r-1) mod 3)`, seed `1000+r`, and
two arms: expansion and contraction with their respective frozen winners.
There is no further baseline arm, tuning, early success selection, restart,
depth increase or library update. New PRNG seeds assess repetition within
the same task family, not unseen mathematical domains. This adds 200 arms.
Unknown arms do not themselves block subsequent declared rounds; a checker
failure, pin mismatch or shared resource limit stops the campaign.

## Protected obligations and receipts

Rust owns candidate reconstruction, exact witness checks, residuals, visit
memory and path traces. Python validates protocol envelopes, ranks already
checked pilot measurements and supervises proof tools; it creates no semantic
identity or mathematical certificate. A batch remains provisional until its
Rust replay and every selected Lean/MM proof pass. Persist a no-clobber
admission receipt for each batch before proceeding, and a frozen selection
receipt before the first continuation. No result becomes a knowledge epoch.

The supervisor checks pins before each backend/checker call and at completion.
Include the native executable, Lean/MM binaries, database, protected library
files and implementation sources in its pin manifest. No concurrent rebuild
of the native backend is permitted during the campaign. Full dependency
checking occurs once, under the pinned database, not once per round. Keep
partial exports/logs on interruption; never label them admitted on a flag
alone. Duplicate/missing arms, mismatched request echoes, inconsistent counts,
missing axiom audits and partial proof-label traces are protocol failures.

## Enforceable finite resources

One invocation in a fresh `0153-evidence/run-01` directory. No internal retries.
At most 254 search arms, 12,192 selected search edges plus four calibration
edges, and one exact Rust replay of every batch. At most 1,560,576 enumerated
candidate visits including replay: 254 * 48 * 64 * 2, where a bounded tree
has at most 63 eligible internal positions. A Rust batch debits a 500,000
work-unit cap before each counted primitive; the shared counter, including
replay, is capped at 25,000,000. The source tree cap stays 127 nodes / depth 16.
Library loading uses at most 200 units per native call and 50,000 units across
all actual calls and replays (208 planned calls, at most 41,600 load units).
Before each native call, reserve its 500,000 work / 200 library unit upper
bounds; after a complete export, charge the actual ledger and release only
the unused reservation. A failed call without a ledger retains the reserved
upper bound explicitly, rather than pretending its work was zero.

The campaign supervisor allows at most **424 children**, **4,800 seconds**
total wall time, 180 wall / 160 CPU seconds per child, 8 GiB child address
space, 32 MiB per file and **512 MiB** retained files. The maximum planned
child count is 421. All base checks, negatives, replay, pin scans, generation,
candidate rejection, selection and checkpointing consume the same wall
account. Reserve five seconds and one MiB for the final checkpoint. Each child
is also bounded by remaining shared time. Run the outer CLI under Linux
`timeout --signal=TERM --kill-after=5s 4795s`; SIGTERM triggers an Unknown
checkpoint where possible, with the outer tool providing a hard final bound.
Memory/file/fuel exhaustion and missing checkpoint evidence remain explicit.
There is no claim of resumability after a failed checkpoint.

Compilation and finite unit/regression checks precede the invocation. No
external engineering proof-checker runs and no trial search precede it.
After a stopped or completed campaign, a new invocation requires a separately
written finite contract; the user's 100-round authorization is not a fuel reset.

## Reproduction

```sh
cargo build --locked -p adva-witness --example search_campaign
timeout --signal=TERM --kill-after=5s 4795s \
  python python/adva/adva.py search-campaign \
  --native target/debug/examples/search_campaign \
  --lean /home/ubuntu/.local/bin/lean \
  --metamath /home/ubuntu/MetaMath/metamath-exe/metamath \
  --database /home/ubuntu/MetaMath/set.mm/set.mm \
  --output docs/research/0153-evidence/run-01
```

Results, actual costs, limits and selection provenance belong in a separate
evidence index. This pre-execution contract itself asserts no successful run.
