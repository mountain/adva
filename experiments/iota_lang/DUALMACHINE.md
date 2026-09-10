# DualMachine specification, version 0

Authoring artefact of the iota-lang completion line (adva research 0167).
Substrate-side only: nothing here is connected into adva.

The recorded iota-lang sources declared three term forms in `Parser.java` and
ran none of them:

```
Binary         < a b >      parsed, no rule anywhere
Applicative    ( a b )      marshalled by onCons, no coherent loop
Concatenative  [ a b c ]    parsed, no rule anywhere
```

This specification fixes the semantics of the two *construction* forms as one
machine with two regimes, and states why the third form is not a construction.
It is the design the recorded sources never contained.

## 1. The claim under test

> `()` is time and `[]` is space, and one dual stack carries both.

Formally:

- a **time frame** `(a b)` is an application: its head decides everything that
  happens to the rest of the term;
- a **space frame** `[a b c]` is an ordered family of simultaneously present
  subterms: there is no head, and no element decides any other;
- both are evaluated by the same dual stack, and the two regimes cannot
  interfere.

This is a bounded hypothesis about two nested brackets. It is exactly the item
0070 lists as a nonclaim ("a general normal form for mixed nested brackets"),
and it is asserted here for `()` and `[]` only.

The hypothesis holds for the space regime and for the three simplest time cases,
and it is **not yet reproduced** for the time regime in general; section 9
records the measured state and the single remaining defect.

## 2. State

One dual stack `(l, r)`. No second stack, no mode flag.

| Stack | Meaning | Order |
| --- | --- | --- |
| left `l` | the reduced position: the head that is pending | top of stack = next to reduce |
| right `r` | evaluated subterms already produced | top of stack = innermost / last produced |

`l` is the **time coordinate**: at most one head is pending, and it is the only
thing that can cause a reduction. `r` is the **space coordinate**: every
subterm that has already been evaluated sits there, ordered, whether or not
anything is pending.

## 3. Invariant

> **I1.** Every reduction rule consumes exactly one head from the top of `l`.
> **I2.** Every rule that produces subterms pushes them to `r`, top-first in
> application order, and pushes at most one head back to `l`.
> **I3.** The two regimes of section 5 both obey I1 and I2, so a space frame
> nested inside a time frame, and a time frame nested inside a space frame, are
> both handled by the same rules.

Consequence: `r` accumulates in exactly one order for both regimes, and no rule
needs to know which regime its term was written in. I2 is the property the
recorded `onCons` and `onS` violate, in opposite directions (0167 section 4).

## 4. Termination and reading

Each regime declares its own stop condition and its own read-out:

| Regime | Frame | Stop condition | Read-out |
| --- | --- | --- | --- |
| time | `(a b)` | `l` empty and `r` holds exactly one term | that term |
| space | `[a b c]` | `l` empty | the ordered family in `r` (n terms, n >= 0) |

The recorded halt condition (`l` empty) is the **space** stop condition
applied to **time** frames, which is why the recorded loop reads intermediate
states as results (0167 section 5).

A term that stops with `l` empty and no rule applicable is a **stuck term**, not
a result: it is reported, never silently returned as a value.

## 5. Rules

### 5.1 Marshalling (both regimes)

A compound term on top of `l` is split by its own constructor:

```
(a b) on l          =>  a on l , b on r        (head to time, operand to space)
[a b c] on l        =>  a,b,c on r, in order   (all elements to space, nothing to time)
```

The head of an application is the only thing that ever returns to `l`; that is
what makes `()` a temporal form.

### 5.2 Reduction (time frames only)

With the conventional left/right convention of section 2, the combinator rules
are the recorded ones once their push order obeys I2:

```
i     x            =>  x
k     x y          =>  x
s     x y z        =>  (x z) (y z)
```

`(x z)` and `(y z)` are produced as pending applications on `r`; the rule does
not evaluate them, because the head `x` may be a variable. They are evaluated
when they become the pending head.

### 5.3 Space frames have no reduction rules

There is no rule whose head is a space frame. `[]` orders and collects; it
never rewrites. A space frame is a value: its evaluation is the evaluation of
its elements, in order and independently.

This is the whole difference between the two regimes. `()` has rules that
consume a head; `[]` has none, so its elements are never dependent.

## 6. Mixed nesting

- `[(i x) y]` — space containing a time frame: the time frame is evaluated as a
  subterm, then the results are ordered by the space frame.
- `([a b] c)` — time whose head is a space frame: the space frame is evaluated
  to an ordered family, but it is not a combinator, so no rule applies to it as
  a head. The term is **stuck** and reported as such. Applying a space frame is
  not a licensed operation in version 0.

The second case is a decision, not an oversight: licensing `([a b] c)` would
mean giving `[]` a head-consuming behaviour, i.e. making it a third reduction
mechanism, which section 1 denies.

## 7. The angle form is not a third regime

`<L | R>` is not marshalled, not reduced and not evaluated here. Reasons, all
recorded before this specification:

