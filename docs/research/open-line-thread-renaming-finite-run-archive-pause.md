# Open-line thread renaming: finite run passed, archive verification paused

Status: `FiniteRunPassedArchiveUnknown`. The receiver execution supplied new
finite evidence, but the separately required archive verifier did not complete.
No claim-registry entry or vocabulary promotion follows.

## Frozen problem and dependencies

On 2026-10-23 merged `main` remained
`2154b3c6716e7b5a19b98b81aca7940c0c93fe7d`. Draft PR 226 was based on that
main and its predecessor head was
`b0b2570194ce514a4e66dd4cc4550e04ea15328c`. New draft PR 227 concerns an
independent finite positivity/epistemic-identity model and does not change this
open-line dependency chain.

The validation contract froze the exact repaired runner bytes, two positive
source pairs, ten controls, one supervised run, zero receiver corrections, 30
seconds and 1 MiB. It required a successful pytest import before execution.
Research 0090 coverage remains open; dependent 0092 promotion remains blocked;
both Research 0123 arithmetic words remain Proposed.

## Environment gate

A disposable virtual environment used Python 3.12.14 and pytest 9.1.1. Package
resolution, preparation and installation were reported as 6.14 s, 0.141 s and
0.013 s. Setup plus import preflight took 7.426210941 s. Setup peak RSS was not
measured. No dependency was vendored and the setup did not modify repository
content.

## Finite execution result

The sole supervised receiver run completed:

- 52 assertions and 12 receiver calls passed;
- forward and reversed sources both received the same explicit correspondence;
- raw thread order remained `(a,b)` versus `(b,a)` after fresh renaming;
- all ten frozen substitutions or malformed mappings were refused for their
  exact expected reasons;
- the six-entry occurrence and source mutations retained their four untouched
  tail pairs instead of silently truncating them;
- all twelve case records serialized and decoded within the 1 MiB bound;
- neither checked result authorizes a continuation.

Formation took 0.000411934 s; first receive 0.001530396 s; reversed reuse
0.000925551 s; all controls 0.004069190 s; serialization and decode 0.002922168
s. Work before summary was 0.162214087 s and supervised wall time was
0.272369062 s. Child peak RSS was 25,792 KiB and supervisor peak RSS 13,056 KiB.
These are process maxima, not a hard or combined memory bound.

This is finite experimental support for one complete-name renaming relation. It
is not yet an admitted complete certificate because the contract also required
independent archive verification.

## Archive-verifier pause

The first verifier attempt incorrectly compared the historical attempt-2
`run.py-after-correction` coordinate with the current repaired runner. The sole
allowed correction separated those identities. Its replay then stopped on an
independent implementation mistake: it requested `negative_controls` from the
new validation contract, while that unchanged list remains in the inherited
`contract.json`. No archive report was written and no third verifier run was
made.

Thus exact cases, execution, stdout, empty stderr and supervision are retained,
but the combined success criterion remains Unknown. The receiver must not be
rerun merely to repair this documentary verifier.

## Mathematical and vocabulary boundary

No new word was formed. In particular, this does not establish unrestricted
alpha-equivalence, native source transport, braid or topological equivalence,
history semantics, M6 filling, native `free`, arithmetic universality or
hypothesized arithmetic truth. Additive zero and multiplicative unity remain
different typed readings and were not evaluated. Practical benefit for Jiamin
Zhao remains unmeasured.

The evidence helps Mingli and later agents separate three layers: a finite
receiver run can succeed; its evidence can remain exactly preserved; and an
independent archive certificate can still be absent. That prevents a successful
local run from silently becoming a stronger public claim.

The smallest continuation is to freeze a verifier-only contract, change only
the negative-control lookup to the inherited `contract.json`, and permit one
archive-verification run over immutable attempt-4 evidence. Do not rerun the
receiver or enlarge the mathematical scope.

This record is project-original work by Codex (OpenAI), submitted through
Mingli Yuan's authorized GitHub account proxy. It is not his authorship, review,
endorsement or correctness guarantee. It is contributed under Unknown v0.3 and
imports no external expression or payload.
