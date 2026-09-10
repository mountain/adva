# Golden-ratio receipts: staged resources, exact re-derivation, and eight refusals

Date: 2026-09-10. Direction and motivating questions: Mingli Yuan / 苑明理.
Formalization, staging and bounded execution: assistant.
Status: documentary resource staging plus one executed external exact
calibration. No native word, Rust type, IR change, stable keyword or geometry
admission is introduced.

Base: `99193036aa1651f8d1299901d57e3fd9a987e322`. Library base:
`bc92ddc` (`adva-library`, its own repository, recorded separately because
the outer checkout pins it as a submodule).

## 1. What arrived, and where it now lives

A local resource directory outside the checkout
(`/Users/mingli/Adva/resources/golden-ratio`, a sibling of this repository)
delivered 15 artifacts: a Chinese research atlas, a delivery container and its
members, a captured PDF and seven plates. One delivered entry, `.DS_Store`, is
macOS directory metadata and is excluded and recorded as excluded.

Every artifact is now staged byte for byte under
[`adva-library/golden-ratio/`](../../adva-library/golden-ratio/README.md) and
described once in
[`index.json`](../../adva-library/golden-ratio/index.json): delivered name,
staged path, role, SHA256, byte count, digest source, delivered structure and
the check that consumes it. Staging changes no delivered byte, and the
delivered directory was not modified. The staged set is 15 artifacts and
3,683,241 bytes; the largest is the captured PDF at 2,714,704 bytes.

The atlas itself is the primary presentation. It reads the Wikipedia article
at `oldid=1370346489`, extends the AEG paper lines on the one-hole template,
the figure-eight arithmetic word and the HNN realization, lists corrections to
earlier notes, and names its own minimal next step: a versioned task/witness
pair whose checker separates four receipt kinds.

## 2. Two boundaries the delivery itself carries

**The delivered digest record is partial.** `source/SHA256.json` covers five
container members and no plate. The seven plates and the captured PDF carry no
delivered digest, so their pins are first established here and are internally
consistent only. The staged index states this; the bounded run re-derives every
digest, compares the five delivered claims with the staged copies, and compares
all six container members with the staged files byte for byte. A digest still
records byte integrity only: not authentication, not semantic identity, not
proof.

**A picture is not a witness.** The plates are illustrations. The run checks
their media type and pixel dimensions and nothing else; no length, angle,
incidence or proportion is read out of a rendered image. The PDF is a browser
print-to-PDF capture; the run confirms only that it is a well-formed PDF whose
metadata names the article and whose bytes contain the revision identifier the
atlas cites. Neither object may be cited as evidence for an arithmetic or
geometric claim. That the atlas author *chose* those figures is provenance, not
support.

The figures carry a third boundary on top of the partial digest record: they were
not read at all. Section 3 separates what the carrier already decides, which
figure-to-claim correspondence is ours rather than the delivery's, and who would
count as the observer of a reading.

## 3. Plates: carrier, denotation and observer

No delivered figure was read. This section records what can be said without
reading one, and keeps three layers apart: what the carrier decides, which
correspondence is ours, and who would be the observer.

### 3.1 What the carrier already decides

The seven plate files are single-chunk VP8 lossless WebP renders, all exactly
500 px wide; the one JPEG carries no EXIF or XMP segment and no application
marker of its own; the figure rendered by the delivery's plotting script is a
2520x900 PNG. The delivered images therefore contain pixels only: no author, no
source revision, no licence, no page context and no scale. Two consequences
follow without any reading. A proportion cannot be measured off these files,
because nothing in them fixes a unit. And a name of the form `.svg.webp` at a
uniform width indicates a rendered thumbnail of a vector source rather than the
source object, so a discrepancy between a plate and its source would be
invisible here.

The atlas names none of the seven delivered figures, and the delivery carries no
caption for them. The Commons-style filename is the only per-figure description
that exists, which is why every content gloss in the staged index is marked
name-derived and none of them is a content observation.

### 3.2 The denotation table is ours, not the delivery's

The table below proposes a correspondence between each delivered figure and one
topic the atlas argues. It is constructed here: the delivery supplies no caption
and the atlas supplies no figure reference. Every row states what the bounded
run actually did with the corresponding statement, so no row may be read as a
certification of a picture.

