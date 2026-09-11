# meaning-interpretation-pdf-png-v0

The meaning of the binaries between the two PDFs.

## Objects

| object | role | pages | geometry |
|---|---|---|---|
| `/Users/mingli/BP001(8).pdf` | strategy roadmap (NeoLab, rev 8) | 10 | 1920 x 1080 pts |
| `/Users/mingli/NeoLab - TrustBase(1).pdf` | pitch deck (Jiamin Zhao, "From Generation to Verification") | 14 | 959.76 x 540 pts (16:9) |
| `/Users/mingli/slide-01.png … slide-14.png` | the binaries **between** the two PDFs: raster renderings of the pitch at 150 dpi, one batch, Sep 9 14:11 | 14 | 2000 x 1125 px, 8-bit RGB |

## Probe facts (probe.json, hypotheses-v1.json)

1. **Count invariant**: 14 PNGs = 14 pitch pages = 14 text-layer pages. `14 = 14 = 14`.
2. **Geometry invariant, exact**: the projection scales by 150/72 = 25/12. `540 * 25/12 = 1125` exact; `959.76 * 25/12 = 1999.5 → 2000` (round-up). Aspect 16:9 survives to within 1e-2.
3. **Structure invariant, dropped**: the text layer survives the projection only as pixels. The PNGs are no longer grep-able; the words live in the evidence text layer, not in the PNG bytes.
4. **Carrier overlap, partial**: pearson(words per page, PNG bytes) = **0.4648**. The two carriers share ~46% of their variance — correlated, not identical.
5. **Outliers**: slide-09 (value matrix) = 68 words / 204 KB = 3.0 KB/word; slide-14 (thesis page) = 27 words / 234 KB = **8.66 KB/word**. The thesis is carried visually 2.9x heavier per word than the matrix. Totals: 420 words / 1,827,308 bytes = 0.235 words per KB.

## Arithmetic of the relation

```
BP001 (10 pages, strategy)
   ↓ derive (Aug 25 → Sep 9)
TrustBase (14 pages, pitch)
   ↓ rasterize (150 dpi, ×25/12)
slide-01…14.png (14 pixel pages)
```

One content, three bodies. The first arrow is a **derivation** (strategy → pitch); the second arrow is a **projection** (text+vector → pixels). The binaries between the two PDFs are exactly the image of the second arrow: the pitch's visible face.

The projection splits into two lossy quotients, and they are duals:

| quotient | keeps | drops |
|---|---|---|
| P_text (pdftotext) | words, in order | layout, typography, geometry |
| P_pixel (pdftoppm) | layout, typography, geometry | words-as-words |

The deck's full meaning = words ⊗ layout. Neither quotient alone carries it: the text layer cannot show *which* slide carries the thesis visually; the pixel layer cannot say *what* the thesis is. The overlap r = 0.4648 measures how much of the meaning survives in either carrier alone — a little under half.

## The meaning, in three readings

**1. Projection reading (geometric).** The middle binaries are the geometric half of the pitch: the half that pdftotext threw away. Together with the evidence text layer they reconstruct the deck; each alone is a fragment. This is the dual-pair pattern already on file (dual-pair-receipt): same object, two representations, neither sufficient alone.

**2. Surface reading (the thesis applied to itself).** "AI generation is becoming cheap. Verification is not." Generating the deck was cheap: strategy → 14 slides. Verifying what the deck says requires *reading* it — and the raster layer is where human reading happens. The binaries between the two PDFs sit at precisely the spot where TrustBase's own thesis bites: they are the checkable surface of the pitch. And the check is consistent: the pixel-heaviest slide (14, 234 KB) is the one that states "trust must become explicit, independently checkable, and bounded" — the thesis is carried by the visual layer more than by the word layer, and the pixel layer is the only place that weight is visible.

**3. Positional reading (between the two PDFs).** BP001's words became TrustBase's slides; TrustBase's slides became the PNGs. The middle binaries are the moment the pitch acquires a face — the point where the strategy's meaning becomes visible to an eye, not just readable to a machine. They are the third body in "一分为三": strategy (Knowledge), pitch text (the plan's words), pitch pixels (the plan's face).

## Holes

- **No OCR executed**: no OCR engine on this machine; H5 (pixel-text equivalence) stays Unknown. The pixel layer's typography, color, and layout semantics were not machine-read — only size-distribution proxies.
- **150 dpi is a lossy quotient** of the vector page: sub-150-dpi detail (thin rules, small glyph features) is discarded without measurement.
- **mtime granularity**: all 14 PNGs share the same second (14:11); intra-batch order is unverifiable from timestamps alone.
