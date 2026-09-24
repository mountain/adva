# 0211 — Six places, two alphabets, and the policy of a finite arithmetic truth

Date: 2026-09-23. Direction: Mingli Yuan. Analysis, checker and note:
deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted through his account
as an authorized proxy. Account use is not his authorship, review or endorsement.

Status: one bounded external exact experiment. No Rust witness, no stable API
change, no library admission, no Seal, and no claim about any text.

Base: `79f6353511d736ae743b109f1c573b652eff170a`. Library gitlink:
`73a6af4ac4ed8225366d3c16794e309cff15f51d`.

---

## 1. Why six places, and what this note deliberately does not import

The direction motivating this note is that two of the programme's working
ideas — an arithmetic truth that a finite observer can settle, and an
exploration that never claims to have closed — have older Chinese formulations.
The structures named were the six-line configuration of the *Zhouyi* and the
eighty-one-head, nine-praise address system of the *Taixuan*.

**No text, edition, transcription, commentary, sequence, name table or
annotation from either work is imported here, and none is needed.** Everything
below is a finite combinatorial or arithmetic object that the contract declares
in full:

| Object | Declaration |
|---|---|
| Six places | `1..6`, with two declared involutive matchings `κ = (1 2)(3 4)(5 6)` and `τ = (1 4)(2 5)(3 6)` |
| First alphabet | the `64` words of `F₂⁶`, one bit per place |
| Three maps on it | complement (placewise negation), reversal, and the inner-four reading `N(x) = (x₂,x₃,x₄,x₃,x₄,x₅)` |
| Second alphabet | the `729` six-place ternary addresses, split into a head of four places and a position of two |
| Declared successor | the position advances by one and the ninth position returns a boundary instead of carrying |
| A three-step partition arithmetic | `49` items, three splits, a strip of `1 + r(left) + r(right-after)` with `r` read mod four |

Any classical name that appears to fit one of the resulting objects is left
unattached. Attaching it needs a sourced review that this note does not
perform, and importing the text to do it would need an admission record it
does not have. The reading of the two alphabets as "binary" and "ternary" is
therefore a statement about `2⁶ = 64` and `3⁶ = 729`, nothing more.

## 2. The two declared pairings generate a regular group, and the six-cycle is not in it

`κ` and `τ` are both fixed-point-free involutions, and they are *transversal*:
no place is paired with the same partner by both. Their union is a graph of
degree two everywhere, hence a disjoint union of cycles, and the exhaustion
confirms it is a **single** six-cycle, `1-2-5-6-3-4-1`.

The group they generate has order **six**, its element orders are
`1, 2, 2, 2, 3, 3`, and it acts **freely** (no non-identity element fixes a
place) and transitively. Six points, six elements, free: the action is
**regular**, so the six places are the six elements of that group itself. The
product `τκ` has order three.

One distinction is worth keeping, because it is easy to lose: the alternating
walk that produces the six-cycle is **not** an element of the group. The group
has no element of order six. A cycle in the union of two matchings is a cycle
of a graph; it is not a group element, and calling it "the six-cycle of the
group" would be the same conflation as reading an orbit partition off a
generating set.

## 3. Three maps on the sixty-four states

`N` is `F₂`-linear — all `4096` ordered pairs were checked — of **rank four**,
so it destroys two of the six bits. Its kernel is spanned by the two outer
places:

```
ker N = {000000, 100000, 000001, 100001}          |ker N| = 4
im  N has 16 words
```

So the first and last places are exactly the information `N` cannot see:
changing either leaves the reading unchanged. The image of each unit place is

```
e₁ ↦ 000000   e₂ ↦ 100000   e₃ ↦ 010100
e₄ ↦ 001010   e₅ ↦ 000001   e₆ ↦ 000000
```

`N` commutes with complement and with reversal. The complement commutation is
not luck: `N(1⃗) = 1⃗`, so complementation is a translation that `N` fixes. In
general `N(x + e) = N(x) + N(e)`, so a single-place change becomes the change
of that place's *image* — and for the two outer places the image is zero, which
is the same statement as the kernel.

## 4. The eventual image: two states rest, two oscillate

The second iterate collapses further:

```
N²(x) = (x₃, x₄, x₃, x₄, x₃, x₄)                 rank 2,  |ker N²| = 16
N⁴ = N²
Per(N) = im N² = { 000000, 010101, 101010, 111111 }
```

