# Source-bound WholeCut6 distributivity formation

Date: 2026-10-14. Base source:
`cd10e3e31fa149a3039037fb4a55c67d610b8ce5`.

This is the first finite implementation step from
[Issue #102](https://github.com/mountain/adva/issues/102) and
[note 0102, section 10](0102-bootstrap-zero-whole-cut-grammar.md).
It extends the research-test-local whole-cut checker. It introduces no native
operation, semantic identity, arithmetic equation, EquationCell or stable API.
Issue #102 remains Open for complete constructor/boundary coverage and the
syntax-only coordination theorem; this result is not full Bootstrap Zero
completion.

## Question, source and bounded contract

Can one named record retain both ordered distributivity-shaped expressions,
exact allocation and binding data, and the source's thread/residual data while
rejecting incomplete bindings, undeclared repeated occurrences and substituted
sources?

The input authority is an independently supplied `WholeCut6` and an ordered
three-hole boundary. The candidate contains its claimed source and boundary,
but `_validate_distributivity(expected, boundary, witness)` compares those
claims with the caller's inputs rather than recovering trusted inputs from
the candidate. `_validate_whole(expected)` rechecks the existing production,
port, hole, alternative and residual requirements. Source equality retains
the whole source, including data outside the three selected holes.

This trial uses project-original finite fixtures and the already checked
research-local production and retention components. There are no imported
external mathematical assumptions, external research inputs, scalar values or
cross-domain equivalence claims.

The checker is direct finite checking, with no candidate search or automatic
continuation. Recursive AM formation has a maximum of 256 visited syntax
positions and depth 32 per expression; raw thread formation has a maximum of
256 steps per word. A repeated host AST is counted at each syntax position.
Exceeding these limits is an explicit formation failure for this bounded
profile, not a theorem that the larger expression is impossible. The trial
fixtures have six port occurrences, four open holes/residuals, seven binding
positions and one two-step thread word. The executed test family is fixed;
there is no unbounded outer search.

## The integrated record

`DistributivityRecord` retains:

- its name and complete independently checked source;
- the exact ordered three-hole boundary;
- source and target AM expressions;
- the entire ordered source production ledger;
- seven ordered, typed hole bindings indexed by expression and tree position;
- the entire source through-channel/thread ledger; and
- the entire ordered source residual ledger.

The expressions have these raw shapes:

```text
source: tensor(hole A, plus(hole B, hole C))
target: plus(tensor(hole A, hole B), tensor(hole A, hole C))
```

Their equality with the required shapes is structural formation checking.
It is not evaluation or a proof of arithmetic distributivity.

The binding record gives a declared `Use(source, occurrence, value_type)` at
each hole position:

| Expression position | Hole | Required use |
| --- | --- | --- |
| source `(0,)` | A | Source boundary's A occurrence |
| source `(1, 0)` | B | Source boundary's B occurrence |
| source `(1, 1)` | C | Source boundary's C occurrence |
| target `(0, 0)` | A | The same first A occurrence |
| target `(0, 1)` | B | The same B occurrence |
| target `(1, 0)` | A | Another explicitly allocated A-source occurrence |
| target `(1, 1)` | C | The same C occurrence |

The repeated A has the same declared source and type as the first A, but its
occurrence is distinct from all three source-expression occurrences. All four
target occurrences must be distinct. Every use is checked against the source
port ledger and its complete production ledger. A candidate cannot invent the
extra occurrence or authorize allocation by naming it.

In this first fragment the extra A occurrence is already explicitly allocated
in the caller's source. The record checks that allocation; it does not perform
copying or allocate a native identity. Reuse of the first A/B/C labels across
the two presentations is checked view correspondence, not a second execution.
The fourth open hole, associated with the extra A allocation, remains in the
source hole/residual ledger. No hole binding adds a through edge, selects an
alternative or closes the source.

The source fixture has a nonempty ordered thread word with separately named
crossings at gaps 1 and 4, respectively `over` and `under`. `ThreadStep` keeps
crossing marks separate from incidence polarity and motion. Step names, exact
integer gaps, the crossing alphabet and the finite word budget are checked.
The witness retains the complete channel records and word order. This is raw
thread-history retention; the new checker neither executes a braid quotient
nor proves cancellation or equality of braid histories. Empty words remain
allowed for continuity with earlier raw fixtures.

## Recursive AM formation and repaired controls

`AMTerm` now includes typed `Hole` and `Use` leaves. `_validate_am` walks every
nested constructor, checks nonempty leaf names, source-bound hole/use payloads
and the finite budget, and rejects an occurrence used twice within one AM
expression. It is called for alternative bodies and both witness expressions.
It does not supply general AM type inference or interpret the constructors.

The three malformed forms accepted by the 2026-10-14 audit are now rejected:

| Historical accepted probe | New failure |
| --- | --- |
| Empty `WholeCut6.name` | Nonempty carrier name required |
| Channel `motion = "invalid"` | Declared Motion alphabet required |
| Alternative `Plus(object(), Atom("B"))` | Unsupported constructor at a recursive position |

The added negative controls also reject each of the seven individually omitted
bindings, reordered or altered bindings, B/C exchange, occurrence reuse,
invented occurrences, omitted/reordered production entries, candidate source
replacement, lost alternatives/holes/residuals, lost or reordered thread words,
wrong typed references, malformed thread steps and exceeded finite budgets.
A second fixture with fresh names is checked against its own independently
supplied source; it cannot inherit acceptance against the first source.

## Review finding and correction

A separate read-only Codex review found one false acceptance in the first
candidate: positions `(False,)` and `(0.0,)` compared equal to `(0,)` under
Python tuple equality. This was a checker error despite the then-passing
suite. The correction requires an exact tuple of exact integer coordinates
before position comparison. Boolean, float and list-coordinate controls now
execute and are rejected. The initial Ruff check also reported long lines;
formatting corrected those findings before the final checks.

The review also identified remaining pre-existing WholeCut6 name coverage:
an empty channel name and an empty residual name retained in both
`OpenPort.residual` and `WholeCut6.residuals` can still pass the old outer
formation rules. They remain part of Issue #102's complete
typed-name/boundary audit. This implementation does not claim complete grammar
formation or discharge note 0102 section 15.

## Executed verification

Source implementation and controls:

- [integrated checker](../../tests/python/test_bootstrap_zero_whole_cut_grammar.py);
- [distributivity replay and negative controls](../../tests/python/test_bootstrap_zero_distributivity_record.py).

Local Python 3.12.14 / pytest 8.4.2 replay, using isolated dependencies outside
the repository:

```sh
python -m pytest -q tests/python/test_bootstrap_zero*.py -p no:cacheprovider
```

**1063 passed in 1.10 seconds**: the existing 1036 cases and 27 new cases.
Ruff check and formatting passed for the two changed Python files. The new
module contains its valid witnesses and executable negative controls; no
historical evidence payload was rewritten.

The dedicated remote [run 38528818098](https://github.com/mountain/adva/actions/runs/38528818098)
at candidate `64fee9fd322d357f05acaf0841b3258979341b14` also passed.
The actual [Python job log](https://github.com/mountain/adva/actions/runs/38528818098/job/115735469787)
records Python 3.12.15, Ruff lint/format success and **1063 passed in 1.78s**.
This is a new remote targeted replay; complete repository CI is a separate gate
and later heads do not inherit success. A root integration replay independently
returned 1063 passed in 0.95s on Python 3.12.14.

No full Rust workspace build, full-workspace replay or interpreter-body
implementation is claimed by the local/targeted verification above.
The next step is to finish the remaining constructor/typed-boundary coverage
and then state the accepted finite domain and per-constructor coordination
argument. An M6 semantic filler is not an added closure requirement.

Direction: Mingli Yuan. Implementation, analysis and report: Codex (OpenAI),
submitted through Mingli Yuan's GitHub account (`mountain`) as an authorized
proxy. A separate Codex agent performed the read-only check described above;
Mingli did not perform that review. Account use is not personal authorship,
endorsement or a correctness guarantee. Project-original additions contributed
under Unknown v0.3; no third-party text or code imported.
