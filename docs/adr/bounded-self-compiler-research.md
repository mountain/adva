# Bounded structured self compiler (research v0)

Status: accepted for the separately bounded research experiment in
`experiments/bounded_self_compiler/contract.json`. Actual outcomes and residuals
belong in its evidence and research report. Authored by ChatGPT (OpenAI), submitted
through Mingli Yuan's account as authorized proxy; account ownership is not review
or a correctness guarantee.

The current PSC0 compiler accepts finite Real/Bool programs; `compile` also occurs
as an M6 crossing name. Neither occurrence supplies an executable self compiler.
The arithmetic interpreter's object grammar cannot express its own interpreter.
We therefore define a separate structured research language with generic typed
v1 data-machine primitives, `Seq`, `If` and `While`. Compiler source uses exactly
this grammar. It does not call a host compiler during its execution.

The previous v0 Rust module and its source-bound checkpoint profile remain frozen.
The new `data_machine_v1` module explicitly copies that implementation and changes
only its version, declared finite capacities and four generic instructions:
`length`, `field_dynamic`, `pack`, and `stack_length`. `pack` preserves stack order
and leaves the stack intact. Dynamic indexing rejects negative/out-of-range
indices. Every failure rolls back data writes and consumes one instruction.
Typed register checks, full-state trace hashing, independent-context native
reception and original lifetime fuel apply to this version as well. Capacity
limits are finite, declared in the run contract, and do not grow during execution.
The duplication keeps old evidence readable without redefining its transition.

The external Python seed emits and patches forward addresses. The Adva compiler
instead traverses source data with explicit stacks, counts the sizes of structured
subtrees, computes addresses and constructs target instruction data. A pure wire
codec encodes source and decodes the returned target. It cannot emit or resolve
control instructions. Names and register declarations pass through as data. Rust
validates the decoded target before native execution. Invalid typed programs are
not admitted just because structural lowering succeeded.

A separate receiver checks every block interval, primitive, branch and back edge
and returns a research correspondence receipt. A direct AST control evaluator
checks fixture terminal observations and ordered primitive register states.
These are external research checks, not a Rust `GraftTrace`, native semantic
identity, library admission or unrestricted correctness proof. Source and target
fuel are not equated: target-generated control consumes additional steps. Global
capacity and output limits can independently stop a computation as Unknown.

Self bootstrap means `C0(S) = C1`, `C1(S) = C2`, `C2(S) = C3`, with canonical target
bytes equal and independently received source/target correspondence. The source
and mutated-source controls must rule out opaque reproduction of a stored compiler.
A hand-written self compiler is not the second Futamura projection. General
specialization and its self-application remain separately typed obligations.
