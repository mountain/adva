# Neutral Carrier and Triadic Mechanism Frontiers

Status: bounded Rust research grammar following the reusable witness and
graft-derived instantiation work in notes
[0107](0107-reusable-six-word-witness-kernel.md) and
[0108](0108-graft-derived-witness-instantiation.md). It does not change
`adva.ir` version 1, the Lisp parser, evaluation, proof theory, or the
research-only typed-aperture ontology.

## 0. Correction

The earlier search for three persistent carrier kinds mixed two levels. A
program and proof are commonly inputs to computation and verification, while a
model is commonly the result of learning before it is reused as a method.
Making all three file kinds hides this phase change.

The revised proposal has one neutral carrier and nine primitive interface
words:

| position | labels | grammatical role |
|---|---|---|
| input view | subject, method, object | nouns |
| mechanism edge | compute, verify, learn | verbs |
| output view | history, result, evidence | nouns |

Program, proof, and model remain possible human readings. They are not carrier
variants in the grammar. In particular, a learned result can be routed to the
method position of a later step without changing file kind.

The proposed common suffix is `.adva`. Existing `.adva` files are Lisp source,
so V0 records the suffix candidate but deliberately introduces no second
decoder, magic header, or stable persistent envelope.

## 1. Neutral structure and labelled boundaries

One finite carrier is

\[
A=(k,H),
\]

where `k` is a nonsemantic witness-artifact cache coordinate and `H` is a
canonical finite research frontier. There is no field saying `program`,
`proof`, or `model`.

One local form has the outer shape

\[
(S,M,O)
\xrightarrow{\;m\;}
(H,R,E),
\qquad
m\in\{\mathsf{compute},\mathsf{verify},\mathsf{learn}\}.
\]

The input labels let a loader locate the subject, method, and object. The
output labels let a persistence layer locate history, result, and evidence.
This is a six-position boundary with three process labels, not six intrinsic
types of neutral structure.

The possible cross-step identities are

\[
\{H,R,E\}
\times
\{\mathsf{compute},\mathsf{verify},\mathsf{learn}\}
\times
\{S,M,O\},
\]

giving 27 typed routes from nine primitive words. The local grammar does not
implement routing or feedback. The separate persistence boundary now records
cross-frame routes through shared document-local carrier references.

## 2. Outer arity versus inner holes

The fixed three-input/three-output form is outer syntax. Each carrier occupying
one position may itself expose an inner open frontier. These levels must not be
collapsed.

A V0 frontier site records

\[
(d,h,o),
\]

where `d` is one of the existing construction/space/time witness coordinates,
and `(h,o)` is a research-local hole/occurrence coordinate. The coordinate does
not allocate semantic identity and does not identify this frontier with a
function hole, cut port, proof obligation, typed aperture, metavariable, or
singular point.

The same open site receives a mechanism-relative reading:

| neutral condition | compute | verify | learn |
|---|---|---|---|
| open site | unbound input error | declared assumption or obligation | target question |
| replacement | bound argument | discharge or witness | candidate filling |
| residual open site | rejected execution | conditional result | continuing frontier |

## 3. Three formation disciplines

### 3.1 Compute

V0 checks

\[
H(S)=\varnothing,
\qquad
H(O)=\varnothing.
\]

An open subject or object is rejected. The method frontier is retained because
an open program interface may still require the existing explicit graft and
instance checks. This grammar does not claim that passing the input gate is
sufficient for execution.

### 3.2 Verify

Let `D` be the declared subject frontier, `A` its actual current frontier, and
`X` the explicitly discharged sites. V0 requires

\[
A\cap X=\varnothing,
\qquad
A\cup X=D.
\]

If `A` is nonempty, the result is conditional. If `A` is empty and every
declared site has a discharge record, it is closed. An actual site outside `D`
is undeclared; a site in `D` but neither actual nor discharged is unexplained.
Both are rejected. This intentionally makes weakening explicit rather than
silent.

The discharge record carries a witness-artifact reference, but this bounded
checker does not replay it as a logical proof.

### 3.3 Learn

Learning requires an open subject and returns a nonempty finite proposal

\[
F:H(S)\rightharpoonup\mathsf{Carrier}.
\]

Every target must be a distinct member of the current frontier. If the
replacement for target `h` has frontier `H(F(h))`, the retained result is

\[
H(S[F])=
\bigl(H(S)\setminus\operatorname{dom}F\bigr)
\uplus
\coprod_{h\in\operatorname{dom}F}H(F(h)).
\]

The union is occurrence-sensitive. A replacement colliding with an existing
or another replacement coordinate is rejected instead of authorizing implicit
contraction. A plan may be partial and may introduce more subholes than it
fills. Thus formation proves neither progress nor termination.

## 4. Executable boundary

The Rust companion exposes:

- `MechanismV0`, `InputLabelV0`, and `OutputLabelV0` for the nine primitive
  words;
- `NeutralCarrierV0` and `OpenFrontierV0` for neutral cached content with a
  research-local frontier;
- `MechanismInputV0` and `MechanismOutputV0` for the two labelled triples;
- `MechanismFormV0::check` for the three formation disciplines; and
- `FillPlanV0` for finite learning proposals with retained replacement
  frontiers.

Tests check canonical frontier coordinates, neutral carrier serialization,
open-compute rejection, conditional and closed verification, explicit
discharge, refusal of undeclared or unexplained sites, partial learning,
replacement subholes, repeated targets, and cross-replacement collisions.

## 5. The nonstopping cycle

The intended global shape is coinductive:

\[
A_0\longrightarrow A_1\longrightarrow A_2\longrightarrow\cdots.
\]

This does not mean that one local execution runs forever without producing a
carrier. A usable cycle must be productive: each finite step must yield
history, result, and evidence that can be retained before a later chart reloads
them. The current V0 checks only one local formation and no feedback law.

A plausible audited route is

\[
\text{open subject}
\xrightarrow{\mathsf{learn}}
\text{fill proposal}
\xrightarrow{\mathsf{verify}}
\text{accounted substitution}
\xrightarrow{\mathsf{compute}}
\text{closed result},
\]

after which a later learning view may expose a new frontier. The arrows are a
research plan, not implemented scheduling semantics.

## 6. Result and remaining gap

The experiment supports the structural distinction that motivated it:

\[
\boxed{
\text{compute refuses openings},\quad
\text{verify accounts for openings},\quad
\text{learn proposes fillings}.
}
\]

It does not yet establish that subject/method/object and
history/result/evidence are the characteristic nouns forced by the opposite
processes. The vocabulary remains a human-readable working chart. The next
theoretical task is to define the opposite-edge characteristic operator that
could confirm or replace these names. The next engineering task was a separate
decision for a self-describing `.adva` envelope and an explicit output-to-input
substitution record; neither is inferred from this local checker. That
decision is now implemented as a neutral carrier table plus mechanism-labelled
transition frames, without changing this grammar claim, in
[`0110-neutral-adva-document-load-save.md`](0110-neutral-adva-document-load-save.md).
