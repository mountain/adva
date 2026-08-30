# Nested Frames Glue One Shared Surgery

Status: bounded finite calibration of relational `P S P*` under one nested,
overlapping call-frame pair. It uses exact Rust frame paths, region roles,
events, cuts, and slices. It is not a stable nerve, sheaf, descent, dual-cycle,
or factorization API.

## Nested fixture

The root calls

```text
wrapper(left, right) = call add-two(left, right)
```

and `add-two` performs the single body event

```text
add(frontier(left, right)).
```

An independent `neg` supplies the same Boolean concurrency square as the
preceding nonzero calibration.

The compiler graft trace contains two call frames:

1. the parent frame for `wrapper`;
2. the child frame for `add-two`, whose exact `region_in_parent` is
   `callee_body`.

Both frames have body region `{add}` and the same entry and exit wires. This is
intentional overlap, not duplicated program content.

## The double-counting obstruction

Let

\[
S_{\mathrm{add}}
=
\{(\varnothing,\{\mathrm{add}\}),
  (\{\mathrm{neg}\},\{\mathrm{add},\mathrm{neg}\})\}.
\]

If one assigns a separate copy of this surgery to each syntax frame and then
composes parent and child sequentially, finite relation composition gives

\[
S_{\mathrm{add}}\,S_{\mathrm{add}}=\varnothing.
\]

After the first step, the only `add` event is already complete; no second edge
can execute it again. Thus nested syntax substitution does not imply repeated
causal surgery.

This is the nested analogue of the earlier warning that frame intersections
do not partition events.

## Glued frame stack

The test forms one intensional frame stack retaining, for each frame:

- exact frame ID;
- exact scope path;
- exact `GraftRegionRole`; and
- ordered holes.

Entry incidence maps the joint input expression to the two lower cuts, and
exit incidence maps the two upper cuts to the joint output expression. The
shared `add` surgery is inserted exactly once:

\[
T_{\mathrm{nested\ add}}
=
P_{\mathrm{out}}
\,S_{\mathrm{add}}
\,P^*_{\mathrm{in}}.
\]

Reversing all relations again produces the converse transformation.

Each exact body slice contains one `OperationNode`, while its graft
intersections record that same node in both parent and child body roles. The
model therefore retains overlap without duplicating the event.

## Structural conclusion

The characteristic surgery belongs to the exact program slice/event, not to a
fresh copy attached to every syntax frame. Graft frames are overlapping
scope-readings of that surgery.

Accordingly, the next candidate for `P*` needs more than a set of independent
frame incidences. It should retain a compatible frame stack or, more
generally, the finite incidence nerve of frames over one slice. Gluing must be
performed by original event identity.

This resembles a descent condition, but the present evidence does not justify
installing sheaf terminology or laws. The next E0 calibration should decorate
each dual-face surgery once with its complete ordered list of intersecting
frame roles, then verify that contraction/expansion preserves this overlap
decoration and composes over adjacent slices.
