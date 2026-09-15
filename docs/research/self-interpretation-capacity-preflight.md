# The capacity a self-interpreter would have to fit in

Status: completed bounded capacity preflight, 2026-09-16. Base:
`9c3be81f11e22162af0ac1637188688778363a13`.

Direction: Mingli Yuan. Design, implementation and record:
deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted through Mingli Yuan's
GitHub account (`mountain`) as an authorized proxy; not his authorship, review,
endorsement or guarantee. No independent human review.

## Question and level

[The interpreter report](bounded-native-data-interpreter.md) leaves two possible
next dependencies: a checked translation between the machine carrier and Adva's
program/process boundary, or a separately scoped extension admitting the
interpreter's own instruction grammar. It also states that self interpretation
"additionally requires an admitted representation and correct interpretation of
this machine's own instruction grammar, with its overhead and residual state
recorded".

This preflight measures that prerequisite instead of arguing about it. Inside the
bounds the profile already declares — 128 program instructions, 16 registers, 127
data nodes, depth 12, node arity 8, stack 256, state 8192 nodes, lifetime fuel
2048, 32768 input bytes — is there room for an *inspectable* representation of the
51-instruction object interpreter, and for dispatch over it? The level is a
capability measurement on an existing profile: counting plus twelve executed
boundary and cost cases. No new semantics, no Rust change, no PSC0 promotion, no
self-interpreter, and no proof that self interpretation is impossible.

Contract, checker and retained record: `experiments/self_interpretation_capacity/`.

## Result 1: the inspectable encoding does not fit the node bound

Take the honest encoding of the object program: one node per instruction whose
fields are that instruction's numeric operands as integer leaves, the 51
instructions grouped under one spine of ≤8-field nodes. The count from the
unchanged `programs/bounded-interpreter/interpreter.adva` is exact:

```text
1 spine root + 7 group nodes + 51 instruction nodes + 110 operand leaves = 169 nodes
declared bound: 127 nodes
```

169 > 127, so that representation cannot be admitted at all. Depth is not the
binding constraint (the encoding is 4 levels deep against a bound of 12); the node
count is. Two instructions also carry a `reject` reason string, which a tree of
integers and tags cannot carry at all — a second, smaller gap in the same place.

## Result 2: the only encoding that fits cannot be unpacked in the language

One scheme does fit: pack each instruction's numeric operands into a single
integer leaf, giving 1 + 7 + 2×51 = **110 nodes** ≤ 127. But unpacking base-N
operands needs integer division, modulo or a bit operation, and the declared
vocabulary has none: its 19 instruction variants are `input`, `constant`, `copy`,
`clear`, `push`, `pop`, `is_empty`, `tag`, `field`, `as_integer`, `box_integer`,
`node`, `add`, `multiply`, `equal`, `jump`, `branch`, `return`, `reject`. There is
also no ordering comparison, which is why dispatch below must be an equality
ladder.

So the representation that fits the data bound is a representation the language
cannot read. Fitting the bound and being inspectable are, at this profile, two
different things.

## Result 3: the program bound is consumed by dispatch alone

Executed: a 17-case opcode ladder over the 17 opcodes the object program actually
uses, each case returning a distinct declared integer and one declared fallback for
an unmatched tag. The generated program is **90 instructions of the 128 allowed** —
3 per case plus a two-instruction body and its prologue. For scale: the whole
object interpreter is 51 instructions and interprets 3 tags.

Its runtime cost is position-dependent, as a linear equality ladder must be:

| tag | 0 | 8 | 16 | unmatched |
| --- | --- | --- | --- | --- |
| native steps | 9 | 33 | 57 | 56 |

That is 3 native steps per ladder position. Reaching the last opcode of 17 costs 57
steps before its semantics begin.

## Result 4: a data-driven index step costs four native steps, and the static alternative is dearer

There is no indirect register addressing: every register operand in the instruction
set is a static index. A self-interpreter must therefore reach the object register
file either by a data-driven loop or by a static ladder over the index. Both were
measured:

| Route | Cost recorded |
| --- | --- |
| data-driven index iteration | 4 native steps per iteration; total steps 8 / 24 / 40 at workloads 0 / 4 / 8 |
| static 16-case index ladder | 85 instructions of the 128 allowed |

## Result 5: the bound is located from both sides, not assumed

The executed boundary cases pin the node bound exactly, and every refusal names the
bound it hit:

| Generated input | Observed |
| --- | --- |
| exactly 127 nodes | admitted, `Returned`, 2 native steps, received node count 127 |
| 128 nodes | refused before execution, exit 2, `adva: data capacity exceeded` |
| depth 13 | refused before execution, exit 2, `adva: data capacity exceeded` |
| a node with arity 9 | refused before execution, exit 2, `adva: node arity exceeds 8` |

With `input-127-nodes` accepted and `input-128-nodes` refused, the counting in
Result 1 is a statement about a real admission edge rather than about a paper
limit.

## What this supports

Within the bounds this profile already declares, the object program's own
instruction grammar has no *inspectable* representation, and the instruction budget
for interpreting it is largely spent before any opcode semantics is written. The
three constraints are now measured rather than guessed:

1. **Data:** 169 nodes are needed and 127 are allowed; the 110-node packed
   alternative needs an unpacking operation the vocabulary does not have.
2. **Program size:** a 17-case dispatch ladder alone costs 90 of 128 instructions.
3. **Fuel:** each interpreted step must pay at least one ladder traversal (3 native
   steps at best) and its operand accesses (4 native steps per index iteration),
   against a 2048-unit lifetime budget and a frozen sample that needs 134 object
   steps. This last item is a lower-bound reading of the measured rates, not an
   executed end-to-end interpretation.

For the choice the report leaves open, this is the first evidence that discriminates:
a *checked translation* between the carrier and the program/process boundary does
not by itself move any of the three bounds, whereas the *separately scoped
extension* route must name which bound moves — data nodes (or a new unpacking
operation), program instructions, and lifetime fuel — and record the overhead, as
the report already demands.

## What this does not establish

- No self-interpreter was written, run or refuted. Nothing here is an impossibility
  theorem, and the report's open question about the interpreter's own grammar stays
  open.
- Only two encoding schemes were counted. A third scheme inside 127 nodes may exist;
  this preflight did not search for one and claims no completeness.
- The measured ladder and index costs price *this* object program's 17 opcodes. A
  smaller instruction set, or a different profile, would price differently.
- The counting function reads declared bounds and the object program's bytes. It
  executes nothing, and its verdict is arithmetic about a bound, not a run.
- No provenance, sharing/graft, SourceId or stable-promotion question is touched.
  As in the report, the correspondence with native sharing and graft identity
  remains an open obligation.
- Adding indirect register addressing, integer division or a larger bound would
  change these numbers, and that is exactly what a separately scoped extension is
  for; this note records the price it would have to justify, not a prohibition.

## Files and reproduction

- Contract and checker: `experiments/self_interpretation_capacity/contract.json`,
  `check.py`.
- Retained record: `experiments/self_interpretation_capacity/evidence/attempt-1` —
  47 files from 12 CLI launches: generated programs, generated inputs, every run,
  every refusal's stderr, `encoding-count.json` and `results.json`.
- Regressions receive that record without executing anything:
  `tests/python/test_self_interpretation_capacity.py`.
- The object program, the machine and every declared bound are unchanged; no
  campaign, fuel or search was reset or repeated.