| delivered figure | atlas topic it could illustrate | what the run established |
| --- | --- | --- |
| `plates/fibonacci-spiral.webp` | the Fibonacci square chain and its spiral reading | Nesting, area and coverage of the square chain are exact in the golden case for `n <= 16`; the arc chain is a different object, and the atlas's own residual - a model error separate from the ratio error - has no bound here |
| `plates/whirling-squares.webp` | the whirling-square division of the golden rectangle | One-step image, nesting, area, diameter, fixed point and the coverage identity are verified; the plate illustrates that chain and does not certify it |
| `plates/fake-real-log-spiral.webp` | the atlas's separation of a logarithmic spiral from a circular-arc imitation | Refusal R5: over one quarter turn an arc keeps radius ratio `1` while the spiral contracts by `phi^-1`, exactly, so the two are not similar |
| `plates/golden-triangle-and-fibonacci-spiral.webp` | the golden triangle and its gnomon subdivision | Executed: `cos 36` is verified as a Chebyshev root instead of being taken from a table, the two tile shapes are identified by the cosine law, bisecting a base angle cuts the opposite leg into `1/phi` and `1`, the smaller tile is the original scaled by `1/phi`, and the Heron area ratios `1/phi^2` and `1/phi` hold. The arc chain the plate also shows carries the same unbounded model error as the first row |
| `plates/dodecahedron-vertices.webp` | the dual dodecahedron of the twelve-vertex icosahedron | Executed: the twenty face centroids are the dual's vertices and sit at the icosahedron's inradius, whose closed form and the radius ratio are checked; the twelve faces are shown to be regular pentagons with diagonal-to-side ratio `phi`; and an inscribed cube is found by exact search with its edges as pentagon diagonals. The inscribed **octahedron** was not run |
| `plates/icosahedron-golden-rectangles.webp` | twelve vertices on three mutually perpendicular golden rectangles, the atlas's Borromean candidate | The vertex set is verified: 12 distinct vertices, 66 squared distances with minimum `4`, 30 edges, degree 5, 20 faces. The three rectangles are exactly the corner sets of those vertices; their boundaries are **pairwise disjoint** while their filled sets share the origin, and a translated copy is detected as meeting while a nearby copy is not. The link certificate itself remains **not constructed** |
| `plates/divina-proportione-illustration-13.jpg` | the Pacioli/Leonardo historical layer | Source object only. The atlas itself requires original text and later readings to be registered separately; nothing historical is imported |
| `source/golden_geometry.png` | the three explanatory panels of the delivery's plotting script | Illustration only. The script is staged and digest-checked but **not executed**: it needs external libraries and renders a figure that carries no evidence. Its third panel's configuration is now checked exactly, and its first two panels restate the rectangle and arc-versus-spiral distinctions that the run already settles |
| `source/reference/Golden_ratio.pdf` | the article revision the atlas read | Byte probe only: title, creation date and `oldid=1370346489` confirmed; the text is not parsed and nothing is imported from it |

Eight of the nine rows end in a residual or an explicit `Not executed`; only the
arc-versus-spiral row is fully settled, and it is settled by an exact refusal
rather than by looking at the figure. That is the honest state of the denotation
layer: the exact core is checked, the figures are not, and the figure-to-claim
correspondence is a proposal with obligations rather than a receipt.

### 3.3 Who would be the observer

A reading of a figure is an observation under a declared policy, not a
certificate: it selects what is looked at, at which resolution and with which
expectations. No such reading was performed here. The external model of this
session declares no image input, so this run has no image-reading observer at
all; a future reading, by a person or by an image-capable model, would have to be
registered as a **proposed** interpretation carrying its own observer, time,
frame and residual, as the library's other meaning documents are. A machine
reading would be another observer of the same plate, not an upgrade of it.

Nothing in this record becomes evidence because a figure looks like a theorem.

## 4. The executed calibration

Contract: [`experiments/golden_ratio/contract.json`](../../experiments/golden_ratio/contract.json),
written before execution. Checker and witness:
[`calibration.py`](../../experiments/golden_ratio/calibration.py) and
[`evidence.json`](../../experiments/golden_ratio/evidence.json).

