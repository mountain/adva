# ADR 0041: compare policies without changing verifier rules

Status: accepted for Research 0153 only, 2026-09-06.

Research 0152 exposed a zero-residual-gain cycle despite valid local proofs.
The user requests policy comparison followed by 100 rounds using the best
measured choice. This is a search-policy experiment, not new stable semantics.

Keep the old checker, library, proof-export and log-admission rules unchanged.
Use a new Rust example with runtime/test-enforced byte-identical protected
blocks from the prior private example implementation, and a new bounded
supervisor importing the existing external log checkers. The temporary source
duplication is explicit and pinned; changing either block blocks the trial.
Do not refactor the fingerprinted source merely to expose private functions.

Add exact-syntax visit preference and a fixed, budgeted exploration schedule.
These control which already checked arithmetic candidate is proposed next;
they authorize no native identity, path deletion, implicit sharing or truth.
Charge memory/filter work and retain relaxed-filter events and Unknown paths.

Rank the three policies on the fixed pilot independently for expansion and
contraction. Freeze winners before 100 new-seed rounds. Keep the weak scope:
pilot-best under a declared cost ordering is not a generally optimal policy.
The outer entry remains adva.py. Each round needs Rust replay and complete
Lean/MM checking before its research receipt is admitted. The agenda's
specialization, exact native data, coverage/invariance and logic gates remain
unfulfilled by this arithmetic campaign.
