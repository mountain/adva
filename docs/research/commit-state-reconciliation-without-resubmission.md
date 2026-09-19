# Commit-state reconciliation without resubmission

Date: 2026-09-19. Status: bounded external experiment and one Proposed word;
not native admission.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
not his review, endorsement or correctness guarantee. Original code, prose,
terminology and synthetic evidence are contributed under Unknown v0.3. No
external content is incorporated.

## Dependency and problem

Current main was `e98592b7dc0c3fabba3fa897a491c78f5c55c45e`. Draft PR 199
remained open; PR 201 contained research notes without its raw runs/checker and
was not a runtime dependency. The current history-surface result does not change
ledger semantics. PR 199's two executed boundaries show that pre-write and
post-write/pre-COMMIT process exit restore the original logical ledger in their
declared schedules. They do not tell a caller what to do after an observation
whose COMMIT result is unknown.

The frozen question is: **can a receiver inspect durable state and distinguish an
exact committed result from an empty selected ledger, while refusing to infer a
result from every mismatch?** It must not resubmit, renew allowance, change the
question or rerun mathematics. Research 0123's arithmetic-universality and
hypothesized-arithmetic-truth remain proposals. This experiment neither supplies
Research 0090 coverage nor unlocks Research 0092 vocabulary lifting.

## Proposed word

`commit-state-reconcile` is Proposed, with the complete machine-readable boundary
in `docs/terminology/commit-state-reconcile-v0.json`.

Inputs are the receiver-selected complete expected request, the complete candidate
including its transition key, and one existing trusted ledger. Outputs are exactly:

- `StoredCommitted`: the validated ledger stores the exact canonical candidate and
  its checked result;
- `ProvenUncommittedLedger`: the validated selected ledger has no accepted row;
- `UnknownCommitState`: neither conclusion is safe under the fixed bindings.

The middle result is deliberately local. It does not prove that an external action
never occurred, that another database does not exist, or that power loss preserved
all storage. `UnknownCommitState` never grants retry permission. Expansion/replay
means running the receiver and retaining the complete request, response, ledger
digest and unchanged ledger bytes; it is not shorthand for a new submission.

## Frozen experiment and result

The contract predates execution and fixes nine reconciliation cases over two
different exact-rational decision families:

| Cases | Expected outcome | Observed |
|---|---:|---:|
| Valid empty ledger, primary and asymmetric reuse | 2 ProvenUncommittedLedger | 2 |
| Exact committed ledger, primary and asymmetric reuse | 2 StoredCommitted | 2 |
| Changed candidate or changed expected history | 2 UnknownCommitState | 2 |
| Checker fingerprint tamper, corrupt file, missing file | 3 UnknownCommitState | 3 |

The two `StoredCommitted` responses reproduce the exact stored checked results and
allowance `(3,3,0)`. The two empty witnesses return allowance `(3,2,1)` and no
stored result. All nine calls have `parent_checked=false`, `debit_delta=0` and
`retry_authorized=false`. Every existing ledger's SHA-256 is identical before and
after inspection. The asymmetric case changes prior, kernel, loss and cost, so it
is a substantive reuse rather than a renamed fixture.

Five negative cases keep different failure causes inside one conservative status.
That is intentional: a coordinator needs permission to proceed, not a guess about
which damaged or mismatched layer will eventually explain the observation.

Without this word, the old receiver emits the instruction “reconcile existing
ledger” on uncertain commit cleanup but exposes no callable read-only relation.
With it, the same candidate and finite state receive one of three bounded statuses.
This is an interface/expressibility comparison, not measured solver acceleration.

## Costs and reproduction

The first campaign passed **107 supervisor assertions** in **15 child processes**:
four ledger initializations, two committed fixture constructions and nine read-only
reconciliations. Total counted receiver work was **3,735 units**, with zero search
candidates and no corrective replay. Campaign wall time was **0.910727763 seconds**;
summed non-overlapping child lifetime was 0.844389415 seconds. Serialization took
0.035655356 seconds and fixture construction 0.000047720 seconds. Individual
reconciliation calls took 0.0461–0.0627 seconds and 1–25 receiver units.

Highest child RSS was **13,696 KiB (13.38 MiB)** and supervisor RSS **15,104 KiB
(14.75 MiB)**. These are category maxima, not aggregate memory. Research, reading,
word formation, network and publication costs were not measured. Evidence packing
and byte verification took **0.096807888 seconds** outside campaign time.

Replay from the repository root, using a fresh output directory:

```sh
timeout 35s python3 -B -S experiments/commit_state_reconcile/run.py --output /tmp/adva-commit-reconcile-new
```

`evidence/execution.json` is the compact record. The manifest hashes all **68
files**; `attempt-1.tar.gz` contains 1,257,111 expanded bytes of exact requests,
responses, ledgers and commands. Archive byte verification is not independent
semantic verification.

## Boundary, usefulness and next minimum

The result is an external finite read-only tool, not a theorem about arbitrary
storage. It shares Python and SQLite with the writer. There is no actual interruption
inside COMMIT, power-loss/disk-flush model, hostile concurrent replacement,
authentication, external action, or distributed exactly-once guarantee. It changes
neither additive-zero nor multiplicative-one domains and grants no native
communicate/accept/free/Close/Seal, M6, universality, learning or social trust.

It helps Mingli and later agents decide whether a continuation result may be read,
whether the selected ledger is empty, or whether work must pause without replay.
Benefit for Jiamin's real task remains unmeasured.

The next minimum is an **independent snapshot receiver**: serialize only the schema,
bound metadata, transition row and file digest into a versioned receipt, then check
that receipt in a separate process without opening SQLite. This would reduce shared
implementation coupling. It still must not simulate power loss or authorize retry.
