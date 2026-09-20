# Six experiments for navigation through holes and fillings

Status: **design only; no implementation, experiment, or performance result**.
Version: 0.2, 2026-09-20. This continues the paused navigation discussion after
Mingli requested a design covering three uses and their possible duals.
The earlier v0 and v1 contracts remain historical, unexecuted proposals.
This document does not activate them or request a native API change.

Direction and the two-endpoint interpretation: Mingli Yuan. Experimental
formalization, writing, and self-review: Codex (OpenAI), contributed under
Unknown v0.3 through Mingli Yuan's authorized account proxy. Account use is
not Mingli's authorship, technical review, endorsement, or correctness guarantee.
No independent reviewer or executed navigation trial is claimed. The separate
design-validation record distinguishes fixture checks from an experiment.

## 1. Question and three distinct hypotheses

Can information shared across construction histories and open boundary
relations improve (a) learning direction, (b) discovery of a relation between
two objects, and (c) construction of a joint witness for three objects?

Mingli locates one endpoint at the common origin of expression chains and the
other at the relation intersection of the original unfilled holes. Both are
part of the problem description. The second endpoint must be observable before
the answer is known. In this design they are process observations; calling them
analytic singularities needs a separate representation argument.

Keep three hypotheses separate:

1. A shared network and both endpoint observations improve decisions beyond
   local narrowing.
2. A spectral reading adds useful information beyond a nonspectral global
   method; a circular-law-informed prior adds information beyond that reading.
3. Exchanging which side of a hole/filling relation is unknown gives useful
   counterpart queries. It need not give equal cost or invertible histories.

A positive result for hypothesis 1 does not establish hypotheses 2 or 3.

## 2. One relation, six queries

For a fixed task contract Gamma and observer Q, define Fit(h, f; Gamma, Q):
f can be grafted into the ordered three-hole context h, all declared observations
hold, and the required role, occurrence, and history conditions survive.
The witness contains the substitution and its retained residual, not a Boolean
alone. Gamma and Q cannot be relaxed while seeking a witness.

The finite Boolean incidence matrix I[h,f] is a reference representation of
this relation. Fixing h queries a row; fixing f queries a column. The complete
matrix is reserved for the isolated evaluation oracle, not supplied to search.
Unknown entries in the online network remain unknown, never false.

This is relation converse at the query level. It does not implement native D*,
inverse evaluation, geometric conjugation, or a one-to-one correspondence.
Empty and multivalued fibres are expected outcomes. Six protocol cells do not
by themselves establish six independent mathematical effects.

| ID | Use | Given | Seek | Required witness |
| --- | --- | --- | --- | --- |
| E1 | Learning a filling direction | Training hole tasks and checked trails; a new hole task | A learned ordering of filling edits | Correct fillings on held-out tasks plus measured transfer beyond no-reuse |
| E2 | Learning a hole direction | Training filling examples and checked trails; new examples | A learned ordering of context/abstraction edits | One context satisfying fixed positive and negative obligations on held-out tasks |
| E3 | Relating two holes | h1, h2 | A common filling f | Fit(h1,f) and Fit(h2,f), in the same declared environment |
| E4 | Relating two fillings | f1, f2 | A common context h | Fit(h,f1) and Fit(h,f2), under the unchanged task specification |
| E5 | Joining three holes | h1, h2, h3 | One simultaneously valid filling f | All three incidences plus joint interface compatibility |
| E6 | Joining three fillings | f1, f2, f3 | One simultaneously valid context h | All three incidences plus joint interface compatibility |

E3/E4 initially test a relation witnessed by one common mediator. They do not
exhaust every possible multistep relation between arbitrary programs. E5/E6
must use one shared mediator; three different pairwise mediators do not pass.
Context inference in E2/E4/E6 is confined to a declared grammar. It does not
claim invention of an unrestricted language or recovery of a unique origin.

## 3. Small, exact arithmetic carrier

The first candidate carrier is external arithmetic over F5 with input variables
x,y. This is an explicit synthetic interpretation, not Rust-owned Adva IR.

- A context is a binary expression with exactly two operations from +, -, *;
  each of the three labeled holes occurs exactly once. Two tree shapes, six
  leaf permutations and nine operation pairs give 108 syntactic contexts.
- An atomic filling is one of x, y, 0, 1, 2, x+y, x-y, x*y, in that order.
  A filling is an ordered triple of these atoms: 512 syntactic candidates.
- Contexts with equal values remain distinct syntactic histories. Every slot,
  atom occurrence, substitution, attempt, rejection, rollback and reopen is
  logged. Synthetic identifiers are not native SourceId or OccurrenceId.
