# Integration review and caller-owned input snapshots

Date: 2026-09-14. Authored by **ChatGPT (OpenAI)**, submitted through
Mingli Yuan's GitHub account as an authorized proxy. Account use does not
imply personal authorship, review, endorsement or a correctness guarantee.

## Scope and integration state

The inspected main was `2dd67b80c028ad77d77a88c8189e82246b59caa9`.
The remote had already merged the two Möbius receipt commits, and GitHub
returned no open PR. This is therefore an audit and corrective main commit,
not a second merge of that branch. Later-main work is preserved.

The review focuses on the newly merged receipt receiver and composition
boundary. Other changes since the earlier Zot commit were inventoried; their
area-method, inequality and link-calibration experiments were not rerun here.
The formal project boundaries and agenda did not change over that interval.

## Finding and correction

**The composition gate is arithmetically reproducible, but its accepted
Python result retained aliases to caller-owned input lists.**

The returned history reused the route-label list and both coordinate-change
lists; the intermediate frame reused the first receipt's ordered probes.
Changing any of these inputs after acceptance changed the accepted record
without another verification. The eight controls (four fields in F_5 and
F_7) all reproduced the defect. Complete before/after values remain in
`before/probe.stdout`; its 26696 counted work units are recorded.

The correction copies those four lists when constructing the result. It
does not change the arithmetic, matching rules, statuses, schemas, resource
limits, or parent receiver. Input and output now have independent ownership
for those fields. The returned dictionary itself remains mutable: this is
not an immutable object, authenticated history, or protection against a
caller explicitly rewriting a result. Concurrent mutation during verification
is outside this single-threaded research profile.

`tests/python/test_mobius_transport_receipt.py` adds standard-library unittest
coverage, also collectable by pytest. It checks input-to-result and
result-to-input isolation in sixteen subcases, then compares the complete
existing 24-case composition suite with retained non-timing evidence.
All three test methods passed, using 96446 of the unchanged shared 100000
work-unit allowance. No budget is reset between tests.

## Executed checks

The fixed review contract was written before execution in `contract.json`.
`run_review.py` records every invocation, exit status, source hash and
comparison. The before and after directories are separate; existing
historical evidence was not overwritten.

| Check | Observed result |
| --- | --- |
| Receiver calibration | All 34 controls and 4774 word-point checks reproduce the retained non-timing record |
| Composition before correction | Two fresh children reproduce all 24 cases and retained non-timing evidence |
| Caller-mutation probe | Eight accepted records change after caller input mutation; defect retained |
| Corrected focused regression | Three test methods pass, including sixteen ownership subcases and the complete original suite |
| Composition after correction | Two fresh children still reproduce the original non-timing record |
| Real Node Zot replay | 38 checks; all 1023 weighted row ledgers and the probability table agree with retained V8 evidence |
| Real Node Keraia-boundary replay | 146 checks; exhaustive parser counts, exact syntax tails and input controls agree |

The Node runtime was v24.19.0 and Python was 3.12.14. This closes the earlier
real-Node replay gap. QuickJS and the full repository Rust/Python suites were
not run. Pytest was absent on this host; the new tests ran directly with
stdlib unittest, not through a mocked test interface.

The before phase recorded four top-level commands in 0.722 seconds; the
composition command itself launched its two declared children. The after
phase recorded a regression command and a two-child composition command in
0.333 seconds. The unchanged Node campaigns used 665350 CEK transitions and
56317 oracle entries for Zot, and 679554 parser/counting operations for
Keraia. These are different work units and must not be summed as one cost.
Timings exclude reading, authoring, network, subsequent report preparation
and final report writes. Node's 256 MiB old-space cap is not a total RSS cap.

`before/execution.json` says Passed for the original replay comparisons;
it also explicitly records `caller_aliases_found: 8`. It must not be read as
an alias-free review verdict. The corrected validation is in `after/`.

## Consequence for the next task

The merged work supplies an explicit middle-interface check: independently
valid legs can still fail to compose when their intermediate action, scope,
ordered probes or predicate differs. The snapshot fix preserves that checked
question and route after the caller reuses its working data.

This is a useful prerequisite for later reuse, not a Keraia or Q4 speedup.
A Keraia bridge still needs actual evaluator states, input-cursor and read
effects, step-cost transport and code-weight preservation. A finite-field
Möbius frame is not already that state interface. No native identity, Q4/M6
cell, Keraia evaluator, library admission, runtime-tail certificate or Seal
is introduced; the Pascal growth obligation remains Open.
