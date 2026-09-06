# Research 0152 continuation 01: noninteractive Metamath transport

Written before `run-02`, 2026-09-06. This is a revised finite run contract,
not an automatic budget reset. The user authorized continuing successful
bounded methods and then committing/merging; the mathematical scope is
unchanged from the original Research 0152 contract.

## Retained obstruction

`run-01` passed the complete set.mm dependency audit, all calibration controls,
and depth 2. Depth 3 was Rust-replayed and Lean-checked, but Metamath's default
interactive pager stopped its verified-label output at `adva152e138`. It
consumed the remaining input at the paging prompt and spun at EOF. After the
exact child process was inspected, it was explicitly stopped with SIGTERM.
The supervisor retained `Blocked`; depth 3 is NOT admitted. No depth 4 ran.
The original supervisor source is archived beside the failure report with
the same SHA256 as that report. No failed record is replaced or relabelled.

## Boundary repair and justification

Every Metamath invocation now starts `SET SCROLL CONTINUOUS`, before `READ`
and `VERIFY PROOF`. This is the verifier's documented noninteractive output
mode (`src/mmhlpb.c`, `HELP SET SCROLL`), not a change to its proof rules.
A regression test requires that prefix for base, positive and negative
verification commands. The strict full-audit completion check, exact selected
label trace, explicit proof-error detection, negative controls, database pin,
Lean axiom allowlist and Rust replay are unchanged. Formatting the new Python
module before this run changes no policy. Rust source and the original
mathematical contract remain byte unchanged.

## New finite invocation

Execute exactly one invocation in fresh `0152-evidence/run-02`. Recheck the
entire pinned database, calibration and all negative controls, then the same
three depths, seeds, two policies, 48-step cap and proof exports. Do not skip
the already completed depth 2 or count it twice in comparative conclusions.
The original per-invocation budgets apply: 900 total wall seconds, 180 wall /
160 CPU seconds per child, 24 children, 8 GiB child address space, 32 MiB per
file, 128 MiB retained total, 250,000 candidate visits including replay and
50,000 library units including replay. No internal retries or further rounds.
The scope cap, checking gate, Unknown/exhaustion rules, checkpoint reserve and
path retention are unchanged. The manual diagnostic stop and this fresh
invocation are recorded separately, not hidden in a reported speedup.

This repair is expected to remove the observed I/O obstruction because it
eliminates the exact paging prompt seen in the retained log. It predicts
nothing about which search policy will succeed or be cheaper. Failure of the
repaired protocol stops this invocation; no further continuation is implied.