- The task fixes a target function and optional role/history obligations.
  Exact acceptance checks all 25 points of F5 squared. Context inference must
  preserve that same target; it cannot choose an easier target after seeing f.
- Local narrowing initially uses the five input probes (0,0), (1,0), (0,1),
  (1,1), (2,1). At a partial candidate, propagate sets of possible values for
  unfinished parts. Reject only when a target value is outside the resulting
  over-approximation. A surviving prefix is not accepted as a solution.
- The online semantic checker evaluates syntax directly at all 25 inputs.
  The separate offline checker expands polynomials over F5 and reduces modulo
  x^5-x and y^5-y before comparison. Agreement covers finite functions, not
  equality of unreduced polynomials or program histories.

The complete incidence has at most 108 times 512 entries per fixed target and
boundary policy. Construct it only inside the bounded oracle process. A solver
cannot read its files, accepted-candidate list, hidden labels, or task-generation
witness. All generation and oracle costs are retained in the campaign account.

These finite arithmetic choices make the six questions testable. They do not
identify six scalar coordinates with Teichmuller coordinates or prove a circular
law for the resulting matrices. A later native binding must use the existing
Rust validation boundary and retain a certificate and residual.

## 4. Concrete fixtures and failure cases

The following algebraic witnesses specify sanity fixtures. Their elementary
identities and the finite counterexample are checked in design-validation.json;
no navigation policy has been run. Performance tasks must be separately frozen,
not selected for beating a baseline on these displayed examples.

For E3/E5 fix the target x+y and define:

    hA = (hole1 + hole2) * hole3
    hB = hole1 * hole3 + hole2
    hC = hole1 + hole2 * hole3
    f  = (x, y, 1)

E3 uses hA,hB; E5 adds hC. The same f satisfies all required equations.
For E4/E6 fix the same target, use the context (hole1+hole2)+hole3, and give
the fillings (x,y,0), (x,0,y), and (0,x,y). E4 uses two; E6 uses all three.
Multiple correct mediators remain valid and must not be collapsed by value.

For the essential pairwise-without-joint control, explicitly restrict the
filling pool to (1,0,0), (0,1,0), (0,0,1). All are constant programs. The three
hole tasks use the sum context and target 1, with additional respective slot
conditions f1=0, f2=0, f3=0. Every pair admits a filling, but no member of this
frozen pool fills all three. Transposing this same finite incidence supplies
the E6 counterpart: every pair of fillings has an accepting context, but all
three have none. The restriction to this three-element pool is explicit; no
claim is made about every expression in the main grammar.

Other controls required in every relevant orientation:

1. Wrong slot order or changed role policy: refuse the stored witness even
   where scalar outputs happen to agree.
2. Empty and multivalued fibres: preserve each outcome without inventing a
   unique context or filling.
3. A proposed universal context and a zero-filling shortcut: fixed negative
   examples or nonconstant targets must defeat vacuous acceptance.
4. Five-probe collision: two candidates agree on visible probes but differ
   on an unobserved input. If none exists in a frozen cohort, report that fact;
   do not fabricate a collision or widen the grammar after looking at results.
5. Rollback: the active search can return to its root; learned records, cost,
   failed assumptions and unknown frontiers survive. History never resets.
6. A revised target, domain or boundary condition invalidates inapplicable
   reuse. Budget exhaustion never creates a negative incidence.
7. A real chart change transports metric, observer and endpoint bindings;
   changing coordinates while leaving the observer behind is refused.

## 5. Learning requires transfer

E1 learns which filling edit to try; E2 learns which context edit to try.
The initial edit catalog is fixed by the candidate grammar. Context edits
change one operation, tree shape or slot permutation. Filling edits change
one atomic slot. Do not infer equal programs from an edit's output values.

Both experiments propose 16 development tasks followed by 16 held-out tasks.
Freeze the task files, generator, exact train/test partition and hashes before
the first policy comparison. Split by declared syntax family and boundary
policy, not by random copies of the same expression. Report whether transfer
is within a family or across held-out families.

A deliberately small learner records attempts, independently verified successes
and charged cost by (edited slot, operation/atom class, endpoint-feature bin).
Rank by (successes+1)/(attempts+2), divided by mean charged cost, with denominator
at least one. Freeze the feature bins before development. Counts update during
development and are fixed for held-out episodes. IDs, hashes and hidden oracle
classes cannot be features. This learns a reusable priority rule, not new
grammar. Any stronger characteristic or macro learner needs a new contract.

