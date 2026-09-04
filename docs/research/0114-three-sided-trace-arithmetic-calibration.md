# Three-Sided Trace-Arithmetic Calibration

Status: executable research experiment; truth fiber remains open

## 1. Question

Can semantic drift be narrowed from time, space, and construction at once
without imposing a unique threading order?

The experiment starts from the persisted first reveal witness. Its two raw
positive paths remain distinct:

```text
left   compute verify compute
right  verify compute verify
```

The existing `M6` formation certificate admits this boundary. It does not say
that the sides have the same execution, interpretation, provenance, or truth.

## 2. Three direct projections

The output retains both paths and derives these codes independently.

| side | coordinates | left minus right | state |
|---|---|---:|---|
| time | frames, causal handoffs, transferred ports | `(0, 0, 0)` | matched |
| space | labelled start and end carrier IDs | all zero | matched |
| construction | compute, verify, learn, length, alternations | `(+1, -1, 0, 0, 0)` | diverged |

These are path-to-side projections, not the stronger cross-side equations:

```text
T = chi_T(S, C)
S = chi_S(C, T)
C = chi_C(T, S)
```

All three `chi` witnesses remain open in version zero. The zero time and space
residuals therefore cannot be promoted into semantic compatibility.

## 3. Additive and multiplicative readings

The additive residual is a product of typed ledgers rather than one integer.
`+1 compute` cannot cancel `-1 verify`, and neither can cancel a time or space
coordinate.

With symbolic commutative mechanism weights, the paths normalize to:

```text
left   mechanism.compute^2 * mechanism.verify
right  mechanism.compute   * mechanism.verify^2
```

Their `right / left` residual is not one. This does not contradict positive
braid `M6` formation: it shows that the naive independent commutative-weight
map does not automatically descend through that relation. A holonomy witness
or a more appropriate target algebra is required.

Zero during a future evaluated multiplicative expression remains an execution
fault under the existing guarded arithmetic. This calibration stays symbolic.

## 4. Order and arithmetic collisions

`compute verify compute verify` and `verify compute verify compute` have the
same mechanism incidence, length, and alternation count, while their ordered
words remain different. Arithmetic projection is therefore useful for
candidate lookup and partitioning, not for unique threading, trace identity,
or proof. Exact paths and BLAKE3 coordinates remain beside the projections.

## 5. Truth fiber

The output truth fiber remains `open` with no shared truth coordinate. A later
witness must place both readings over one explicit truth coordinate and
discharge the relevant cross-side and holonomy obligations. An external-world
claim also needs a versioned observation anchor and trust policy.

## 6. Reproduction

```bash
cargo run -p adva-witness --bin adva -- \
  trace-arithmetic programs/bootstrap-0/first-reveal-witness.adva \
  --output target/first-trace-arithmetic.adva \
  --print
```

The command loads only the persisted reveal witness. Its output retains source
digests, both paths, three projections, typed additive residual, commutative
holonomy, five questions, and the open truth fiber.

## 7. Nonclaims

This experiment does not define the three `chi` maps, prove semantic
compatibility, authenticate an observation, select a global naming scheme,
make the two `M6` words inverses or conjugates, find canonical threading,
execute mechanisms, or turn document-local coordinates into global identities.
