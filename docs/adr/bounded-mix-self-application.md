# Conservative input binding and a separate v2 capacity profile

Status: bounded research decision, 2026-09-16. Authored by ChatGPT (OpenAI),
through Mingli Yuan's authorized account proxy; not his authorship or review.

The user requests progress from self compilation toward `mix` and the second
and third Futamura projections. The existing program-independent binding
specializer is ordinary structured Adva source, compiled by the received Adva
compiler: 238 instructions and 41 registers. Its input is `[wire(q), s]`;
its output constructs `[s, d]` and executes a relocated copy of `q`. The
external receiver checks the literal constructor and every relocated body
instruction, with a source/static/residual binding receipt. Rust still owns
admission, execution and complete checkpoint replay.

This design satisfies the conservative binding contract without requiring a
self interpreter: it preserves the original body rather than interpreting its
semantics at specialization time. A full in-language interpreter, binding-time
analysis, constant propagation and interpreter elimination remain obligations
for a useful optimizing `mix`. Conservative self-application is not evidence
that those optimizing dependencies have been completed.

The completed v1 campaign retains 67 native calls, five first/second target-code
equalities, eighteen source/residual terminal pairs and controls. Native
`mix(mix,mix)` was rejected at instruction 58,551 with `node arity exceeds 2048`.
The external structural construction requires 3,959 target instructions and a
3,959-field code vector. The refusal is retained under
`experiments/bounded_mix/evidence/v1-attempt-01`; it is not a compiler generator
execution, nor a reason to edit v1's historical transition profile.

## Separately versioned capacity successor

The v2 research machine changes only schema/type/profile versioning and the
following bounds:

| Boundary | Frozen v1 | Separate v2 |
| --- | ---: | ---: |
| Instructions per program | 2,048 | 4,096 |
| Node arity and admitted field shape | 2,048 | 4,096 |

All 23 instruction variants and their execution rules remain the same. Fuel
remains 200,000; registers 64; tree nodes 16,384; tree depth 48; stack entries
4,096; aggregate state nodes 131,072; source/input bytes 524,288; report bytes
64 MiB. V2 has a separate source-bound transition fingerprint, program/run
schemas, Rust types and CLI (`data-run-v2`). Cross-profile checkpoints are
refused. There is no compiler, evaluator, loader or `mix` host callback.

The duplication keeps v0/v1 source-bound evidence byte-for-byte readable.
A source-delta regression permits only the version renaming and six textual
capacity substitutions; native tests additionally check admission at the old
and new boundaries, unchanged arithmetic/rollback and refusal behavior,
common-input state/trace correspondence, and cross-profile replay refusal.
This changes no PSC0 operation registry, IR identities or stable certificate.

The existing target wire carries instructions, names and register types, not
the target machine's schema. Selecting the v2 schema is an explicit external
codec/profile choice, followed by Rust admission. It is not instruction
generation or new semantic authority. The same native-generated mix body is
used in both profiles; the existing v1 source compiler remains unchanged.

## Separate execution contract

`experiments/bounded_mix/contract-v1.json` binds the retained v1 obstruction
and authorizes one new finite v2 attempt, with no restart of the old attempt
and no renewal of an old checkpoint's fuel. The machine delta is fixed before
running. The new attempt must generate and admit `mix(mix,mix)`, run it on two
different interpreters, compare its generated compilers with `mix(mix,I)`, and
compare each compiler's emitted residual with `mix(I,p)`. Terminal observations,
native replay, mutation/refusal controls and costs are retained independently.

Success establishes these conservative, finite code-producing instances only.
The source register/scratch-name boundary, finite capacity, external source
admission/loader and absence of optimization remain explicit residuals. No
unrestricted projection theorem, faster compiler, complete ADVA self interpreter
or general optimizing `mix` is promoted from this result.