Every navigation arm uses the same learner and budgets; only the available
direction features differ. Also run no-reuse and shuffled-training-outcome
controls. Charge development and storage in full, and report costs after 1, 4
and 16 held-out tasks. A gain on a repeated training task is not transfer.
E3-E6 each propose 16 frozen queries and no parameter training on those queries.

## 6. Shared navigation comparisons

All arms have the same candidate grammar, exact checker, initial public
information and local narrowing. None may prune solely from a heuristic score.
Every fourth proposal follows the original canonical order, to expose rather
than conceal starvation. Ties use that same order. All candidate attempts count.

| Arm | Added information | What a benefit would establish |
| --- | --- | --- |
| L | Local narrowing and canonical enumeration | Baseline |
| D | Both process endpoints and the retained relation graph | Benefit of nonlocal, nonspectral guidance |
| S | The same graph and endpoints, with a finite spectral response | Incremental benefit of this spectral reading |
| C | The same spectral response, reweighted by a unit-disk prior | Incremental benefit of this particular circular-law-informed prior |

Include a conventional exact baseline: indexed intersections of compatibility
sets assembled by on-demand checking. Its index construction and reuse are
charged; it does not receive the complete offline incidence for free.

Online graph vertices represent candidate prefixes, retained checked relations
and public task constraints. Edges require an explicit generation step or
already observed relation. Endpoint bindings point to the construction origin
and the original hole-relation observations. Edges to an answer cannot be
inserted using oracle knowledge. Preserve failures separately from positive
edges. Each query starts from the same development snapshot; discoveries in one
test query or arm are not silently supplied to another.

For D, a proposed finite realization is a Dirichlet potential on the undirected
shadow of the observed graph, with the generation origin at 0 and the relevant
constraint observation at 1. This uses only known graph structure. Disconnected
or contradictory endpoint bindings yield no direction and canonical fallback.
For multiple required relations compute separate components and use their
minimum when ranking a common mediator; final acceptance still checks all of
them jointly. The exact edge weights and prefix-to-observation mapping must be
frozen and checked before any comparison. It is a harmonic guidance baseline,
not a claim that every process graph already has a unique geometric potential.

One concrete proposed S/C calibration is as follows. For a frozen directed
observation matrix A, use M=(A-mean(A))/s with
s=FrobeniusNorm(A-mean(A))/sqrt(n). Store the convention A[v,u] for u-to-v edges.
If s=0, return no spectral direction. Set eta=1/4 and, for each z on the 25-point
grid with real and imaginary coordinates {-1,-1/2,0,1/2,1}, form

    B_z = z I - M
    R_z = (B_z* B_z + eta^2 I)^(-1) B_z*
    u_z = R_z e_origin
    v_z,j = R_z* e_constraint,j
    score_j(v) = sum_z w_z |u_z(v)|^2 |v_z,j(v)|^2

Here * is the ordinary complex adjoint in this external numerical model, not
Adva D*. S uses equal weights on all 25 grid points. C assigns equal weights
to the 13 points inside or on the unit disk, zero to the others. Both pay for
all 25 responses, so their comparison changes only the prior. This is a coarse
finite disk-weighting heuristic, not an exact integral or a consequence of the
circular-law theorem. Take the minimum across required j and divide by the
estimated next-check cost; use no hidden compatibility label in that estimate.
Freeze the numerical backend, tolerance, graph refresh rule and fallback in an
implementation contract. Numerical failure returns no direction, not acceptance.

The observation graph may be dependent, sparse, symmetric, acyclic or otherwise
outside circular-law assumptions. Retain such failures of the prior. A visually
round eigenvalue plot is not a theorem, a global gradient or a speedup result.
The existing frame H, -JH and exp(-tJH) are structural controls; their known
spectral supports must not be relabeled as a uniform disk.

## 7. Geometry gate and honest claim levels

Two three-boundary surfaces glued along all three pairs give a genus-two closed
surface with three length and three twist parameters. To apply that model here,
record the actual expression-to-boundary map, orientations and allowed twists.
If conjugacy fixes twists, report the resulting subspace. Matrix size six, six
ports and real dimension six are different quantities.

Before claiming a Teichmuller or circular-law-guided Adva result, bind:

1. both three-hole expressions and their typed input/output correspondence;
2. the two endpoint observations, computable before finding a solution;
3. the retained source/history-to-geometric-parameter map and its residual;
4. the induced operator family, normalization, parameter/size distinction,
   observation error and conditions under which a disk prior is defensible;
5. the inverse query's domain and metric/observer transport.

These bridges are OPEN. The proposed finite graph S/C calibration can test an
explicit heuristic without them, but must then be reported only at that level.
It cannot discharge the central geometric hypothesis by running an unrelated
random matrix or solving a supplied incidence table.

