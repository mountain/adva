# Research 0153 evidence

The single bounded invocation follows the
[pre-execution contract](../0153-frozen-verifier-search-campaign.md) through
the outer **`python/adva/adva.py search-campaign`** CLI. It first compares
three policies, then conditionally performs 100 rounds with frozen winners.
The final report and individual admission receipts, not this index alone,
determine completion. No failed or exhausted path is removed.

Executed on 2026-09-06: [the final report](run-01/report.json) is
**Completed**, with all **100 continuation rounds / 200 tasks Reached**.
No research retry or extra round was run.

## Completed pilot and frozen choice

The base Metamath audit and all calibration controls passed. All three pilot
batches also passed Rust deterministic replay and complete Lean/Metamath
checking. Each policy has eighteen arms: depths 2,3,4, expansion/contraction,
and seeds 1,7,19. The random paths, candidate order, residuals and Rust witness
content match the corresponding retained Research 0152 baseline exactly.
Instrumentation adds explicit visit-audit/filter costs without changing those
baseline choices.

| Policy | Expansion reached | Contraction reached | Total reached | Selected steps | Declared work units |
| --- | ---: | ---: | ---: | ---: | ---: |
| Random | 7 / 9 | 3 / 9 | 10 / 18 | 466 | 18,442 |
| Visit-memory random (`tabu`) | 6 / 9 | 6 / 9 | 12 / 18 | 409 | 79,410 |
| Visit-memory residual/exploration (`hybrid`) | 9 / 9 | 9 / 9 | 18 / 18 | 87 | 4,557 |

Work units include candidate enumeration, witness checks, exact-tree memory
comparisons and policy-selection scans. Failed paths contribute their full
cost. These are declared bounded logical operations, not CPU instructions or
isolated external-verifier wall times. The pilot contains 962 selected search
edges; four additional edges belong to calibration. Every one is checked,
including edges on Unknown paths.

The [selection receipt](run-01/selection.json) chooses **hybrid for both
directions** under the predeclared lexicographic ranking. It is best among
these three policies on this pilot, not a globally optimal search algorithm.
Expansion and contraction were ranked separately rather than pooling away
the earlier direction mismatch. The chosen policy normally minimizes the
unchanged residual among unvisited arithmetic-tree neighbors; every fourth
selected step chooses uniformly among eligible neighbors. If no fresh
neighbor exists, it permits and records a revisit. It never erases the path.

Visit memory alone is not uniformly beneficial: it reduced expansion success
from 7/9 to 6/9 and substantially increased counted work. The successful
hybrid combines memory, the old residual and periodic exploration. This
three-arm comparison does not isolate which component contributes how much,
and does not establish that period four is optimal. In particular it is not
a proof that every zero-gain zigzag can or should be discarded.

## Continuation boundary

The continuation uses rounds 1..100, depth `2 + ((r-1) mod 3)`, seed `1000+r`,
and two arms per round. Winners are frozen before round 1, with their receipt
digest attached to each admission. No intermediate result retunes the policy,
changes the verifier, raises the per-arm 48-step limit, or extends the library.
These new seeds test repetition within the same arithmetic task family, not
unseen mathematical structure, world observations or learned semantics.

All 100 continuation rounds completed under that frozen selection. There were
**1,049 selected steps**, **zero Unknown tasks**, **zero selected revisits**,
**zero forced filter relaxations**, and **143 scheduled exploration steps**.
The maximum path length was **30**, below the 48-step cap. This is a finite
observation of no revisits, not proof that the policy can never revisit or
that revisiting is semantically unnecessary.

| Continuation depth | Tasks reached | Selected steps | Longest path | Declared work units |
| --- | ---: | ---: | ---: | ---: |
| 2 | 68 / 68 | 152 | 3 | 1,970 |
| 3 | 66 / 66 | 250 | 7 | 6,926 |
| 4 | 66 / 66 | 647 | 30 | 56,659 |
| Total | 200 / 200 | 1,049 | 30 | 65,555 |

Expansion used 678 steps and 51,617 work units, with maximum length 30;
contraction used 371 steps and 13,938 work units, with maximum length 7.
The imbalance survives even with the same winning policy. No claim of shortest
paths, general convergence or unrestricted knowledge-space geometry follows.
There is no continuation baseline on these 100 new seeds, so the pilot
comparison must not be presented as a measured 100-round speedup over random.

## Verification and provenance