```sh
python3 -S experiments/golden_ratio/calibration.py --output target/golden-ratio-fresh.json
```

The output path must not exist. Routes: one. Budget: 30 seconds, 20,000 checks,
200,000 nodes, 8 MiB of staged bytes, one child process with a 30-second cap,
1 MiB of output. Result: **Passed**, 969 checks, 2,916 nodes, 0.117 s before
serialization, one child process, no unbounded search, no random sampling and
no transcendental evaluation.

The active contract is version 1, which supersedes the frozen version zero by
digest; the version-zero file stays byte identical and the run checks that its
digest is unchanged. The successor carries the recorded amendment (the
boundary-disjointness obligation of section 3.2), the receiving audit's
corrections of section 8, and an explicit table of which bounds the run itself
installs. The run also attempts the declared process limits and records the
outcome: `RLIMIT_CPU` is installed here, and `RLIMIT_AS` is **refused** on this
platform because the process address space already exceeds the declared bound.
A recorded refusal is not enforcement, so the caller owns that bound.

The run has four tiers.

**Tier 0, resource integrity (15 artifacts).** Every staged artifact matches
its recorded digest and byte count; the five delivered claims agree; all six
container members equal their staged copies; the PDF probe checks the pinned
bytes, the header, the trailer and the revision marker `oldid=1370346489`, and
parses the title `Golden ratio - Wikipedia` and the creation date
`D:20260910123359+00'00'` out of the information dictionary in the staged bytes
and compares them with the declared values. That is a byte probe, not a PDF
validator, and it says nothing about the document's content; the eight images expose
the recorded media type and dimensions (the seven plates are 500 px wide; the
rendered figure is 2520x900).

**Tier 1, independent exact re-derivation.** The delivered checker encodes
`a + b*phi` over rationals. This run deliberately uses a second encoding of
the same field, `(p + q*sqrt 5)/2` with rational `p, q`, a different
conjugation, a different norm and a comparison that decides signs with rational
squares. In that encoding it re-derives: the minimal polynomial and the
positive embedding; the field/ring boundary, including that `3 - phi` has
norm 5 and leaves `Z[phi]` under inversion while `phi^2` stays; inverses for
all 24 nonzero small elements and the refusal of zero; `phi^n = F_n*phi +
F_{n-1}`, Cassini, the straddling convergent bracket with gap
`1/(F_n*F_{n+1})`, Binet, Lucas, `L_n^2 - 5F_n^2 = 4(-1)^n` and the
near-integer residual `0 < phi^-n < 1/2` for `2 <= n <= 24`, with the
n = 1 failure of that bound checked rather than assumed; the matrix power
identity; the affine word `abbbaBAAB`, its residual as an exact polynomial
`-(t^2 - 3t + 1)`, and the fact that the polynomial evaluated at `phi`
agrees with the concrete composition; rectangle images, area, diameter,
nesting, fixed point, coverage identity and strictly positive residual for
`n <= 16`; the twelve icosahedron vertices with 66 squared distances, 30
edges, degree 5 and 20 triangular faces; the three golden rectangles they
determine, whose corner sets are exactly those vertices, whose filled sets
share the origin while their boundaries are pairwise disjoint, and whose
disjointness test is controlled in both directions by a translated copy that
must meet and a nearby copy that must not; three exact hyperbolic `cosh`
values; eight substitution steps; the golden triangle and its gnomon, whose
cosines, tile shapes, base-angle bisector subdivision, self-similarity and
Heron area ratios are exact, with `cos 36` verified as a Chebyshev root rather
than taken from a table; the dual dodecahedron, whose twenty face centroids sit
at the icosahedron's inradius with both closed forms and the radius ratio
checked, whose twelve faces are regular pentagons with diagonal-to-side ratio
`phi`, and which contains a cube found by exact search whose edges are pentagon
diagonals; and three bounded golden-section searches with identical interval
traces.

Five checks are *new instances* rather than restatements of the delivered
fixtures: the inverse word at the same parameter, the reverse cut from
`21/13`, an eighth substitution step, a third search target `5/8`, and the
word at a non-root parameter.

