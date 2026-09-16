# First tooling helpers for the problem workflow, 2026-09-16

Direction: Mingli Yuan asked for the tools that
[the tooling workflow](../TOOLING_WORKFLOW.md) names to be filled in. Design,
implementation, execution and record: deepseek-v4-flash-vision-exp (DeepSeek Harness),
submitted through Mingli Yuan's GitHub account (`mountain`) as an authorized proxy;
not his authorship, review, endorsement or guarantee. ChatGPT (OpenAI) wrote the
workflow document this implements; that document's roles and limits are unchanged and
this note does not claim its review.

## What section 6 asked for

The workflow's minimal engineering order lists three first deliverables: read-only
navigation over claims, code, evidence, versions and follow-up corrections; a problem
card with an attempt list and a handoff summary; and a small execution adapter that
prioritises the data interpreter and the existing exchange checker. It also states the
display rule that several facts must stay apart instead of collapsing into one green
success.

## What now exists

| Item | Tool | What it does |
| --- | --- | --- |
| First: read-only navigation | [`scripts/navigate.py`](../../scripts/navigate.py) | Finds claims by question keywords or exact id, prints recorded status, dimension, dependencies and counterexample boundary beside observed file presence, classifies each record as `historical`, `runnable-here` or `not-yet-executed`, and exposes a follow-up correction index built from note headers. |
| Second: problem worksheet | [`scripts/problem_card.py`](../../scripts/problem_card.py) | Prints the ten-field card of section 2 with a JSON skeleton, and validates a filled card: missing fields are listed and left missing, an unconfirmed handoff stays open, a failure must retain its first witness, a `not-run` attempt must keep its reason, and a successor round that changes the question, scope or budget must record a reason. |
| Third: bounded execution adapter | [`scripts/run_bounded.py`](../../scripts/run_bounded.py) | Runs a declared plan under a declared budget and prints five separate axes: whether the material was accepted, whether execution completed, what the checker's own output says, what the result applies to, and what stays unknown. Includes the exchange-chain plan and a data-machine sample plan, and reports `not-started` with the reason and remediation command when a plan cannot run here. |

The three commands are stdlib-only and read-only apart from their own output
directory. None of them executes a research campaign, allocates a native identity,
registers a claim or grants admission.

## Checks

- `python -m pytest -q tests/python/test_tooling_workflow.py` — **10 passed**. The
  tests check the properties the workflow states, not merely exit codes: that
  conclusions are labelled `RECORDED` or `OBSERVED HERE` and that the header keeps the
  no-inference rule; that a missing field list is exactly the missing fields; that a
  failed attempt without a retained first failure and a `not-run` attempt without a
  reason are both refused; that an unconfirmed handoff and an unexplained budget change
  stay open; that both declared plans carry scope, budget, requirements and residual;
  and that a plan whose inputs are absent returns `not-started` with its remediation.
- `python3 scripts/run_bounded.py --plan exchange-chain` on this host: material
  accepted, execution completed, and the axes kept apart — top-level `status
  DisclosedByteChainChecked` with `received_rounds 5`, and per-row `source_binding
  Unverified`, `semantic_acceptance Withheld`, `native_admission not-granted`. The
  replay of a refusal is therefore not reported as a success.
- `python3 scripts/run_bounded.py --plan data-machine-sample` on this host: the
  declared sample suspends (`status Suspended`) after 17 quantum steps, and the run
  record keeps the wall and CPU budgets it declared.
- Resource limits are reported per attempt as `applied` or `refused-by-host`. On this
  macOS host `RLIMIT_AS` is refused by the kernel (`ValueError: current limit exceeds
  maximum limit`), which is the same host limitation already recorded for
  `test_phase_runner` and the Pascal replay; no limit was relaxed to hide it.

## Limits

- The navigation tool reports recorded fields and filesystem presence. It does not
  prove a claim, does not re-run a checker it finds, and cannot tell a live result from
  a retained artifact beyond what the record and the files say.
- The card validator checks structure and the specific rules the workflow states. It
  cannot judge whether a question is well formed, whether a check scope is sufficient,
  or whether a budget is realistic.
- The adapter runs only the plans declared in its own source. A plan is a declared
  command with a declared budget, not a general sandbox, and the exchange-chain plan
  reads retained bytes rather than contacting anyone.
- The workflow's empirical question — whether this reduces repeated work for a new
  participant — has not been tested with participants, and nothing here answers it.
