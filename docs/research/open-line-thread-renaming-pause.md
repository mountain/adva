# Open-line thread renaming correspondence: paused implementation record

Date: 2026-10-21. Status: **Unknown / paused after the sole correction replay**.
Baseline: proposed predecessor `e50810d93f9720b5c11975b60e34f73ae2c15f1b`
on draft PR #226; latest merged main remained `2154b3c6716e7b5a19b98b81aca7940c0c93fe7d`.

Authored by Codex (OpenAI), through Mingli Yuan's authorized GitHub account
proxy; not his authorship, review, endorsement or correctness guarantee.
Original code, fixtures and prose under Unknown v0.3. No external expression
or payload is incorporated; pytest remains a separately installed dependency.

## Frozen question and intended receiver

The [contract](../../experiments/open_line_thread_renaming/contract.json) was
written before implementation. It asks whether one explicit finite
correspondence can rename every declared identity in the canonical two-step
open `WholeCut6` source to the fresh instance while preserving raw step order.
The same correspondence was required to work on forward and reversed words;
swapping the two step targets was a required refusal.

The candidate has ten ordered namespace maps: whole, cells, ports, sources,
occurrences, channels, thread steps, holes, residuals and alternatives. Both
complete sources must pass the existing validator. The receiver then checks
coverage and injectivity, renames every source field and the fixed AM term,
and requires exact equality with the independently supplied target. This was
one route, zero search, at most 12 receiver calls, 30 seconds per attempt,
1 MiB evidence and one correction replay. No native code or predecessor
evidence was to be changed.

This is literal finite syntax with no arithmetic domain. Research 0123's
`arithmetic-universality` and `hypothesized-arithmetic-truth` remain Proposed;
additive zero and multiplicative unity are neither identified nor evaluated.
Research 0090 coverage and dependent 0092 promotion remain Open. No M6 filler,
topology, braid law, historical inverse, native `free`, general alpha-equivalence
or source-changing transport is established by an intended local checker.

## Attempt 1 and the single correction

Attempt 1 stopped at assertion 7 while checking reuse on the reversed word.
The implementation had used raw word occurrence order as the declaration order
of the `thread_steps` namespace. The forward mapping declared `(a,b)`, while
the reversed source exposed `(b,a)`, so one map could not satisfy both even
though applying that map step-by-step would preserve either occurrence order.

The sole permitted correction changed only namespace enumeration:

```diff
- tuple(step.name for channel in form.channels for step in channel.thread)
+ tuple(sorted(step.name for channel in form.channels for step in channel.thread))
```

`rename_source` continued to traverse the raw word without sorting. This
clarifies a necessary distinction: **the canonical declaration order of a
renaming map is not the occurrence order that the map must preserve.** It is a
process/representation clarification, not an admitted mathematical result.

The attempt used one child process, 0.155295 s wall, child peak RSS 25,460 KiB
and supervisor peak RSS 12,928 KiB. It wrote no serialized case record. The
attempt-1 script bytes were overwritten by the correction and therefore lack
a retained SHA-256; the exact one-line delta above is known, but byte-exact
attempt-1 replay is unavailable. This archive defect is not hidden.

## Correction replay and stopping residual

Attempt 2 advanced to assertion 29 in the negative-control loop, then stopped.
Static inspection locates a second implementation defect: `swap_targets`
constructs only two pairs from `pairs[0]` and `pairs[1]`. For six-entry source
or occurrence namespaces it silently drops `pairs[2:]`. The harness expected
a target-order refusal but received an earlier source-coverage refusal. Because
the sole correction replay had been consumed, no further patch or run was made.

The replay used one child process, 0.184715 s wall, child peak RSS 24,896 KiB
and supervisor peak RSS 12,928 KiB. It also stopped before `cases.json`, so no
positive correspondence or negative control is admitted even though control
flow reached part of the family. The two attempt wall times sum to 0.340010 s;
these runs are sequential. Process RSS maxima are not file sizes or concurrent
total memory. The retained experiment directory was 24,580 bytes before this
note/outcome record. Dependency setup reported 8.24 s resolution, 130 ms
preparation and 8 ms installation; total environment-setup wall time was not
measured separately.

Construction, successful receiving/reuse, serialization, primitive work units,
hard memory enforcement, authoring time and real-user value remain unmeasured.
Zero search nodes were visited. No new or revised word was formed.

[outcome.json](../../experiments/open_line_thread_renaming/outcome.json) binds
the classifications, measured costs and SHA-256 coordinates. Both stdout files
are empty; exact tracebacks and supervisor summaries remain under
`evidence/attempt-1/` and `evidence/attempt-2/`. The current
[run.py](../../experiments/open_line_thread_renaming/run.py) is the attempt-2
source and intentionally retains the second defect. It is evidence and a
continuation point, not a successful tool.

## Value and next bounded continuation

The run produced no mathematical success certificate, but it separated two
orders that a future receiver must not conflate:

1. canonical declaration order makes one explicit finite map inspectable;
2. raw occurrence order is preserved when applying that map to each word.

That distinction helps Mingli and subsequent agents formulate the next checker
without sorting away the object being studied. It has no measured benefit for
Jiamin and supplies no social-trust, expressive-power or acceleration claim.

The smallest continuation is mechanical and must use a **new** finite contract:
preserve both failed attempts, change `swap_targets` to return the two swapped
pairs followed by `*pairs[2:]`, and permit at most one supervised run with the
same source family, controls and limits. If that run passes, archive its exact
cases before making any correspondence claim. Do not expand to braid reduction,
three-interface geometry, all-fillings closure or universal grammar in that run.