## 8. Budgets, records and decision rules

Proposed limits, to be enforced by a bounded worker and outer supervisor before
execution: 2,000 proposals and 2,000,000 symbolic work units per episode; 10 wall
seconds and 8 CPU seconds per episode; 768 MiB peak worker memory; 1 MiB evidence
per episode; 128 MiB per campaign; 1,800 wall seconds and 1,200 CPU seconds for
the whole campaign, including fixture generation, oracle, learning, spectral
construction, indexing, verification and checkpointing. Maximum campaign symbolic
work is 1,000,000,000 units. A symbolic unit is one scalar field operation,
comparison, candidate/edge visit, table lookup, retained event, or 64-byte
serialization/hash block. Keep these categories separately.

Numerical work has its own cap: 500,000,000 estimated real arithmetic operations
per episode and 50,000,000,000 per campaign. Precharge each complete dense n-by-n
response by the declared conservative model 32*n^3+64*n^2; charge vector work,
matrix construction and additional factorizations separately. This is a cost
model rather than a claim about a BLAS backend's actual instruction count.
All actual CPU and wall time are measured, including opaque library calls.
No automatic retry, pool enlargement or continuation.
The campaign cap may stop the suite before all episodes finish: retain missing
cells as Unknown, never drop them from the success-rate denominator.

Limit an observed graph to 64 vertices per numerical response. Any truncation
uses a predeclared query-local selection and an explicit omitted-region residual;
do not call that observation the complete global graph. Reserve 10 percent of
each work/evidence allowance for recording and graceful exit. A native library
call that cannot be interrupted cooperatively runs in the supervised worker.

Retain candidate order, witnesses, full assumption changes, rejected and unknown
incidences, learner state, endpoint bindings, matrix construction, numerical
residual, fairness fallbacks and every cost category. Compare first-valid-witness
cost, solved fraction under equal budgets, unresolved alternatives, wrong-guide
detours, and cold versus amortized cost. Report all wins, ties and losses.

Semantic correctness must pass every control. Any invalid accepted witness
invalidates that arm's result. Search exhaustion gives Unknown unless the
separate checker supplies a complete finite nonexistence certificate for the
declared pool. A numerical or engineering checker failure is Failed.

For a descriptive performance signal, require at least 12 of 16 held-out cases
to improve, median total CPU cost at most 0.8 times the comparator, and no
drop in solved fraction. For a fixed-budget comparison, an unsolved episode
receives the full eight-second CPU allowance in the capped cost statistic;
retain its actual CPU time and censoring flag as well. This statistic is not
the unobserved completion time. Add development/setup amortization explicitly.
Report this as a small-sample design threshold, not a
statistical significance test. Use D/L, S/D and C/S separately. Learning also
has to beat no-reuse after charging training. Failure to meet a threshold is a
retained negative or inconclusive result; do not retune on the test set.

Freeze an implementation manifest before execution: task bytes and split,
generator/checker hashes, exact feature bins and graph construction, numerical
backend/error policy, proposal ordering, counters, supervisor and output paths.
These implementation items are not yet supplied by this design document.

## 9. Order and deliverables

First implement E3/E4 to test the common incidence and converse query. Next use
E5/E6 to test simultaneous gluing and the pairwise-only counterexample. Finally
use E1/E2 to test retained knowledge and held-out transfer. This is an execution
order, not an automatic scheduled run. Execution and result integration remain
unperformed in this design checkpoint.

Each experiment will emit a contract, source-bound event ledger, candidate and
checker result, cost report and residual. Keep the initial geometry-gate report
separate from the six performance reports. The earlier request to submit and
merge experimental results is not fulfilled by saving this design.

## 10. Sources and publication review

Repository premises: Research 0079 (typed apertures), 0106 (three-hole projective
bridge), 0129 (bounded trials), the received iota frame, and the research agenda.
External bibliographic references, with no copied text, data, code or figures:

- Bai, Z. D. (1997), Circular law, DOI 10.1214/aop/1024404298.
- Tao and Vu, with Krishnapur appendix, arXiv:0807.4898.
- Hyperbolic Geometry Notes #4, Fenchel-Nielsen Coordinates:
  https://lamington.wordpress.com/2010/04/18/hyperbolic-geometry-notes-4-fenchel-nielsen-coordinates/

This proposal and its synthetic fixtures are original project contributions.
The formulas are explicit proposed methods or standard mathematical facts,
not transcriptions of a source implementation. The reviewer is Codex itself;
no human or independent validation is represented. Design-file validation checks
syntax, consistency and the displayed arithmetic fixtures only; it is not an
executed navigation experiment.
