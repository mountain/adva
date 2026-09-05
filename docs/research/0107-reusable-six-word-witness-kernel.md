# Reusable Six-Word Witness Kernel

Status: bounded Rust research implementation. This note makes one corrected
six-word formation/execution proposal executable without changing PSC0 or
`adva.ir` version 1.

## 0. Corrected seed table

The registry contains exactly these declarations:

| term | type word | value word | retained ledger reading |
|---|---|---|---|
| `{}` | `[] > ()` | `() < []` | `[] -> ()` |
| `[]` | `() > {}` | `{} < ()` | `() -> {}` |
| `()` | `{} > []` | `[] < {}` | `{} -> []` |
| `\|` | `\|\|\|` | `1` | three unit slots, not one erased occurrence |
| `>` | `<\|>` | `+` | central unit slot |
| `<` | `>\|<` | `*` | central unit slot |

The formerly written first type word `[] > {}` is rejected: its oriented role
boundary differs from the value boundary `() < []`.

## 1. Two different normalizations

Formation is additive and relative to a declared external interface:

\[
A(P)=\partial_{\mathrm{actual}}P-\partial_{\mathrm{declared}}P.
\]

A component may enter `Instantiate`, `Compose`, or `Seal` only when `A(P)=0`.
This local precondition prevents two malformed children with opposite defects
from being accepted merely because their final scalar sum is zero.

Execution transport is multiplicative. For an exact transition from `p` to
`q`, V0 stores

\[
M(P)=\frac{\operatorname{poly}(q)}{\operatorname{poly}(p)}.
\]

The residual is one exactly when the two canonical sparse polynomials are
equal. `BigInt` coefficients avoid floating-point and fixed-width coefficient
overflow. Variable exponents remain bounded by `u32` in V0.

These judgments have different zeros. Formation zero is an accepted signed
boundary balance. A concrete arithmetic zero during execution is `ZeroFault`.
The final program value is not the transport residual and is not required to
equal one; it is only required to avoid the declared zero fault.

## 2. Why the printed `1` is insufficient

The seed

```text
| : ||| = 1
```

is represented with unit-slot support `[0,1,2]`. The scalar surface `1` is a
projection. Replacing its support by only `[1]` fails formation. Likewise the
values `+` and `*` retain their central witness slot `[1]` rather than becoming
bare host-language operators.

## 3. Reuse model

Reuse has three separate records:

| record | reusable content | deliberately fresh content |
|---|---|---|
| `CellTemplateV0` | ordered hole contract, result expression, body proof | none |
| `WitnessArtifactV0` | checked proof DAG node and exact `A/M` summary | none |
| `CellInstanceV0` | references the template and cached artifact | instance ordinal and existing occurrence bindings |

The store computes a BLAKE3 content key from canonical proof JSON. The key is
only a cache coordinate. Two instantiations may have the same artifact key and
still have different `InstanceIdV0`, `OccurrenceId`, and `OccurrencePath`
records. Equal keys therefore never imply equal programs.

Exactly three ordered holes are required. Their roles are a bijection over
construction, space, and time, their result variables each occur once, and one
semantic occurrence cannot fill two holes. Explicit sharing is represented by
distinct checked occurrences that may retain the same source.

The type-state path is

```text
CellTemplateV0 --A=0--> FormedCellV0
    --fresh bindings--> CellInstanceV0
    --M=1, guards--> ExecutedCellV0
```

## 4. Proof DAG

`WitnessProofV0` has five nodes:

- `Seed`, checked against the single six-word registry;
- `ArithmeticTransition`, which derives relative `A` and exact `M`;
- `Instantiate`, which cites one template artifact and three formed children;
- `Compose`, which cites left, connector, and right formed components; and
- `Seal`, which requires both additive zero and multiplicative one.

Dependencies must already exist on ordinary insertion. A separate graph
validator rejects missing dependencies and cycles in imported graphs.

## 5. Concrete zero discipline

Symbolic nonzero and concrete nonzero are different. A nonzero polynomial can
still vanish under a particular hole environment. Each arithmetic transition
therefore retains its before/after expression trees as runtime obligations.
Evaluation is strict at every visited node. For example, with

```text
(x + y) + z
```

the environment `x=1,y=-1,z=2` faults at the inner addition even though the
outer mathematical result would be two.

## 6. Executable evidence

The Rust tests check:

1. all corrected seeds and their exact surfaces;
2. rejection of the old typo and collapsed unit multiplicity;
3. exact distributive polynomial normalization;
4. reuse of one proof artifact by fresh instances and occurrences;
5. rejection of implicit occurrence aliasing;
6. concrete intermediate-zero failure;
7. rejection of non-unit execution transport;
8. rejection of nonzero relative formation residuals before composition;
9. proof-DAG cycle rejection; and
10. linear use of the three template variables.

## 7. Boundary of the result

This implementation is not a parser for the six glyphs, a stable type system,
an extension of `ProgramTerm`, a new builtin-operation registry, a general
interpreter, a specializer, or a proof of universality. Commutative polynomial
normalization is an exact witness observation; it does not erase ordered
syntax, sources, occurrences, graft paths, or history, and it does not create
an equation cell.

The first part of the next engineering decision is implemented by the bounded
adapter in
[`0108-graft-derived-witness-instantiation.md`](0108-graft-derived-witness-instantiation.md):
instances may derive their occurrence bindings from an existing certified
three-hole `GraftTrace` frame. `ProgramTerm`, exact runtime arithmetic, and
merged-lineage selection remain deliberately unresolved.
