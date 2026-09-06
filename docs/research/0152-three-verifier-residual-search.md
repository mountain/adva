# Research 0152: three-verifier residual-guided arithmetic search

Status: pre-execution contract, 2026-09-06. Research only; no stable API change.
Read with Research 0126, 0127, 0129, 0149–0151 and ADR 0040. The agenda's
0090 coverage and invariance obligations remain open.

## Question, level and interface

Can independently checked instances of the frozen library's doubling law
support bounded forward/backward search, and does a discrete residual improve
this particular search compared with a seeded random walk?

The common syntax is `x`, `2`, ordered addition and multiplication. Its three
interpretations are Adva's research `ExactExprV0` polynomial arithmetic, Lean
`Int`, and Metamath complex classes under `A e. CC`. The explicit map sends
`x` to `x : Int` / `A`, and maps `2`, `+`, `*` to the respective arithmetic
operations. This is an interpretation of a small ring-law syntax, NOT a
formal translation between the full foundations of Lean and set.mm. Adva
guarded execution additionally refuses zero; that side condition is retained
separately. No equality of native programs, histories, sources or occurrences
is inferred from these arithmetic statements.

The loaded Research 0150 epoch 1 provides `2*x = x+x`. Each step expands
`2*t` to `t+t` or contracts a literally duplicated arithmetic subtree, at an
explicit ordered syntax position. Rust reconstructs and checks the entire
before/after pair and produces an arithmetic witness. Lean checks a generated
proof using `Int.two_mul`, symmetry and congruence. Metamath checks a generated
uncompressed proof using `2timesd`, complex closure and `oveq1d`/`oveq2d`.
These arithmetic syntax paths are not native occurrence IDs. Arithmetic
duplication here does not add implicit sharing to the linear program core.

Pinned sources: Lean 4.24.0, release commit
`797c613eb9b6d4ec95db23e3e00af9ac6657f24b`, official Linux archive SHA256
`b14f5e5159219dd1a1956c3b806813319f5e94ccd5bdfd56f54520609a5bb5ec`;
local Metamath 0.199.pre, set.mm commit
`cf7f961faff0f17b72f05daf986daed963184da4`. The runner records actual binary
and database digests. A full `VERIFY PROOF *` audit of the pinned database is
required before relying on its theorem dependencies. Lean uses core imports,
no mathlib, no `sorry`, custom axioms, `native_decide` or compiler oracle.
`#print axioms` is checked against the explicit allowlist
`propext`, `Classical.choice`, `Quot.sound`; absence is stronger.

## Protected obligations and admission

Three accepting implementations are not by themselves the T/X/K computation
constraint. There is no majority vote, native cell, M6 result, smooth topology,
SGD convergence theorem, new language word or observer specialization here.
The topology available to search is an ordered, directed rewrite multigraph;
repeated endpoints retain their traversals. A residual is a declared objective
on syntax, not a metric on knowledge in general.

Rust validates every enumerated candidate. External verification is batched
over the selected edges; until both external batches pass, a round is only a
provisional Rust result. A round is admitted only if both external checkers
accept every selected edge. No search edge is promoted to the old library.
The old immutable library, epoch and recipe journals remain byte unchanged.
All selected paths, returns, unselected candidate scores, failures and final
residuals are retained. Passing finite tests is not universal correctness of
the proof exporters. External parsing/translation remains a trusted boundary
and is exercised by negative controls.

Calibration includes forward, reverse and contextual steps. Required negative
controls: Rust unequal-polynomial rejection; Rust invalid rewrite position;
Lean false equality with a mismatching proof; Metamath false equality with a
mismatching proof; rejection of a Lean `sorryAx` dependency. The zero case
records polynomial equality and guarded-execution refusal without treating
the latter as a mathematical counterexample. Missing tools, unknown versions,
failed base audit or failed controls block search, with evidence retained.

## Fixed experiment and success gate

After calibration passes, run exactly three rounds, depths 2, 3 and 4. Each
round contains expansion and contraction tasks between nested doubling and
the fully expanded addition tree, with seeds 1, 7 and 19. Each task/seed has
two arms: uniform seeded neighbor choice and minimum syntax residual with
seeded tie-breaking. Both enumerate and Rust-check the same neighborhood
definition at every visited node. The residual is recursive ordered tree
mismatch: identical nodes score zero; equal binary constructors sum child
residuals; different constructors score the sum of subtree node counts.
The discrete descent is `residual(before)-residual(after)`. No parameter
learning or statistical SGD claim is made. Uphill moves are allowed if all
neighbors are uphill, and paths may revisit nodes.

Each arm stops at literal target syntax or after 48 selected steps; exhaustion
is `Unknown`, not nonexistence. The complete path is checked, not just its
endpoints. Report successes, steps, enumerated candidate counts, Rust witness
checks and external batch costs separately; do not call fewer selected steps
an end-to-end speedup. Three rounds proceed on checker success, not on an
assumed advantage for the guided arm. Failures or unfavorable comparisons
remain evidence. Any failed checker stops continuation.

## Enforced finite resources

One recorded invocation, exclusive new output directory (never overwrite).
The supervisor enforces 900 seconds total wall time including database audit,
search, all subprocess verification, replay and final checkpoint; each child
has at most 180 seconds wall time, 160 CPU seconds, 8 GiB address space and
32 MiB output/file limit. At most 24 children, no subprocess retry. A final
checkpoint has a reserved five seconds; each command is bounded by the
remaining shared deadline. The supervisor process checks total retained bytes
against 128 MiB before each child and before completion. The fixed tree cap
is 127 nodes, depth at most 16; candidates outside it are recorded as bounded
exclusions, never nonexistence. At most 36 arms, 1,728 selected edges,
250,000 enumerated candidates and 50,000 library-loading budget units. The
1,728 selected-edge cap is for the search records; the four calibration edges
and one exact replay of every Rust export are additionally accounted. These
caps include unsuccessful candidates; each round is replayed by re-running
Rust once and comparing the complete deterministic export. Replay and all
external checks count toward the shared subprocess/deadline limits.

Engineering verification before the recorded invocation allows at most eight
external proof-checker executions, each bounded to 180 seconds, with logs
retained separately. Compilation and ordinary finite unit/regression tests
are engineering checks, not additional research searches. No automatic trial
restart or scope widening. A failed run needs a separately written revised
finite contract and rechecked boundary before continuation.

## Reproduction and results

The outer entry point is `python/adva/adva.py verifier-search`; it dispatches
`python/adva/verifier_search.py` and the new Rust `verifier_search` example.
The runner records exact commands, versions, hashes, counts, timing, residuals
and limitations. This contract is not a result; completed evidence belongs in
a separate immutable directory. Example invocation after a locked build:

```sh
cargo build --locked -p adva-witness --example verifier_search
python python/adva/adva.py verifier-search \
  --native target/debug/examples/verifier_search \
  --lean /home/ubuntu/.local/bin/lean \
  --metamath /home/ubuntu/MetaMath/metamath-exe/metamath \
  --database /home/ubuntu/MetaMath/set.mm/set.mm \
  --output docs/research/0152-evidence/run-01
```
