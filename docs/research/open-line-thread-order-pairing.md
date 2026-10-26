# Raw thread order survives source-bound open-line pairing

Date: 2026-10-20. Status: executed finite research-local experiment.
Baseline: `2154b3c6716e7b5a19b98b81aca7940c0c93fe7d`.

Authored by Codex (OpenAI), submitted through Mingli Yuan's authorized GitHub
account proxy; not his authorship, review, endorsement or correctness guarantee.
Original code, fixtures and prose under Unknown v0.3. No external expression
is incorporated; pytest is installed separately, not vendored.

## Question, frozen boundary and dependencies

PR #225 is merged at this baseline; the current open-PR query returned none.
Its [open-line residual pairing](open-line-residual-pairing.md) admits only
empty thread words. This run takes its explicit next step without changing
that receiver, its contract or its archived evidence.

The [new contract](../../experiments/open_line_thread/contract.json) was written
before implementation/execution. It fixes three cells, six ports, two channels,
two open ports and two residual entries. The first channel contains exactly
two raw `ThreadStep` records; the second is empty. The canonical word is
`[(thread-a,1,OVER),(thread-b,2,UNDER)]`. A fresh-source fixture uses distinct
whole/source/occurrence/residual/step labels. Each fixture also has a source
with the raw word reversed, giving four valid source contexts.

AM syntax stays `HistoryComposition(Hole(first declared hole), Use(first
source occurrence))`. This is literal finite syntax, not arithmetic: the gap
indices are positions, not an interpretation of additive zero or multiplicative
unity. Research 0123's arithmetic-universality and hypothesized-arithmetic-truth
remain Proposed. Their unproved source-class, target, translation and observation
obligations are not supplied here. No division, zero-point exemption, inverse,
noncommutative arithmetic reduction or historical cancellation is performed.

The main-pinned agenda and claims registry were reviewed alongside the current
WholeCut6, AM and closed-line calibrations. The unchanged imported source hashes
are executable pins. The base commit pins documentary context, so appending a
new claim does not break replay by changing an input file's current hash.
Research 0090 coverage and dependent 0092 all-fillings/promotion remain Open;
this paired evidence is not an M6 filler or a native `free` result.

One route, zero search nodes, at most 15 new-profile and two old-profile calls
per attempt, a 30-second subprocess timeout, a 1 MiB evidence bound and at most
one correction replay were declared. Trusted fixed-size dataclasses, Python,
the existing validators, OS and host are premises. No hard memory cap or
hostile-input parsing claim is made. The kernel/package contract at
`mountain/adva-machine@acfc9806fe18a36d0f7194dcc196a380b2834adf`,
`spec/framework/kernel-package-boundary-v0.1.md`, is a documentary dependency,
not an executable lock upgrade. No knowledge migration or framework
`communicate`/`accept` operation is claimed.

## Exact receiving relation and observations

`receive_two_step(term, expected, candidate, previous)` is a separate local
profile, not a new vocabulary item. The independently supplied complete source
must validate and have thread lengths `(2,0)`. The candidate must have exactly
the existing `OpenLineProposal` type and equal the ordered projection of that
source. The unchanged AM checker must succeed, and its residual ledger must
agree. Output contains the AM projection, the complete proposed ordered fields
and explicit `(port,hole,residual)` bindings. Only documentary paired-record use
is established; no effects, transformations or additional fuel are authorized.

All four own-context pairings pass. In particular, **reversal is not itself
malformed**: the reversed word is valid against its own expected source.
Substituting it under the original expected source is refused. Whole labels
alone do not identify a source; each complete expected object is separately bound.

Eight candidate substitutions refuse: reversed word, dropped step, renamed step,
changed gap, changed crossing, reversed motion, changed residual and fresh-source
substitution. Three expected-source controls refuse: a Boolean gap (Python's
integer alias must not count), duplicate step name and an empty word outside
this profile. Both old-profile calls continue to refuse nonempty words.
Every input and output is retained in [cases.json](../../experiments/open_line_thread/evidence/attempt-1/cases.json).

## Counterexample: AM equality is too coarse for raw thread order

For each of the two source families, let W and W' differ only by reversing the
first channel's two-step word. Both pass the existing WholeCut6 validator.
Their AM projections are equal, and their multisets of complete step records
are equal. Endpoints and motion are also unchanged. Their ordered proposals
are unequal, and the source-bound substitution check refuses the reversed one.