`pins.json` retains executable, implementation, database, checker and library
digests. The old 0152 Rust arithmetic/proof-export blocks are byte-identical
inside the new private example adapter, with runtime and unit-test drift
checks. The existing Python proof-log admission functions are imported
unchanged. Lean uses the same 4.24.0 core; Metamath uses the same 0.199.pre
binary and pinned database. Its full 47,670-proof base audit is repeated once
in this invocation, with the 3,008 axioms/syntax rules still imported.

The negative controls include unequal polynomials, invalid rewrite positions,
nonduplicate contraction, guarded zero refusal, false Lean/MM equalities and
rejection of Lean sorryAx. Metamath exit code zero alone remains insufficient.
All selected proof labels and Lean axiom audits must match the Rust batch.
The arithmetic interpretations remain scoped; they do not authorize native
program equality, implicit sharing, a new word, three-computation completeness
or SGD convergence.

Every `rust-*.stdout` is the complete JSON export, with path, candidates,
memory annotations, cost ledger and witness nodes. `replay-*.stdout` must
match it byte for byte. Proof sources and logs are retained separately, and
each `admission-*.json` binds the checked export digest. Reading those receipts
is not itself a checked library import. No old epoch or recipe journal changes.

## Costs and audit

The complete invocation includes 54 pilot arms and 200 continuation arms.
The pilot retains **14 Unknown paths** (eight random, six tabu); the 100-round
continuation retains none. In total **2,015 selected edge proofs** passed all
three checks: four calibration, 962 pilot, and 1,049 continuation edges.
Every Lean audit lists only `propext`, inside the unchanged allowlist.

Actual recorded resources:

- 421 / 424 subprocesses; 104 complete Rust exports plus 104 exact replays;
- 335,928 / 25,000,000 declared work units including replay;
- 26,690 / 1,560,576 enumerated candidate visits including replay;
- 41,600 / 50,000 library-loading units, at 200 per native call;
- 586.78 seconds wall time before final checkpoint, under the 4,800-second bound;
- 390.40 child CPU seconds and peak child RSS 625,684 KiB;
- 422 pin scans consuming 176.36 seconds, included in total wall time;
- 29,714,270 final retained bytes, below the 512 MiB limit.

The work ledger has no unresolved native reservations. It charges actual
completed-call ledgers, including replay, rather than counting unused reserved
fuel as work performed. The final checkpoint uses the reserved five seconds
and one MiB; its own serialization/fsync time is outside the report's
self-measured wall counter. No separate timing precision is claimed for it.
No native rebuild ran concurrently with the campaign.

A separate read-only handoff audit matched all pinned files before regression
rebuilds, all 104 export/replay pairs, all 104 admission hashes, all 2,015
per-label axiom lists, and all 100 frozen-selection references. This is an
artifact consistency audit, not another research search or independent
mathematical proof checker.

SHA256:

- final report: `0c38b39a6e4b7da1e422d75d085ba98f7ddc1e7181ff43b2f8fa63c8d12774c6`
- selection: `c8d017eeb2c538b2e0191d58ccab7a707205da2ba550bd7978947a4039fa4724`

The practical result is a better calibrated **proposal policy** for this
family, with a frozen verification boundary. The result is not 100 library
evolutions: epoch 1 and the prior recipe book retain their original bytes.

## Engineering validation

Eight new Rust example tests and eight new Python campaign tests passed
before execution, alongside the seven existing verifier-transport tests.
They cover frozen-block drift, exact-syntax memory, relaxed filtering, the
fixed exploration schedule, ledger exhaustion, pilot ranking/ties, exact
100-round scheduling, malformed transport, pins and no-clobber checkpoints.
An initial unit test exposed a source-block delimiter matching its own string
literal; the delimiter was anchored to a definition line before the trial.
No research trial was started or restarted for that engineering correction.

Post-run handoff checks passed: `cargo fmt --check`; locked workspace,
all-target/all-feature Clippy with warnings denied; **211 workspace Rust
tests**, **8 campaign example tests**, **6 frozen verifier example tests**;
and **706 Python tests plus three subtests**. Ruff passes for the new Python
module and its tests. The original `adva.py prime-check` entry still passes
all five frozen cases (five native calls, 258/5,120 fuel). These engineering
checks are separate from the campaign's recorded search/verifier ledger and
did not start an additional campaign or change its frozen policy.

The registry parses with 101 unique claim IDs and the new dependencies
resolve. The pre-existing dangling symbolic-probe-matrix-shadow dependency
on `adva.exact.structural-forward-differential.v1` remains outside this change.
No remote CI execution, commit or merge is asserted by these local checks.
