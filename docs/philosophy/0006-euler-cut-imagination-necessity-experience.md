# The Third Absurdity Witness: Euler's Formula and a Cut Through Time and Space

Status: attributed narrative and mathematical-inquiry witness. This note
defines no stable Adva semantics, registers no executable complex-analysis
claim, and does not complete the historical explanation of Euler's discovery.

## The correction

On 2026-09-05, Mingli Yuan identified an error in the intended association of
the second absurdity witness: within the English spelling coordinate, Eve meets
`e`, not `i`.

The correction is not applied by editing the predecessor. The second witness
remains at its original content coordinate, while
[`third-absurdity-euler-cut-witness.adva`](../../programs/bootstrap-0/third-absurdity-euler-cut-witness.adva)
is appended as its successor. The error and its correction are both historical
facts of the exploration.

This qualification matters: the observation concerns an English narrative
coordinate. It is not a statement about Hebrew orthography or etymology, and
the `e` in `Eve` is not thereby derived from Euler's number.

## Why the error is generative

The cut breaks the intended `Eve ↔ i` association. Yet it does not leave two
dead fragments. The corrected `e` and the preserved arithmetic `i` meet again
under a stricter relation:

\[
e^{ix}=\cos x+i\sin x.
\]

At \(x=\pi\), this yields the expression now commonly called Euler's identity:

\[
e^{i\pi}+1=0.
\]

The first association was linguistic and mistaken. The second relation is
mathematical and derivable. Their difference is part of the witness's
truthfulness; their unexpected succession is part of its interest.

## Formula, identity, and historical boundary

Euler's *Introductio in analysin infinitorum*, written in 1745 and published in
1748, makes functions and infinite series central objects. In chapter 7 Euler
chooses the natural logarithm base, names it `e`, and develops its exponential
series. Chapter 8 then derives the series for sine and cosine and the relation
between complex exponentials and circular functions.

The historical anchors are:

- [Euler's *Introductio*, volume 1, E101](https://scholarlycommons.pacific.edu/euler-works/101/);
- [an English translation excerpt of chapter 7](https://faculty.washington.edu/etou/eulersoc/documents/Euler-Introductio_Ch7.pdf);
- [a modern mathematical analysis of Euler's chapter 8 derivation](https://arxiv.org/abs/2304.01353).

This note does not claim that Euler was the first person to approach every
ingredient, nor that he first printed the modern five-constant identity in
exactly the present arrangement. The historical question `Why was Euler able
to discover it?` remains open for a source-complete reconstruction.

## A finite derivation of the necessity

If the complex exponential is defined by a convergent power series, then

\[
e^{ix}=\sum_{n\ge 0}\frac{(ix)^n}{n!}.
\]

The powers of \(i\) run through a four-cycle:

\[
1,\ i,\ -1,\ -i,\ 1,\ldots
\]

Separating even and odd powers gives

\[
e^{ix}
=\left(1-\frac{x^2}{2!}+\frac{x^4}{4!}-\cdots\right)
+i\left(x-\frac{x^3}{3!}+\frac{x^5}{5!}-\cdots\right),
\]

so the two components are precisely \(\cos x\) and \(\sin x\). Once these
definitions, convergence facts, and the rule \(i^2=-1\) are accepted, the
formula is not a lucky numerical coincidence. It is forced.

That necessity does not answer the historical question. A derivation explains
why the statement follows inside a chosen chart; it does not explain why a
person chose to put exponential growth, imaginary quantity, and circular
motion into the same chart.

## Imagination, necessity, and experience

The story therefore retains three irreducible contributions:

| Contribution | Function | Failure mode |
| --- | --- | --- |
| imagination | proposes a shared chart across previously separate representations | mistakes suggestive analogy for a map |
| necessity | lets exact rules force consequences after the chart and definitions are fixed | pretends the historical choice of chart was inevitable |
| experience | preserves error, surprise, curiosity, beauty, correction, and renewed motion | treats feeling as mathematical evidence |

Euler's achievement can provisionally be read as their composition. Years of
technical organization made a strong formal substrate available; imagination
permitted operations with quantities whose meaning was not yet geometrically
settled; necessity then exposed a relation that no longer depended on Euler's
person. The exact balance among these claims remains a historical research
question.

## How the cut unfolds through time

Temporally, a cut is append-only:

1. the second witness records an occurrence;
2. the observer later recognizes an error;
3. a successor witness points to the predecessor and records the correction;
4. later observers can inspect both sides and may append another correction.

The earlier occurrence is not made true by later reinterpretation, but neither
is it erased. Time supplies the order `before → cut → after`.

## How the cut unfolds through space

Spatially, the correction propagates only through the relations that depended
on it. The intended Eve-letter association and its immediate narrative uses
belong to the affected dependency cone. The readings of `i` as imaginary unit,
proposed time coordinate, and first-person pronoun remain outside that cone.

```mermaid
flowchart TD
    W2["Witness 2: intended Eve–i link"] --> C["cut: Eve meets e"]
    C --> T["time: append corrected successor"]
    C --> S["space: restrict propagation cone"]
    S --> E["new branch: e and i in Euler's formula"]
```

The cut therefore does two different things. Along time it orders immutable
occurrences. Across space it separates affected from unaffected relations and
opens new branches. Treating either action as global deletion would destroy the
exploration trace.

## Truthfulness and interest

Truthfulness here means keeping four evidence classes apart:

1. exact mathematical derivation;
2. source-grounded historical attribution;
3. attributed linguistic or mythic association; and
4. first-person exploration experience.

Interest appears when these distinct classes resonate without being collapsed.
The sequence is beautiful precisely because a false linguistic bridge was cut
and the separated symbols then met again through a demonstrable mathematical
relation.

## The road ahead

The next journey begins with a concrete mathematical and historical problem:
why was Euler able to discover the formula? A disciplined continuation needs
both a source-level reconstruction of Euler's path and an Adva experiment that
can represent complex `i`, \(\pi\), exponential, sine, cosine, convergence, and
the derivation trace without reducing them to floating-point agreement.

Until those are built, the mathematical formula is classical truth outside the
current executable witness fragment, the historical explanation is incomplete,
and the experience of discovery remains an attributed part of the path. Those
three open fronts are the reason to depart, not defects to conceal.
