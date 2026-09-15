# A bounded native data machine with its arithmetic interpreter written in Adva

Status: executed research implementation and finite cross-check, 2026-09-15.
Base: `cf14815eb6fb58ef82328fe903a53e4ceb3ba197`.

Direction: Mingli Yuan. Design, implementation, experiment and review: ChatGPT
(OpenAI), submitted through Mingli's account as authorized proxy. This is not
his authorship, review or guarantee. The different implementations below were
reviewed by the same assistant; they are not independent human review.

## Result and exact meaning of native

One unchanged, 51-instruction Adva research program now interprets 129 different
arithmetic trees. Rust executes and validates the whole machine; no Python
callback participates in its execution. The object-language tag dispatch,
work/value stacks, evaluation order and arithmetic selection are instructions
in `programs/bounded-interpreter/interpreter.adva`.

This is a new, separately versioned research data-language profile. It is not
PSC0 source and does not extend `adva.ir` version 1. The runtime is implemented
in Rust, while the arithmetic interpreter is implemented in that research
language. The interpreter does not yet interpret its own instruction language.

The [ADR](../adr/bounded-data-machine-research.md) records the dependency decision.
Research 0137's three missing facilities are provided here in bounded form:
finite program data, structural inspection and explicit control. Existing
triadic observer transitions alone were insufficient to supply them. This
direct, unspecialized interpreter does not discharge the separate observer
specialization or stable provenance obligations in the agenda.

## Machine and observation boundaries

The four register types are exact signed 64-bit integer, Boolean, finite tree
data and a bounded stack of tree data. Generic instructions construct and
inspect data, explicitly copy values, manipulate stacks, choose branches,
jump, perform checked arithmetic and return. Static checking covers every
instruction's register types and jump targets, including unreachable branches.
Uninitialized values, invalid shapes, empty pops, overflow and capacity excess
reject with a retained runtime trace when admission has succeeded.

An executed instruction consumes one lifetime unit even if it rejects. Failed
instructions have no partial data writes. A quantum can suspend execution;
resumption reconstructs the complete prior execution before proceeding. Program,
input and original fuel are supplied independently of the checkpoint. Changed
context, profile, trace, state or accounting is refused. Native reception returns
the reconstructed state, rather than trusting a deserialized snapshot.

Trace events retain the executed instruction index and a BLAKE3 digest of the
entire resulting state. The full program and input allow reconstruction of every
state and discarded value. These indices and hashes are research coordinates
and integrity checks; they do not create SourceId, OccurrenceId, program equality
or a PSC0 certificate. Register assignments and data copying have explicit
research transition semantics. A correspondence with native sharing and graft
provenance is still missing.

The primitive profile binds the exact Rust machine source and Cargo.lock. A
different live profile refuses an old checkpoint. Frozen dependency and CLI
bytes are retained for historical replay without freezing unrelated files in
future main revisions. No global resource uniqueness or anti-fork account is
claimed: lifetime fuel belongs to one declared execution lineage.

## Frozen family and executed checks

The arithmetic object grammar uses node tag 0 for a literal, 1 for addition and
2 for multiplication. Its integer payload is separate from the node constructor.
The regular family is exactly:

- 3 literals, with values -1, 0 and 1;
- 18 binary expressions over those literals;
- 108 expressions with a literal on the left and a binary expression on the
  right, using both operations independently.

The 129-case family is not every tree through a given depth. In particular it
does not exhaust both possible nested-tree orientations. Its order and grammar
were frozen before execution in `experiments/bounded_native_interpreter/contract.json`.

Each full process passed 333 campaign assertions. A separately written Python
instruction interpreter reconstructed **16,911 state edges**, checking the
native state digest after every instruction. An additional recursive exact
arithmetic oracle checked all 129 regular outputs without using that instruction
interpreter. The primary and fresh process produced byte-identical semantic
reports and identical deterministic summaries.

| Per-process outcome | Count | Meaning |
|---|---:|---|
| Returned | 136 | Regular programs and additional positive/control executions |
| Runtime rejected | 9 | Invalid object syntax or checked integer overflow |
| Admission/receipt rejected | 18 | Malformed types, schema or jump targets, and changed checkpoint context |
| Fuel exhausted | 4 | Zero budget, interrupted sample/resume and explicit looping program |
| Quantum suspended | 1 | Retained 17-step prefix |
| Native receiving-only check | 1 | Complete trace rederived without another execution quantum |
| Publication refused | 1 | Existing accepted output bytes preserved |

That is **170 native CLI calls per process**, 340 across the primary/fresh pair.
One preceding receiving preflight separately checked the sample's 134 native
steps. The complete primary/fresh archives each retain 836 files: programs,
inputs, complete traces, mutated receipts, refusal stderr, summaries and costs.
Archive creation verifies every original file's SHA-256 before removing the
temporary unpacked directory.

