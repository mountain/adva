# Research 0163: Evidence stutter and the boundary of repeated learning

Date: 2026-09-08. Status: completed external finite audit; proposed vocabulary;
native learning and `free` remain **Open**.

## Question and repository state

Research 0162 retains a baseline 100-round campaign plus three more bounded
100-round cycles. Every round reports six completed `learn` protocol steps
and six completed `run` launches, while `free` is not run because its
adapter is unavailable. The retained summary correctly labels the loop
`Unknown`.

This audit asks a narrower question: across the declared output carrier, did
the 400 rounds produce any byte-level variation, or did the protocol repeat
the same evidence?

The input is pinned to repository commit
`1526f89feb096f21ee30a2e74fcdad0809321dcc` and complete tree
`e91b0d45cc2c9bcf732e7c1a327e3d82a46f677a`. Pull request 152 is a
separate, still-open draft based on the older
`1c5979d78dc9c2b79b633ea492c38fe09090f221`; this audit does not treat its
unmerged Research 0158 proposal as mainline evidence or stack new work on it.

## Frozen finite problem

For each retained round `r`, define the external byte projection

```text
P(r) = (
  learn-transition[1..6],
  learn-frontier[1..6],
  run-transition[1..6]
)
```

Each coordinate records path, byte count, and the blob object ID from the
pinned complete Git tree. Four directories times 100 rounds times 18
coordinates gives 7,200 entries.

The finite classifier is:

- `EvidenceStutter`: coverage is exact and every normalized `P(r)` is
  identical;
- `VariationObserved`: coverage is exact and at least two projections differ;
- `UnknownCoverageGap`: an expected coordinate is missing;
- `RejectedMalformedIndex`: coordinates are malformed or duplicated.

Variation is necessary for learning under this projection, not sufficient.
Stutter under this projection does not exclude differences in omitted timing,
reports, external inputs, or a future semantic observer.

The contract fixes zero search candidates, at most 8,000 entries, ten wall
seconds, eight CPU seconds, 256 MiB address space, 2 MiB input/output files,
and one correction replay. No `Real`, additive-zero, multiplicative-identity,
LABS, cryptographic, or native `free` judgment is made.

## Result

The exact coverage check found:

| Quantity | Result |
| --- | ---: |
| retained rounds | 400 / 400 |
| projected artifacts | 7,200 / 7,200 |
| normalized round fingerprints | 1 |
| later projections equal to the baseline | 399 |
| distinct blob IDs per fixed learn coordinate | 1 |
| distinct blob IDs per fixed run coordinate | 1 |

Thus the finite result is `EvidenceStutter`. Protocol completion is real
process evidence, but these 399 later projections do not provide new
byte-carrier evidence under the declared observer.

Three controls passed:

1. changing one OID in a fresh copied instance gives `VariationObserved`;
2. removing one coordinate gives `UnknownCoverageGap`;
3. duplicating one coordinate gives `RejectedMalformedIndex`.

This is also a coverage dependency in the spirit of Research 0090: incomplete
observation cannot be closed as stutter. It does not discharge 0090's original
prefix-family calibration or activate Research 0092.

## Proposed word: `evidence-stutter`

**Action.** Detect that a finite, fully covered sequence of completed
executions repeats the same declared evidence projection.

**Input.** A finite ordered round family, an explicit projection, exact
coordinate coverage, and retained byte identities.

**Output.** `EvidenceStutter`, `VariationObserved`,
`UnknownCoverageGap`, or `RejectedMalformedIndex`.

**Applicability.** A pinned, quiescent artifact set and a projection declared
before classification. The projection must include every coordinate that the
claim quantifies over.

**Witness.** The 7,200-entry pinned index and its single normalized round
fingerprint.

**Refusal.** Missing coordinates are `Unknown`; changed coordinates are
`VariationObserved`; duplicate or malformed coordinates are rejected.

**Replay.** Run the command in the experiment README against the retained
index and a fresh output path.

**Residual.** The word does not decide semantic novelty, useful knowledge,
source identity, report/timing novelty, external observations, human value, or
whether a different observer would distinguish the rounds. It never authorizes
`free`, deletion, automatic fuel renewal, or native equality.

The word is **Proposed**. The finite classifier is implemented and tested, but
the natural-language meaning and usefulness still require review.

## Cost comparison

The successful replay classified 7,200 entries and ran all three controls in
144.675 ms before serialization. Peak RSS reported by the child was 22,496 KiB
(about 21.97 MiB). The input is 1,304,750 bytes and the report is 9,656 bytes;
file size is not treated as peak memory. Search candidates: zero.

The requested external timing utility was unavailable and launched no
experiment. The first actual child then failed after classification because
the report constructor used JSON's `true` spelling in Python. The sole
correction changed it to `True`; inputs, classifier, outcomes, and budgets
were unchanged. The retained corrected replay passed. Research, authoring,
GitHub transfer, and prior 0162 execution time are not included.

Without this word, all 400 rounds remain correctly described as protocol
completed. With it, the same finite resource sees one baseline and 399
stuttering replays. A hypothetical stop after one confirmation would avoid
requesting 398 rounds, 7,164 artifact writes, and 4,776 child launches.
That is counterfactual accounting, not a measured runtime speedup and not
permission to discard the archived evidence.

## Help, limits, and next step

This distinction helps Mingli and later agents avoid using repetition count as
a proxy for learning or trust. It preserves the useful fact that the protocol
is repeatable while exposing the missing source of variation. Benefit to
Jiamin's real task has not been tested.

The next minimum step is not another 100-round replay. Define one versioned
`advance` receipt that binds a round to its predecessor and requires an
admitted delta in question, resource, observation, or checked result. Test it
once with an unchanged input (must return `EvidenceStutter`) and once with a
new, independently checked resource (may return `VariationObserved`, but
must not yet claim learning). Only a separately justified semantic checker may
promote that variation to learned knowledge or authorize a later `free`.

## Evidence

- [Frozen contract](../../experiments/evidence_stutter/contract.json)
- [Exact input index](../../experiments/evidence_stutter/input-index.json)
- [Checker](../../experiments/evidence_stutter/calibration.py)
- [Successful evidence](../../experiments/evidence_stutter/evidence.json)
- [Failed invocation and sole correction](../../experiments/evidence_stutter/failed-invocation.json)
