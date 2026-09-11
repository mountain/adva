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
fixture retains its conflicting pair rather than an invented image. Two refusal
controls keep it from being vacuous in either direction: a surjection that does
not descend still fails, so many-to-one is not sufficient, and a constant
observation descends for a step the non-constant observation rejects.

## 2. The five bindings, and which of them exist

The correction's last section names the next admissible bridge: applying the
criterion to an Adva example needs a declared checked carrier, a one-step
transition, an observation `q`, a reachable domain, and an explicit forgotten
residual. Four of the five already exist in the checked kernel, and the tests
read exactly those rather than inventing new ones:

| Binding | Where it comes from | Present |
|---|---|---|
| checked carrier | `TriadicObserverTransitionV0::slice`, a checked `ProgramSlice` | yes |
| one-step transition | the checked `lineage_links` between the lower and upper cut incidences | yes |
| observation `q` | read from `TriadicCutIncidenceV0::domain` under the declared `TriadicObserverPolicyV0` | yes |
| explicit forgotten residual | `source_free_wire_indices` on either cut, retained rather than omitted | yes, and non-empty cases exist |
| reachable domain | derived from the lineage relation, not stored | derived here |

So the missing binding was never a type. Reachability is a derived finite set.

## 3. The declared step family

`triadic-flow` has six checked nodes — `constant, discard, copy, add, id, id` —
and the tests declare a family of nested cuts over them
(`[], [0], [0,1], [0,1,2], all`). Fourteen of the pairs are admitted as
transitions. Every admitted step has a **non-empty lower cut** carrying three
input sources, so unlike the composition fixture used elsewhere, nothing here is
vacuous on the lower side.

## 4. What the instantiation established

**Reading one, the role set, descends and is degenerate.** Which roles a cut
carries, as a three-bit mask, descends on every step of the family, and it
descends to itself. The reason is structural rather than numerical: a role label
is a function of the input-source fibre and the checked lineage relation
preserves source identity. So the per-incidence observer role is conserved by one
step.

**Reading two, the role counts, does not descend.** The number of incidences of
each role is a different reading of the same checked data, and it fails. The
retained conflicting pair is two admitted steps that share a lower reading and
differ in the upper one:

| Step | Lower counts | Upper counts | Lineage links |
|---|---|---|---|
| `[] -> [0,1]` | `[1,1,1]` | `[1,1,1]` | 3 |
| `[] -> [0,1,2]` | `[1,1,1]` | `[2,1,1]` | 4 |

The duplication is in the temporal role, and it is the fixture's checked `copy`
rather than a recount. This is a real obstruction read out of checked data, and
it has the same shape as the correction's published failing fixture. The two
readings differ only in whether a duplicated role is counted once or twice, which
is the correction's own point that the choice of observation decides whether
descent exists.

**Composition is satisfied, and this fixture cannot test it.** Descending the
composed transition `[] -> [0,1,2]` gives the same map as descending its two
stages, so the law holds. But every descended map this fixture admits is the
identity, so a wrong composition would agree as well. That limitation is asserted
in the test rather than left as an impression: a fixture able to discriminate
composition needs an observation that is not source-determined.

**A residual on the observation side is exercised.** For the step `[0] -> [0,1]`
the **lower** cut carries one source-free wire — that is, the residual sits on the
side where the observation is taken, not on the far side. The cut has four wires
and three source-carrying incidences, no chart claims the free wire, and the
reading that descends still descends, because the residual carries no incidence
for the observation to see. This is the binding the earlier fixture could not
exercise, and it is now exercised on a non-empty cut.

## 5. What this does not establish

- **No period, cycle or chaos statement is made about any Adva object.** The
  descended maps are finite role readings. Least period is not computed, and the
  correction's warning applies unchanged: a fixed point of `F` cubed is not
  thereby a point of least period three, and a phase-tagged stage map is not a
  full-cycle return map.
- **No quotient of a checked diagram is constructed.** What descends is a reading
  of already-derived incidences, not a new diagram, slice or program
  transformation. No native identity is allocated, merged or forgotten.
- **One fixture and one declared cut family.** The counts obstruction and the
  composition limitation are properties of this fixture's declared family; they
  are not theorems about checked transitions in general, and no second fixture
  was tried for either.
- **Composition is checked on one two-stage path**, not across an arbitrary
  chain, and not against a fixture that can discriminate it.
- Nothing here supplies the transport, holonomy or entropy structure the
  correction leaves open.

## 6. Reproduce

```sh
cargo test -p adva-lisp --test observer_quotient_descent
```

Seven tests, no fixtures beyond the module source embedded in the file, and no
external service, path or data dependency.
