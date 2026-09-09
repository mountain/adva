# WholeCut6 production-accounting follow-up

Date: 2026-09-09. Scope: one syntax-only sub-obligation of Issue #102.
Direction: Mingli Yuan; implementation and audit: ChatGPT/Codex.
Base: `a70cedc82834fc800dc3471c7b4d244cd44c88d4`.

## Problem and pre-change witness

The grammar in note 0102 sections 3--5 requires explicit source production:
every initial occurrence must be allocated exactly once, and repeated source
names need a declared production ledger. The test-local WholeCut6 record did
not represent that ledger. Its validator accepted six distinct occurrences
assigned to one source without any allocation declaration. This is a gap in
the research fixture, not a discovered Rust identity-admission vulnerability.

Before editing, the existing three-file suite passed 31 tests (0.16 seconds
reported by pytest). This direct probe also returned normally:

```python
from dataclasses import replace
import test_bootstrap_zero_whole_cut_grammar as g
f = g._fixture()
bad = replace(f, ports=tuple(
    replace(p, source="undeclared-shared-source") for p in f.ports
))
g._validate_whole(bad)
```

Run the probe with `tests/python` on PYTHONPATH. At the patched version it
raises ValueError because the retained productions disagree with the changed
port sources. Removing the ledger entirely also fails.

## Narrow implementation

`Production(source, occurrences)` is a research-local declaration. WholeCut6
now requires an explicit tuple of these records. There is no default ledger
inferred from arbitrary submitted port labels. The canonical positive fixture
constructs its own six singleton declarations explicitly.

The validator requires one nonempty production per source, nonempty string
names, exact agreement between each declared occurrence and its port source,
one value type per source, and exact occurrence coverage with multiplicity one.
An unknown, missing or repeated occurrence fails. Splitting one source across
duplicate entries fails; multiple distinct occurrences in one declared source
entry are permitted. Their order remains recorded, and accepted reordered
records are still unequal raw records.

These declarations account for initial allocation. They do not execute a copy,
allocate SourceId/OccurrenceId, authorize sharing in Rust, reconstruct erased
history, or change the six-port minimum. Arithmetic here is finite natural
number counting; neither Real evaluation nor a multiplicative-unit judgment
is involved. The existing bridge reuses the checked payload and still has no
M6 filler. Alternative/fibre retention is not inferred from this ledger.

## Local preservation argument

Assume the existing six-port distinct-occurrence and unit-multiplicity checks
and the declared Python record types. Let P be the six port occurrences and
L the flattened production occurrence list. Acceptance checks Counter(L) =
Counter(P), so every occurrence is allocated once, and no extra occurrence is
allocated. Each member's source is checked against its unique port record;
distinct entry sources prohibit two competing source declarations. The
value-type check excludes a source spanning incompatible declared types.
The routine only reads these records and does not normalize their order.

This proves the stated allocation invariant for accepted typed records under
the host arithmetic assumptions. It does not prove the complete coordination
theorem in note 0102 section 15 or validate arbitrary deserialized host objects.

## Finite validation and replay

The contract was frozen before editing in
`experiments/whole_cut_production/contract.json`. One finite route covers all
203 canonical restricted-growth partitions of six positions into source
groups. A Bell-number recurrence independently checks the family size; the
restricted-growth representation enumerates each such partition once. For
each allocation, positive validation and line/circle readout pass; omission,
duplicate occurrence and wrong source controls are rejected. This finite
coverage is over source grouping, not arbitrary names, types or future arities.

Additional controls cover undeclared sharing, absent/empty/extra productions,
split duplicate-source declarations, conflicting source types, malformed names,
and preservation of the raw occurrence order. One fresh-name three-source
instance reuses the rule and retains all occurrences through the open M6 bridge.

Reproduce from a checkout using the project's test environment:

```sh
python -m pytest -q \
  tests/python/test_bootstrap_zero_whole_cut_grammar.py \
  tests/python/test_bootstrap_zero_cell_carrier_views.py \
  tests/python/test_bootstrap_zero_whole_cut_m6_bridge.py \
  tests/python/test_bootstrap_zero_production_ledger.py
```

The implementation pass returned **244 passed in 0.38 seconds** (0.706 seconds
outer tool wall time). The local run used a 30-second process timeout and
pytest 9.1.1 installed in an isolated dependency directory. No full workspace,
native Rust, other-Python-version or remote-CI pass is claimed. After formatting
and import/tuple-style fixes, one final replay passed all 244 tests in 0.36
seconds (0.665 seconds outer subprocess wall time). Its largest child RSS was
29,904 KiB on Linux, not aggregate simultaneous memory. Separate construction,
verification and serialization costs were not measured. There was no failing
implementation-test run or adaptive search expansion. Ruff 0.16.6 lint and
format checks passed; the initial three style findings are retained in
`experiments/whole_cut_production/evidence.json` with source hashes and outputs.

## Issue disposition

Issue #102 stays open. This patch is a candidate completion of its production
accounting substep and needs review/merge before becoming mainline evidence.
Remaining work includes alternative and fibre ledgers, distributivity binding
accounting, all five interpreter declaration checks, and the full syntax
coordination obligation. Native interpreter bodies and an M6 semantic filler
are not being added as requirements for the original syntax-only milestone.

The next smallest step is one named open hole with two retained alternatives:
select one explicitly and reject a record that silently drops the other.
This follows the existing note 0102 contract rather than expanding its scope.
