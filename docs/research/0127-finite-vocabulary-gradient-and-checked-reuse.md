# Research 0127: Finite Vocabulary Gradients and Checked Reuse

Status: external finite experiment, a set-cover derivation, and retained negative
results. No new native semantic operation, physical law, or general speedup.

## Origin and exact question

On 2026-09-05, Mingli Yuan (苑明理) proposed working at a shared finite arithmetic
boundary, with the ordered growth of proofs advancing the scope of warranted
trust. He asked whether energy and gradients could give directions in knowledge
geometry, then authorized implementing and testing this research direction.

This follows his attributed [Geometry of Truth hypothesis](0125-geometry-of-truth-interface-hypothesis.md)
and the finite vocabulary interface in [PR #126](https://github.com/mountain/adva/pull/126).
The definitions, implementation and comparisons below were constructed by
ChatGPT in response. The experimental names **有限见证势能** (finite witness
potential), **关系残差势能** (relation-residual potential), and **见证覆盖**
(witnessed coverage) are documentary vocabulary, not native Adva words.

The question is deliberately narrower than the motivating philosophy:

> Given a finite ordered model, can a residual over explicit relation obligations
> guide the selection of Boolean vocabulary, and can checked intermediate
> coverage be reused at a measured cost competitive with ordinary caching?

The experiment stays external to the native agenda. It neither instantiates
SourceId/OccurrenceId nor promotes specialization, learning, eigenvalues,
feedback, physical causality, or a stable observer-transport certificate.

## From a knowledge space to a computable direction

Fix a finite poset P, a monotone coarse interface Q0, and a declared candidate
family F of monotone Boolean predicates. A word has a precise referent: one
predicate on these model states. Knowledge here concerns this relation, not
all facts about the states or a judgement of a person's trustworthiness.

For selected predicates S, the interface is (Q0, S), compared coordinatewise.
The hard requirement is to preserve all declared true comparisons. Monotone
predicates ensure this; arbitrary names or nonmonotone predicates are rejected.
The remaining task is to remove false comparisons:

\[
U=\{(x,y):x\not\preceq y,\ Q_0(x)\le Q_0(y)\},\qquad
D_f=\{(x,y)\in U:f(x)=1,\ f(y)=0\}.
\]

Define

\[
E(S)=\left|U\setminus\bigcup_{f\in S}D_f\right|,\qquad
\Delta_f(S)=E(S)-E(S\cup\{f\}).
\]

E=0 is exactly the order-embedding condition under the fixed contract. It does
not mean zero physical energy, global truth, or zero future verification cost.
Existing witnesses remain statements under their original task and versions;
changing the target relation requires fresh checking of a table.

The search graph has predicate families as vertices and admitted additions as
directed edges. The discrete difference dE on an edge is -Delta. A cost-sensitive
direction can use Delta/c for positive, declared action cost c. This needs no
smooth manifold or Euclidean distance. Calling it a continuous gradient would
require an additional geometry and metric; none is assumed here.

The executable search uses **one unit per added predicate**, not elapsed time.
All gain evaluations and table construction/checking also consume computation;
those costs are reported separately. A predicted time-normalized gradient is a
future policy, not an implemented capability or guaranteed advance estimate.

In the motivating vocabulary, the person supplies the task and acceptable
budget; scale supplies measurement units; form supplies the model and allowed
maps; language supplies referents and checkable assertions. Coherence here is
the exact agreement of declared comparisons and interface comparisons. These
are operational interpretations, not a derivation of three physical worlds or
of vocabulary as the spectrum of a dynamical operator.

## Elementary derivation and its boundary

For S contained in T and f outside T,

\[
\Delta_f(S)=|D_f\setminus\textstyle\bigcup_{g\in S}D_g|
\ge |D_f\setminus\textstyle\bigcup_{g\in T}D_g|=\Delta_f(T).
\]

Thus coverage has diminishing returns, while E is nonincreasing under admitted
additions. If the available family covers U and E is positive, some available
addition has positive gain. This follows by taking an uncovered pair and a
predicate that covers it. For the complete monotone Boolean family, the
principal upset of x separates x from each y for which x is not below y.

Consequently, this particular full-family residual does not have a positive
energy plateau that requires a zero-gain step. The coarse terminal objective
1[E>0] can be flat even when relation-residual directions exist. A plateau is
therefore partly a question of which obligations the interface exposes, rather
than evidence that an unspecified knowledge space has no direction.

The resulting vocabulary minimization is an instance of **set cover**.
Greedy marginal coverage is an established heuristic; see
[Chvatal (1979)](https://doi.org/10.1287/moor.4.3.233).
This derivation does not claim a new optimization theorem. It also does not
extend diminishing returns to arbitrary theorem search, altered weights,
nonmonotone transformations, or history-dependent runtime costs.

## Frozen search comparison

Enumerate all 3^6 antisymmetric assignments on four labelled states and retain
the 219 transitive orders. A separate test enumerates every subset of forward
edges in all 24 vertex permutations and takes transitive closures, obtaining
exactly the same set. This is the entire labelled four-state family, not a
random sample, a held-out benchmark, or a claim about larger tasks.

Q0 is empty for the comparison. Candidates are all nonconstant monotone Boolean
predicates; bit i of mask m is its value at state i. Ties use increasing mask
tuples. Each bounded policy permits at most three new words and 100 candidate
energy queries, including the initial empty family. Setup is outside this
query counter but has its own finite bound: at most 14 admitted words, checked
on 16 ordered pairs each. All energy calls charged by the search are tested
against an instrumented call counter.

| Policy | Completed tasks | Actual candidate-energy queries across 219 tasks |
| --- | ---: | ---: |
| Strict descent on terminal score 1[E>0] | 0 | 1,459 |
| Strict greedy descent on relation residual E | 120 | 3,136 |
| Relation-residual beam search, width 4 | 168 | 5,998 |
| Exact cardinality-ordered scalar oracle | 176 feasible with three words | 8,918 to establish minima for all 219 tasks |

The terminal score is a deliberate negative control, not a competitive existing
solver. Beam search spends more actual queries despite a common upper limit;
the table is not an equal-runtime speedup claim. Its eight missed feasible
cases are retained, and all interruptions/failures return Unknown. Unknown
does not assert nonexistence or supply a resumable native frontier.

Without the three-word bound, the frozen greedy policy finds an embedding in
every case, but exceeds the exact minimum in 62 cases:

| Greedy words | Exact minimum words | Tasks |
| ---: | ---: | ---: |
| 2 | 2 | 12 |
| 3 | 3 | 108 |
| 4 | 3 | 52 |
| 4 | 4 | 37 |
| 5 | 3 | 4 |
| 5 | 4 | 6 |

The exact oracle tests every shorter candidate family before its first success
using the scalar coordinate specification. This supplies scoped finite
minimality evidence, separately from any interrupted heuristic search.

## A retained direction counterexample

Use states 0,1,2,3 with only strict relations 0<1 and 0<2. State 3 is independent.
The encoded relation is 33831. The greedy path selects masks 6,8,2,4,7; its
energy falls 10,6,3,2,1,0 and it needs five words. An optimal path selects
7,10,12; its energy falls 10,7,3,0 and needs three words.

The first gain of the shorter path is **three**, while the first gain of the
greedy path is **four**. Under a three-word budget, following the largest local
gradient loses a solution. The width-four beam also misses this particular
case. Direction, path length, and available resource must be kept distinct.

This is a concrete reason to retain alternatives and investigate bounded
lookahead, without claiming that lookahead is already complete or cheaper.
It is also consistent with the older separation between search planning and
checked proof construction; see [Bundy, Proof Planning (1996)](https://cdn.aaai.org/AIPS/1996/AIPS96-033.pdf).

## Checked reuse against ordinary caching

For each task, freeze every candidate subset of at most three predicates.
Across all tasks this gives 10,246 identical queries for each implementation:

1. Scalar: reconstruct coordinate comparisons for every query.
2. Cached: precompute each predicate's exclusion mask and combine masks.
3. Checked: construct and serialize a task-bound coverage table, independently
   check every row and candidate admission, then use the same mask combination.

The checker reconstructs Boolean coordinate values and comparisons independently
of the producer's coverage function. It rejects changed task/coarse-interface
bindings, incorrect coverage, missing rows, unsupported schema and Boolean
values masquerading as integer identifiers. A digest is a reproducibility
coordinate, not authentication. This is a bounded external Python checker,
not a native Adva proof object or authority to identify program occurrences.

Five cold-table repetitions rotate implementation order. Timers include
admission, cache/table construction, checking where applicable, query execution,
reference comparison, answer serialization and hashing. Shared preparation and
independent scalar-reference generation are separately measured and then added
to each reported total. Imports, interpreter startup and final artifact file
writing are excluded, so these are in-process observations rather than complete
application latency. Memory instrumentation uses separate runs.

Observed on 2026-09-05, Python 3.12.13, Linux x86_64:

| Method | Median method time | With shared preparation/audit | Largest retained evaluator payload |
| --- | ---: | ---: | ---: |
| Full scalar recomputation | 116.951 ms | 251.151 ms | 741 bytes |
| Ordinary coverage cache | 17.082 ms | 151.282 ms | 2,093 bytes |
| Independently checked coverage cache | 32.224 ms | 166.423 ms | 2,320 bytes |

Shared preparation/reference cost was 134.200 ms. Peak traced allocations during
separate method runs were 28,176 / 27,344 / 45,934 bytes respectively; the shared
workload, interpreter and untracked native memory are outside those allocation
figures. One task table is retained at a time. The 65,536-byte enforced cap is
on recursively measured evaluator payload, not a process-memory guarantee.
The frozen finite bounds also limit the query family to 470 subsets per task.

Every implementation produced answer digest
`c247784b4d4fb655c53a0d5ccdcf354fa60578ba4791087d86a365a9007da132`.
The checked route beats scalar recomputation in this observation, but is about
10% slower than ordinary caching when common preparation is included. Its
table-construction and query phase alone is about 1.89 times the cached phase.
No extra speed advantage over ordinary caching has been demonstrated. Native
transport, cross-task reuse, mutation maintenance, I/O amortization and practical
user benefits remain open; the current table is rebuilt for each task.

## Replay, tests, and acceptance boundary

```bash
python -m experiments.knowledge_geometry.gradient \
  --check examples/verified_witness/knowledge-gradient-four-states.json
python -m unittest discover -s tests/python -p test_knowledge_gradient.py -v
python -m experiments.knowledge_geometry.gradient \
  --benchmark /tmp/knowledge-gradient-benchmark.json
```

The deterministic artifact retains all tasks, task-bound coverage tables, exact
minima, heuristic outputs, residuals, limits and query-trace digests. CI replays
it under the existing Python matrix. Eight tests cover independent universe
enumeration, coverage versus scalar semantics on the full query family,
tampering/stale bindings, nonoptimal gradient and beam failure, terminal
plateau, exact query accounting and zero-fuel Unknown, coarse-coordinate
preservation, and complete artifact replay. Timings are observational data and
are not asserted as CI performance thresholds.

The useful advance is a precise, falsifiable connection between a vocabulary
interface and search direction, together with a negative performance result
against a real cache baseline. It does not establish a theory of general trust.
The next acceptance gate is a real task with an independently stated user need,
followed by a comparison that includes target formation, checking, reuse count,
memory and human effort. That task has not yet been specified for Jiamin.