These four words are the **entire** periodic set: the fixed states are exactly
the two constant words, the only non-trivial cycle is the pair
`101010 ↔ 010101`, and **every one of the sixty-four states reaches this set
within two steps**. Nothing else is periodic.

This is the cleanest finite form of "perpetual exploration" the experiment
found, and it is worth stating precisely rather than rhetorically. Iterating
this reading is an exploration that cannot wander: after two steps it is
confined to four states, and on those four it either rests at a fixed point or
alternates forever. There is no third outcome, no escape, and no state that
takes longer than two steps to get there. The exploration is finite, and its
non-closure — when it has one — is exactly a two-cycle.

A second, smaller fact: on those four states, the clock generated by `κ` and
`τ` and the inner reading `N` do the same thing. Both fix the two constant
words and both swap the alternating pair.

## 5. Four orbit partitions, and one count I got wrong by hand

`N` is not the only map that partitions the sixty-four states. Exhaustion gives:

| Group generated by | Orbits | Sizes |
|---|---:|---|
| complement | 32 | 32 × 2, no fixed state |
| reversal | 36 | 28 × 2 and 8 fixed |
| complement and reversal | **20** | 8 × 2 and 12 × 4 |
| `κ` and `τ` acting on places | 16 | 2 × 1, 1 × 2, 6 × 3, 7 × 6 |

The eight reversal-fixed words are the palindromes
`000000 001100 010010 011110 100001 101101 110011 111111`.

**Correction, recorded rather than quietly repaired.** I derived the
complement-and-reversal row by hand as 18, on the belief that no state is fixed by both involutions at
once. That belief is wrong for six places: the condition `reverse(x) = ¬x`
pairs places `(1,6), (2,5), (3,4)` with no unpaired middle place, so it has
`2³ = 8` solutions. Burnside then gives `(64 + 0 + 8 + 8)/4 = 20`, and the
checker refused the retained count of 18. A middle place would have made the
hand argument right; six places do not have one.

The last row is a **different partition** of a different group, and the checker
asserts the inequality rather than leaving it implied: the group generated by
the two pairings is not the group generated by the two classical involutions,
and the reversal is not an element of it. Four groups, four partitions, none of
them interchangeable.

## 6. A second alphabet on the same six places

The second interface has six ternary places, split as four head places
(`3⁴ = 81` heads) and two position places (`3² = 9` positions). The
head-and-position pair is a bijection onto `3⁶ = 729` addresses; all 729 were
checked in both directions.

Its declared successor is **partial**:

```
advances                     648
boundaries (no successor)     81
advances changing one ternary digit   486
advances changing two ternary digits  162
```

The `162` is not an accident: the nine positions written in two ternary places
carry on two of their eight steps (`2 → 3` and `6 → 7`), and `2 × 81 = 162`.

The sharper statement is a comparison. The six-place ternary **numeral**
successor is total: it has `729` steps and carries into a head place `81` times.
The declared successor agrees with it on **all 648** of the steps where no
carry occurs and refuses exactly the other `81`. So the declaration is not a
different arithmetic; it is the numeral successor with its carry domain cut
off. The contract also **declares** that the interface carries `731` states
against the `729` addresses, so two declared states have no address at all.

That last pair of numbers is a **declaration, not a measurement**, and the
distinction is kept because an earlier draft of this section read it as a
measurement. The checker enumerates the `729` addresses and nothing else: it
enumerates no declared state set, so it neither counts the `731` states nor
measures the shortfall. It **reads** the declared shortfall from the contract's
own declaration of it instead of typing the `2` again, and its second field is
renamed `declared_state_count_declared_in_the_contract` so that it no longer
reads as a computed count; the first field keeps its retained name only because
the paired test reads that name, and it is labelled in the checker as a
declaration. `731` is therefore `729` plus the declared two, and "731 against
729, so two have no address" is arithmetic on one declared and one computed
number. What the exhaustion does establish is the exact half: the `729` addresses
are in bijection with the head-and-position pairs, and the declared successor
agrees with the numeral successor on all `648` steps of its domain.

## 7. One step is not the same relation on the two interfaces

| | first alphabet | second alphabet |
|---|---:|---:|
| states | 64 | 729 |
| canonical step | change one place | advance the position |
| steps | 384 | 648 |
| steps changing exactly one place | 384 | 486 |
| steps changing two places | 0 | 162 |
| states with no successor | 0 | 81 |

