# Six relation-query experiments: execution arrangement

Date: 2026-09-21. Status: preparation plan; **not frozen, not implemented,
not run**. This is an arrangement of the user-supplied Chinese design summary
v0.2 dated 2026-09-20, not a replacement for its full protocol.

The referenced `six-experiments-design.md` and `suite-proposal.json` were not
found in the local workspace or the GitHub code search performed for this
preparation. Their repository, revision and exact bytes remain required inputs.
In particular, this plan does not reconstruct the missing numerical algorithms
and then attribute those choices to v0.2.

[Structured plan](plan.json) · [Chinese arrangement](ARRANGEMENT.zh-CN.md)

Research direction and the process interpretation of the two ends: Mingli
Yuan. Arrangement and self-review: Codex (OpenAI), a project-original
contribution under Unknown v0.3, through Mingli Yuan's authorized account
proxy. Account use does not imply his authorship, technical review or guarantee.
No independent reviewer has been assigned.

## Placement and scope

This directory is the proposed home for the external finite F5 experiment in
`mountain/adva`. The machine and library checkout revisions in `plan.json`
record preparation context only; they do not update executable dependency
locks or admit material into the library. No stable semantic API is changed.

For a fixed task, observer and boundary, define one checked relation R(h, f).
The two query directions must call that same relation, including its ordered
substitution map, role requirements, observations and retained history.
Expression identifiers preserve construction syntax even when values agree.
These are external fixture identifiers, not native Adva semantic identities.

The declared candidate grammar contains 108 contexts and 512 ordered fillings.
The implementation must show the context count as two binary tree shapes,
six hole permutations and nine ordered operation pairs, without quotienting
by algebraic equality. The eight filling expressions remain distinct syntax.
The five screening points must be fixed before search. Acceptance checks all
25 F5 inputs and all boundary conditions, with a separate polynomial verifier.
An oracle disagreement invalidates the affected experiment; it is not a vote
to accept the candidate. The evaluator's answer table must never be exposed
to proposers, graph builders, feature selection or learned policies.

## Work packages and release gates

Engineering effort is sequenced by these gates, not by an assumed calendar
duration. The series runtime cap does not include unlimited implementation
work: authoring and development checks are recorded separately and cannot be
reported as experimental results. All work that supplies campaign data,
including generation, learning, verification, indexing and writing evidence,
belongs to the campaign's declared accounting boundary.

| Gate | Concrete deliverables to create | Required exit condition |
| --- | --- | --- |
| G0: reconcile and freeze | Original protocol references and hashes; change/deviation ledger; run contract; feature and accounting specification | Resolve every run-critical omission below; publish exact input and implementation hashes before observing benchmark outcomes |
| G1: relation and supervisor | Context/filling enumerators; direct checker; independent polynomial checker; ordered substitution/history receipts; resource supervisor; adversarial fixtures | Enumerators retain 108/512 syntax entries; both checkers agree; controls detect violations; forced exits retain valid partial records within all caps |
| G2: E3/E4 | 16 frozen queries each, L/D/S/C and on-demand compatibility-index runs, separate calibration records | Same mediator checked on both sides; unchanged target and roles; all run outcomes and costs retained; no checker, leakage or accounting failure |
| G3: E5/E6 | 16 frozen queries each with the same strategy comparison | Three connection witnesses and interface compatibility; restricted pairwise-positive/triple-negative fixtures and their transpose checked |
| G4: E1/E2 | 16 training and 16 held-out tasks each; frozen policies; no-reuse and shuffled-label controls; reuse accounting | Family-disjoint split; no test-label feedback; fixed positive/negative requirements; training and construction fully charged |
| G5: report | Per-query receipts, paired comparisons, cost and censoring tables, omissions and open obligations | Claims match the declared finite scope; failed, slower, Unknown and NotRun outcomes remain visible |

G2/G3 do not require a speed improvement to unlock the next correctness gate.
A negative heuristic result is admissible evidence. A broken checker, leaked
answer, lost history or unenforced budget blocks dependent experiments. A
failed implementation check is retained with a correction record; campaign
attempts do not automatically restart after a fix.

## Six experiments and acceptance

