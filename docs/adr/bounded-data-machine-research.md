# ADR: a bounded research data machine and an interpreter written in Adva

Status: research implementation decision, 2026-09-15.

Direction: Mingli Yuan. Design and implementation: ChatGPT (OpenAI), submitted
through his account as authorized proxy; not his authorship, review or guarantee.

## Dependency decision

Research 0137 found that named finite composition cannot inspect program data
or supply stateful interpretation. A triadic observer transition retains exact
PSC0 process evidence but does not provide those operations. This implementation
therefore requires a stronger, separately typed execution carrier. It does not
derive an interpreter from observer equality or from the Keraia mass result.

The current user instruction selects the minimal research interpreter described
in that audit. We introduce finite tagged data and bounded control in the Rust
research companion, with a dedicated schema. This is an unspecialized language
calibration. Observer specialization and its correspondence obligations remain
open; neither specialization nor a new PSC0 operation is needed or claimed by
this separate machine. Promotion to the stable language remains downstream of
the agenda's exactness, data/control and provenance gates.

## Language and ownership

The program is a typed register instruction list, serialized as an `.adva`
research program. A register contains an exact signed integer, a Boolean, finite
tree data or a bounded stack of tree data. Tree data has two constructors:
an integer and an ordered tagged node. Construction, inspection, explicit copy,
stack manipulation, checked arithmetic, jumps, branches and return are generic
Rust instructions. The runtime contains no arithmetic-tree evaluator callback.

The object-language interpreter is an ordinary program in this instruction
language. Its program chooses the meaning of literal/add/multiply tags and
manages its own work stack and value stack. The same program bytes accept many
different input trees. Changing its arithmetic instruction must change the
result. A separate node-construction fixture exercises data unrelated to the
arithmetic grammar. These controls distinguish an interpreted program from a
schema selecting a hard-coded Rust arithmetic evaluator.

Static validation checks all register types, operands, constants and jump
targets. Runtime reads of uninitialized registers, invalid shapes, empty pops,
integer overflow and capacity excess reject explicitly. Register assignments
and stack changes are recorded machine transitions. Values are owned finite
trees; the copy/projection instructions have declared copying behavior and
there is no pointer identity or shared mutable tree alias.

This carrier does not allocate PSC0 SourceId, OccurrenceId or equation cells.
Instruction indices and tree positions are research coordinates, not stable
semantic identities. The machine's replay certificate is scoped to this
instruction profile; it cannot be supplied to the existing diagram importer.
Mapping these executions to PSC0 sharing/graft provenance remains an obligation.

## Execution, suspension and reception

One admitted instruction consumes one lifetime fuel unit, including a failing
instruction. A quantum limits this invocation without increasing lifetime fuel.
Outcomes distinguish return, semantic rejection, quantum suspension and lifetime
exhaustion. All dynamic steps retain their instruction coordinate and digest of
the complete resulting state. Digests are integrity checks, never identities.
The complete program and input permit reconstruction of every intermediate state.

Continuation takes the expected program, input and original fuel separately.
It validates the entire checkpoint by replay from those inputs, compares every
trace edge and final state, and only then executes another quantum. Replaying
the prefix has its own counted checking cost. Exhausted lifetime fuel stays
exhausted. No global uniqueness or anti-fork resource ledger is claimed; the
account is local to one declared run lineage.

All source, input, checkpoint, data, stack, instruction, register, fuel and output
sizes have hard limits. CLI output is no-clobber. Outer process limits include
parsing, replay, execution and serialization. The frozen experiment contract
records the exact cases and two-process acceptance rule.

## Acceptance and limits

Native execution and checkpoint reception must pass Rust tests. The bounded
campaign additionally uses a separately written Python instruction interpreter,
with complete state-digest comparison at each edge, and a direct exact arithmetic
oracle over the 129 declared trees. The implementations are different code paths
reviewed by the same assistant, not independent human review.

Suspended-then-resumed and uninterrupted execution must retain identical traces,
final state and lifetime cost. Mutated input, program, fuel, profile, trace or
checkpoint must be refused before continuation. Invalid data/control cases and
overflow must remain distinct from successful results.

The object grammar contains arithmetic trees, not the instructions of its own
interpreter. Consequently this is an Adva research program interpreting another
finite language, not self interpretation. General strings, lambda substitution,
unbounded recursion, Keraia admission, universality and native Q4/M6 remain out
of scope. A self interpreter needs a later encoding and execution theorem for
the instruction language itself, with separately budgeted interpretation cost.
