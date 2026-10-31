# Serialized leaf opaque-fixture consumer boundary

Date: 2026-10-31  
Status: **Unknown/paused** on draft PR #230; not merged  
Frozen contracts: `experiments/native_input_binding_serialized_leaf_request/opaque-consumer-contract-20261031.json` and its sole-correction overlay `opaque-consumer-contract-20261031-v1.json`  
Outcome: `experiments/native_input_binding_serialized_leaf_request/opaque-consumer-outcome-20261031.json`

## Dependency and status reading

The run began from main commit
`87a1a6933bca3fdb5c176cbf612729e278d172f7`. PR #229's separately compiled
consumer experiment is merged; no pull request was open before this run.
`AGENTS.md`, the research engineering agenda, `docs/claims.toml`, Research
0123 and the predecessor serialized-leaf records were reread.

The status partition remains strict. Research 0123's
`arithmetic-universality` and `hypothesized-arithmetic-truth` are Proposed
words rather than proved mathematics. Research 0090 coverage is incomplete,
so Research 0092 all-fillings closure and vocabulary promotion remain blocked.
Local image equality supplies no M6 filler.

## Frozen question and route

Can a separately compiled minimal Rust consumer receive one exact canonical
request fixture without importing the producer test module, accepting the
current module and refusing a renamed expected module and changed profile?

The request pins module `native-binding-process`, body
`(frontier (use static) (use dynamic))`, rational input `1/1`, external
leaf `(s-KX-L, occ-KX-L, t-KX-L, tocc-KX-L)`, source signature
`Real, Real -> Real, Real`, and residual signature `Real -> Real, Real`.
The consumer grammar admits exactly five root keys. It checks the byte bound,
strict root shape, profile, leaf, one occurrence-map entry, exact canonical
source/residual JSON strings, their declared module, and exact request bytes.

Only one route was allowed: construct the fixture once, then compile one
producer-independent consumer and execute one positive and two refusal cases.
Search was zero; request size was bounded by 65,536 bytes; outer structural
work by 512 items; the workflow by 15 minutes; and one implementation
correction replay was reserved. The consumer deliberately does not rebuild or
certify the full native certificate, event map, ordered history or graft trace.

## Evidence

Fixture construction succeeded in
[workflow 41211976708](https://github.com/mountain/adva/actions/runs/41211976708).
The exact UTF-8 JSON fixture has 4,464 bytes and SHA-256
`d4d619a621ac7fd2943daa9c6eb0757acc79023314ecf9ed7dcf2f9cb0c84d4d`.
Recursive counting gives 21 outer JSON items; parsing the two embedded diagram
strings gives 59 source and 75 residual items. These counts describe the
fixture; they do not assert semantic certification.

The first implementation attempt,
[workflow 41212123407](https://github.com/mountain/adva/actions/runs/41212123407),
stopped at `rustfmt --check` before semantic execution. The sole permitted
correction changed only the function-signature layout and the pinned consumer
digest.

The corrected replay,
[workflow 41212182710](https://github.com/mountain/adva/actions/runs/41212182710),
passed formatting, all three SHA-256 pins, the explicit ban on producer
path-import/call patterns, Clippy, 41 selected Rust regressions, and 1,110
Bootstrap tests. It then failed on the first new case before entering
`receive`: the workflow passed a repository-relative fixture path while the
test process resolved it from `crates/adva-lisp`. The matching case is a
harness failure, and the renamed-module and changed-profile cases are NotRun.
The correction budget was exhausted, so no second repair or replay was made.

This is a reproducible negative boundary, not a consumer success. The source
compiles independently and the dependency ban holds, but the intended
input/output relation has not been observed.

## Cost and vocabulary

The construction, invalid formatting attempt and corrected native jobs used
29.883 s, 11.085 s and 20.867 s of job wall time respectively (61.835 s
summed; jobs outside this sequence may overlap). There were nine Cargo
invocations across the recorded route, one dedicated fixture construction,
zero search candidates, 4,464 retained serialization bytes and zero completed
new semantic cases. The final Bootstrap replay took 2.56 s. Peak memory was
not reported and is therefore missing.

No word was formed or revised. Existing fixture, snapshot, `InvalidContext`
and `Unknown/NotRun` language already expresses the failure. In particular,
this run supplies no evidence for arithmetic universality, hypothesized
arithmetic truth, M6 filling, social trust, or practical value for Jiamin Zhao.

## Who this helps and residual obligations

This record helps Mingli Yuan and later human or AI agents avoid two silent
conflations: a separately compiled target is not enough if it imports the
producer, and a checked-in fixture is not received merely because it exists at
a repository-relative path. It gives an exact fixture and an exact failing
boundary for continuation. It does not yet help Jiamin perform a real task.

SHA-256 integrity is not authentication. The minimal consumer is not an
independent implementation of the full native receiver. Exact peak memory,
real receiver structural consumption, malicious-input behavior, Research
0090 coverage and Research 0092 promotion all remain open.

The next minimum step, under a fresh contract, is to pass the fixture through
an absolute `GITHUB_WORKSPACE` path (or copy it beside the staged test) and
run only the unchanged matching, renamed-module and changed-profile cases
once. No broader regression replay or new vocabulary claim is needed.