| Experiment | Fixed input and search direction | Acceptance and principal failure control |
| --- | --- | --- |
| E3 | Two contexts; find one filling | The identical ordered filling satisfies both original tasks. Check empty and multiple solution families. |
| E4 | Two fillings; find one context | One context in the published grammar satisfies both fixed targets and role conditions. Reject weakened goals and unrestricted catch-all holes. |
| E5 | Three contexts; find one filling | All three checks and their joint interface compatibility pass. Pairwise success alone cannot be accepted. |
| E6 | Three fillings; find one context | The same context passes all three checks, retaining three distinct connections and their provenance. |
| E1 | Checked training traces and a new context task; learn filling proposal order | Held-out improvement survives total training/build cost and fixed-budget success accounting. |
| E2 | Checked training traces and a new filling; learn context proposal order | Generalizes across the frozen split while retaining positive and negative constraints and the original grammar. |

The provided `(x,y,1)` common filling for hA/hB/hC, and the sum context for
`(x,y,0)`, `(x,0,y)`, `(0,x,y)`, are public calibration witnesses. Record
algebraic calibration separately from navigation; do not count memorizing
these fixtures as held-out success.

For the restricted negative fixture, use only `(1,0,0)`, `(0,1,0)`, `(0,0,1)`.
All tasks require sum one; task i additionally requires component i to be
zero. The transpose must carry these role predicates as part of the same
relation. Do not recreate it by silently changing the task target or claiming
the full 512-element pool is empty.

Additional required controls: hole-order mutation, changed roles, prohibited
zero shortcut, overly broad context, agreement at the five screening points
but disagreement at an unscreened point, and history preservation after a
failed proposal and fallback. Every control needs an exact fixture and expected
outcome before the manifest is frozen.

## Strategy comparison and information boundary

All arms use the same candidate pool, task, observer and exact checker.

| Arm | Permitted additional mechanism | Incremental comparison |
| --- | --- | --- |
| L | Local rejection and fixed enumeration | Reference |
| D | Two ends and harmonic potential on the observed relation graph | D/L: global structure |
| S | The same graph rules and ends; 25 regularized matrix responses | S/D: spectral response |
| C | The same responses; only inside/outside unit-disk weighting changes | C/S: disk prior |
| I | Ordinary compatibility sets constructed on demand | Index construction and lookup both charged |

Each fourth proposal uses the next eligible fixed-order candidate. Freeze
tie breaking, duplicate handling and graph refresh timing. Graphs can differ
between runs as a consequence of their checked histories, but the construction
rules and allowed initial information cannot differ between D/S/C.

The second end must be computable from the initial unfilled-hole relations.
Edges asserted to express compatibility require a checked receipt. Structural
process edges must be separately typed and cannot impersonate a successful
answer. No complete compatibility table or independent random matrix may
replace the declared observed process graph. Record all vertices/edges omitted
by the 64-vertex truncation rule. Numerical scores rank proposals only.

Schedule query blocks within E3/E4, then E5/E6, then E1/E2. Freeze a balanced
arm order and seeds before the campaign to reduce order effects. Do not share
runtime caches or checked answers between arms unless an explicitly charged,
identical input is declared for each. E1/E2's exact control-arm matrix and
whether learned priors affect each of L/D/S/C/I await the full protocol.

## Resource arrangement

Per-round hard caps: 2,000 proposals, 2,000,000 symbolic units, 10 s wall,
8 s CPU, and 500,000,000 estimated real operations. Entire series hard caps:
1,800 s wall, 1,200 s CPU, 1,000,000,000 symbolic units, 50,000,000,000 estimated
real operations, 768 MiB worker memory and 128 MiB total evidence.

Reserve at least 10% for controlled exit. Proposed work cutoffs are 90% of
each consumable limit; per-round cutoffs are consequently 1,800 proposals,
1,800,000 symbolic units, 9 s wall, 7.2 s CPU and 450,000,000 real operations.
Do not consume the exit reserve to propose one more candidate. Memory remains
a hard process limit. Aggregate evidence includes temporary/partial output,
and a supervisor must enforce the aggregate limit, not just a per-file cap.
The full protocol must settle the reservation and accounting details before
these proposed cutoffs become a frozen run contract.

At n=64, one complete matrix response costs `32*n^3 + 64*n^2 = 8,650,752`
estimated real operations; a 25-response refresh costs 216,268,800. Two such
refreshes cost 432,537,600 before other numerical work. Pre-debit the full
response cost even if the call fails; include numerical CPU and failure
handling. A needed refresh that cannot be afforded produces the protocol's
declared fallback or Unknown, never an unrecorded change to the algorithm.

