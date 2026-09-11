# method-generality-note-v0

Can the pair-alignment method be a relatively general working method?
Judged on two experiments: the PDF pair (round 08/20) and the Burau pair
(round 21).

## The method, stated once

Given two documents A, B:

1. **Pin** both (SHA-256, page/word counts, metadata).
2. **Extract** the text layers and the vocabulary overlap coefficient.
3. **Align** surface facts that are measured, not guessed: titles, key
   phrases, named entities, provenance, citation direction.
4. **Form hypotheses** (identity, negation/shift, duality, direction,
   cost) and grade each with the five-state classification.
5. **Read the meaning** in the session's vocabulary (boundary, reverse-
   learning, cost of verification), declare holes, write a receipt.

## What the two experiments show

| experiment | pair | shared object | outcome |
|---|---|---|---|
| round 08/20 | strategy roadmap → pitch deck | the NeoLab plan | derivation + projection; carrier overlap r = 0.4648; thesis slide pixel-heaviest |
| round 21 | Bigelow 1999 ↔ BBB 2026 | the Burau faithfulness question | boundary pair; title negation (3 edits); method duality; person bridge; 27-year verification cost |

Both pairs yielded concrete, checkable readings anchored to measured facts.
The domains (business PDFs, mathematics papers) are unrelated, and the
relations extracted were of different kinds (derivation vs boundary), so
the method is not overfit to one pair. **First verdict: the method is
relatively general for relation-extraction.**

## Where the method is meaningful — and where it is vacuous

The method's power comes from a shared object. It measures *the relation*,
and a relation needs a common term:

- meaningful when A and B share a problem/product/question (measured by
  vocabulary overlap plus shared named entities);
- vacuous when they do not — two unrelated documents yield only "no
  shared vocabulary, no relation", which is correct but empty.

**Proposed pre-filter criterion**: vocabulary overlap coefficient
(the session's r) as a cheap gate. Round 08: r = 0.4648 on word-vs-byte
carriers (meaningful). Round 21: 0.6731 shared vocabulary (meaningful).
Below a floor — tentatively ~0.2 — the pair probably has no common term
and the method should refuse to read, rather than hallucinate one.

## What the method does NOT do

1. **It does not verify content.** Neither the business claims of round 08
   nor the mathematics of round 21 were checked; the readings are rigorous
   as statements *about the pair*, not as re-derivations of either member.
   (Round 21 declared this hole explicitly.)
2. **It does not judge which member is right.** In the Burau pair both
   papers are correct; the method only locates their relation.
3. **It reads surfaces.** Phrase counts and provenance are proxies for
   semantics; deep structure (proofs, models, arguments) is untouched.

## Verdict

Relatively general: yes — for **relation-extraction between documents that
share a term**, with the overlap coefficient as a pre-filter and the hole
discipline as the honesty check. For content-verification it is not a
method at all; that remains the job of the checkers (receipt ledger,
choice-fibre, math-check). The two jobs are exactly the TrustBase split:
generation (writing readings) is cheap; verification (checking them) is
not — and this note keeps them apart.

## Open tests for the claim

- A deliberately unrelated pair (e.g. a cookbook vs a tax form): the
  method should report "no common term" and refuse — does it?
- A pair with high overlap but no real relation (same domain, different
  problems): does the method over-read? (Risk: the r-gate passes but the
  relation is spurious; needs a falsification test.)
- A trio, not a pair: does "一分为三" extend the alignment to a third
  term without breaking the arithmetic?