Every one of the `384` single-place steps changes exactly one place, every
state has six of them, and no state is terminal: the first interface's step
relation is total, symmetric and six-regular. The second interface's step
relation is a partial function with `81` terminals and a quarter of its steps
moving two places at once. "One step" therefore names two different relations.
(This is also why the binary interface's own *numeral* successor is a poor
match for it: only `32` of `64` binary numeral steps change a single place.)

## 8. The two interfaces read each other one way only

Reading a binary word as a ternary address place by place embeds it
**isometrically**: all `4096` ordered pairs agree on Hamming distance, the
image is exactly the `64` addresses whose six digits lie in `{0,1}`, and the
third digit value is never used. On that reading the second interface carries
the first with a spare value at every place.

The other direction fails, and fails at two different strengths:

* **Counting alone:** `729 > 64`, so every binary reading of the ternary
  addresses has a fibre of at least `⌈729/64⌉ = 12`.
* **Place by place:** if the reading must be one binary function per ternary
  place, the fibre of an image point is the product of the per-place fibres,
  and the smallest achievable largest fibre is **`64`** — not 12. Insisting
  that the reading respect the place structure costs a factor of more than
  five over what the address count alone forces.

In places: an injective binary reading needs `⌈log₂ 729⌉ = 10` binary places,
while a place-by-place reading needs `2 × 6 = 12`. **The placement structure
costs exactly two binary places.**

Finally, the two interface sizes are coprime and their joint period is
`64 × 729 = 46656 = 6⁶`. Two six-place observers with different alphabets
generate a six-place *seximal* address space and nothing smaller.

## 9. A finite arithmetic truth that is a policy, not a theorem

The last experiment is pure arithmetic and imports nothing. A pile of `49`
items is split three times; at each split one item is set aside and each of the
two piles is read mod four, with the two readings plus the set-aside item
forming a strip that is removed. The pile is always left a positive multiple
of four, so the three strips sum to `49 − 4k` and the outcome `k` has four
possible values.

**The remainder convention is derived, not assumed.** Reading a zero remainder
as four gives strips `{5: 36, 9: 12}` at the first split; reading it as zero
gives `{1: 12, 5: 36}` and never produces a nine. If the outcome set is
declared to be the classical two values, exactly one of the two conventions
survives. This is a case where the arithmetic decides the convention.

Then the distribution. Three declared split policies, each a distribution over
admissible split points, give three different exact answers:

| Outcome | classical | uniform over splits | independent items | uniform over residue classes |
|---|---:|---:|---:|---:|
| 9 | 3/16 = 0.1875 | 110/559 = 0.196780 | 0.187499862 | 3/16 |
| 8 | 7/16 = 0.4375 | 8633/19565 = 0.441247 | 0.437501069 | 7/16 |
| 7 | 5/16 = 0.3125 | 735193/2426060 = 0.303040 | 0.312498052 | 5/16 |
| 6 | 1/16 = 0.0625 | 95/1612 = 0.058933 | 0.062501017 | 1/16 |

**The classical table is exactly the residue-class policy and is not the
uniform-split policy.** The two differ by exact rationals, not by noise:

```
outcome 9:  +83/8944        outcome 8:  +1173/313040
outcome 7:  -91803/9704240  outcome 6:  -23/6448
```

The nearly-classical column is worth reading carefully. Under the independent
item policy each item goes left or right on its own, and the answers agree with
the classical ones to six decimal places. **They are not equal.** A floating
comparison would report agreement; the exact rationals do not. That is the
whole difference between a measurement at floating resolution and a statement
about a rational.

Two further exact facts separate the two classical step parameters, which are
usually quoted together:

* The first split strips five with probability **exactly `3/4`**, which *is*
  the classical value, and it is the uniform-split value because `48` is a
  multiple of four and the four residue classes are exactly balanced. The
  classical first parameter is a theorem of the uniform policy.
* The second and third splits strip four with probability **`(n+1)/2n`** at a
  pile of `n` admissible splits, and `n = 4k+3` there, so the value is
  `1/2 + 1/(2n)` — **strictly greater than `1/2` at every pile the procedure
  can reach** (`22/43, 20/39, 18/35, 16/31, 14/27, 12/23` for piles
  `44, 40, 36, 32, 28, 24`). The classical `1/2` is the limit as the pile
  grows, and it is never attained. The cause is one residue class: the range
  of split points has `4k+3` members, so three classes hold `k+1` and one holds
  `k`, and exactly that imbalance lifts the probability above one half.

