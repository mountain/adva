# WholeCut6 retention and declaration follow-up

Date: 2026-09-09. Direction: Mingli Yuan; implementation and review: ChatGPT/Codex.
Base: `7a900db49a08276d2e76a53fdb191a295ece37ac`, which includes PR #162.
Status: bounded syntax-only closure attempt; **Issue #102 remains Open**.

## Frozen question and observed gap

The user authorized one further attempt at the original Issue #102 criteria,
without requiring success. The contract in
`experiments/whole_cut_retention/contract.json` was frozen before this edit.
One route covers declared alternative retention, finite inverse-image ledgers,
and the five interpreter declarations. Individual execution is capped at 30
seconds; at most 5,000 cases, with no automatic continuation or scope growth.

The base validator accepted two distinct open ports assigned the same hole
name. This executable pre-edit probe returned normally:

```python
from dataclasses import replace
import test_bootstrap_zero_whole_cut_grammar as g
w = g._fixture(open_last=True)
a, b = w.open_ports
g._validate_whole(replace(w, open_ports=(a, replace(b, hole=a.hole))))
```

The new hole ledger rejects this alias. This is a research-fixture defect,
not a claim that a Rust admission boundary was compromised.

## Changes and exact scope

### Alternatives and selection

WholeCut6 requires explicit HoleDecl and AlternativeDecl tuples. Open ports
have distinct hole names; hole declarations cover exactly those holes and retain
their port/type association. Each alternative family is nonempty, has distinct
local option names, and declares the hole's type. A hole need not yet have an
alternative declaration: absence is unexplored/unspecified, not proof of an
empty filling fibre. Its port remains open and no selection is admitted until
an explicit option is available. Option bodies retain the
existing raw AMTerm records. The constructor boundary is checked, but this is
not a full recursive AM typing or parser implementation.

ChoiceWitness records a named selection, its source, the selected complete
option payload and the complete ordered alternative ledger. Validation takes
an independently supplied expected WholeCut6. A submitted source cannot
authorize itself: both the retained source and alternatives must equal the
expected records, and the selection must belong to the named hole.

This is a selection declaration. It does not insert a missing through edge,
delete an OpenPort, create an M6 filler, or make a CircleView admissible. It
records a choice without claiming physical, native or semantic closure.

### Retraction fibres

Retract now requires a FibreAccount: named expansion/boundary, explicitly
typed domain and codomain points, a finite map table and a fibre ledger.
The map table must be total and single-valued on the declared domain, and
each target must belong to the declared codomain. The checker independently
reconstructs inverse images and compares full typed member payloads.
Every codomain point has an entry, including empty fibres. Raw member order
is retained; only the coverage comparison uses multisets.

The account's boundary names must match the Retract record. Existing split
formation and traversal formation now recheck it. These are declared finite
maps between research-local point sets, not observed native program execution,
Rust source identities, a derived D*, or proof that a generator is a semantic
section. The old split-boundary check remains a syntax judgment only.

### Five interpreter declarations

The test-local RetainedSyntax packet attaches the WholeCut6, explicit
retractions, collision records and extension declarations. One declaration
family must have exactly the original ordered signatures I_K, I_X, I_t,
I_thread and I_AM, with the target names from note 0102 section 11.

The validator checks the independently supplied expected packet using the
existing component checks, verifies collision member snapshots against its
ports, and requires each declaration to retain that entire packet. A missing
alternative, residual, retraction, collision or extension in any one declared
source fails. A separately valid fresh packet cannot replace the old expected
packet. This is an explicit preservation check for declarations; it does not
execute target views or give a semantic interpretation to their names.

## Local preservation arguments

1. Selection acceptance requires literal equality to the caller's expected
   source and ordered alternative ledger. Therefore selecting one member
   cannot remove another member, any other hole, or the retained source data.
   Membership checks the complete option record, not just its display name.
