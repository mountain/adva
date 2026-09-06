# Research 0152 execution evidence

Executed on 2026-09-06 through the outer **`python/adva/adva.py` CLI**.
The revised [run-02 report](run-02/report.json) is `Completed`: calibration
and three bounded search rounds passed all three verifier gates. This is
scoped arithmetic evidence, not three-computation completeness or SGD.

## What was checked

The Rust backend loaded the unchanged Research 0150 epoch 1 and reconstructed
its doubling seed. It checked every enumerated arithmetic rewrite candidate
with the existing exact polynomial/witness checker. The selected paths were
exported as explicit Lean and Metamath proofs, not simply submitted as strings
for a numerical agreement test. Each Rust export was rerun and matched byte
for byte before external admission. That replay is same-implementation
regression evidence, not an independent Rust verifier.

Lean 4.24.0 was installed from its pinned official Linux archive, with SHA256
verified before extraction. It uses core `Init`, not mathlib. All **792**
selected-step theorems (four calibration plus 788 search edges) passed Lean
and Metamath. Lean's per-theorem axiom audit reports only `propext`, inside
the declared allowlist. The Metamath base audit checked **47,670** `$p`
proofs; its **3,008** `$a` statements remain imported axioms/syntax rules,
not newly proved assertions. Versions and actual binary/database digests
are in the report. The native executable's post-run SHA256 matches the
recorded preflight SHA256.

Calibration passed forward, reverse and both contextual positions. Rust
rejected unequal polynomials, an invalid position and nonduplicate
contraction. Lean rejected a false equality; its deliberately contaminated
`sorry` theorem exposed `sorryAx` and was rejected by the admission policy.
Metamath rejected the mismatching final equality **despite returning exit
code zero**. Its log, not exit status alone, is therefore checked. Zero
preserves the polynomial law but fails Adva guarded execution; those are
different judgments, not a disagreement resolved by voting.

## Search comparison, including failures

Each row contains six arms per policy: two task directions and seeds
1, 7, 19. A task stops on literal target syntax or at 48 selected steps.
Step totals below include exhausted paths; they are not a speed ratio.

| Depth | Random reached | Residual reached | Random steps | Residual steps |
| --- | ---: | ---: | ---: | ---: |
| 2 | 6 / 6 | 6 / 6 | 43 | 13 |
| 3 | 3 / 6 | 3 / 6 | 173 | 153 |
| 4 | 1 / 6 | 3 / 6 | 250 | 156 |
| Total | 10 / 18 | 12 / 18 | 466 | 322 |

The direction split is essential. For **contraction**, the residual policy
reached 9/9 targets versus random's 3/9. For **expansion**, it reached only
3/9 versus random's 7/9. Thus the finite comparison does NOT support a general
superiority claim. Seeds are fixed diagnostic replicates on a deliberately
small hand-specified family, not an out-of-sample statistical benchmark.

There is a concrete counterexample to treating repeated zigzag as progress.
At depth 3, residual-guided expansion with seed 1 repeatedly expands and
contracts arithmetic position `[1,1]`, with residual **22 -> 22 -> 22**.
It returns to the same syntax after two steps and exhausts fuel at 48.
The other two expansion seeds at depths 3 and 4 also exhaust. Their
statuses are `Unknown`; no nonexistence or convergence is inferred. The
ordered tree residual gives zero directional gain on this loop while the
path and verification costs grow. A future policy must address that exposed
plateau/direction mismatch; this run does not silently add tabu, annealing,
new fuel or a learned parameter to make the comparison succeed.

Full paths, both directions, candidate-order scores, selected indices,
bound exclusions and final residuals remain in `rust-2.stdout`,
`rust-3.stdout`, `rust-4.stdout` and their exact replay counterparts.
These files are JSON despite their `.stdout` suffix. Arithmetic paths are
not native source/occurrence identities. There is no knowledge-epoch update,
stable operation, new word or deletion of exploration history.

