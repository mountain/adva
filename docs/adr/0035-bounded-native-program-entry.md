# ADR 0035: a bounded native program entry before host orchestration

Status: proposed implementation; see Research 0140 for execution evidence.

## Context

The existing Rust libraries parse, compile and evaluate PSC0 programs, while
the `adva` executable exposes particular research methods. A Python supervisor
cannot make an unsupported `.adva` payload executable. The user requests the
native Adva implementation first, then six-call orchestration.

## Decision

Add `adva run program.adva --output result.adva` and a Rust-owned, version-zero
`adva.run.program.research` envelope containing `source`, `module`, `entry`,
`inputs`, and `fuel`. Use `adva-lisp` parsing, linking, compilation, diagram
checking, and evaluation. Keep the existing operation registry and IR intact.

The first profile admits one module, one definition, no imports or calls,
at most eight Real input ports, 4096 source bytes, lexical depth 32, sixteen
AST terms, and four copy operations. The whole JSON input is capped at 16 KiB.
Fuel is 1..16 AST admission units, charged before compilation. It is not a
promise that one AST term costs one machine instruction. Small structural
caps prevent call expansion and repeated-copy lineage amplification before
the compiler starts. Unsupported profiles are explicitly rejected.

Results retain the original input, selected entry, complete compiler artifact
(including source/occurrence history and graft certificates), evaluation
certificate, phase costs and rejection diagnostics. `Real` is the existing
IEEE-754 f64 realization. Nonfinite inputs/results are refused. No numeric
result is promoted to an exact arithmetic theorem or a history identity.

The CLI requires a new `.adva` output path. It writes and syncs a same-directory
temporary file, then publishes it by a non-overwriting hard link. A filesystem
without this facility returns an I/O error. Completion and rejection reports
are distinct; semantic rejection saves a report and returns existing CLI error
code 2. Filesystem/argument failures return 2 and may have no report. A saved
JSON report is data: independently checking it requires recompilation/replay
and the checked diagram import boundary, not deserializing success flags.

## Consequences

`adva-witness` now also depends on `adva-lisp`; Rust remains semantic authority.
The command is useful for executing a first program and retaining its actual
evidence without Python. It does not accept the two Pascal proposal schemas,
execute neutral-carrier graphs, implement general method dispatch, or finish
the proposed self-interpreter. `learn`, `free`, `contract`, `seal`, and `Seal`
keep their existing scopes. The next layer may call this executable only after
its requested method has a native contract, checker and resource account.