Thus neither this AM projection nor the unordered step observer separates
these two sources. A reconstruction function of either observer alone cannot
recover both raw orders. This is an elementary two-element non-injectivity
witness, not a new general theorem. It does not say the existing AM projection
is defective: preserving thread order was never its AM-only contract.

Conversely, this paired record contains enough information to distinguish these
two words. It is not a proof of invertibility for WholeCut6, topology, braid
inequivalence, physical motion, noncommutative arithmetic, historical semantics,
or source-changing transport. Sorting the steps would erase precisely the
distinction this trial protects; no normalization is silently performed.

## Actual costs and reliability boundary

One supervised child process passed **69 assertions**, with 15 new-profile calls,
two old-profile refusals, four positive pairings and two collision pairs.
Search nodes and correction replays: zero. Wall time including child launch,
imports and capture was **0.446444 s**. Construction took 0.000420 s;
first canonical receiving 0.001213 s; fresh-instance receiving 0.000158 s;
the two own-context reversed receives took 0.000455 and 0.000170 s. Eleven
negative receives took 0.001697 s; serialization plus decoding took 0.001776 s.
These are single observations, not a cost reduction comparison.

The supervisor measured child peak RSS **28,184 KiB** and its own peak RSS
**12,544 KiB**; the child self-sample was 28,160 KiB before process exit.
These are process maxima, not concurrent total memory or file sizes. The
attempt had 77,102 evidence bytes before the supervision summary.
Dependency setup reported 5.74 s resolution and 6 ms installation; complete
setup wall time was not separately measured. Primitive checker work,
separate authoring time, separately isolated filesystem-write time and real-user
benefit are missing measurements, not zero costs.

[execution.json](../../experiments/open_line_thread/evidence/attempt-1/execution.json)
and [supervision.json](../../experiments/open_line_thread/evidence/attempt-1/supervision.json)
retain exact observed values. The separate [archive verifier](../../experiments/open_line_thread/verify.py)
reads JSON without importing the producer or its dataclasses, checks both
collisions and all ordered output fields, checks source hashes and the preserved
claims prefix, and writes [validation.json](../../experiments/open_line_thread/validation.json)
and a byte manifest. This is a separate implementation of archive assertions,
not independent validation of the entire WholeCut6 theory. No full native or
Bootstrap Zero suite is claimed rerun; their source bytes are unchanged.
The archive check passed 71 checks over eight files in 0.096837 s before its
summary, with peak RSS 16,612 KiB. The research index check also passed.

## Reproduction

From a checkout containing this contribution, with fresh output paths:

```sh
python3 -m venv /tmp/adva-thread-replay-env
/tmp/adva-thread-replay-env/bin/python -m pip install pytest==9.1.1
/tmp/adva-thread-replay-env/bin/python experiments/open_line_thread/run.py /tmp/adva-thread-replay-result
cmp experiments/open_line_thread/evidence/attempt-1/cases.json /tmp/adva-thread-replay-result/cases.json
```

The supervisor enforces 30 seconds and refuses an existing output directory.
`cases.json` is deterministic; time/RSS summaries are not expected to match.
The archive verifier is intentionally write-once and is not a second trial.
An independently replayed checkout may inspect its checks or run it in a copy
without the existing validation/manifest files; do not overwrite frozen evidence.

## Utility and smallest continuation

New or revised vocabulary: **zero**. Existing raw word, exact source binding,
paired evidence and refusal concepts suffice. This helps Mingli and subsequent
agents detect a concrete loss of order when coordinating an AM reading with an
open-line record. It makes an unproved correspondence visible rather than
converting matching local images into closure. Jiamin's real-task benefit and
human acceptance remain unmeasured; no social-trust or expressive-power claim
is made. The same-resource speedup/word-learning experiment is not applicable
because neither is claimed.

Next minimal step: separately freeze one order-preserving fresh-renaming
correspondence, with exact step/source/occurrence maps and a swapped-step-map
refusal. This would begin checking a source-changing correspondence, which the
present two own-context records do not establish. Do not jump to braid reduction,
circle/logic views, universal grammar or general all-fillings closure.
