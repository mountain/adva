# Bounded Metamath proof steps executed by an Adva research program

Status: finite implementation and retained local execution, 2026-10-15.
This advances [Issue #29 C](https://github.com/mountain/adva/issues/29), without
closing it. It differs from [Research 0152](0152-three-verifier-residual-search.md):
the proof-step checks here are instructions of the Adva program, rather than
an external verifier call.

## Implemented boundary

[`checker.adva`](../../programs/bounded-metamath-step/checker.adva) has 264
instructions and 32 registers in the **existing research data-machine-v1**.
No Rust/Python machine implementation, operation registry, dependency lock,
stable profile or historical evidence was changed. This is an inherited local
machine consumer, not another completed KPB-14 consumer migration.

The [frozen contract](../../experiments/bounded_metamath_step/contract.json)
and [original toy database](../../experiments/bounded_metamath_step/database.mm)
declare one mandatory variable `p`, three assertion frames and two supported
active push labels. A proof is a bounded integer label sequence and an expected
typed token sequence. Its initial proof stack is empty. Adva performs:

1. Complete shape, tag, integer-token and input-bound checks.
2. Frozen-label dispatch, active-hypothesis refusal and proof-stack operations.
3. `wff` type checking before assertion application.
4. Extraction of the actual substitution string from the popped stack value.
5. Explicit token-loop construction of `|- p`, `wff ~ p` and `|- p p` instances.
   The repeated-variable rule reads the same substitution string twice.
6. Final singleton, type, length and token-by-token comparison with the target.

The ISA audit found no missing operation for this finite question. v0 could
encode a smaller cons-list variant; existing v1 `Length`, `FieldDynamic`,
`StackLength` and `Pack` provide a clearer implementation. Equality remains
integer equality, so no host tree-equality primitive performs proof checking.
The Python authoring script emits the ordinary instruction list; native
execution never loads that script or the external Metamath tool.

## Scope is not supplied by the proof

The label table is part of program bytes. The original `.mm` file first opens
a block containing `fr $f wff q`, closes it, and only then declares the active
`fq $f wff q`. The target `|- q` is validly typed in the final context. Using
`fr` instead of `fq` differs only in hypothesis-label activity, so the control
isolates scope rather than introducing a second substitution mismatch.

The [official Metamath manual](https://us.metamath.org/downloads/metamath.pdf),
sections 2.2 and 4.2, supplies the hypothesis/frame rules. Closing a block
ends local hypothesis activity; it does not invalidate earlier assertions.
This program recognizes one frozen final context, not dynamic scope entry/exit.
The correspondence from `.mm` declarations to its hard-coded label/frame table
was manually audited. There is no native `.mm` parser certifying that boundary.

## Retained evidence

[`evidence/attempt-1`](../../experiments/bounded_metamath_step/evidence/attempt-1/)
contains two fresh-process archives, exact program/input/native traces, native
replay receipts, external commands and outputs, source snapshots and SHA-256
bindings. Each process completed 34 native runs and 90 subprocesses. A separate
Python implementation of the generic v1 instructions checked every state edge:
7,120 reference transitions per process. Every native run was also received
again by Rust `--check`. All 34 native reports and replay receipts match across
the two processes.

| Frozen family | Adva result | Independent Metamath result |
| --- | --- | --- |
| 8 correct cases, including non-singleton substitution strings and repeated occurrences | Returned exact target | Accepted |
| 11 wrong substitutions, types, labels, scope or stack cases | Explicit Rejected | Refused |
| 2 correct proofs beyond the token/proof-length contract | Rejected with the declared bound reason | Accepted |

Additional native controls cover malformed input, runtime construction limits,
stack depth exactly four, quantum suspension, continuation, fuel exhaustion,
changed-input continuation refusal and two program mutations. Changing an
assertion-dispatch constant breaks an otherwise correct proof. Deliberately
bypassing the inactive-label branch makes the mutated program return `|- q`
for `fr ax`, while the unmodified program and external checker refuse it.
The negative control therefore penetrates the missing scope check.

The frozen v1 profile is
`e9a700a7ca68f73587b18be1230f908e358a7d30f0a3f7d62397493b378b5797`.
Each run has lifetime fuel 8,192; proof length is at most eight, stack depth
four, and each expression at most four tokens. A quantum of 17 suspends; total
fuel 17 exhausts. Resuming the exhausted checkpoint keeps it exhausted. These
resource outcomes do not establish that a proof is invalid.

External software is official `metamath/metamath-exe` commit
`9898f5d1bb27045d764dd01672862a1c2a3b4f5e`, version `0.200.pre 17-Aug-2026`.
Its source, binary, build command and compiler are separately identified in
the tool record; neither source nor binary is redistributed here. Every case
uses `VERIFY PROOF *`. The tool can return exit zero and even print a verification
summary after an error, so acceptance additionally excludes error/incomplete
diagnostics. External success never authorizes an Adva result.

The first engineering preflight passed 21 cases and 33 native runs. Review
then strengthened the scope fixture, added its penetrating mutation, and
corrected output-capacity reservation from one file to three files plus the
final summary. These were evidence-isolation/resource improvements; no native
false acceptance was discovered. A separate Codex agent inspected the program
and ran native red-team probes. These are separate implementation paths and
agent reviews, not independent human review or a verified compiler theorem.

## Limits and next obligation

The toy assertions are arbitrary formal-system axioms, including `|- p`.
They exercise Metamath's proof mechanism and do **not** establish propositional
logic soundness or formalize a mathematical theorem. The supported label set is
a strict subset even of this toy database; `fp` is an assertion-frame premise,
not a supported proof input label. Unknown labels and out-of-contract tokens
are refused, not silently interpreted under another database.

There is no arbitrary assertion database, `$e` essential hypothesis checking,
`$d` disjoint-variable checking, multiple mandatory variables, nested/dynamic
scope, compressed proof, `.mm` front end, proof search or general theorem
proving. No PSC0 source/occurrence/graft certificate or native `Seal` follows
from a machine replay receipt. The current executable dependency pin is intact.

The next bounded step is one independently fixed assertion frame with an
essential hypothesis, followed by two-variable simultaneous substitution and
explicit disjoint-variable obligations. Each needs a successor contract and
negative controls; a full parser and a larger proof library remain downstream.

Original implementation, fixtures, analysis and reports by Codex (OpenAI),
contributed under Unknown v0.3 through Mingli Yuan's authorized GitHub account
proxy. Account use is not his authorship, review, endorsement or correctness
guarantee. Software dependencies retain their separate licenses. The exact
executed checks and residual, rather than a contributor's identity, support
the finite claims above.
