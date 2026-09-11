# Independent reproduction of the quotient criterion, and its first checked instantiation

Date: 2026-09-11. Direction: Mingli Yuan. Reading, implementation and check:
assistant (DeepSeek Harness), submitted through his account as an authorized
proxy.

Status: bounded native test, run by `cargo test`. It adds no stable API, no
claim entry and no native semantic change.

Base: `c2132ef` (the correction commit). This note continues
[the correction](triadic-period-bridge-correction.md) rather than restating it.

## 1. What was reproduced

That correction makes the quotient criterion executable: for a finite total map
`F` on `S` and a surjection `q: S -> Y`, a map `g` with `q F = g q` exists
exactly when `q(s) = q(t)` implies `q(F(s)) = q(F(t))`.

`crates/adva-lisp/tests/observer_quotient_descent.rs` re-implements that
criterion and reproduces the four fixture tables the correction publishes. This
is a cross-implementation check: a second implementation, in a different
language, on the same inputs, with the same published outputs.

| Fixture | `F` | `q` | Published result | Reproduced |
|---|---|---|---|---|
| Failed descent | `[0,2,2,3]` | `[0,0,1,1]` | no descent | yes, conflicting pair `(0,1)` |
| Non-injective quotient | `[2,3,2,3]` | `[0,0,1,1]` | `g=[1,1]` | yes |
| Two-cycle quotient | `[2,3,0,1]` | `[0,0,1,1]` | `g=[1,0]` | yes |
| Finite three-cycle quotient | `[2,3,4,5,0,1]` | `[0,0,1,1,2,2]` | `g=[1,2,0]` | yes |

The reimplementation also rechecks the commuting equation on every state after
building `g`, instead of inferring it from the pairwise test, and the failing
fixture retains its conflicting pair rather than an invented image.

Two refusal controls show the test is not vacuous in either direction: a
surjection that does not descend still fails (many-to-one is not sufficient), and
a constant observation descends for a step that the non-constant observation
rejects.

## 2. What was added beyond reproduction

The correction's last section names the next admissible bridge: applying the
criterion to an Adva example needs a declared checked carrier, a one-step
transition, an observation `q`, a reachable domain, and an explicit forgotten
residual. Four of those five already exist in the checked kernel, and the test
reads exactly those:

| Binding | Where it comes from | Present |
|---|---|---|
| checked carrier | `TriadicObserverTransitionV0::slice`, a checked `ProgramSlice` (`crates/adva-ir/src/process.rs`) | yes |
| one-step transition | the checked `lineage_links` between the lower and upper cut incidences | yes |
| observation `q` | the role label of each lower incidence, from `TriadicCutIncidenceV0::domain`, assigned by the declared `TriadicObserverPolicyV0` | yes |
| reachable domain | computed from the lineage relation, not stored | computed here |
| explicit forgotten residual | `source_free_wire_indices` on both cuts, retained rather than omitted | present as a field, empty for this fixture |

So the missing binding is not a type. Reachability is a derived finite set, and
the test derives it and asserts that reachable and unchecked incidences partition
the lower cut exactly.

## 3. What the instantiation established

On the `triadic-flow` fixture (three declared input roles, one branching step),
with the observation read from checked data:

- **The role label descends, and descends to itself.** Each lower incidence
  carries its own role to its image. The reason is structural rather than
  numerical: a role label is a function of the input-source fibre, and the
  checked lineage relation preserves source identity. So the per-incidence
  observer reading is conserved by one step.
- **The cut-level reading does not descend.** The two cuts have three and four
  incidences, and the branch is a checked copy, so no map between the
  incidence-index readings of the two cuts can be bijective. The per-incidence
  reading descends while the reading of the whole cut does not, and the
  difference is entirely a matter of what is taken to be one observation.
- **Recorded exactly, and not asserted as a partition tautology.** The fixture
  has `reachable = 3` and `unreachable = 0`, images `[{0},{1},{2}]`, and empty
  source-free sets on both cuts with three frontier wires each. The test asserts
  those numbers rather than only the identity that they sum to the lower count.

## 4. What this does not establish

- **This fixture does not exercise the forgotten-residual binding.** Every lower
  incidence is carried across the step, so nothing is unchecked, and both
  source-free sets are empty. A non-empty source-free residual is exercised by a
  different fixture, in the sibling test
  `triadic_transition_retains_source_free_wires_outside_all_three_views`; this
  note does not extend that result.
- **No period, cycle or chaos statement is made about any Adva object.** The
  descended map is a finite role-label map. Least period is not computed here,
  and the correction's own warning applies unchanged: a fixed point of `F` cubed
  is not thereby a point of least period three, and a phase-tagged stage map is
  not a full-cycle return map.
- **No quotient of a checked diagram is constructed.** What descends is a
  reading of already-derived incidences, not a new diagram, slice or program
  transformation. No native identity is allocated, merged or forgotten.
- The direction is one step. Nothing here composes descent across adjacent
  steps, and nothing here supplies the transport, holonomy or entropy structure
  the correction leaves open.

## 5. Reproduce

```sh
cargo test -p adva-lisp --test observer_quotient_descent
```

Four tests, no fixtures beyond the module source embedded in the file, and no
external service, path or data dependency.