1. 0070: the unmarked angle form denotes a **relation over a typed singular
   middle object**, not a value, and needs a middle `N_D`, two pinch maps, an
   observer policy `Q`, a version `v`, and a resolution `rho`.
2. 0070 section 1.1: Conway order admissibility and through compatibility are
   **logically independent** judgements, so the form carries a tuple of
   judgements and not one outcome.
3. 0021: objectification of a presented form is a non-injective, non-natural
   quotient that does not commute with scaling, so making the form evaluate to
   a value would silently discard the presentation.

An angle form therefore has no normal form to reduce to. In version 0 it is
**refused**: a `<L R>` term reaching the machine produces an explicit refusal
naming the missing middle object, never a wrong value and never a silent
stuck term. Refusal is the honest reading of "not yet authorized".

## 8. Implementation note: what building it changed in the design

Three points in the specification above were wrong or incomplete before the
machine existed, and are recorded here because they are the substance of the
work rather than its detail.

**8.1 Value move (I2's base case).** A head with no rule is not stuck. In
`(x y)` the atom `x` has no rule, and treating that as a stall makes the machine
refuse every term it cannot reduce — including `(x y)`, whose normal form is
itself. The correct reading is that a head with no rule has no further work and
*is* a value: it moves to the space stack. This one rule is what makes `(x y)`,
`((k x) y)` and `[x]` terminate with a read-out.

**8.2 Spine flattening.** `(a b c)` is right-nested application. A machine that
re-marshals one bracket at a time never has `S`'s three arguments in hand at the
same moment, so the recorded `onS` rule could not fire on `(((s x) y) z)` at
all. An application is therefore read by flattening its spine once: the head
plus its arguments, arguments pushed in reverse so the first sits on top — the
convention the recorded `onS`, `onK` and `onI` already assume.

**8.3 Frame ownership instead of counting.** A frame must own its arguments.
Delimiting by a shared stack's depth is not enough once frames nest, because a
nested frame's arguments sit above the enclosing frame's reading position. The
machine therefore records, per frame, the space-stack depth it opened at, and a
closing frame takes exactly the values above that depth.

## 9. Measured state of version 0

Run: `experiments/iota_lang/run-dual.sh`, evidence
`docs/research/0167-evidence/dualmachine-v0.jsonl`. 29 cases, 9 pass.

| Group | Cases | Pass | What it checks |
| --- | --- | --- | --- |
| A | 17 | 3 | the cases recorded in iota-lang `SKITest` |
| B | 6 | 6 | the space frame: order, headlessness, nesting, no reduction |
| C | 3 | 0 | mixed nesting (0 = stalls as specified, not a pass) |
| D | 3 | 3 | the angle form is refused in every position |

Passing: `testXY`, `testI`, `testK`; all six space cases; all three refusals.
The space regime is complete for version 0. Group C stalls where section 6 says
it should, and a stall is not a pass, so it is reported as such rather than
counted.

**The remaining defect is one, and it is structural.** `S` and `iota` produce
*pending applications* as their parts:

```
S x y z   =>  ((x z) (y z))
iota x    =>  (x S K)
```

The machine stages those parts on the space stack, but a closing frame only
*assembles* its parts and does not evaluate them. So `(((s x) y) z)` yields
`(((y z) (x z)) x)` — the parts are present, in the wrong order, and
unreduced — and `iota` yields `(((ι k) s) x)`, which is the expansion with its
`x S K` ordering reversed and its parts never evaluated.

The fix is explicit and does not change any rule: a rule that produces terms
must emit a work item that evaluates each part to a value and *then* assembles,
rather than writing terms into the frame's operand list. The machine already has
that item (`Item.APPLY`); what is missing is a variadic form of it, plus the
ordering discipline that the last argument is evaluated last. Until that exists,
every group A case that needs `S` or `iota` fails, which is 14 of the 17.

Version 0 therefore does not reproduce the recorded contract, and this section
is the reason. No failure was tuned away to make a test pass.

## 10. What version 0 does not license

- `([a b] c)` is refused as a stall (section 6), so a space family can never be
  applied. That is a decision, and the fixture asserts the stall explicitly.
- The three `testII`-family cases cannot pass in principle: the recorded suite
  gives five different expect-strings for one term, and none of them is the term
  it builds. They are kept in the suite as recorded so the contradiction stays
  visible.
- `testFalse` asserts `S K x y = y`; the machine computes `(x y)`, which is the
  standard value and agrees with the same machine's `testS`. That is a contract
  defect, not a machine defect, and the suite keeps both cases.
- No typing, no confluence claim, no general normal form for nesting beyond
  section 6, and nothing whatsoever about the angle form.

## 11. What this specification does not settle

- Whether the two regimes are the intended reading of the author's `()` and
  `[]`. This is a design decision taken here and recorded, not a recovered
  intention.
- Any semantics for the angle form, any objectification, any number, any
  ordering relation.
- Any typing. The machine is untyped; `([a b] c)` is refused as stuck because
  no rule applies, not because a type checker rejected it.
- Confluence or a general normal form for arbitrary mixed nesting beyond the
  two licensed cases in section 6.
- Anything about adva. This is a substrate-side machine.
