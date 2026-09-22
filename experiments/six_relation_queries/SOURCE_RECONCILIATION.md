# Original v0.2 source reconciliation

Date: 2026-09-22. Documentation only. G0 remains Open; all six experiments
remain NotRun. No implementation, navigation trial or native exchange occurred.

## Located source and provenance

Repository: `mountain/adva`. Branch: `research/trail-navigation-pilot-20260920`.
Immutable revision: `b3450c59f8e01eba46062e114ff291415aefeb77`.
Directory: `experiments/trail_navigation/`.

- [English design](https://github.com/mountain/adva/blob/b3450c59f8e01eba46062e114ff291415aefeb77/experiments/trail_navigation/six-experiments-design.md)
- [Structured proposal](https://github.com/mountain/adva/blob/b3450c59f8e01eba46062e114ff291415aefeb77/experiments/trail_navigation/suite-proposal.json)
- [Chinese design](https://github.com/mountain/adva/blob/b3450c59f8e01eba46062e114ff291415aefeb77/experiments/trail_navigation/six-experiments-design.zh.md)
- [Historical design validation](https://github.com/mountain/adva/blob/b3450c59f8e01eba46062e114ff291415aefeb77/experiments/trail_navigation/design-validation.json)

Exact sizes, SHA-256 digests and Git blob IDs are in `plan.json`. The original
UTF-8 bytes were rehashed and matched both the Git tree and historical manifest.
This establishes source identity, not algorithm correctness. The historical
150 arithmetic fixture checks are not new navigation results or rerun here.

Both work lines start at `22c500263db4a261a3a4ed20d9e0941c374475a1`:

- Design: `6ef29b48759ca66fb4c74a75071738bd755d84f2` retained the paused
  checkpoint; `b3450c59f8e01eba46062e114ff291415aefeb77` added v0.2 sources.
- Arrangement: `c09351ef76484ad2045fe76ae4eb7a219114b196` independently
  recorded the Chinese summary and missing-source fields on main.

The original commit is dated 2026-09-20 23:48:52 UTC (September 21 in Beijing).
At audit main `a9187cd8ddc3d73db0346b8b8e6be1b43788c0f9`, the design branch
was two commits ahead and seven behind. Default-branch code search found only
references. Recursive, untruncated trees of all 185 adva, six adva-library and
three adva-machine current branches located the originals on this branch.
This was a current-tree path search, not all-history blob-content exhaustion.

## Recovered design parameters

These are source-pinned proposals, not a frozen executable algorithm:

- Screening: `(0,0), (1,0), (0,1), (1,1), (2,1)`.
- Independent checker: polynomial expansion over F5 reduced modulo `x^5-x`
  and `y^5-y`, alongside direct evaluation and separate interface checks.
- Learner: count attempts, checked successes and costs by edited slot,
  operation/atom class and endpoint-feature bin. Rank by
  `(successes+1)/(attempts+2)` divided by mean charged cost, denominator at
  least one. Update during development and freeze before held-out episodes.
- D: Dirichlet potential on the observed graph's undirected shadow; origin 0,
  relevant constraint 1; minimum across required constraints. Disconnected or
  contradictory endpoint bindings give no direction and canonical fallback.
- S/C: `A[v,u]` for edge u to v; center A and divide by its centered Frobenius
  norm over sqrt(n). Zero denominator gives no direction. Use eta=1/4 and
  the 25 complex grid points with each coordinate in `{-1,-1/2,0,1/2,1}`.
  The original regularized response and score are retained in `plan.json`.
  S averages all 25 points; C averages the 13 closed-unit-disk points. Both
  pay for all 25 responses. Numerical failure never authorizes acceptance.
- Ties: canonical order. Every fourth proposal uses fixed-order exploration.
- Evidence: 1 MiB per round, 128 MiB across the campaign.

## Explicit differences and retained boundaries

1. **Statuses.** Source section 8 and JSON exit use Unknown for missing or
   truncated cells. This arrangement retains its explicit refinement:
   unstarted is NotRun with a reason; started unresolved is Unknown. Retain
   every roster entry and do not shrink the success-rate denominator because
   a round was unstarted. Exact reporting/allocation remains a freeze input;
   neither category supplies a fabricated measured solve time.
2. **Screening collisions.** Source section 4 requires a collision fixture
   only if present in the frozen cohort. Otherwise report absence; do not
   fabricate a collision or expand the grammar after observing results.
   The existing control ID denotes this conditional check.
3. **Evidence cap.** The missing per-round 1 MiB source cap is restored in
   the arrangement. No supervisor is claimed to enforce it yet.
4. **Reserve.** The source proposes 10% work/evidence reserve. The arrangement's
   90% work cutoffs remain proposed; exact timer, accounting and graceful-exit
   semantics still require an implementation contract.
5. **Learning arms.** The source specifies the same learner and budgets for
   navigation arms, differing only in direction features. The exact control
   matrix and participation of the separately named index baseline are still
   open. No extra trained index experiment is inferred.

The label `full_protocol` in the arrangement means the full English design
relative to the Chinese summary. The original explicitly leaves implementation
freeze items open. Locating that document does not close G0.

## Remaining freeze obligations

Task bytes and split; targets and role/history predicates; canonical enumeration
and duplicate handling; feature bins and control matrix; exact initial graph,
edge weights and endpoint maps; refresh schedule and 64-vertex selection with
omitted-region residual; backend, tolerances and conditioning/error checks;
checker and supervisor sources; forced-exit evidence; seeds and balanced arm
schedule; shared costs, reuse measurements and reporting denominators; environment
manifest. Their existing hash fields remain null. Geometry remains separately Open.

Only source provenance and stated design parameters are pinned. No runnable
contract, missing numerical policy, native admission or performance claim is
invented. The paused source branch and its original evidence remain unchanged.

## Review and validation scope

Original project documentation under Unknown v0.3, authored and self-reviewed
by Codex (OpenAI), submitted through Mingli Yuan's authorized account proxy.
This refers to and reconciles existing first-party project design, with no new
third-party text, data, code or figures. Account use is not human technical
review, endorsement or a correctness guarantee. No independent reviewer.

Checks for this change: source byte/hash binding; JSON consistency; source
parameter agreement; preserved gate states and null implementation hashes;
25/13 grid counts; staged diff/whitespace and known-withdrawal scan. Local
publication scanning covers the exact publication payload and a fetched-file
validation subset, not a clone of all upstream history. Repository-wide CI
remains a separate check. No historical experiment was rerun.