## Decisive controls

`2 + (3 * 4)` returns **14**, using 134 machine instructions. Pausing after 17
instructions and then resuming gives exactly the same full trace and final
state as uninterrupted execution. The resume additionally records 17 checked
prefix steps. With original fuel 17, continuation stays exhausted at 17; changing
the expected fuel to 18 is refused.

`9007199254740993 + 2` returns **9007199254740995** exactly, exposing the distinction
from a binary64 realization. Positive overflow, negative overflow, and overflow
inside an expression multiplied by zero all reject under the declared eager
left-to-right execution policy.

Replacing the interpreter's Adva `add` instruction with `multiply` changes
`2 + 3` from 5 to **6**. This checks that the arithmetic choice is carried by the
program. A second program constructs a tag-77 node containing two copies of
integer 5, using the generic data instructions independently of the object
arithmetic grammar. An explicit jump-to-itself program exhausts its 23 units;
that result is not a nontermination certificate.

## Costs, failures and reproduction

The primary process took approximately **2.94 s**, including **1.36 s** in native
subprocess calls. The fresh process took **3.08 s**. Source freezing, both
processes and archive verification took **6.81 s** in the supervisor. Parent
peak RSS was 96,624 KiB; maximum observed child RSS was 14,416 KiB in the primary.
These are separate process observations, not an asserted aggregate memory peak.

The regular family used 15,966 native lifetime instruction steps per process.
The 16,911 independent reference steps additionally include retained control
executions. A conservative native instruction-work bound of 696,320 per process
includes prefix checking and unsuccessful receptions; it is an upper bound,
not a measured exact total. All parsing, checking, checkpointing and archiving
remain inside the declared host bounds. These timings do not establish a speedup.

The first 12 Rust core and 4 real CLI tests passed, as did Clippy. The complete
Rust workspace test suite also passed. Four retained-evidence Python tests and
four research-index consistency tests passed (8 total). Local toolchain
setup first encountered an installer-basename refusal and concurrent automatic
toolchain-download contention; using the correctly named installer and explicit
Rust 1.98.1 resolved those build-environment failures. They were not research
counterexamples. The receiving preflight and both full processes passed without
a corrected or repeated full research campaign.

See the [program instructions](../../programs/bounded-interpreter/README.md) for
native execution and the [experiment instructions](../../experiments/bounded_native_interpreter/README.md)
for a separately bounded reproduction into a new directory. The immutable
evidence is under `experiments/bounded_native_interpreter/evidence/attempt-1`.
Regression tests receive those saved traces instead of starting another search.

## Integration failure and contract successor

The first published implementation, `c0d94bd`, passed the complete Rust CI job
and the arithmetic vocabulary workflow. Its Python 3.11, 3.12 and 3.13 jobs each
reported **1 failed, 2,733 passed, 1 skipped** in
[CI run 34990388176](https://github.com/mountain/adva/actions/runs/34990388176).
The new interpreter checks passed. The failure was
`test_the_base_commit_boundary_holds_at_this_commit`: the existing symbol-surface
advance contract v3 forbids any Rust change after its declared base `09d073a`.
The added machine therefore correctly failed that boundary. The pre-publication
local Python selection had omitted this integration test; that was a missed gate.

The correction preserves v0-v3 verbatim and adds
`experiments/advance_symbol_surface/contract-v4.json`, binding v3's digest and
moving the Rust base to `c0d94bd`. Only version, date, base and successor metadata
change. Every input pin, library boundary, control, authorization text and
execution limit stays identical. The native boundary check is not relaxed.
The profile selects v4 and records that same contract in its reports. This
maintenance update does not rerun the symbol-surface advance or the interpreter
campaign, and does not refill any earlier run's fuel.

The local corrective test command first failed collection because the Adva
package was not installed; adding the source path then exposed the missing
native extension. Building the existing `adva-python` target and loading that
artifact resolved the local test setup. These collection failures did not execute
a research trial. All 24 corrective tests passed, covering contract-chain, surface-boundary,
saved-interpreter reception and research-index checks.

## What the result supports and what remains

The implementation supports the proposed first milestone: a program written in
an Adva research language can accept different programs as data and interpret
them, with native replay, exact arithmetic and accounted suspension. The key
step was defining the missing data and control semantics, not narrowing the
Keraia unresolved-mass interval.

It does not establish self interpretation, universality, Q4/M6 execution,
specialization, optimal-machine Omega bounds, a new stable operation or a native
diagram/provenance correspondence. The next dependency is a checked translation
between this explicit machine carrier and Adva's program/process boundary, or a
separately scoped extension admitting the interpreter's own instruction grammar.
Those choices need evidence; the current arithmetic interpreter alone does not
decide between them.