So the classical four-outcome table is a truth about a declared reading of
"divide into two", reproduced exactly by one policy among the three natural
ones, with one of its two parameters exact and the other a limit that the
procedure never reaches. **Nothing in the arithmetic alone selects the table.**
That is a concrete instance of the programme's own distinction that an
arithmetic check needs an interpretation.

## 10. The same syntax, two declared scopes

A smaller check runs the same point the other way. A monadic syllogism family
is declared with `64` moods, four figures, and two existence scopes; all `512`
contracts were decided against all `255` non-empty occupancy masks, with the
set-theoretic semantics imported rather than reproved.

```
valid forms, scope "boolean"          figure 1: 4   figure 2: 4   figure 3: 4   figure 4: 3   total 15
valid forms, scope "terms non-empty"  figure 1: 6   figure 2: 6   figure 3: 6   figure 4: 6   total 24
```

The syntax is identical. Only the declared scope moves, and it moves nine
forms. A finite success has a scope, and the scope is part of the statement.

## 11. What the checker ran

```console
python3 experiments/six_place_interface/checker.py --output experiments/six_place_interface/evidence.json
```

[`checker.py`](../../experiments/six_place_interface/checker.py) uses the
standard library only — integers, sets and `Fraction`; no floating-point value
enters any acceptance test — and its output is compared against the retained
[`evidence.json`](../../experiments/six_place_interface/evidence.json) with
timings removed. The retained run records **548 assertions** over the nine
sections, with `RLIMIT_CPU`, `RLIMIT_FSIZE` and the wall alarm installed. The
checker launches no child process and allocates no large structure, so it
installs **no address-space ceiling**: the contract's memory figure is a
declared budget observed as peak RSS, and it is not an enforced limit. It also
refuses to overwrite an existing output path.

An earlier revision of this checker did install an address-space limit. That
made the repository's portability inventory inconsistent with its own frozen
bytes, and the audit test failed. Rather than edit another experiment's frozen
inventory and its reviewed category counts, the limit was removed, because it
buys nothing here: with no child process there is no address-space failure to
guard. The failure was real, it was caught by an existing check, and it is
recorded here rather than rewritten away.

The four controls that keep the checks from being vacuous:

* the six-cycle is asserted **not** to be a group element, so the group-order
  check is not reading the walk as the group;
* the two involutions' partition is asserted **not** to equal the generated
  group's partition, so the four orbit tables cannot be one table copied;
* the uniform-split and independent-item policies are asserted **not** to
  reproduce the classical table, so the "only the residue-class policy
  reproduces it" line is a comparison and not a tautology;
* the two remainder conventions are asserted to give different first-strip
  counts, so the convention argument is decided by data.

## 12. Residual and non-claims

Not established here, and not implied by anything above:

* **No text is identified.** Neither classical work is quoted, transcribed or
  represented, and no state, orbit, kernel or cycle found above is claimed to
  be a hexagram, a head, a praise or a line of any edition. The apparent fits
  — four states at the centre of the inner reading, eight reversal-fixed
  states, a pairing orbit count — are recorded as structure and left
  unattached, because attaching them requires a sourced review this note does
  not perform.
* **The places of the two interfaces are not claimed to be the same objects.**
  Their comparison goes through one declared place-to-place correspondence. A
  different correspondence changes the embedding's arithmetic but not the
  counting bounds, which do not depend on it.
* **The third ternary digit value is not a third truth value and not an
  unknown.** It is an address digit; the "unknown" of the programme is an
  evidence boundary on a query, a different object, and the two are not
  merged here.
* **The arithmetic result is about the declared policies, not about any
  historical procedure.** No procedure is described, no textual form is
  claimed, and which policy a historical practice used is not decided. The
  endpoint conventions are separated only at the first split; the piles
  reached at the second and third splits depend on the policy, and the closed
  form `1/2 + 1/(2n)` is a property of the declared policy rather than of any
  practice.
* **The syllogism check is about the declared monadic fragment and its two
  scopes.** It is not a statement about Aristotelian logic, modal logic or any
  historical logic.
* **No native consequence.** No `SourceId`, no observer, no aperture, no
  operation, no `Seal`, no claim promotion, and no connection to the six
  native primitive words. The six places here are six declared positions in a
  finite combinatorial object.

The next useful step, if this line continues, is not a wider search but a
**sourced** one: a reviewed, admitted reading that can say which finite object
above corresponds to which named structure, with the source's own version
recorded. Until that exists, the mathematics stands on its own and the names
stay off.
