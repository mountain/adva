# Open-line residual pairing and a lossy-projection counterexample

Date: 2026-10-19. Status: executed finite research-only proposal.
Baseline: `5f427e8a2bd637ec5aa418a46ed614a677cc66ff`.

Authored by Codex (OpenAI), through Mingli Yuan's authorized account proxy;
not his authorship, review, endorsement or correctness guarantee. Original
code, fixtures and prose contributed under Unknown v0.3; no external expression
is imported. Pytest remains a separately installed dependency.

## Question and dependency audit

At the checked baseline, PRs #217, #221, #222 and #224 are merged. The open-PR
query returned no results. Research 0270 supplies only closed LineView pairing:
its residual ledger is necessarily empty. This trial continues its explicit
open-line-proposal residual, rather than repeating the closed tests.

Research 0123 still records arithmetic-universality and
hypothesized-arithmetic-truth as proposed words. This run has no arithmetic
domain and supplies neither word with a universality theorem. In particular,
additive zero and multiplicative unity are not identified; division at zero,
noncommutative order and historical inverses are not evaluated here.
Research 0090 coverage and the dependent 0092 promotion remain outstanding.
A test-local pairing is not an all-fillings closure or an M6 filler.

The [frozen contract](../../experiments/open_line_residual/contract.json)
fixes three cells, six ports, two through channels, two open ports, two
residual entries and empty thread words. AM syntax is exactly
`HistoryComposition(Hole(first declared hole), Use(first source occurrence))`.
Only a canonical source, a freshly renamed source and a residual-renamed
counterpart are constructed. There is one route, no search and nine receiving
calls. Native semantic code and the existing LineView are unchanged.

## What was received

`OpenLineProposal` is a test-local candidate record, not a promoted word or
stable interface. It retains ordered ports, channels, open ports, hole
declarations and residual entries. The caller supplies the complete expected
WholeCut6 independently. Its existing validator must succeed; the candidate
must equal the projection of that expected source; AM formation and projection
must succeed; the two residual ledgers must agree exactly. Output retains the
AM projection, candidate and ordered `(port, hole, residual)` bindings.

The canonical and fresh-source instances both receive. Fresh whole,
occurrence and residual identities differ. Both calls to the existing closed
LineView refuse with `a closed line view needs a perfect through matching`.
Seven controls refuse: foreign whole, reversed ports, omitted channel,
reversed open ports, omitted residual, consistently renamed residuals from
another valid source, and a rebound hole declaration. Exact inputs, outputs
and refusal strings are in [cases.json](../../experiments/open_line_residual/evidence/attempt-1/cases.json).

## Counterexample and its precise implication

Let E forget open-port/hole/residual bindings and retain only `(name, ports,
channels)`. The canonical source W and a source W' obtained by consistently
renaming both residual entries pass the same WholeCut6 validator. Yet
`W != W'` and `E(W) == E(W')`. Their OpenLineProposal records differ, and the
receiver refuses W' as a candidate when W is independently expected.

Thus E is not injective even on this two-element family: a reconstruction
function on E alone cannot recover both exact residual ledgers. This follows
directly from the exhibited equality and inequality; no general classification
of all views is claimed. E is a deliberately lossy research projection, not
the existing closed LineView applied outside its admitted domain. A complete
source-bound pairing retains information that E forgets. It does not prove
that OpenLineProposal by itself reconstructs every field of WholeCut6.

## Executed cost and scope

The one supervised process passed 24 assertions: two positive cases, seven
candidate refusals, two old-view refusals and one collision pair. Total wall
time including import and launch was 0.404583 s; measured child peak RSS was
28,248 KiB on Linux. In-process construction took 0.000574 s; first receiving
0.000196 s; new-instance receiving 0.000137 s; seven negative receives
0.000454 s; serialization plus decoding 0.001711 s. These single observations
are not a speed comparison. Formation/authoring cost and primitive checker
work units were not measured. Temporary pytest setup resolved dependencies in
14.07 s, downloaded/prepared them in 2.39 s and installed in 8 ms; complete
setup wall time was not separately measured. No implementation correction or
search replay occurred. Peak RSS is process memory, not artifact size or a
concurrent-machine total. Memory has no enforced hard cap in this trial.

The supervisor enforced 30 s. The 1 MiB evidence and zero-search bounds were
checked. Sources are trusted finite dataclasses, not adversarial objects or
arbitrary JSON. The JSON evidence is a transport record, not a new receiver.
The previous implementation modules are imported unchanged; there is no new
Rust certificate, independently implemented validator or human review.

## Exact reproduction

The contract pins the pre-run claims registry as context. This branch appends
a scoped claim after execution, so replay must use the pinned baseline plus
the unchanged experiment files, not silently replace the registry digest:

```sh
# From a checkout containing this report/PR commit; use fresh paths.
git worktree add --detach /tmp/adva-open-line-replay 5f427e8a2bd637ec5aa418a46ed614a677cc66ff
mkdir -p /tmp/adva-open-line-replay/experiments/open_line_residual
git show HEAD:experiments/open_line_residual/run.py > /tmp/adva-open-line-replay/experiments/open_line_residual/run.py
git show HEAD:experiments/open_line_residual/contract.json > /tmp/adva-open-line-replay/experiments/open_line_residual/contract.json
python3 -m venv /tmp/adva-open-line-env
/tmp/adva-open-line-env/bin/python -m pip install pytest==9.1.1
timeout 30s /tmp/adva-open-line-env/bin/python /tmp/adva-open-line-replay/experiments/open_line_residual/run.py /tmp/adva-open-line-result
```

Replay costs vary. Immutable inputs, outcomes and bindings should match;
wall-time/RSS fields are observations, not frozen equality requirements.
The retained [supervision](../../experiments/open_line_residual/supervision.json)
and [execution](../../experiments/open_line_residual/evidence/attempt-1/execution.json)
record the original run. The manifest checks artifacts without re-running it.

## Continuation value and residual

New words: zero. The proposal is merely a scoped local record. It helps Mingli
and subsequent agents ask which open obligations a view retains, and prevents
empty-residual success from standing in for nonempty-residual transport.
Jiamin's real-task benefit remains unmeasured. No expressive-power or
acceleration claim is made; a same-resource ablation is therefore not asserted.

This is source-bound pairing, not a source-changing transport. Neither
nonempty thread history, source transformations, three-interface geometry,
observer invariance, coverage, learning, native free nor universality has been
established. The next minimal step is one fixed nonempty thread word in the
same open profile, with a reversed-word refusal; freeze its budget separately
and preserve all present source, hole and residual bindings.
