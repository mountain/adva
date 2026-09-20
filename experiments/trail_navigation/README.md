# Trail navigation: design checkpoints

Status: **not implemented, not executed, not accepted for semantic use**.
Execution was paused at Mingli Yuan's request on 2026-09-20. Design resumed
after his request for three uses and their possible hole/filling duals.
No experiment, performance result, failure certificate or change to native
`search` / `learn` is claimed.

The current [six-experiment design](six-experiments-design.md), its
[Chinese reading copy](six-experiments-design.zh.md), and the
[structured proposal](suite-proposal.json) specify three pairs: learning a
filling/context direction, finding a relation between two holes/fillings, and
finding a joint witness for three holes/fillings. They include shared controls,
proposed budgets and explicit geometry/implementation obligations. The six
trials remain unimplemented and unexecuted; this checkpoint does not fulfill
the earlier request to merge completed experimental results.

Mingli's question concerns a shared network of construction and spatial trails
that can support navigation, learning, exploration history and failure rollback.
The existence of some global estimate is not the central difficulty. The open
question is when an experience on one path can guide another path, and which
contextual distinctions must remain to avoid an invalid transfer.

Two earlier contracts are retained, as separate unexecuted proposals:

- `contract.json`: unexecuted v0, a supplied arithmetic bridge and search-order
  comparison. It tests use of an already supplied relationship, not formation of
  a useful relation network. It was superseded before implementation or execution.
- `contract-v1.json`: unexecuted v1 proposal. A finite failed search subtree
  yields a scoped nogood; after rollback, another task can reuse it only while
  its premises and domains remain applicable. A deliberately scope-blind control
  would expose an invalid reuse after a premise changes. This remains a proposed
  calibration, not an agreed complete characterization of Mingli's idea.

## Earlier resumption questions

The six-query design above is now the primary proposal. The earlier failure
reuse questions below remain relevant to its scope and history checks.

Before implementing, reconsider whether scoped failure reuse is the right
smallest question. In particular:

1. Which equivalence on retained histories preserves the continuations that
   matter to a declared observer and task?
2. What can the network infer from trails, and what correspondence or scope is
   still supplied from outside? Do not report supplied structure as learned.
3. How does rollback retain knowledge that changes the next decision, including
   unresolved outcomes that must not become negative certificates?
4. Does navigation reduce complete work after charging construction, checking,
   persistence and scope checks? Retain ties and losses as well as gains.

The v1 proposal would exercise ordinary scoped finite nogood learning. It would
not establish a new algorithm, native Adva learning, autonomous cross-domain
translation, a universal direction field or global convergence. Native binding,
learned correspondences and changing representations remain separate questions.

No automatic continuation or future run is scheduled. The earlier request to
submit and merge completed experimental work is not reported as fulfilled by
this design checkpoint. Keep this checkpoint separate from main until the work
is resumed and its intended outcome is established.

Direction and pause: Mingli Yuan. Design, writing and self-review: Codex
(OpenAI), contributed under Unknown v0.3 through Mingli Yuan's authorized GitHub
account proxy. Account use is not his authorship, technical review, endorsement
or a correctness guarantee. These files are original project contributions;
no third-party text, data, code or images are incorporated.