## Resources and the retained failed attempt

The successful invocation used **21 / 24 children**, **8,640 / 250,000**
enumerated candidate visits including replay, **1,600 / 50,000** library
loading units including replay, and 792 selected edges including calibration.
The search itself performed 4,320 neighbor checks and 788 export rechecks,
or 5,108 Rust witness checks; replay doubles those search counts. Calibration
controls are separately explicit in its export, and all their subprocess
costs are charged. No candidate exceeded the tree cap in this run.

Wall time before the final checkpoint was **136.89 seconds**, child CPU
**81.47 seconds**, and child peak RSS **513,380 KiB**. Final retained size
is **9,512,952 bytes**, below 128 MiB. The final report serialization/fsync is
outside its self-reported wall counter and uses the five-second reserve;
no separate nanosecond measurement of that last checkpoint is claimed.
Concurrent ordinary regression builds/tests affected host timing, so these
times are not isolated policy benchmarks. Both policies were externally
checked in common batches; no separate end-to-end speedup is established.

The earlier [run-01 report](run-01/report.json) is still `Blocked`. It passed
calibration and depth 2, then encountered Metamath's interactive pager during
depth 3. The exact inspected child was explicitly stopped with SIGTERM after
129.17 seconds; no depth 3 admission or depth 4 run exists for that attempt.
Its total wall counter is 168.14 seconds, child CPU 167.04 seconds, across
17 children. These failed-attempt costs are additional, not hidden inside
the successful-run figures. The original supervisor is archived as
`run-01/supervisor-source.py`, SHA256
`5f8978f4de4b94cb20aff9d19023be7fb42951890e93aedcf1f8b8548575d9ec`.

The separately written [continuation contract](../0152-continuation-01.md)
permits one finite rerun after inserting the documented
`SET SCROLL CONTINUOUS` command. A transport regression checks that prefix
for every invocation. The complete base audit and all controls were repeated;
the old successful depth 2 is not counted twice. No external engineering
proof-checker invocations preceded either recorded attempt.

Report SHA256:

- run-01: `82cc7a9295731d87233085b83e7d72b7984704a88e8c861f2da21e4f9ffa966e`
- run-02: `0536763721800399ded061d6ddaae70403f0092019614452d4bdb71d0d48bf91`

## Engineering validation and reproduction

Local checks passed: `cargo fmt --check`; workspace/all-target/all-feature
Clippy with warnings denied; **211** workspace Rust tests; **11**, **12**,
and **6** tests in the stability, generation, and verifier-search examples;
and **698** Python tests plus three subtests. The seven new Python transport
tests require no external proof assistant. Ruff passes for the new Python
supervisor and its tests. The old `adva.py prime-check` entry also passed its
five frozen cases, with five native calls and 258/5,120 aggregate fuel.
A pre-existing Rust formatting-only line in `prime_certificate.rs` was
wrapped to satisfy current rustfmt; its checker logic was not changed.

The claim registry parses and its 100 IDs are unique; the new claim's
dependencies resolve. One pre-existing dangling dependency remains:
`adva.bounded-verified.symbolic-probe-matrix-shadow.v0` names the absent
`adva.exact.structural-forward-differential.v1`. This was confirmed in the
base revision and is not silently repaired or claimed valid by this work.

Research 0149–0151 source fingerprints, Cargo.lock, both library snapshots
and the three recipe stages retain their preflight bytes. CI runs the new
Rust example tests and the Python transport regressions; it does not silently
download theorem provers or claim to repeat the full external calibration.

To repeat the finite experiment, follow the build/CLI command in the original
contract and supply a **fresh** output directory, the pinned set.mm database
and Lean release. Each invocation reruns the checks; merely reading this
JSON directory is not a new checked library import. Paths in retained `.mm`
files record the local database used; a new CLI run emits the requested
local path without changing the common arithmetic syntax.
