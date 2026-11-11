# Serialized leaf opaque-fixture consumer boundary

Date: 2026-10-31  
Status: predecessor **Unknown/paused** retained; 2026-11-01 path continuation is a finite success; subsequent integration evidence and merge state are recorded in [PR #230](https://github.com/mountain/adva/pull/230)
Frozen contracts: `experiments/native_input_binding_serialized_leaf_request/opaque-consumer-contract-20261031.json` and its sole-correction overlay `opaque-consumer-contract-20261031-v1.json`  
Outcome: `experiments/native_input_binding_serialized_leaf_request/opaque-consumer-outcome-20261031.json`

Later contract review: the [2026-11-11 independent adapter revision](../../experiments/native_input_binding_serialized_leaf_request/target-adapter-independent-review-20261111/README.md)
separates request-bound native endpoint location from an explicitly selected
cross-diagram predicate and a recorded receiver outcome. It retains the original
finite countermodels and a proposed JSON interface. The real target relation
remains unselected, the Rust adapter remains unimplemented, and no historical
structural or membership result is upgraded to transport or M6 evidence.

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


## 2026-11-01 absolute-path continuation

A fresh contract retained the exact 4,464-byte fixture, consumer source,
three cases, request grammar, arithmetic boundary and refusal conditions.
It permitted no producer invocation and changed only the workflow coordinate
from a repository-relative request path to an absolute
`${GITHUB_WORKSPACE}/experiments/native_input_binding_serialized_leaf_request/canonical-request-20261031.json`.
A contract-record typo omitted the comma from the inherited residual signature.
The v0 record remains visible; the sole correction overlay restores the exact
`Real -> Real, Real` type before execution. No further correction was used.

The dedicated
[path-continuation workflow](https://github.com/mountain/adva/actions/runs/41314658363)
then completed the three frozen cases exactly once:

| Case | Observed assertion |
| --- | --- |
| `matching` | `AcceptedCurrentFixture` |
| `renamed-module` | `Refused("module mismatch")` |
| `changed-profile` | `Refused("profile mismatch")` |

The consumer remained a separately compiled Rust test target. Its source SHA-256
remained `ee07ea03ba1d9f451186a5e8a5eb3356da11d20faaa09e113381f958cfd4e1d3`;
the fixture remained
`d4d619a621ac7fd2943daa9c6eb0757acc79023314ecf9ed7dcf2f9cb0c84d4d`.
The explicit check again found no producer path import, producer module import,
or call to `receive_pinned_serialized_leaf_request`.

The fixture measurement reported 21 outer JSON items, 59 source-diagram items
and 75 residual-diagram items. Read plus JSON parsing took 123,342 ns. Each
semantic case consumed the outer 21-item structural count against a 512-item
bound, so the three executions consumed 63 counted outer items in total.
No new serialization was performed; the consumer read 4,464 frozen request
bytes per case, 13,392 runtime input bytes in total.

The dedicated job used four Cargo invocations and 25.961 s wall time. Clippy
used 7.28 s and a process-tree peak RSS of 263,236 KiB. The matching test used
6.96 s and 448,920 KiB; the two cached refusal tests used 0.05 s each and
30,352 KiB and 30,364 KiB. These are `/usr/bin/time` measurements for each
Cargo process tree, not isolated receiver memory.

The finite result closes only the path-scope harness residual. It shows that
this exact minimal consumer can receive the exact current fixture and preserve
the two inherited refusals without importing the producer. It does not
reconstruct the full native certificate, authenticate the fixture, establish
arbitrary independent implementations, cover Research 0090, promote Research
0092, construct an M6 filler, prove either Research 0123 word, or demonstrate
practical value for Jiamin Zhao.

No word was formed or revised. The existing terms `current fixture`,
`AcceptedCurrentFixture`, `Refused`, `InvalidContext` and
`Unknown/NotRun` remain sufficient.

The draft PR is not integration-ready. Its earlier general bounded-acceptance
workflow still passes the old relative path and therefore fails, while the
dedicated continuation is green. The next minimum step is a new integration
contract that substitutes the now-witnessed absolute path into the existing
bounded-acceptance workflow without changing the consumer or cases. Only then
may the PR's complete checks be used to assess merge readiness.

## 2026-11-01 bounded-acceptance integration contract

The preceding integration pause is the historical state at
`f26881d2f92b6a09db39a6fd4dc30bcae1525462`, with main still at
`87a1a6933bca3fdb5c176cbf612729e278d172f7`. A new, separately finite
[`integration contract`](../../experiments/native_input_binding_serialized_leaf_request/opaque-consumer-integration-contract-20261101.json)
continues from that state. It does not reset or reinterpret either predecessor
contract or their retained failures.

The only executable change is to root the request path in
`bounded-acceptance.yml` at `${GITHUB_WORKSPACE}`. The frozen fixture, both
Rust sources, three assertions, 65,536-byte and 512-item limits, 15-minute
consumer job limits, producer-dependency ban and dependency locks are unchanged.
Both existing consumer workflows run the same three cases once on the new PR
head; these are six executions of three cases, not six distinct semantic cases.
The general workflow retains its existing native and Bootstrap regressions.

Before integration, inspect the actual logs and require all five workflow
families on the same head: bounded acceptance, dedicated path continuation,
complete CI, publication boundary and machine dependency continuity. Retain
their run/job identifiers, tested head and checkout commits, three individual
case results, measured costs and unmeasured quantities in a commit-anchored PR
review. This external result record avoids a result-only source commit
silently triggering another experiment. Merge only that checked head, then
inspect the resulting main commit and its automatically scheduled checks.
Failure or budget exhaustion stops this contract; no repair retry is allocated.

The result, if accepted, is only integration of the exact minimal consumer's
envelope and canonical snapshot checks. It is not full native certificate
verification, general malicious-input validation, Research 0090 coverage,
Research 0092 promotion, an M6 filler or a general arithmetic conclusion.
The 512-item check counts the parsed outer request; it is not a bound on all
parser work or process memory. Existing resource checks are preserved without
claiming stronger enforcement. No word is formed or revised.

Integration contract and one-line workflow repair authored by Codex (OpenAI),
submitted through Mingli Yuan's GitHub account (mountain) as an authorized
proxy. Account use is not his authorship, review, endorsement or correctness
guarantee. Original first-party contribution under Unknown v0.3; no external
text, code or data is imported.

## 2026-11-02 accepted-fixture native successor gate

Main commit `334a85f9e981d81c026841d9b6954f144ae23d79` merged PR
[#230](https://github.com/mountain/adva/pull/230), including the exact
bounded-acceptance path repair. With no open PR remaining, a fresh contract
froze one narrower question: after the exact opaque request has returned
`AcceptedCurrentFixture`, can a second Rust stage complete the existing native
diagram-import obligations without allowing either inherited refusal case to
enter that stage?

The successor does not modify the frozen fixture or consumer. It reads the
same 4,464 bytes, requires byte equality with the checked-in fixture, imports
both embedded diagrams through `adva_lisp::import_diagram_json`, requires both
returned `DiagramValidationCertificate` values to report fully certified,
rechecks their node, source-partition and history-count snapshots against the
returned diagrams, and verifies that the one declared source and target
endpoint exists exactly in the imported occurrence collections with its
context, `SourceId`, `OccurrenceId` and path. A changed-byte control is refused
before it can reuse this gate.

The first remote run
[`41462185788`](https://github.com/mountain/adva/actions/runs/41462185788)
stopped before compilation because `rustfmt --check` required one long return
line to be split. The sole implementation-correction allowance applied exactly
that mechanical layout and changed no test or expected outcome. The correction
run
[`41462412137`](https://github.com/mountain/adva/actions/runs/41462412137)
then completed:

| Consumer case | Consumer result | Native successor |
| --- | --- | --- |
| `matching` | `AcceptedCurrentFixture` | `SuccessorVerified` |
| `renamed-module` | `Refused("module mismatch")` | `NotRun` |
| `changed-profile` | `Refused("profile mismatch")` | `NotRun` |

The successor target passed both tests: the exact fixture completed the two
native imports and mapping checks, while changed bytes were refused at the
accepted-fixture boundary. The run used exactly five Cargo invocations: one
Clippy invocation, three consumer invocations and one successor invocation.
Clippy took 13.54 seconds with a 265,428 KiB process-tree peak RSS. The
successor Cargo test took 0.27 seconds with a 155,052 KiB process-tree peak RSS.
The complete three-case execution step took approximately 6.95 seconds from
its first retained case marker to its final marker; individual consumer Cargo
wall times and RSS were not measured. The four file reads consumed 17,856
fixture bytes in total. No serialization or search ran. The test harness
reported four consumer/successor test invocations containing five passing Rust
tests; internal importer instruction counts and isolated receiver memory remain
unmeasured.

This is a workflow-level permitted-continuation gate, not an in-language
composition theorem. `AcceptedCurrentFixture` still grants no effect, execution,
retry, `free`, identity transport or general acceptance authority. The
successor reuses this repository's native importer and is not an independent
`adva-machine` implementation. Byte equality supplies integrity for this one
fixture, not authentication. Local images and one exact occurrence pair do not
construct an M6 filler. Research 0090 coverage remains open; Research 0092
promotion remains blocked; `arithmetic-universality` and
`hypothesized-arithmetic-truth` remain Proposed. The literal `1/1` remains data,
not a multiplicative-unit or inverse theorem.

No word was formed or revised. Existing `receive`, `accept`, `Refused`,
`Unknown`, certificate and permitted-continuation vocabulary already separates
the stages. `SuccessorVerified` is only a local finite outcome label.

The result helps Mingli Yuan and later agents keep envelope acceptance,
semantic import and permission to continue as three separate obligations. It
does not yet demonstrate practical value for Jiamin Zhao. The next minimum
step is to move this exact post-accept obligation to the pinned
`adva-machine` receiving boundary, or retain `Unknown` if that profile does not
exist; no new request family is needed.

Contract, implementation and report authored by Codex (OpenAI), submitted
through Mingli Yuan's GitHub account as an authorized proxy. Account use is not
his authorship, review, endorsement or correctness guarantee. Original
first-party contribution under Unknown v0.3; no external content is imported.

## 2026-11-03 pinned-machine receiving-profile inventory

PR #231 remains an unmerged draft, while main remains at
`334a85f9e981d81c026841d9b6954f144ae23d79`. The fixed executable dependency is
therefore still `mountain/adva-machine` commit
`a0b710a2517f06f2fe03cc463e855548adf418ac`. A fresh contract froze one route:
enumerate that exact committed tree and determine whether its versioned command
or profile surface already declares the post-`AcceptedCurrentFixture` relation
witnessed by the PR: two native diagram admissions, the qualified endpoint-pair
check and a receiver outcome. Later machine commits, new implementation and a
general build were excluded.

The route ended `Unknown / BudgetViolation`. The frozen byte ceiling was
100,000,000 bytes. Preflight observed 23,262 tracked files and 181,982,554
tracked bytes, but the inventory script printed the over-limit value without
gating the following `git grep`. The grep completed with return code zero in
1,532,160,635 ns, within the 30-second wall limit, but after the byte contract
had already been violated by 81,982,554 bytes. No narrowed replay, correction or
semantic execution was permitted or performed.

The invalidated search reported the primitive
`adva_lisp::import_diagram_json`, `DiagramValidationCertificate`, its existing
tests and documentary occurrence-mapping language. It reported no exact
`AcceptedCurrentFixture`, opaque-successor or native-input-binding profile
identifier. These observations are retained only as partial matches: they do
not certify absence of a suitable profile in the pinned machine, because the
declared complete-tree input bound was exceeded.

Python `resource.getrusage(RUSAGE_CHILDREN)` reported 117,192 KiB after the one
inventory subprocess. This is not isolated receiver memory or a complete
process-tree peak; `/usr/bin/time` was unavailable. There were zero fixture
reads, zero request bytes consumed, zero serialization bytes, zero semantic
cases, zero candidate generation, zero implementation changes and zero replay.

No word was formed or revised. Existing `BudgetViolation`, `Unknown`, partial
match, `receive` and `Refused` vocabulary states the outcome. In particular,
this failed inventory supplies no Research 0090 coverage, Research 0092
promotion, M6 filler, native `free` or `Close`, hypothesized arithmetic truth,
arithmetic universality, authentication, effect authority or practical value
for Jiamin Zhao.

The retained failure helps Mingli Yuan and later agents by exposing a missing
preflight rule: a resource declaration is ineffective if the checker measures
the input but does not stop before consuming it. The next minimum continuation
is not another grep. Freeze a smaller admitted subtree from committed command,
profile, schema and specification registries (with exact file and byte pins),
and require the inventory driver to refuse before search when either count
exceeds its cap. Only that fresh bounded route may answer whether an exact
pinned receiving profile exists.

Contract, outcome and report continuation authored by Codex (OpenAI), submitted
through Mingli Yuan's GitHub account as an authorized proxy. Account use is not
his authorship, review, endorsement or correctness guarantee. Original
first-party contribution under Unknown v0.3; no external content is imported.

## 2026-11-04 fail-closed declaration-surface continuation

Main remains at `334a85f9e981d81c026841d9b6954f144ae23d79`; PR #231
remains the sole open pull request and is an unmerged draft at
`6471626f0c99653f2f19d4fb1b153a1d0bb132e3`. The fixed executable dependency
therefore remains `mountain/adva-machine` commit
`a0b710a2517f06f2fe03cc463e855548adf418ac`.

Following the previous whole-tree byte violation, a fresh contract selected a
much smaller declaration surface: fixed root manifests and entry points,
top-level toolchain/exchange files, framework specifications and schemas,
workspace/experiment binary entry points, and every file explicitly named by
`spec/catalog.json`. The driver had to verify the exact revision, clean tree,
regular tracked files, at most 1,000 files, at most 5,000,000 total bytes, at
most 1,000,000 bytes per file and all SHA-256 values before content search. The
search itself was limited to 30 seconds and 100,000 candidate lines. No
semantic execution was allowed.

The result is `Unknown / CorrectionBudgetExhausted`, with both failures retained.
On attempt one, Python `fnmatch` allowed `toolchain/*` to cross slash boundaries,
selected `toolchain/evidence/local-01/complete.tar.gz`, and reached a UTF-8 decode
refusal after an unreported preflight and partial content reads. The driver
incorrectly labelled this during-search failure `RefusedBeforeSearch`. It used
467,585,526 ns internally and 535,322,018 ns supervisor wall time; child
`ru_maxrss` was 21,544 KiB.

The sole correction replaced `fnmatch` with `PurePosixPath.match` and added an
explicit evidence-path refusal. The correction replay refused during selection
preflight, before content search, because suffix matching still admitted six
archived source paths:

- `experiments/bounded_native_interpreter/evidence/attempt-1/sources/crates/adva-witness/Cargo.toml`
- `experiments/bounded_native_interpreter/evidence/attempt-1/sources/crates/adva-witness/src/bin/adva.rs`
- the same two paths under `bounded_self_compiler/evidence/attempt-1/sources/`
- the same two paths under `bounded_self_compiler/evidence/attempt-2/sources/`

That replay used 4,231,597,903 ns internally and 4,339,744,616 ns supervisor
wall time; child `ru_maxrss` was 21,556 KiB. The correction allowance was then
exhausted, so no root-anchored matcher was implemented and no third execution
was made. Selected file/byte counts, a complete manifest and candidate count
remain missing. There were zero semantic executions, fixture reads, consumed
request bytes and serialization bytes.

No word was formed or revised. Existing `Unknown`, `Refused`, correction budget
and partial-search vocabulary is sufficient. The failed driver does not answer
whether the pinned machine declares the required route, and it supplies no
Research 0090 coverage, Research 0092 promotion, M6 filler, native `free` or
`Close`, hypothesized arithmetic truth, arithmetic universality, authentication,
effect authority or practical value for Jiamin Zhao.

The useful result is a narrower tool obligation: path selection must be anchored
at the repository root, and the outcome grammar must distinguish a preflight
refusal from a decode failure after partial search. The next minimum continuation
is one fresh contract that changes only those two mechanics, retains both failed
attempts, and runs the same declaration-surface inventory once. It must not add
files, widen budgets or execute the request.

Contract, failed driver, outcome and report continuation authored by Codex
(OpenAI), submitted through Mingli Yuan's GitHub account as an authorized proxy.
Account use is not his authorship, review, endorsement or correctness guarantee.
Original first-party contribution under Unknown v0.3; no external content is
imported.
