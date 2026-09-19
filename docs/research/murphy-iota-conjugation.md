# murphy: self-application, conjugation and the compiler boundary

Status: bounded external research record, 2026-09-19. This names and publishes
the existing experiment; it creates no native Adva operation or semantic ID.
The reproducible [publication unit](../../experiments/murphy/README.md) retains
the code, exact inputs, checks, failed attempt and unresolved representation map.

Research direction, left/right-expansion intuition and the name `murphy`:
Mingli Yuan. Formalization, reference implementations and analysis: ChatGPT
(OpenAI), submitted through Mingli Yuan's GitHub account as an authorized proxy.
Account use is not his authorship of the implementation, technical review,
endorsement or correctness guarantee. New original material is contributed
under Unknown v0.3; no independent human review is claimed.

## Object and execution observations

`murphy` names the value `P` obtained from Zot word `0001011011` **before** the
stop/printer wrapper. This follows the
[existing Zot baseline](zot-prefix-machine-weighted-sharing.md), without changing
its retained implementation or evidence. The 125 count measures CEK transitions:
115 across the ten bits, then 10 in the finish wrapper. There are 38 applications,
38 argument pushes, 38 argument-focus steps and 11 completion steps. The original
printer output is empty, while a nonempty closure is returned.

Writing `L(c) = lambda l R. R (lambda r. c (l r))`, the retained value has

```text
One = lambda c h. h (L(c))
D   = lambda r. S (One (iota r))
A   = L(L(D))
P   = lambda h. h A
```

S/K/I bracket abstraction without eta optimization, followed by the standard
Iota encodings of those combinators, produces 823 prefix characters. A separate
lambda normalizer checks equality with the original closure; an eager Iota
interpreter independently checks the finish wrapper's zero printer calls and
returned `K^4 I` behavior. No shortest-code or cost-preservation claim is made.

The user's confirmed ordinary self-application has

```text
P P -> P A -> A A.
```

Its 1,647-character Iota source terminates under the reference leftmost-outermost
Iota/S/K rules after 1,808 contractions: 822 Iota, 549 S and 437 K. Peak tree size
is 7,627 nodes. The lambda beta normal forms of `P` and `P P` have 49 and 84 AST
nodes respectively and are distinct. This does not assert beta-eta or general
observational inequivalence, divergence for other inputs, or native halt status.
The Zot transition count and this combinator contraction count are different units.

## Pure Iota conjugation on a declared coordinate domain

This construction uses a four-slot product `Z(p,q,r,s) = lambda k. k p q r s`,
read as `(p-q) + i*(r-s)` over a scalar domain supporting subtraction. It is an
explicit coordinate representation, not a replacement for the user's proposed
left-expanded Adva list representation. Opaque slots suffice for the checks.

```text
C Z(p,q,r,s) = Z(p,q,s,r)
J Z(p,q,r,s) = Z(s,r,p,q)
N Z(p,q,r,s) = Z(q,p,s,r)
```

The closed programs compile to 743, 671 and 725 pure Iota characters. On these
constructor products, beta normalization proves `C^2 = I`, `J^2 = N`, `J^4 = I`
and `C J C = N J`. A separate combinator reducer checks each output permutation.
No complex-number, arithmetic or matrix primitive was added to the Iota evaluator.

A four-entry table of such coordinates then supports transpose, entrywise
conjugation and conjugate transpose. Their programs contain 743, 3,809 and 3,791
Iota characters. Sixteen formal scalar slots check all output positions, each
involution, and commutation of transpose with entrywise conjugation. These are
linear-coordinate examples; they do not define Adva's reserved `D*`.

## Relation to the existing frame and new carrier

