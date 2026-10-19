# Research 0270: closed LineView coordination replay

Date: 2026-10-17. Status: finite syntax-only result passed.  Codex (OpenAI),
submitted through Mingli Yuan's authorized account proxy, not his authorship,
review or endorsement.  Project-original record under Unknown v0.3.

## Frozen continuation

Research 0269 retained an unexecuted 6,782-byte candidate after its only known
defect was a Ruff formatting difference.  The new
[contract](../../experiments/bootstrap_zero_line_coordination_replay/contract.json)
fixes that exact input digest and permits only the recorded formatting change.
There is one route, no candidate search and no arithmetic domain.

The question is finite: can an accepted AM syntax projection and the built-in
closed `LineView`, each checked against the same independently supplied
`WholeCut6`, retain one ordered occurrence ledger, the complete ordered line
channel ledger and the exact source residual ledger?  The relation is a paired
witness.  It is not reconstruction from `LineView` alone.

## Result

Ruff 0.16.10 changed only the recorded thread-tuple layout.  Lint and format
checks then passed.  The targeted replay passed **8 tests**: the canonical
closed fixture, one independently renamed closed fixture, and six refusals for
a foreign AM term, foreign line view, reordered ports, omitted channel,
invented residual and open source.

The fresh source reuses the same constructor relation without reusing its
whole, occurrence or channel identities.  Both accepted sources have the exact
empty residual ledger.  This is forced by the current domain: `LineView`
accepts only a closed WholeCut6, whose open-port residuals are empty.

The explicit fourteen-module Bootstrap Zero integration replay passed
**1,110 tests**.  The supervisor's display field said fifteen modules because
it subtracted three launcher arguments instead of four; the retained command
contains exactly fourteen explicit paths.  This reporting error was corrected
from the command without rerunning the tests.

## Costs and failures

The targeted process took 0.403498 seconds including launch and reached 29,820
KiB peak child RSS.  The integration process took 1.786555 seconds including
launch and reached 53,852 KiB.  Environment setup took 24.256809 seconds.

Three preflights produced no tests: `/usr/bin/time` was absent; the old ignored
virtual environment had lost its Python target; and `uv` refused to overwrite
that incomplete environment.  A separate temporary environment was therefore
created without changing repository dependencies.  These are tool failures,
not counterexamples.  Construction, receiving, serialization and fresh reuse
are not separately timed, and the inherited receiver exposes no counted work
unit.  No acceleration claim is made.

Full commands, versions and the retained failures are in the
[execution record](../../experiments/bootstrap_zero_line_coordination_replay/evidence/attempt-1/execution.json).

The staged diff, research index, JSON, Ruff and evidence digests pass locally.
The mandatory publication-history scan first remained blocked by partial-clone
object fetching, including one explicit 480-second timeout. A bounded complete
object prefetch then succeeded in 18.460074 seconds. The same checker completed
in 10.531983 seconds, covering 5,664 unique blobs, 14,458 archive members and
429,894,831 expanded bytes with no identified withdrawn copy. The earlier
transport stalls are retained but no longer block publication.

## Vocabulary and boundary

New vocabulary: **zero**.  `PairedLineCoordination` remains a local program
type.  Existing source, occurrence, residual, view and coordination language is
sufficient.

This helps Mingli and later agents separate three claims: an AM term forms; a
closed line view and that term can share exact finite coordinates; the view can
reconstruct its source.  This run establishes only the first two.  It also
prevents the empty residual ledger of a closed object from masquerading as a
test of nonempty residual transport.  Jiamin's practical-task benefit remains
unmeasured.

An explicitly constrained open-line profile would be required before testing
nonempty residual transport.  Circle, thread and logic views; routing,
collision, fibres, split and traversal; native correspondence; observer
invariance; Research 0090 coverage; Research 0092 generation, promotion and
reuse; semantic agreement; M6 filling; native `free`; arithmetic universality;
hypothesized arithmetic truth; and universal grammar remain open.

The smallest continuation is not to broaden `LineView`.  First freeze an
open-line proposal with its admissible open ports, exposed residual coordinates
and a refusal showing why the existing closed view cannot receive it.  Only
then run one positive nonempty-residual instance and one fresh-source reuse.
