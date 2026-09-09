# meaning-gate-test-v0

The meaning of the unrelated pair — and what the refusal taught the method.

## The experiment

First falsification test from method-generality-note-v0: feed the
pair-alignment method a pair with no common term and see whether it
refuses honestly.

Objects: 2025 Instruction 1040 (126 pp) vs American Cookery, Amelia
Simmons 1796 (PG #12815, 43-page container). Two documents from
different centuries, domains, and purposes.

## What the method did

| gate | value | decision |
|---|---|---|
| naive vocabulary overlap | 0.2567 | **admits** (falsified: function words) |
| stopword-filtered content overlap | 0.2092 | **admits** (falsified: generic verbs, homographs) |
| top-25 term-head intersection | **0/25 = 0.00** | **refuses: "no common term"** |

The heads are disjoint: cookbook's head is
{one, pound, put, water, half, butter, sugar, boil, flour, eggs};
the tax form's head is
{line, form, tax, amount, income, filing, return, credit, enter}.
There is no shared term, so the alignment machinery has no surface
to align — and it said so.

## The meaning of the refusal

The null reading is the meaning. The method's output on a pair with
no common term is not a relation, and must not be one: a manufactured
reading would be a hallucination wearing the method's clothes. The
refusal IS the correct result, and it is measurable — the head
intersection is 0, while the same measure gives 0.12 for the NeoLab
derivation pair and 0.56 for the Burau boundary pair.

The three numbers order correctly:

```
0.00  cookbook vs tax form      → refuse
0.12  BP001 vs TrustBase        → weak common term: derivation
0.56  BBB vs Bigelow            → strong common term: boundary
```

## What the test taught the method (gate correction)

The 0.2 vocabulary-overlap proposal from method-generality-note-v0 is
**falsified**: two variants of it admit a cookbook/tax-form pair.
The discriminating signal lives in the head of the frequency
distribution, not the body: what a document is *about* shows up at the
top of its content-word ranking, and grammatical scaffolding lives in
the long tail.

**Superseding gate**: intersection fraction of the top-25 content-word
heads; refuse below 0.08 (provisional, two calibrations only).

This is the falsification loop doing its job: the method's own open-
tests section predicted the risk ("the r-gate passes but the relation
is spurious") and the experiment found exactly that failure — then
corrected the instrument.

## Holes

- Homographs remain a residual risk at the head: "line" tops the tax
  head and appears in recipes (a line of a recipe vs a line of a
  form). In this pair the heads came out disjoint, but no sense
  disambiguation was performed; a pair whose heads share homographs
  could still pass the gate spuriously.
- The 0.08 refusal threshold rests on only two calibrations (0.12,
  0.56); it needs a boundary sweep (pairs at 0.05–0.15) to be set.
- The cookbook PDF container is generated (txt2pdf.py): the text is
  the public-domain original, but the layout is ours — declared, not
  hidden.
