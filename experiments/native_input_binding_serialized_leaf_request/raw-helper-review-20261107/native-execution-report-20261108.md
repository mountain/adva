# Pinned raw-helper native controls, 2026-11-08

**Finite result: `Passed` for the helper's fixed synthetic profile only.**

This continuation executes the smallest native obligation left by the
2026-11-07 static review. It does not revisit the opaque target request and does
not change `NoExactRouteViaPinnedRawHelper`: the unmodified helper still carries
neither the target's caller-supplied diagram pair nor its qualified
cross-diagram endpoint relation.

## Frozen question and boundary

- Repository dependency: [`mountain/adva-machine@a0b710a`](https://github.com/mountain/adva-machine/commit/a0b710a2517f06f2fe03cc463e855548adf418ac).
- Arithmetic domain: the helper's fixed exact-integer roundtrip fixture.
- Types retained: request bytes, receiver/context binding, semantic and origin
  dimensions, and receiver build binding. Additive zero and multiplicative unit
  are not identified or transported; zero, invertibility, noncommutative order
  and history receive no new claim.
- Quantification: exactly three already-present full test selectors; each must
  resolve to exactly one passing test.
- Candidate grammar: no candidate generation and no new vocabulary proposal.
- Resource limits: one offline build, 180 s build wall limit, three tests with
  10 s each, 2 GiB address-space cap, 128 MiB per-file cap, no semantic retry.
- Success: one resolved test executable and three exact one-test passes.
- Refusal: a pass remains local to the fixed profile and cannot supply the
  original target's A+B+C+D receiving route.

The exact run contract is
[`native-execution-contract-20261108.json`](native-execution-contract-20261108.json).

## Retained implementation error and one correction replay

[Run 42492311898](https://github.com/mountain/adva/actions/runs/42492311898)
ended before semantic execution because the original 2,048-block
`RLIMIT_FSIZE` was applied to linker outputs. `rust-lld` received signal 25
(`File size limit exceeded`). The attempt used 0.89 s wall time and 151,576 KiB
maximum RSS; zero semantic tests ran. Its 6,392-byte artifact ZIP has SHA-256
`51d637d9a52f420d2e7fe1001f0f5a76e553dc90fd31fbf76bd442d0d63e1553`.
The structured record is
[`native-execution-first-attempt-20261108.json`](native-execution-first-attempt-20261108.json).

The sole permitted implementation correction changed only the per-file cap to
262,144 blocks of 512 bytes (128 MiB). Machine pin, selectors, semantic scope,
offline rule, wall limits and address-space cap were unchanged. This is a
correction replay, not a semantic retry.

## Executed result

[Correction run 42492652789](https://github.com/mountain/adva/actions/runs/42492652789)
completed the one offline build and directly ran these exact selectors:

1. `intake::tests::received_fixed_proof_checks_and_reuses_independently`
2. `intake::tests::every_semantic_and_origin_dimension_is_exactly_bound`
3. `intake::tests::altered_receiver_binding_cannot_authorize_itself_even_when_repinned`

Each invocation reported `running 1 test` and
`test result: ok. 1 passed; 0 failed`. The first two harness reports finished
in 0.01 s and the third in 0.00 s. The retained outcome records three tests run
and three passed, with zero opaque-request reads and executions.

The test executable SHA-256 was
`e4300de3a455d4a9939a1d0d802384015d14fa3d9b1dd985653f37224723429e`.
The toolchain was `rustc 1.99.1 (58cf8f9c3 2026-10-13)` and
`cargo 1.99.1 (5f94df478 2026-08-27)` on `x86_64-unknown-linux-gnu`.

## Actual costs and evidence

| Stage | Wall clock | Maximum RSS | Retained result |
| --- | ---: | ---: | --- |
| First erroneous build | 0.89 s | 151,576 KiB | implementation-limit error; 0 tests |
| Corrected offline build | 14.24 s | 1,040,124 KiB | one test executable |
| Selector 0 | below 0.01 s timer resolution | 7,784 KiB | 1/1 pass |
| Selector 1 | below 0.01 s timer resolution | 6,324 KiB | 1/1 pass |
| Selector 2 | below 0.01 s timer resolution | 6,188 KiB | 1/1 pass |

These are per-command GNU `time` maxima, not whole-job peak memory or additive
memory costs. Dependency receipt, setup, report serialization and artifact
upload elapsed time were not isolated. There was no candidate search: 0
candidates and 0 search nodes. Construction time for the workflow and report
was not instrumented.

The successful artifact contains 44,447 uncompressed bytes and a 10,696-byte
ZIP with SHA-256
`b986c77e7014ac013a42350a36f997b0074e63bbd1b4d3e8f714020678e5349b`:
[artifact 13622400929](https://github.com/mountain/adva/actions/runs/42492652789/artifacts/13622400929).
It retains the build JSON stream and stderr, exact selectors, exit codes,
stdout/stderr, GNU time reports, toolchain identity, executable hash, plan
check, reference verification and serialized outcome. The stable repository
copy is [`native-execution-outcome-20261108.json`](native-execution-outcome-20261108.json).

## Replay

After obtaining the exact pinned dependency through the repository's existing
dependency checker, the semantic part is:

```sh
export CARGO_NET_OFFLINE=true
export CARGO_TARGET_DIR=/bounded/local/target
cargo test --locked --offline \
  --manifest-path /exact/adva-machine/experiments/native_evidence_intake/Cargo.toml \
  --no-run --message-format=json

/resolved/adva_native_evidence_intake TEST_SELECTOR \
  --exact --nocapture --test-threads=1
```

Resolve the executable from the sole `compiler-artifact` JSON row whose target
name is `adva-native-evidence-intake` and test profile is true. Substitute each
of the three full selectors above, preserve the declared limits, and require
exactly one test per invocation. This replays the fixed helper controls, not the
target request.

## Claim status, vocabulary and residual

This finite run upgrades only the three listed native controls from `NotRun` to
executed passes. It does not prove the static interpretation, arbitrary-input
correctness, authentication, arithmetic universality, hypothesized arithmetic
truth, Research 0090 coverage, Research 0092 promotion, M6 filling, native
`free`/`Close`, shortest construction, social trust or practical adoption.

No new word is formed or revised. `ImplementationLimitError` is an outcome
classification in the retained attempt, not a learned mathematical word. Word
formation, validation and new-instance reuse costs are therefore not claimed.

The residual for Mingli Yuan, Jiamin Zhao and later agents is now sharper: the
existing helper's own positive and rejection machinery is executable at the
pin, but an original-target continuation still requires a separately versioned
adapter that carries both supplied diagrams and their qualified endpoint
relation. Its minimum controls remain a valid target case, a foreign or
wrong-path endpoint, and a same-value/different-origin substitution. Local
image equality alone must not yield an M6 filler.

Original contract, workflow, evidence synthesis and report: Codex (OpenAI),
contributed under Unknown v0.3 and submitted through Mingli Yuan's GitHub
account as authorized proxy. Account ownership is not authorship, review,
endorsement or a correctness guarantee. Dependency source is not copied into
this repository.