Even before learning controls, five arms imply 320 nonlearning rounds
(`4*16*5`). If each arm receives a complete training/test pass, learning adds
320 (`2*32*5`). Thus a 640-round illustrative schedule could reach 5,120 s
round CPU and 6,400 s round wall before shared overhead, above the series caps.
This is a worst-case arithmetic check, not a runtime prediction or the final
round count. All 16 queries remain in the frozen roster. The global cap takes
precedence: active unresolved rounds become Unknown; unstarted entries become
NotRun with a global-stop reason. Do not renew the suite budget between stages
or shrink the roster after seeing results. Report incomplete comparison blocks
and do not claim the 16-case signal for an incomplete block.

The supervisor must measure workers, numerical libraries and child processes;
one process's CPU timer alone is insufficient. Freeze thread counts and the
host/version manifest. Precharge symbolic scalar operations, comparisons,
candidate/edge visits, lookups, record events and 64-byte serialization/hash
blocks. Checker, index, learning, graph, scheduler, evaluator and output costs
must be assigned once, with shared costs separately itemized and fully charged.
Validate deadline, CPU, memory, evidence, symbolic and numerical exits before
the campaign. This document is not an implemented supervisor.

## Evidence and reporting contract to implement

Each round record must bind experiment/task/arm IDs, source and freeze hashes,
candidate order, visible graph versions, checked edges, substitutions, role
checks, raw checker outcomes, first accepted witness cost, residual candidates,
failed detours, actual wall/CPU, itemized costs, stop reason and censoring.
Retain append-only failure history and the continuation cursor; no automatic
retry is scheduled. A completed exhaustive finite negative result requires
checker coverage evidence for the entire declared candidate pool. Budget
exhaustion is Unknown and cannot establish an empty solution set.

Keep actual CPU and capped statistical cost in separate fields. An unresolved
started round receives 8 s in capped CPU statistics; this is not a measured
solve time. Unstarted entries remain separately missing/NotRun, rather than
fabricated measurements. Define their reporting denominator before launch.
Fully include training, graph/index construction, checking and output in total
cost. For reuse N=1,4,16, report build/training plus the actual declared N-use
workload and amortization; do not assume N identical runtimes without labelling
that as a projection. Freeze the allocation convention before testing.

The provisional performance signal requires a complete 16-query paired block:
at least 12 improvements, median total CPU cost at most 80% of the comparator,
and no success-rate decrease. Preserve the original costs and all censoring.
Report D/L, S/D and C/S separately; an index advantage or C regression must
remain visible. This is a small-sample signal, not statistical significance.

## Required inputs before freezing

1. Original full protocol and structured proposal, exact source revisions and
   hashes, and a reconciliation of this arrangement with their contents.
2. All query files, E1/E2 family and boundary split, screening points, target
   and role predicates, expected adversarial-control outcomes, and provenance.
3. Feature allowlist and training update rules, negative-condition retention,
   policy freeze point, shuffled-label procedure and exact control-arm matrix.
4. Initial graph, edge types/evidence, both end readers, harmonic boundary
   conditions, disconnected-case policy, candidate scoring and tie rules.
5. Operator construction/normalization, all 25 response points and
   regularizers, S/C weights, refresh schedule and 64-vertex truncation.
6. Numerical precision, residual/conditioning thresholds, error and fallback
   policy, pinned dependencies/thread counts and operation-accounting scope.
7. Independent checker implementation and boundary checks; prevent oracle
   leakage and preserve syntax/history in all receipts.
8. Enforceable supervisor and evidence schema, forced-exit results, immutable
   schedule, shared-cost attribution, NotRun denominator and reuse protocol.

Until these inputs are resolved, all six experiments remain NotRun. No hash
field is filled with a placeholder digest and no runnable launch command is
advertised.

## Separate geometry gate

A later geometry deliverable must specify boundary pairing for the two
three-hole expressions, legal operations for the three twists, readings of
both ends, and the process-to-parameter-to-operator map. If conjugation fixes
twists, give the reachable subspace. Six ports, a 6x6 matrix, six experiments
and a six-dimensional parameter space are distinct objects. This gate remains
Open independently of finite-graph performance. No native D*, reverse history,
Teichmueller implementation, two-singularity theorem or circular-law speedup
follows from this preparation or from an eventual finite heuristic result.
