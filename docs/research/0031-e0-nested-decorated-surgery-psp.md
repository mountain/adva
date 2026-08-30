# Nested Graft Roles on Finite E0 Dual-Face Surgeries

Status: bounded finite calibration joining the earlier E0 dual-cut model to the
nested relational `P S P*` model. It uses one declared six-edge projective
chart, exact Rust cuts, slices, and graft frames, and Python finite relations.
It is not a canonical E0 grid, planarization theorem, stable pullback, or
unrestricted factorization theorem.

## One common checked carrier

The fixture wraps the existing causal diamond

```text
copy -> {neg, id} -> add
```

inside the nested call chain

```text
root -> wrapper -> diamond -> add-two.
```

`wrapper` and `diamond` are ordered two-hole frames. Their body regions are
the same original events `{neg,id,add}`. The `add-two` frame contains `neg`
and `id` in ordered argument regions 0 and 1, and `add` in its body. Thus one
checked DAG simultaneously carries:

- the two legal schedules `neg,id,add` and `id,neg,add`;
- exact ordered substitution scopes and nested region roles; and
- the declared cellular dual used by the earlier E0 cut calibration.

No recompilation or value equality is used to identify the carriers.

## The two finite grids

Reuse the bounded projective point frame

\[
G=\{-2,-1,0,1,2,\infty\}
\]

in oriented homogeneous coordinates and its exact image

\[
J(G),\qquad J(X,Y)=(-Y,X),\qquad z\mapsto -1/z.
\]

The six checked wire identities are paired bijectively with the six points of
`G`; the corresponding cellular-dual edges retain the `J(G)` labels. This is
a declared finite edge chart. The test verifies pointwise that every dual
label is exactly the oriented `J` lift and that both projective label sets are
injective. It does not derive the cellular embedding from projective geometry.

## One decorated surgery per event

For an enabled event `e`, let `partial e*` be the mod-two boundary of its dual
face. The cut transition remains the symmetric difference

\[
C' = C\mathbin{\triangle}\partial e^*.
\]

The new decoration attached to this one surgery is the ordered list

\[
\mathcal R(e)
=
\bigl(
  \text{frame ID},
  \text{scope path},
  \text{region in parent},
  \text{event region}
\bigr)
\]

over every intersecting compiler frame. `event region` distinguishes `body`
from `argument:0`, `argument:1`, and so on. For each body event, the test
compares this list against the exact graft intersections of the adjacent
Rust `ProgramSlice`.

The event is not copied when several frames contain it. Frame overlap is
decoration on one NodeId-indexed face surgery.

## Characteristic expression and gluing

After `copy`, the body has the two decorated surgery words

\[
S_1=S_{\mathrm{neg}}S_{\mathrm{id}}S_{\mathrm{add}},
\qquad
S_2=S_{\mathrm{id}}S_{\mathrm{neg}}S_{\mathrm{add}}.
\]

The words are distinct schedule traces, but their independent first two face
toggles commute and produce the same final decorated cut. Every word contains
each original body event once.

Splitting the first word after `neg` gives two adjacent exact slices with
event sets `{neg}` and `{id,add}`. Rust composition equals the direct outer
slice, and applying the corresponding decorated surgery subwords gives the
same final dual state. Hence slice gluing and dual-face gluing agree on this
fixture without counting the nested frame overlap twice.

## Polarized relational factorization

Let the input expression retain the complete call-frame stack, exact paths,
parent roles, ordered holes, and wrapper entry wires. Let the output
expression retain the same stack, the body NodeIds, and wrapper exit wire.
`P*_in` relates the input expression to the checked decorated cut immediately
after `copy`; `P_out` relates the terminal body cut to the output expression.

Both schedule words induce the same finite characteristic relation `S`, and
exact set composition gives

\[
T
=
P_{\mathrm{out}}\,S\,P^*_{\mathrm{in}}.
\]

Taking relational converses of all three factors gives the exact reverse
expansion.

## What advanced, and what did not

This closes the specific bridge left open by the preceding calibrations:

- `S` is now literally realized by contraction/expansion of cycles on the
  declared cellular dual;
- each surgery carries every intersecting nested frame role;
- overlapping frames do not duplicate causal content; and
- adjacent decorated surgeries compose with exact same-diagram slices.

The remaining obstruction is no longer whether these ingredients can coexist
on a nontrivial finite example. It is canonicity and generality. The repository
still has no theorem constructing the cellular dual from an arbitrary E0
grid embedding, no oriented integer-chain replacement for the mod-two toggle,
no total treatment of zero-event frames, and no native `P`, `P*`, or `S` type.
Those are the next obligations before promoting the formula beyond bounded
research evidence.
