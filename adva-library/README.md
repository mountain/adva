# Adva library: reusable research inputs and presentations

This directory stages the two Pascal documents requested by Mingli Yuan on
2026-09-06, together with a bounded orchestration design. The GitHub connection
did not expose a separate `mountain/adva-library` repository at preparation
time. This is a reviewable directory inside `adva`, not a newly created
repository or a claim that a language module/loader exists.

- `pascal-task.adva`: three distinct Human/World/Machine roles, a shared Pascal
  question, finite resources, an explicit meeting gap and acceptance scope.
- `pascal-witness.adva`: three presentations, the normalized conic proof,
  exact arithmetic checks, reuse and counterexamples, and retained residuals.
- `index.json`: file types, byte digests, source attribution and native status.
- `learn-free-six.contract.json`: orchestration contract with two six-slot
  phases. The `free` adapter remains absent until its meaning is defined.
- `phase-runner/`: the fixed native learn method inputs copied from draft
  PR #136, pinned to commit `4cbbfebfead3918b4da46920d55708d10f3baee8`.

The Pascal files are preserved byte for byte from their delivered versions.
They remain proposed research JSON documents. Their arithmetic is external
evidence, not a native Rust import certificate. The three Human identities,
meeting time/place and acceptance are unresolved. Placing them in this
directory does not register `run`, `free`, an interpreter, or a builtin.

The six-stage roundtrip does not execute the Pascal documents. It is a
separate existing arithmetic calibration useful for testing orchestration.
The missing Pascal importer must remain visible; this directory does not
bridge the two tasks by renaming files.

## Bounded runner

From the repository root, use a new report directory:

```sh
python experiments/phase_runner/run_six.py \
  --contract adva-library/learn-free-six.contract.json \
  --report-dir target/learn-free-six
```

With no backend supplied, this records the missing implementation and zero
native launches. It produces `learn-report.json`, `free-report.json` and
`run-report.json`. Six report slots are not six executions or six successes.

The existing learn calibration can be invoked after obtaining an executable
built from the declared draft source:

```sh
python experiments/phase_runner/run_six.py \
  --contract adva-library/learn-free-six.contract.json \
  --report-dir target/learn-free-six-with-backend \
  --backend /absolute/path/to/adva
```

The command hashes the supplied binary for the record; a digest alone is not
authenticated build provenance. Supplying main's binary does not add #136's
draft method. The `free` phase remains blocked even when learn succeeds.
There is no Python substitute for the native arithmetic operation.

## Reporting and continuation

Each phase has six requested slots and an independent count of actual
launches. A missing adapter records NotRun. A timeout preserves Unknown; a
guard refusal, invalid output or backend error stops that phase and preserves
the remaining slots as NotRun. Partial output files are retained. Inputs and
outputs are hashed for integrity, without assigning native semantic identities.

A Completed slot means that the configured subprocess protocol completed.
It is not a universal learning theorem, a proof of free, human acceptance,
or an independent semantic validation by Python. The native backend remains
responsible for arithmetic and history validation. Fatal report-storage
failure can still occur and must be surfaced; no program promises that all
physical execution and I/O errors are impossible.

Child cleanup is limited to the process group created for each backend call.
This supervisor is for a declared backend; it is not a security sandbox for
programs that deliberately detach or evade operating-system limits.

See `docs/research/0139-library-six-phase-and-communication.md` for the missing
free predicate and the distinction among contract, seal and Seal.
