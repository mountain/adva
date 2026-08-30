# Nonzero Ordered-Frame Relational `P S P*`

Status: bounded finite calibration of the first arithmetic frame whose
characteristic surgery crosses its own body. It uses exact Rust graft, cut,
step, and slice data. It does not install stable `P`, `P*`, relation, dual
cycle, or pullback types.

## Fixture

The nonzero two-hole callee is

```text
add-two(left, right) = add(frontier(left, right)).
```

The root calls this frame on ordered arguments `x,y` and places one independent
`neg(z)` beside it. Lowering produces two independent events:

\[
e_0=\operatorname{add},
\qquad
e_1=\operatorname{neg}.
\]

The call frame records:

- ordered holes `((0,left),(1,right))`;
- two unchanged argument-producing regions with no nodes;
- body region `{e0}`;
- two entry wires consumed by `add`; and
- one different exit wire produced by `add`.

The complete cut lattice is the Boolean square

\[
\varnothing,
\{e_0\},
\{e_1\},
\{e_0,e_1\}.
\]

## Failure of unpolarized incidence

Because checked wires are linear, no cut contains both all entry wires and the
exit wire. Before `add`, the exit does not yet exist; after `add`, its entry
wires have been consumed.

Therefore the zero-event definition

\[
F\;R\;c
\quad\Longleftrightarrow\quad
\text{entry}(F)\cup\text{exit}(F)\subseteq c
\]

has empty support for this genuine nonzero frame. A scope/cut relation must be
polarized by boundary role.

## Polarized incidence

Let `X_F` be the intensional input expression retaining the frame ID, ordered
hole names, and exact entry wires. Let `Y_F` retain the same frame ID, body
event, and exact exit wire.

Define

\[
P^*_{\mathrm{in}}:X_F\rightsquigarrow\operatorname{Cut}(P)
\]

by entry compatibility. The independent `neg` gives two supported lower cuts:

\[
P^*_{\mathrm{in}}
=
\{(X_F,\varnothing),(X_F,\{e_1\})\}.
\]

Define

\[
P_{\mathrm{out}}:\operatorname{Cut}(P)\rightsquigarrow Y_F
\]

by exit compatibility:

\[
P_{\mathrm{out}}
=
\{(\{e_0\},Y_F),(\{e_0,e_1\},Y_F)\}.
\]

The body surgery consists of the two parallel checked advances

\[
S_{e_0}
=
\{(\varnothing,\{e_0\}),(\{e_1\},\{e_0,e_1\})\}.
\]

Finite relation composition then gives the literal equality

\[
T_{\mathrm{add}}
=
P_{\mathrm{out}}\,S_{e_0}\,P^*_{\mathrm{in}},
\]

where `T_add` maps the exact ordered input expression to the exact body-output
expression.

Reversing all three relations yields

\[
T_{\mathrm{add}}^{\mathrm{op}}
=
P_{\mathrm{in}}\,S_{e_0}^{\mathrm{op}}\,P^*_{\mathrm{out}}.
\]

Thus contraction and expansion exchange input/output boundary roles. This is
the first exact finite appearance of the expected chirality.

## Slice agreement

Both body paths,

\[
\operatorname{Slice}(\varnothing,\{e_0\})
\quad\text{and}\quad
\operatorname{Slice}(\{e_1\},\{e_0,e_1\}),
\]

retain the same original `add` node and the same graft-frame intersection:
empty argument-event lists and body event `{e0}`. Their whole cuts differ only
by the independent `neg` context.

This confirms that the concurrency fibre is not an accidental relabeling. It
is exact context around one unchanged frame-local transformation.

## Consequence for the model

The notation `P S P*` is viable in this bounded case, but `P` and `P*` cannot
be understood as one unpolarized relation and its converse. They are
boundary-polarized synthesis and analysis incidences:

\[
P^*_{\mathrm{in}}
\quad\text{and}\quad
P_{\mathrm{out}}.
\]

Only after reversing the transformation do their opposite-polarity converses
appear.

The next obstruction test is nesting. Parent and child graft frames overlap on
body events, so naive relational composition may double-count a surgery or
lose whether an event belongs to an argument region or callee body. Nested
factorization must retain `GraftRegionRole` and exact frame path, not just frame
membership.
