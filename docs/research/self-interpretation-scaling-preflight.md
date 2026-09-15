# What interpreting a subset of the machine's own grammar costs

Status: completed bounded construction and scaling measurement, 2026-09-16. Base:
`7e110e1ca0f40a02d4c332bfae9e7264f1db0913`.

Direction: Mingli Yuan. Design, implementation and record:
deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted through Mingli Yuan's
GitHub account (`mountain`) as an authorized proxy; not his authorship, review,
endorsement or guarantee. No independent human review.

## Question and level

[The capacity preflight](self-interpretation-capacity-preflight.md) measured that
the full object program has no inspectable encoding inside the declared node bound,
and that a 17-case dispatch ladder spends 90 of 128 instructions. It left the
follow-up it named itself: which declared bound would a separately scoped extension
have to move? This preflight answers with construction and execution rather than
arithmetic.

A generated **meta program** — a program in the same language as the objects it
interprets — receives an encoded object program as data and interprets it. The
object language is a declared strict subset of this machine's own instruction
grammar: `input d`, `return s`, `constant v d`, `copy s d`, with two object register
slots and a fixed object program length. Nothing changes the machine, its bounds or
the frozen campaign; the object program is never read by the generating code at run
time, only by the meta program from data.

Contract, checker and retained record: `experiments/self_interpretation_scaling/`.

## Result 1: a declared subset of the machine's own grammar is interpreted (executed)

The object program and the object input arrive as one data value: a bundle node
whose first field is the object program and whose second field is the object-level
input. The meta program fetches an instruction by field position, reads its opcode
with `tag`, dispatches by equality, and moves values between two object slots held
in its own registers.

Four object programs it had never seen were interpreted correctly:

| Object program (as data) | Object input | Result | Native steps |
| --- | --- | --- | --- |
| `input 1; return 1` | 7 | 7 | 35 |
| `input 0; return 0` | 9 | 9 | 29 |
| `input 1; input 0; return 0` | 4 | 4 | 44 |
| `constant 5 1; return 1` | 0 | 5 | 44 |

Five malformed or out-of-subset object programs were refused with the declared
reason retained in the run report, not merely as a generic failure: an unsupported
object opcode; an object program that falls off its end; an out-of-range return
slot; an out-of-range input slot; and an object read of a slot no object instruction
wrote, which the meta program's own machine state refuses as `uninitialized
register`. The CLI prints one generic line for a runtime rejection, so each reason
is read from the retained run, and both admission refusals and runtime refusals are
kept distinct.

This is bounded and narrow — two object slots, a fixed object length, at most four
opcodes, no object fuel, no cost accounting and no provenance — but it is execution,
not argument: the profile can interpret a fragment of its own instruction grammar
with the program supplied as data.

## Result 2: the measured prices

| Component | Measured |
| --- | --- |
| Opcode body: `input` / `return` / `constant` / `copy` | 13 / 11 / 16 / 26 instructions |
| Opcode dispatch case | 3 instructions, so an opcode case plus its body is 19 |
| One more interpreted object instruction | 33 instructions |
| Native steps per interpreted object instruction | 14.5 to 22, over the four positive runs |

The generator's length model was checked against every generated program: fixed
overhead once, then per object instruction a fetch and dispatch block whose size is
the sum of the measured bodies. All eight generated sizes agree exactly with the
model, so the reported prices describe the programs that were actually built.

## Result 3: where the declared instruction bound bites (executed refusals)

| Generated meta program | Instructions | Against the bound of 128 |
| --- | --- | --- |
| 2 opcodes, 2 object instructions | 70 | admitted and executed |
| 3 opcodes, 2 object instructions | 108 | admitted and executed |
| 4 opcodes, 2 object instructions | 166 | **refused at admission** |
| 19-opcode ladder, 1 object instruction | 295 | **refused at admission** |

Both over-bound programs were submitted to the unchanged CLI and refused before
execution with `adva: invalid program schema or capacity`. The consequence is
narrow and concrete: a meta program for a **four-opcode** subset of this machine's
own grammar already exceeds the declared instruction bound, and the nineteen-opcode
ladder is 2.3 times that bound before any real body, object register file, fuel
accounting or provenance is written. The ladder's fifteen unmeasured opcodes are
declared placeholders charged the shortest measured body, so 295 understates any
real nineteen-opcode meta.

## Result 4: what the full grammar would demand (derived, not executed)

Composing only measured quantities, a meta program for the full 19-opcode,
16-slot grammar would need, at minimum:

1. **Program instructions.** 3 + n × (2 + 3×19 + Σ bodies) + 2, where Σ bodies uses
   the four measured bodies and the shortest measured body for the other fifteen,
   gives 295 for a single object instruction. Bodies for the remaining fifteen
   opcodes must select among sixteen object slots, which the measured `copy` body
   already shows is the expensive part (26 instructions for a two-slot read and
   write ladder). The declared bound of 128 is below even the placeholder floor.
2. **An object register file.** Sixteen object slots cannot live in the meta
   program's sixteen registers, which already hold fourteen values; the object file
   must be simulated on a stack, at the 4 native steps per index iteration measured
   in the capacity preflight.
3. **Lifetime fuel.** At the measured 14.5 to 22 native steps per interpreted object
   instruction, the 2048-unit lifetime budget covers roughly 93 to 141 interpreted
   object instructions, before the stack-simulated register file is added. The frozen
   arithmetic sample alone takes 134 object instructions.

None of these three is a proof of impossibility. They are the prices of the specific
bounds this profile declares, and the reason a separately scoped extension has to
name which bound moves.

## What this means for the open choice

The two dependencies the interpreter report leaves open are now differently priced.
A *checked translation* between the machine carrier and the program/process boundary
moves none of these bounds: it addresses provenance correspondence, not program,
data or fuel capacity. A *separately scoped extension admitting the interpreter's own
instruction grammar* must move at least the program instruction bound — by a factor
the measured 295-instruction placeholder floor makes concrete — and either the data
node bound or the operation vocabulary (unpacking), and the lifetime fuel bound, and
would still need indirect register addressing to avoid paying the stack-simulated
register file. Those are the items an ADR for that extension would have to justify,
and this preflight is the evidence that prices them.

## What this does not establish

- The full instruction grammar was not interpreted. Only four opcodes, two object
  slots, a fixed object program length and no object-level fuel or cost accounting
  were implemented.
- No impossibility is claimed, and no bound was widened: a different profile, a
  smaller instruction set, or an extension that adds indirect addressing or an
  unpacking operation changes every number here.
- The fifteen placeholder bodies are the shortest measured body, so the 295 figure
  is a floor for a ladder, not an estimate of a working nineteen-opcode interpreter.
- The native-step figures are per interpreted object instruction of this subset on
  this host, not a universal rate.
- Nothing about provenance, sharing or graft identity is touched.

## Files and reproduction

- Contract and checker: `experiments/self_interpretation_scaling/contract.json`,
  `check.py`.
- Retained record: `experiments/self_interpretation_scaling/evidence/attempt-1` —
  43 files from 11 bounded CLI launches, within a budget of 24: every generated meta
  program, every object bundle, every run, every refusal and `results.json`.
- Regressions receive that record without executing anything:
  `tests/python/test_self_interpretation_scaling.py`.
- Registered as `adva.bounded-experiment.self-interpretation-scaling.v0` and
  recorded in agenda section 14.
