# Round 31: the two halves of the period-three situation

Date: 2026-09-11. Direction: Mingli Yuan. Reading and finite checks: assistant
(DeepSeek Harness), submitted through his account as an authorized proxy.

This round is a reading round. It adds no native semantics, no new epoch, and no
library word. Its finite content is registered as `receipt-31.json`; its
adva-side records are Research 0167 and 0168, named and pinned below rather than
duplicated here.

## 1. What this round read

The 1975 paper is conventionally quoted as "a point of period three". Read from
the published pages, its hypothesis is the inequality `d <= a < b < c` with
`b = F(a)`, `c = F^2(a)`, `d = F^3(a)`. Period three satisfies it; it is not it.
The paper also does not claim sensitivity, does not contain the phrase
"scrambled set", and does not cite Sharkovsky. Those are four separate
corrections, and each one changes what the result can be used to say.

The correction that matters for this programme is the second clause of the
uncountable-set conclusion. Alongside "the pair never merges" there is "the pair
comes arbitrarily close infinitely often". Together they say: there are
uncountably many pairs whose histories stay distinct while their *values* become
indistinguishable infinitely often. That is the formal version of the rule this
programme already runs on — value agreement recovers no provenance — except that
here it is a theorem about a class of maps rather than a discipline about
bookkeeping.

## 2. Why it is a round and not an aside

AEG's own hierarchy is

```
expression tree -> marked history -> operator -> geometric or quotient state -> endpoint value
```

with each arrow forgetting information. Homotopy continuation, the second half of
the same author's career, takes the same position on the numerical side: a
solution is a tracked path, and a loop around the discriminant locus permutes the
solutions, so "the same solution" is defined only up to a path class. This
programme's identity discipline takes the same position a third time: identity is
carried by source, occurrence and history, never by value.

All three refuse the last arrow. The 1975 theorem states the price of taking it.
So the two halves are not a coincidence of one biography and they are not an
irony: they are an impossibility statement and a constructive workaround for the
same act of forgetting, and this programme is already on the workaround side
without having described itself that way.

**No source found in this round links the two programmes as an intention.** The
link is an outside reading, recorded as one, and it is the reason this round
exists rather than a claim it makes.

## 3. What the finite content is

One exact consequence was checked and registered on the adva side. A period-three
interval map forces, by its covering relation, the transition matrix
`[[0,1],[1,1]]`; the golden one-hole recursion of the atlas carries
`[[1,1],[1,0]]`; the two are the same linear map under a swap of basis, and both
square to a matrix of trace 3 with characteristic polynomial `t^2 - 3t + 1`.
That identity is exact and is derived, not stipulated — the covering relation is
computed from exact interval images.

Two controls refuse the dynamical reading of it, and they are the reason the round
is worth recording:

- the golden one-hole map is monotone, has one attracting fixed point and no
  two-cycle, so the shared polynomial governs a tame map as well;
- the rotation by one third has every point of period three and is an isometry,
  so three alone is not chaos outside an interval.

So the number three is critical for maps that fold, and the shared polynomial
decides nothing. The refusal is the content.

## 4. Holes declared

- No AEG object, no adva object and no three-computer cycle is shown to be an
  interval map, to carry an order structure, or to have a periodic orbit of any
  period. The three cyclic readings of one carrier are compatible with the
  rotation control, and nothing here distinguishes them from it.
- The identification of Human/World/Machine with the temporal, spatial and
  constructive computers remains Open and is not advanced.
- The folding that separates the tame regime from the chaotic one is not
  characterized; only its existence is exhibited by two examples.
- The uncountable set, the sharpness of the Sharkovsky ordering, and the
  statement that the golden ratio is the least entropy at which period three
  appears are imported. They were not reproved.
- This round does not open the continuation contract it argues for. That
  proposal stays a proposal.

## 5. Pins

- `docs/research/0167-li-yorke-period-three-and-homotopy-continuation.md` —
  source audit, corrections, bibliography, flagged items.
- `docs/research/0168-triadic-cycle-and-continuation-discipline.md` — the
  reading as a research plan, the `tau_n` branch point, and three questions.
- `experiments/li_yorke_period_three/` — the registered bounded checker and its
  evidence; claim `adva.bounded-experiment.li-yorke-period-three-matrix.v0`.
- `docs/research/0167-evidence/` — the retained raw reading report and the three
  superseded first-draft scripts, one of which counted fixed points by
  floating-point scan.
- AEG paper series `609ac96b4df802a8a4a6c4079c43c2fae466bc3a`, whose governance
  states the hierarchy quoted in section 2.
