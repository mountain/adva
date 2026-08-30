# Relational `P S P*` on an Ordered Two-Hole Frame

Status: bounded finite calibration following the zero-event scope/cut no-go.
It verifies one exact relational factorization over Rust-certified data. It is
not a stable relation API, a general theorem for arithmetic transformations,
or a canonical dual-loop construction.

## Ordered substitution fixture

Let `F` be the compiler graft frame for the zero-operation two-hole program

```text
ordered-pair(left, right) = frontier(left, right)
```

used in parallel with one independent `neg(z)` event. The frame retains the
ordered holes

\[
((0,\mathrm{left}),(1,\mathrm{right})),
\]

two distinct entry wires, and the identical ordered exit wires. Its argument
and body node regions are empty.

As in the preceding no-go, both causal cuts

\[
c_0=\varnothing,
\qquad
c_1=\{\mathrm{neg}\}
\]

contain every frame boundary wire.

## Incidence maps

Define the test-local relation

\[
P^*\subseteq\{F\}\times\{c_0,c_1\}
\]

by exact boundary compatibility. Therefore

\[
P^*=\{(F,c_0),(F,c_1)\}.
\]

Let `P` be its relational converse. No hole name, hole order, frame identity,
wire identity, or cut identity is quotiented.

The Rust-certified causal step supplies contraction

\[
S_- = \{(c_0,c_1)\},
\]

and its exact relational converse supplies expansion

\[
S_+ = \{(c_1,c_0)\}.
\]

With composition read from right to left in the conventional formula, the
test computes

\[
P\,S_-\,P^*=\operatorname{id}_{F}
\qquad\text{and}\qquad
P\,S_+\,P^*=\operatorname{id}_{F}.
\]

The transformed scope `T` is the identity on the ordered two-hole
presentation. The nontrivial cut surgery is internal to its incidence fibre.

## Why a point selector fails

Replace `P*` by either the earliest singleton `{(F,c0)}` or the latest
singleton `{(F,c1)}`, and take its converse for `P`. Neither contraction nor
expansion closes back to `F`: the surgery leaves the selected point and the
converse has no arrow from the other cut.

Thus the full incidence fibre is not decorative redundancy. It is the least
support closed under both directions of the characteristic surgery.

## What is established

This gives the first literal finite equality of the requested shape, after
weakening maps to relations:

\[
T=P S P^*.
\]

It respects ordered hole names and exact substitution-frame identity. `S` is
derived from a checked causal cut step rather than a numerical evaluation.

What remains open is substantial:

- `T` here is the identity scope transformation;
- the frame is zero-event and the surgery is independent of its holes;
- no canonical E0 cellular dual is constructed in this fixture;
- no theorem covers nonzero, nested, or overlapping frames;
- relational converse has not been justified as the final semantic meaning of
  `P`; and
- equality is finite set equality in a test-local relation calculus, not a
  promoted kernel judgment.

The next useful test is a nonzero multi-hole frame whose characteristic
surgery crosses its own body, followed by relational composition of nested
frames. Failure there would identify whether incidence alone is sufficient or
whether boundary orientation and frame-role decorations must also enter
`P*`.
