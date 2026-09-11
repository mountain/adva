# meaning-gpt4-alphamissense-pair-v0

The relative meaning of the two PDFs, found by meaning.py v3.

## Objects

| object | document | year | pages | words | vocab |
|---|---|---|---|---|---|
| `2303.08774v6.pdf` | OpenAI, "GPT-4 Technical Report" | 2024 | 100 | 46,637 | 6,651 |
| `nenbakraniya.pdf` | Nen Bakraniya, "Accurate Proteome-wide Missense Variant Effect Prediction with AlphaMissense" | 2025 | 37 | 624 | 305 |

Pins: `c33a66da…` / `54fd5158…`. No citation in either direction.

## What the alignment found (align.json)

| phrase | GPT-4 | AlphaMissense | reading |
|---|---|---|---|
| model | 505 | 11 | the shared genre word |
| predict | 46 | 14 | the shared virtue |
| evaluat* | 105 | 3 | generation's report evaluates itself heavily |
| benchmark | 38 | 1 | same |
| safety | 93 | 0 | OpenAI-only concern |
| language | 177 | 0 | domain of the first |
| variant | 2 | 21 | domain of the second |
| missense | 0 | 25 | domain of the second |
| pathogen | 1 | 7 | domain of the second |
| limitation | 21 | 5 | the shared genre closing |

## Arithmetic of the pair

```
GPT-4:         100 pages, 46,637 words, 6,651 vocab
                 next-token prediction, predictable scaling (1/1000th compute)
AlphaMissense:  37 pages, 624 words, 305 vocab
                 missense variant effect prediction, proteome-wide
```

Two documents in one genre, two vocabularies in one overlap (0.6984, inflated
by the deck's small vocabulary), one shared verb: predict. The domains are
complementary: one predicts the next word, the other predicts whether a
mutation matters.

## The meaning, in three readings

**1. Genre reading.** Both are AI-model reports with the same skeleton:
model description, data pipeline, evaluation, limitations. The genre
vocabulary survives across the domain gap (model, predict, limitation);
the domain vocabulary is mutually exclusive (language/safety vs
missense/pathogen). They are the same *kind* of document written for two
different *kinds* of intelligence — and the student deck is the derived,
sparse-text member: 17 words per page, its meaning living in figures,
exactly like the slide PNGs of the round-20 probe.

**2. Generation-versus-verification reading.** This is the session's
thesis found in the wild. GPT-4 is the flagship of generation: next-token
prediction at unprecedented scale. AlphaMissense is the flagship of
verification: it does not produce anything — it checks, mutation by
mutation, which variants are pathogenic. One system writes tokens; the
other audits the genome. The pair shows the division of labor that
TrustBase predicts: generation became cheap and massive; verification
stayed a separate, specialized, bounded task.

**3. Predictability reading.** The deepest shared line: GPT-4's report
makes its *own performance* predictable (forecasting benchmarks from
1/1000th of the compute) — verification applied to generation.
AlphaMissense predicts variant effects — verification applied to biology.
Both documents are about making the future checkable before it arrives:
the same "predictable = checkable" virtue, once pointed at language, once
at proteins.

## Holes

- No experiments re-run: neither GPT-4's benchmarks nor AlphaMissense's
  variant-effect claims were checked; the reading aligns surface facts.
- The student deck's figures were not analyzed at pixel level; most of
  its meaning is outside the text layer.
- The overlap coefficient 0.6984 is inflated by the deck's tiny
  vocabulary and is not comparable at face value with earlier pairs.


## Pixel-layer experiment (appended, receipt-26)

The declared hole — "the deck's figures were not analyzed at pixel level" —
was closed by rendering both PDFs at 150 dpi and measuring ink fraction
per page (pure-Python PNG decode: IHDR + zlib + unfilter; white = all
channels >= 240). pixel-probe.json holds all 137 pages.

| measure | GPT-4 report | AlphaMissense deck | ratio |
|---|---|---|---|
| geometry | 1275x1650 (portrait letter) | 1500x844 (16:9 slides) | — |
| mean ink fraction | 0.0752 | 0.4674 | 6.2x |
| mean bytes/page | 328,907 | 464,387 | 1.4x |
| words/page | 467.6 | 39.4 | 0.08x |
| bytes/word | 703 | 27,274 | 38.8x |
| pearson(words, bytes) | 0.7354 | 0.0772 | — |

Three facts fall out:

1. **The deck is a slide deck.** 16:9 pages, full-bleed imagery with ink
   spikes near 0.98 on the cover/section/result pages (1-4, 7, 8, 23, 24,
   28, 29, 33-35, 37) — the same geometry as the round-20 slide PNGs.
2. **The report is text-carried.** r(words, bytes) = 0.735: its pixel
   weight tracks its text. The deck is pixel-carried: r = 0.077 — its
   byte weight has almost nothing to do with its 624 words.
3. **The deck pays 39x the pixels per word.** Its meaning is bought with
   ink, not vocabulary: 46.7% of every page is non-white, versus 7.5%
   for the report.

This closes the hole quantitatively: the earlier reading ("its meaning
lives in the figures") is no longer an impression but a measured ratio —
the two documents are not just about different domains, they carry
meaning on different layers. The report means through words (r=0.735);
the deck means through ink (r=0.077, 39x bytes/word).

Remaining hole: the pixel probe measures ink quantity, not figure
content — what the figures SAY is still unread (no OCR on raster text,
no figure classification).