**Tier 2, eight refusals.** Each correction the atlas lists becomes an
executable control: R1 the unit-edge icosahedron area `10*phi^2` differs from
`(5*sqrt 3)^2` by the exact comparison `100*phi^4 != 75`; R2 the three
hyperbolic length objects separate because the exact `cosh` values `3/2`,
`7/2` and `sqrt 2` are pairwise distinct; R3 the decimal `2.618` leaves a
nonzero residual where the exact root closes, and `1.618*0.618 != 1`; R4 the
residual area stays strictly positive while the squared diameter falls below
`1/10000`; R5 a circular arc keeps radius ratio 1 while the spiral contracts by
`phi^-1`, so no similarity maps one onto the other; R6 among the 1,680 nonzero
values `m + n*phi` with `|m|, |n| <= 20` the closest is exactly
`phi^-6`, a positive separation, while the one-dimensional projection keeps
approaching zero; R7 the residual polynomial `-(t^2 - 3t + 1)` and the
characteristic polynomial `t^2 - 3t + 1` of `M^2` coexist with two
different actions, and the word acts trivially on a line while `M^2` is not
the identity; R8 the HNN affine realization satisfies `t^{-1}ut = uv` and
`t^{-1}vt = vuv` while `u` and `v` commute, so the nonempty commutator
word maps to the identity.

**Tier 3, four receipt kinds.** The atlas asks one checker to separate a fixed
seed, an unknown tail, an exact closure and a finite-precision stop. The run
emits one receipt of each kind, each carrying all twelve fields the atlas
declares, and then refuses the four relabelings. The sharpest is executable: the
positive tail `x = 1/2` has image `29/18`, which lies inside the
unknown-tail image `(8/5, 13/8)` but *below* the seeded bracket's lower
endpoint `21/13`; so reporting the seeded bracket as tail coverage would
exclude a legal tail. The other three refusals separate a resolution stop from
emptiness, a parameter-specific closure from a general statement, and an open
image interval from a produced rational bracket.

**Tier 4, bounded replay.** The delivered checker runs once as a child process;
its status, 310 check names and twelve payload fields match the recorded
evidence exactly. Timing and platform fields (`cost`, `peak_rss_raw`,
`peak_rss_unit`, the two per-instance millisecond fields) are *excluded*
rather than compared. The replay reproduces a supplied implementation: it is
not an independent oracle, and it is reported as such.

## 5. Receipt terminology and its boundary

The four kinds and the twelve fields are registered as a proposed versioned
terminology contract in
[`docs/terminology/golden-ratio-receipt-v0.json`](../terminology/golden-ratio-receipt-v0.json),
with per-kind preconditions, field notes and the relabeling prohibitions. The
run checks that the contract's field and kind lists are exactly the ones it
emits, so document and executable cannot drift apart silently. A receipt is a
finite record about one declared question; it is not a native operation, not a
proof object, and not permission to reuse a result beyond the scope it declares.

## 6. Claim registry placement

One claim is registered:
`adva.bounded-experiment.golden-ratio-receipt-calibration.v0`. It records the
frozen scope, the budget, the executed result and the forbidden conflations.
The eight refusals and the four relabeling prohibitions are its counterexample
boundary.

## 7. Catalog placement

Two documentary entries are added to the math catalog and stay documentary:

- `arithmetic-golden-ratio-receipt-calibration` (home arithmetic, also a
  geometry reference) carries the executed calibration and its evidence.
- `geometry-golden-ratio-external-reference` (home geometry) carries the
  atlas, the plates and the captured source as an **external reference**: no
  same-home parent chain reaches the pinned Pascal root, so it is not a
  candidate successor. Admitted geometry successors remain zero and the
  Pascal-rooted growth obligation remains Open.

The catalog pins one index plus the atlas, the contract, the checker, the
witness and this record. It cannot pin the 15 staged artifacts individually:
the read-only checker's file bound is 96 files, 89 were already spent, and at
most seven new files fit, so per-artifact digests are enforced by the bounded
calibration of section 4 instead. That
substitution is stated here rather than hidden, and it is the reason the index
is the single pinned root of the resource set.

## 8. Receiving audit and the successor contract

