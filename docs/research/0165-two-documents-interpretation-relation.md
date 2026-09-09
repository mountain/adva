# Research 0165: two document artifacts and their interpretation relation

Date: 2026-09-09. Status: proposed research note; the probing method and
the relation are recorded, the documents themselves are not published.
No claim entry is registered in claims.toml.
Direction: Mingli Yuan. Probing and record: assistant (local AEG repo).

## 1. The two pinned artifacts

| Artifact | SHA-256 | Kind | Metadata |
| --- | --- | --- | --- |
| `BP001(8).pdf` | `1ea0c0beff4da7fe5aefdc5d6650351d6da339e49b6e81ac0ba4bccda5115353` | 10-page PDF 1.3 | Keynote via macOS Quartz; 2026-08-25; title BP001 |
| `NeoLab - TrustBase(1).pdf` | `c88d6b34c966a62290f89dbf2d112c10318930987eaece070c9881fdd004bea9` | 14-page PDF 1.7 | author Jiamin Zhao; 2026-09-09; slide deck |

The files were supplied as "two binaries" at the operating-system root;
`file` identified both as PDF documents, so the Mach-O profiler hole
(`otool: is not an object file`) was recorded and the tooling adapted:
`mdls`/`strings` for metadata and outline, `pdftotext` for content, plus
a bounded Python stream probe.

## 2. The probing method (reusable five stages)

1. pin: SHA-256 plus `file` type;
2. structure: producer/creator metadata, outline/bookmarks;
3. vocabulary: extracted word sets and their intersection;
4. byte relation: 64-byte chunk-hash shared segments;
5. hypotheses: a table of candidate relations, each with a check, the
   observed evidence, and a five-state status (EvidenceStutter /
   VariationObserved / IncidentalVariation / Rejected / Unknown).

The kit and the receipt (receipt 08, chained to receipt 07) are retained
in [0165-evidence](0165-evidence/). Errors and holes are kept, not
hidden; they define the next round.

## 3. The found relation: a dated strategy-to-pitch derivation

Hypotheses H1-H6 (see `0165-evidence/hypotheses-v3.json`) yield one
relation: the first document is the domain strategy, the second is its
generalized platform presentation, separated by two weeks.

- Shared thesis core (different wording):
  - BP001: "Reasoning is becoming abundant. Trustworthy, cumulative
    knowledge is not."; "A tiny verifier gives us trust. It does not
    give us a production system."
  - Deck slide 2: "AI generation is becoming cheap. Verification is
    not."; slide 3: trust must become "explicit, independently
    checkable, and bounded."
- Product vocabulary coined in between: BP001 contains **zero** matches
  for EvidenceBase / Claim DAG / Trust Kernel / Trusted Frontier, while
  the deck's architecture is exactly
  EvidenceBase -> Claim DAG -> Verifiers -> Trust Kernel ->
  Trusted Frontier.
- The deck bookends on "From Generation to Verification" (slides 1 and
  14), the same arc this repository's recent rounds walked: quine relay
  generation (Research 0164) to advance receipts and stutter
  classification (Research 0161/0163).

## 4. Boundary

The two PDFs are organization-internal documents. This repository keeps
only the pins, minimal quotations, the method and the receipts; the full
text extractions and the PDF copies remain in the local AEG repository
and are not published here. The note claims no authorship of the
documents and registers no experiment claim; it records an
interpretation relation and a reusable probing method.

## 5. Open holes (next round)

- TrustBase producer metadata absent; BP001 revision (8) export date may
  lag actual revision rhythm;
- sentence-level alignment of strategy items to slides is sketched, not
  exhaustively enumerated;
- the deck's rendered PNGs remain outside any repository.
