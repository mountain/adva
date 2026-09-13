# Freeze declaration: the Absurdity-emptiness record is not revised in place

Status: one bounded declaration, not a claim, not a Seal, and not a discharge.
It records a direction request, the three byte sequences it freezes, and the
negative control that was actually executed to show what the freeze does and
does not enforce.

## 1. The request, verbatim

> 可以加一个"此记录不再修订"的声明

Mingli Yuan, 2026-09-13, following his closure words `已经收到，确认，封印` and the
documentary checkpoint that recorded them.

## 2. What is frozen

| Path | SHA256 | What checks it |
| --- | --- | --- |
| `docs/research/0174-absurdity-emptiness-counterexample.md` | `b6027c83ee066b0e44776c2b79ac3fc96c5a93fea0d8c9f4dc82b3eae17a20af` | a declared material of the catalog entry `logic-absurdity-emptiness-counterexample` |
| `adva-library/knowledge-boundary/absurdity-emptiness-counterexample-v0.adva` | `a190b2f12d6067acaf411b3dc2dc71c3090273d19d31f81ce5bcb47f79c5e895` | the same entry, as its first material |
| `docs/research/0174-absurdity-emptiness-counterexample-checkpoint.json` | `8812485caf11c03fb0e39a9c7f4aa40a31953cae5568ff3d4bbde3cdcdfa30ba` | the same entry, as its second material |

The research note was registered as a material in the same change that adds this
declaration, so that all three can be checked by one existing reader rather than
by prose alone. Nothing else in the repository is frozen.

## 3. The negative control that was executed

The mechanism was not taken on faith. On 2026-09-13 the catalog was copied into a
temporary directory together with every file it declares, and one newline was
appended to one file at a time:

| Case | Result |
| --- | --- |
| unmutated copy | `CatalogConsistent` |
| one newline appended to note 0174 | `InvalidCatalog`, `reference digest mismatch: docs/research/0174-absurdity-emptiness-counterexample.md` |
| one newline appended to the library document | `InvalidCatalog`, `reference digest mismatch: adva-library/knowledge-boundary/absurdity-emptiness-counterexample-v0.adva` |
| one newline appended to the checkpoint | `InvalidCatalog`, `reference digest mismatch: docs/research/0174-absurdity-emptiness-counterexample-checkpoint.json` |

The unmutated row is what keeps this control from being vacuous: the same
invocation reports `CatalogConsistent` before the mutation and `InvalidCatalog`
after it, so the reader is not a machine that refuses everything. The run used a
copy in a temporary directory; no repository file was mutated to produce these
rows.

## 4. What "not revised" means here, exactly

- These three byte sequences are not edited in place. A correction, a
  supersession or a challenge arrives as **a new appended record** that names
  what it supersedes, exactly as every other note in this directory arrives.
- The freeze is enforced by digest pins, not by a new checker. Editing one of the
  three files fails `math-check` with the reason above, which is a mechanical bar
  rather than a convention.
- **The freeze does not prevent correction, and it must not be used to.** The way
  to lift it is to re-pin the digest, and re-pinning is a deliberate, visible
  commit. A record that cannot be corrected at all would contradict the rule this
  very record carries forward: a challenge may reopen it, appended rather than
  rewritten.

## 5. What the freeze does not mean

- **Not immunity.** A later note may supersede this record and a challenge may
  reopen it. This declaration and the checkpoint that precedes it must not be
  cited as a reason to refuse a reopening.
- **Not a claim, an admission or a Seal.** No native import, no derivation
  certificate and no checked witness stands behind the frozen material, so no
  Rust `Seal` is issued or issuable. The directory-separated Pascal-rooted growth
  obligation keeps its own fixed checkpoint at `RecordedOpen` with
  `native_seal: NotIssued`, and stays `Open`.
- **Not evidence of correctness, and not a review.** The direction confirmed
  receipt and closure; whether the recorded diagnosis, the eight boundary defects
  or the six recognition triggers are right remains open to challenge.
- **Not a resolution of anything carried forward.** Whether a genuine same-scope
  claim and negation pair can be presented under the existing
  `ClosureFindingClassV0` is still `Unknown`, and the source and licence of the
  two third-party WebP images admitted under `experiments/enclosing_circles`
  remain unresolved.
- **Not a freeze of the repository.** The tests, the catalog pins themselves, the
  catalog counts and everything else move normally. A freeze that covered its own
  pins would be a refusal to correct rather than a record.

## 6. This declaration itself

It is not frozen and it does not pin itself. It is an ordinary named note: it may
be superseded or corrected by an appended record like any other. Pinning this
declaration would only move the question one step back, since its own pin would
need a pin.

## 7. Attribution

The frozen request in section 1 is Mingli Yuan's, quoted verbatim; the frozen
records were written by deepseek-v4-flash-vision-exp (DeepSeek Harness) and
submitted through his account as an authorized proxy, unreviewed and unendorsed.
This declaration and the negative control in section 3 are the assistant's work.
The authority here is the executed check and the retained digests, not a name.