An independent receiving review,
[`docs/research/golden-ratio-receiving-review.md`](golden-ratio-receiving-review.md),
audited the producer revisions `9ae99c9` (Adva) and `c9fce90` (library) and
landed as an addendum. It reports its own bounded numbers (738 replayed checks,
2,635 nodes among them), records that pytest was unavailable on the receiving
side, and lists six corrections to this record's prose and contract. Each is now
either fixed in text or turned into an executed check:

1. **The encoding is a rational pair, not an integer pair.** Every element of
   `Q(sqrt 5)` needs rational coefficients; `Z[phi]` is the matching-parity
   integer subset and is tested separately. The successor contract says this,
   and the run now checks a genuinely fractional element: `(2 + phi)/5`
   multiplies back to `2 + phi` and is outside the integer ring.
2. **The near-integer bound holds for `2 <= n <= 24`.** It fails at `n = 1`;
   the guard is now exercised by a check that `phi^-1 > 1/2`.
3. **PDF title and creation date are parsed, not copied.** The routine now
   reads them out of the information dictionary in the staged bytes during the
   run and compares them with the declared values. The scope stays a byte
   probe: header, trailer, revision marker and two metadata strings are not a
   PDF validator.
4. **Declared limits are not installed limits.** The run now attempts
   `RLIMIT_CPU` and `RLIMIT_AS` and records the outcome. Here the CPU limit is
   installed and the address-space limit is refused, because the process
   address space already exceeds the declared bound; the evidence says exactly
   that, and the contract states that where the run cannot install a bound the
   caller owns it.
5. **The word routine returns a translation only.** Equal counts of `a` and
   `A` restore multiplier one but do not in general clear negative powers from
   the translation Laurent polynomial. The docstring no longer claims
   otherwise, the nine-letter word is checked to have no negative power, and a
   two-letter control `Ab` is checked to have one.
6. **Bracket endpoint naming.** The ordered seeded bracket is
   `[21/13, 13/8]`, so `21/13` is the lower endpoint; one control string said
   otherwise. The string is corrected and the naming is now machine-checked.

The historical artifacts are not rewritten: version zero of the contract, the
frozen witness and the delivered resources keep their bytes and their pins. The
corrections live in the [successor contract](../../experiments/golden_ratio/contract-v1.json),
which records its predecessor's digest and the digest of the receiving review,
and which the run verifies before doing any work.

The successor contract is pinned by the executed run rather than by the catalog:
the read-only checker's file bound is 96 files and the catalog is at 95, so one
more reference would leave no room for later growth. The run enforces it instead,
by checking the frozen predecessor's digest and the receiving review's digest
before doing any work, and it stores the successor's own digest in the witness.
The catalog keeps pinning the frozen version-zero contract as the historical
artifact the first executions ran under.

## 9. Residuals and open obligations

- No native Adva, Rust or Lisp operation, type or builtin is created, and no
  `Seal` is issued.
- The replay reproduces a supplied implementation. Only the second encoding is
  an independent derivation, and only for the finite instances listed.
- No general receipt calculus, no general translation theorem between the two
  encodings, and no error bound for the quarter-circle approximation of a
  logarithmic spiral is established.
- The sphere-sampling generator, the Penrose patch matching, the inscribed
  octahedron and the Borromean link certificate in the atlas were not executed
  and are not covered here.
- The atlas's own minimal next step, a three-party versioned task/witness
  presentation in the Pascal style, remains open: those presentations are
  proposed research JSON whose three Human identities and native importer do
  not exist. This record supplies a contract plus an executed witness pair
  instead, and does not pretend to be that presentation.
- The plates carry no delivered digest, so their provenance rests on the
  delivery itself; a future delivery should ship a digest record covering every
  artifact, not only the container members.
- The submodule split matters for replay: `adva-library` is a separate
  repository, so a checkout without it cannot run the calibration, exactly as
  it cannot run `math-check`.

## 10. What this does not claim

That the golden ratio is part of Adva's kernel, surface or API; that a
historian's, artist's or biologist's reading of the atlas is settled; that the
delivered checker is wrong or right beyond the identities re-derived here; that
any plate depicts a construction that has been certified; that the eight
refusals exhaust the atlas's corrections for every future instance; or that a
finite exact witness establishes a general theorem.