2. A total single-valued finite map assigns each domain point once. Comparing
   each recorded fibre against its reconstructed inverse image therefore
   preserves exactly the declared domain coverage and target association.
   Requiring every codomain entry also preserves empty fibres.
3. Requiring five exact signatures and equality of each retained packet to the
   expected packet prevents omission or substitution of declared source data.
   This gives no independent validation of the caller's intended meaning.

These arguments concern well-typed finite Python records in this research
fixture, not untrusted arbitrary host objects, serialized native authority,
authentication, or the entire Bootstrap Zero coordination theorem.

## Validation and reproducibility

Use the project test environment and run:

```sh
python -m pytest -q \
  tests/python/test_bootstrap_zero_whole_cut_grammar.py \
  tests/python/test_bootstrap_zero_cell_carrier_views.py \
  tests/python/test_bootstrap_zero_whole_cut_m6_bridge.py \
  tests/python/test_bootstrap_zero_production_ledger.py \
  tests/python/test_bootstrap_zero_retention.py
```

The first implementation pass returned **988 passed in 1.25 seconds**, with
two pytest deprecation warnings about passing iterator objects to parametrize.
Those finite iterators were materialized as tuples for compatibility; the case
family was unchanged. Ruff lint passed. Subsequent contract review found one
implementation overconstraint: every open hole had been required to have an
alternative family. That rule was corrected to permit unspecified candidates,
while keeping selection/declaration checks bound to their independent expected
records. The pre-review passing evidence is preserved separately, because a
passing suite did not establish that the intended contract was right. One new
control checks an unexplored hole without inferring nonexistence or closure.
The final replay, source hashes, raw
output, process cost and largest-child memory measurement are retained in
`experiments/whole_cut_retention/evidence.json`. No failing implementation-test
run occurred; there was no enlarged search or repeated CI waiting.

The new test family includes:

- both choices at each of the two open holes, with dropped/changed options,
  absent witness and attempted closed-circle negative controls;
- all 3^6 = 729 maps from six declared expansion points to three boundary
  points, with missing-fibre-member and omitted-map-entry controls;
- empty fibres, duplicate assignments, foreign targets, altered point types
  and wrong retraction boundaries;
- all five declarations, each challenged by five source-ledger omissions;
- missing/duplicate/wrong signatures, a fresh-name retraction packet, and
  fresh hole-name selection with refusal of stale expected-source reuse;
- the existing 203 source-partition cases and open-M6 boundary regressions.

No speedup, new arithmetic theorem or new vocabulary is claimed. Real,
additive-zero and multiplicative-unit semantics are unchanged. Peak child
memory is not aggregate system memory. Native Rust/full-workspace tests and
remote CI success are not claimed for this test-local change.

## Why the issue cannot close yet

| Original obligation | Result of this pass |
| --- | --- |
| Production accounting | In merged PR #162; regressions retained |
| Open-hole and alternative retention | Candidate implementation with independent expected-source checks |
| Retraction fibre retention | Candidate explicit finite-map accounting, rechecked on traversal |
| Five interpreter declarations | Candidate signature and complete-source preservation checks |
| Distributivity production and hole bindings | Still absent from the integrated whole-cut checker |
| Complete raw syntax formation | Remaining constructor, typed-name and boundary-witness coverage audit |
| Full coordination theorem | Not established by the component checks or their test count |

In particular, the original distributivity record must jointly retain its
source/target expressions, production ledger, hole bindings, thread ledger
and residuals. Existing distinct Plus/Tensor classes and successful scalar
distributivity examples do not discharge that obligation. The theorem must
cover every declared form, with accepted boundaries tied to the right source;
it cannot be obtained by relabelling this finite packet test as completeness.

The next smallest integrated step is one explicit distributivity formation
record and a countercase with a missing binding or undeclared duplicate
occurrence. Preserve both ordered expressions and do not promote their
arithmetic equality to an EquationCell. This is remaining work within #102,
not a new requirement for an interpreter body or semantic M6 filler.
