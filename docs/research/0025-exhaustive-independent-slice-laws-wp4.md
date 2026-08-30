# Exhaustive Program-Slice Laws on an Independent Diamond

Status: bounded finite Rust verification for WP4 of the program-slice phase.
It exhausts one nontrivial causal partial order using exact structural data. It
does not turn a schedule into part of `ProgramSlice`, prove a new unrestricted
theorem, or construct a dual grid or `P*`.

## Fixture

The checked binder-free program is

```text
add(frontier(neg(left), id(right)))
```

Its original diagram order is `neg = 0`, `id = 1`, `add = 2`. The first two
events are independent, and the final event depends on both. Its complete
causal-past lattice is therefore

```text
empty, {0}, {1}, {0,1}, {0,1,2}.
```

Rust rederives and certifies every one of these five cuts. No scalar value is
evaluated.

## Exhaustion

The test enumerates the complete finite families below, including identity
intervals:

| Family | Exact count | Checked law |
|---|---:|---|
| Downward-closed pasts | 5 | certified causal cut |
| Nested pairs `U <= V` | 14 | certified canonical slice |
| Nested triples `U <= V <= W` | 30 | adjacent composition equals direct outer slice |
| Nested quadruples `U <= V <= W <= X` | 55 | both parenthesizations equal each other and the direct outer slice |

All comparisons are literal equality of Rust `ProgramSlice` data. Consequently
nodes, wires, sources, occurrences, lineage, histories, and boundaries are
compared without a numerical observation or tolerance.

## Schedules are not slices

There are two linear schedules:

```text
0, 1, 2
1, 0, 2
```

Both are checked step by step with `advance_causal_cut`. Their first
intermediate cuts differ, so their path histories remain distinct. Their final
cut and direct whole slice agree because they are two linear extensions of the
same causal partial order.

The second schedule exposes a necessary distinction. Its first two one-event
slices have event vectors `[1]` and `[0]`. Concatenation would produce `[1,0]`,
but exact composition produces `[0,1]`, the unchanged diagram's canonical
order. Thus

\[
\text{schedule word} \neq \text{canonical event vector of a causal interval}.
\]

`ProgramSlice` is correctly an interval of the common partial order. A future
object that must retain a chosen execution route needs an explicit schedule or
path field; that information cannot be reconstructed from the outer slice.

## Effect on the motivating factorization

The finite candidate for `S` is strengthened: exact program intervals form a
category-like same-diagram composition law on every interval of this
independent fixture, with exact units and associativity.

The result does not strengthen the missing synthesis side. A bare outer slice
forgets which linear extension was taken, while graft intersections remain
partial and overlapping and zero-event frames still have no nonempty
node-region intersection. Therefore this exhaustion supplies neither a total
scope/cut correspondence nor `P*`, and it does not establish
`T = P S P*`.