The pinned [Iota frame source](https://github.com/mountain/adva-iota/blob/a9540b4d93076674ce2ea954ad7b08b1bb86fff5/frame_v1/materials/frame.md)
keeps Iota as the only source combinator and represents the imaginary unit by J.
Its `conjugate(t,a,inverse)` function is a similarity transformation. We add the
coordinate complex conjugation `C = diag(I,-I)` and transport it as `C' = T C T^-1`,
together with J, metric G and observer O.

Exact rational checks on the twelve existing frames establish `C'^2 = I`,
`C' J' C' = -J'`, metric compatibility and observed correspondence. For their real
H, `C H C = H`; hence for `A = -J H`, `C A C = -A`. The recorded exponential
coefficient comparisons extend through degree 12. This reverses the operator
parameter in that reading, not a destructive computation's history or event clock.

The [carrier source](https://github.com/mountain/adva-machine/blob/25818eb259dd8a16c50214e825a8b3af3d641333/spec/framework/carrier-matrix-v0.md)
has `W = Lambda^1 E + Lambda^2 E`. Recomputing its declared cube incidence and
exterior actions yields, in its signed basis and actual composition order
`c_2(c_1(c_0 .))`,

```text
Omega = [[0, I3], [-I3, 0]],  Omega^2 = -I6
C     = [[I3, 0], [0, -I3]], C^2 = I6, C Omega C = -Omega.
```

Here C is minus exterior grade parity restricted to W. Each wedge/contraction
flips parity, so a product of three Clifford generators anticommutes with it.
The source's Omega is **minus** the canonical J used by the frame; its orientation
is retained. The carrier's contraction symbol `iota_j` is not the source Iota
combinator. A choice of real form or grading is required: J alone does not select
a unique C, and multiplying by J is not complex conjugation.

Metric adjoints `M^sharp = G^-1 M^T G` reverse composition. A noncommuting pair
checks that retaining the original order fails. Other negative controls show
that leaving C untransported fails on mixed charts and leaving the Euclidean
metric unchanged gives the wrong J adjoint on scaled charts. The earlier frame
and carrier native receiving campaigns were not rerun.

## Kip Thorne: the missing end-leaf interface is observable

The specific probe uses `L = iota 'K' 'i' 'p' ' ' 'T' 'h' 'o' 'r' 'n' 'e'`,
with left-associated application, ten opaque characters and **no terminator**.
This is one explicit realization of the described left-spine idea, not an
assertion that its base/terminator completes the intended list protocol.

| Program applied to L | Contractions | Result skeleton |
| --- | ---: | --- |
| murphy | 898 | `'K' S K 'i' 'p' ' ' 'T' 'h' 'o' 'r' 'n' 'e' A` |
| murphy murphy | 1,813 | same character spine followed by B |
| coordinate C | 823 | same character spine followed by F |
| coordinate C twice | 1,645 | same character spine followed by F F |

`B = lambda r. L(D)(A r)`; `F = lambda p q r s k. k p q s r`. Quoted characters
are distinct from combinators. All characters survive, but the opaque head has
no reduction rule and no printer/decoder is invoked. There is no new text output,
general string transformation, or demonstrated application to the final `e`.
`C(C(L))` is not beta equal to L; the earlier coordinate law is domain-specific.

Likewise, raw binary-tree reflection does not descend to beta-equivalence classes:
canonical Iota K and `(K K) S` both denote K, while their mirrors denote I and
S K. The first proposed counterexample, K versus I K, did not distinguish the
mirrors and was rejected; that failed check and script remain under `attempts/`.

The open bridge is a representation that carries application, endpoint order,
pairing and observation from the right-expanded program/left-expanded data
interface. General program conjugation is not obtained merely by reflecting a
tree or placing C on either side of P.

## Does murphy support a native Adva implementation by Futamura projection?

**Not from the established properties alone.** Term self-application `P P` is
different from supplying the quoted program of a specializer to that specializer.
The fact that a term normalizes on itself is not sufficient: even the identity
combinator has that property. Nor does the absence of `P P = P` obstruct a correct
specializer; that equation is not a Futamura requirement.

Let `q` expect static s and dynamic d, and let quotation/decoding be explicit.
A correct specializer must emit a residual r such that

```text
r = run(mix, [quote(q), s])
observe(run(decode(r), d)) = observe(run(q, [s, d])).
```

After fixing a host/target language H and an Adva interpreter `interp_H` in H,
the projection shapes are `mix(interp_H, p)`, `mix(mix, interp_H)` and
`mix(mix, mix)` for a target program, compiler and compiler generator respectively.
The self-applicable mix must handle its own implementation and code representation;
the target-language execution/loader remains explicit. See the authors'
[Futamura exposition](https://arxiv.org/html/1611.09906v3) for these standard shapes.

For murphy, `P x = x A` supplies a fixed value to a continuation. There is no
established Adva interpreter, code quotation interface, static/dynamic separation
or residual-code generator in this value. A sufficiently powerful continuation
could contain those mechanisms, but that would place the work in the continuation;
it would not show that the 823-character murphy is already a specializer.

The project has a more direct predecessor:
[bounded input-binding mix](bounded-mix-and-three-projections.md). Its retained v2
record includes 48 native calls, two interpreter families and a 3,959-instruction
compiler generator. It preserves the original interpreter body and adds static
literal construction; it has not eliminated interpreter dispatch. Its full Adva
interpreter and loader boundary remain open, and 57-register generated programs
exceed its 48-register source-specialization boundary. This publication reads that
record; it launches none of those native runs again.

An Iota-hosted Adva implementation would require a specified Adva subset and a
correct interpreter for it in Iota. A Futamura compiler route additionally needs
an Iota specializer able to residualize that interpreter, followed by self-
specialization. Machine-code output requires a native backend or corresponding
host target; producing Iota is not by itself CPU-native code or Rust admission.

The next useful finite gate is therefore a **proposal**, not an executed new
campaign: choose the existing arithmetic/tagged subset; define explicit code and
input representations; relate a small Iota interpreter to the existing reference
on returned values, rejection and exhausted-budget outcomes; then test one first
projection with a live dynamic input. Only after residual code and semantics are
checked should the specializer's own program enter the second-projection test.
Whether murphy serves a useful continuation/interface role can be tested within
that bridge; no privileged compiler role is currently demonstrated.

## Publication and validation

The fixed [publication contract](../../experiments/murphy/contract.json) permits
one fresh-process replay of the unchanged finite families. It completed in about
32 seconds: all 125 transition records matched (excluding the runtime-version
label), translation regenerated the exact murphy bytes, the independent eager
wrapper check passed, 400 base and 16 adjoint checks matched, all published Iota
outputs and the 1,808-step trace matched byte-for-byte, and all four text cases
matched their symbolic derivations. Only elapsed time and its verified derived
base-result digest are excluded from the corresponding result comparisons.

Budget exceptions in the shared lambda helper now use TimeoutError and are
reported as Unknown by both callers; the retained successful evidence is unchanged.
The initial report and failed reflection-control record are preserved. The
publication result and exact source digests are retained with the experiment.

Integration initially could not invoke pytest because it is not installed on
this host. The eight unchanged research-index test functions were then called
directly with Python's standard library and all passed. An initial whole-index
link audit also encountered the uninitialized library submodule in the isolated
checkout; the corrected audit checks the new report/package links and the added
index entry, without claiming that inherited submodule links were checked.
Exact staged input/admission hashes, source syntax and whitespace checks passed.

This is original executable research under the repository's publication boundary.
The two copied synthetic inputs have exact project-original admission records;
the Zot MIT reference is used at its inherited path and is not newly vendored.
The paper above is a bibliographic/theory reference only: its text and figures
are not imported. No native Adva run, new dependency lock, stable claim, physical
black-hole assertion or completed general duality is part of this submission.
