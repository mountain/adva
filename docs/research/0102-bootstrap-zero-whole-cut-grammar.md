# Bootstrap Zero Whole-Cut Grammar

Status: syntax-only redesign grounded in
[note 0101](0101-six-port-whole-cut-theory.md). This note proposes the raw
grammar, formation judgments, checked projections, and extension envelope for
the revised Bootstrap Zero kernel.

The proposal changes no stable Rust type, Lisp surface, parser, operation
registry, JSON IR, Python facade, or registered claim. The notation below is a
research language for a finite checker.

---

## 0. Package boundary

The redesigned package is

\[
\mathcal G_0^6=
(\mathcal W_6,\mathcal V_0,\mathcal M_0;
\mathcal I_K,\mathcal I_X,\mathcal I_t,
\mathcal I_{\mathrm{thr}},\mathcal I_{\mathrm{AM}};
\mathcal E_0),
\tag{G06}
\]

where:

- \(\mathcal W_6\) contains atomic whole-cut cells and their triadic carrier;
- \(\mathcal V_0\) is its checked view language;
- \(\mathcal M_0\) is its typed morphism and witness language;
- the five \(\mathcal I\)'s are declarations without interpreter bodies; and
- \(\mathcal E_0\) is a visible but unpopulated extension envelope.

The compact public glyphs remain

```text
{}[]()
<L|R>
```

The second spelling is one atomic cut cell, not the full six-port carrier.
Typed records retain all names, ports, occurrences, holes, histories,
collisions, and residuals.

---

## 1. Lexical classes

All name classes below are countable and pairwise disjoint:

```text
TypeName          SourceName       OccurrenceName
IncidenceName     PortName         HoleName
CutName           CellName         StrandName
CycleName         LocusName        HistoryName
PolicyName        FunctionName     WitnessName
InterpreterName   ExtensionName    ResidualName
```

Equal display strings in two classes do not give equal typed names. In
particular, a port, occurrence, incidence, and hole never become aliases.

The fixed finite alphabets are

```text
Role       ::= K | X | t
Side       ::= L | R
Polarity   ::= + | -
Motion     ::= forward | reverse
Carrier    ::= line | circle
Crossing   ::= over | under
```

The six alphabets remain disjoint. No token coercion is implicit.

For distinct endpoint roles, the remaining role is a partial metasyntactic
operation:

\[
\operatorname{opp}(K,X)=t,
\quad
\operatorname{opp}(X,t)=K,
\quad
\operatorname{opp}(t,K)=X,
\tag{Opp}
\]

with the reversed endpoint pairs admitted. `opp(d,d)` is undefined.

---

## 2. Signatures and extension envelope

A kernel signature contains only declared value types, function boundaries,
and the three role-edge whole-cut cell declarations:

```text
KernelSignature ::= signature {
  types      TypeDecl*
  functions  FunctionDecl*
  cells      WholeCutCellDecl[K,X;t]
             WholeCutCellDecl[X,t;K]
             WholeCutCellDecl[t,K;X]
}
```

The order inside `cells` is public and fixed for the canonical triadic cycle.
Reversal or rotation is a separately named presentation, not raw identity.

An extension is never an untyped miscellaneous field:

```text
ExtensionSlot ::=
    arity | topology | collision-theory | character
  | interpreter | equation | observer | proof | learning
  | omega | arithmetic | physical

ExtensionDecl ::= extend ExtensionName : ExtensionSlot {
  inputs       TypedBoundary
  outputs      TypedBoundary
  preserves    PreservationObligation*
  residuals    ResidualDecl*
  countercases CountercaseDecl*
  status       research | proposed-stable
}
```

The kernel checker may retain an `ExtensionDecl`; it does not execute it.
Adding an equation, interpreter, or physical reading therefore remains
visible at the exact point where the extension enters.

---

## 3. Ports, cuts, and degree occurrences

A port keeps side and polarity separate:

```text
Port ::= port PortName {
  cut         CutName
  side        Side
  polarity    Polarity
  value-type  TypeName
  source      SourceName
  occurrence  OccurrenceName
  multiplicity PositiveNatural
}
```

The initial open stratum requires multiplicity one. A collided presentation
may carry a larger multiplicity, but it also retains the complete member
ledger described in section 8.

A whole-cut cell has one cut, two named ports, and a local coorientation
witness:

```text
WholeCutCell ::= cell CellName <L | CutName R> [Role, Role; Role] {
  left-port   PortName
  right-port  PortName
  coorientation WitnessName
}

CoorientationWitness ::= coorient WitnessName {
  cut CutName
  sides      (L, R)
  polarities (+, -) | (-, +)
}
```

The endpoint roles must be distinct and the middle role must equal `opp` of
the endpoints. Each cell has exactly one `L` port, one `R` port, one `+` port,
and one `-` port. There is no global rule identifying `L` with `+`.

The canonical six-port ledger is

```text
PortLedger6 ::= ports (
  p-KX-L p-KX-R
  p-Xt-L p-Xt-R
  p-tK-L p-tK-R
)
```

Formation checks six distinct port names and six distinct initial occurrence
names. Source names may repeat only through an explicit production ledger.

---

## 4. Whole-cut carrier

The authoritative object form is

```text
WholeCut6 ::= whole6 CellName {
  shell          {}_K []_X ()_t
  cells          (Cell_KX Cell_Xt Cell_tK)
  ports          PortLedger6
  productions    ProductionLedger
  through        ThroughAccount
  circle-order   CycleLedger
  holes          HoleLedger
  alternatives   AlternativeLedger
  residuals      ResidualLedger
  extensions     ExtensionDecl*
}
```

`WholeCut6` is the cyclic assembly of three `WholeCutCell` records. It has no
single compact `<L|R>` rendering; each component cell has that surface.
Compact rendering never determines raw identity.

### 4.1 Production ledger

```text
Production ::= produce SourceName -> (OccurrenceName+)
```

Every occurrence in the port ledger occurs exactly once in the codomain of
the production ledger. An occurrence cannot be manufactured by routing,
collision, projection, or compact rendering.

### 4.2 Through account

```text
ThroughChannel ::= through StrandName {
  from       PortName
  to         PortName
  motion     Motion
  thread     ThreadWord
}

OpenPort ::= open PortName as HoleName residual ResidualName

ThroughAccount ::= account (ThroughChannel | OpenPort)*
```

Every port occurs exactly once in a `ThroughChannel` endpoint or an
`OpenPort`. A minimal closed `WholeCut6` has three channels forming a perfect
matching of its six ports and has no `OpenPort`.

This is the local sustained-computation condition: a cut may not silently
leave a severed endpoint. It does not prove semantic nontermination.

### 4.3 Circle order

```text
CycleLedger ::= cycle CycleName (
  PortName PortName PortName PortName PortName PortName
)
```

The word is cyclically interpreted only by a checked circle projection. Two
rotated spellings remain distinct raw records unless an explicit rotation
witness is supplied.

### 4.4 Hole, alternative, and residual ledgers

```text
HoleDecl        ::= hole HoleName : TypeName at PortName
AlternativeDecl ::= alternatives HoleName (RawForm+)
ResidualDecl    ::= residual ResidualName retains (TypedName*)
```

Every open port has one hole and one residual. Closing a hole selects an
alternative through a separately named witness; it does not erase unused
alternatives.

---

## 5. Formation of the six-port carrier

The primary judgment is

\[
\Sigma;Q\vdash_{\mathsf{whole6}}
W:\mathsf{WholeCut6}.
\tag{Whole6WF}
\]

It requires:

1. exactly the roles \(K,X,t\) and the three role edges \(KX,Xt,tK\);
2. exactly one atomic whole-cut cell on each role edge;
3. two distinct sides and opposite polarities at every cut;
4. six distinct open-stratum ports and occurrences;
5. one complete production entry for every occurrence;
6. total accounting of all ports by a channel or explicit open hole;
7. a circle ledger containing exactly the same six port names once each;
8. literal value-type agreement at every through endpoint;
9. explicit copy, discard, merge, collision, and forgetting records whenever
   the corresponding occurrence census changes; and
10. retention of every hole, unused alternative, collision member, and
    residual.

The checker calculates, but does not treat as an arithmetic-language value,

\[
\deg(W)=\sum_{p\in P(W)}\operatorname{multiplicity}(p).
\tag{DegreeLedger}
\]

The initial carrier must satisfy \(\deg(W)=6\). A collision view preserves
this total by member accounting.

---

## 6. Line and circle views

Views are derived records:

```text
LineView6 ::= line-view CellName {
  ports    PortLedger6
  channels (ThroughChannel ThroughChannel ThroughChannel)
}

CircleView6 ::= circle-view CellName {
  ports PortLedger6
  cycle CycleLedger
}
```

The judgments

\[
W\Downarrow_{\mathsf{line}}L,
\qquad
W\Downarrow_{\mathsf{circle}}C
\tag{ViewProjection}
\]

require literal equality of typed port and occurrence ledgers. A view is
rejected if it creates a new occurrence, forgets an unused port, or replaces
a member ledger by a count.

Carrier duality is a named view-transport form:

```text
DualCarrier ::= dual WitnessName :
  line-view CellName <-> circle-view CellName
  preserving PortLedger6
```

`dual` is neither a polarity flip nor motion reversal. Its two directions are
distinct raw arrows even when packaged by one witness name.

---

## 7. Polarity and conjugation

```text
PolarityFlip ::= flip-polarity WitnessName {
  ports PortLedger -> PortLedger
}

MotionConjugate ::= conjugate-motion WitnessName {
  channels ThroughAccount -> ThroughAccount
}
```

`flip-polarity` exchanges `+` and `-` while preserving side, motion, source,
occurrence, and multiplicity. `conjugate-motion` exchanges `forward` and
`reverse` while preserving side, incidence polarity, source, occurrence, and
multiplicity.

Transport between carriers uses an explicit square:

```text
TransportSquare ::= transport WitnessName {
  dual       DualCarrier
  local-op   PolarityFlip | MotionConjugate
  dual-op    PolarityFlip | MotionConjugate
  boundary   PortLedger6
}
```

Formation checks common boundaries. It does not declare the square equal,
commutative, involutive, or invertible. Those are separate coherence-witness
extensions.

---

## 8. Braid and collision forms

```text
BraidStep ::= crossing CrossingName {
  gap  PositiveNatural
  sign over | under
}

BraidWord ::= braid (BraidStep*)
```

A braid step exchanges two adjacent complete port records. It preserves the
multiset of port, occurrence, source, polarity, side, type, and multiplicity
fields. Crossing sign is not incidence polarity.

The formal inverse spelling reverses word order and exchanges `over` with
`under`. It does not add a cancellation equation.

A collision retains its members:

```text
Collision ::= collide CollisionName {
  inputs (PortName PortName+)
  locus  LocusName
  members (PortSnapshot PortSnapshot+)
  output-multiplicity PositiveNatural
}
```

Formation requires:

\[
\operatorname{members}=\operatorname{inputs}
\quad\text{as a typed occurrence ledger},
\]

and

\[
\operatorname{outputMultiplicity}
=\sum\operatorname{inputMultiplicity}.
\tag{CollisionConservation}
\]

A collision may reduce loci but not occurrences. Opposite polarities remain
two members. No raw cancellation follows.

The grammar leaves a `collision-theory` extension slot for later braid,
singular, inverse, tangle, cactus, or compactification equations.

---

## 9. Generation, retraction, and factored traversal

```text
Generate ::= generate MorphismName : Boundary -> Expansion
Retract  ::= retract  MorphismName : Expansion -> Boundary {
  fibres   FibreLedger
  residual ResidualLedger
}

SplitWitness ::= split WitnessName {
  generate Generate
  retract  Retract
  returns  IdentityBoundary
}

ProjectorPresentation ::= projector MorphismName {
  retract-then-generate (Retract, Generate)
  residual ResidualLedger
}
```

A split witness is well formed only when the typed composite boundary of
`retract after generate` is the displayed identity boundary. This is a
certificate-shaped syntax record, not a runtime equality.

The other order is retained as a projector presentation and is not identified
with an identity.

Traversal is required to expose its factorization:

```text
Traversal ::= traverse MorphismName : Expansion_i -> Expansion_j {
  retract Retract_i
  common  Boundary
  generate Generate_j
  residuals (ResidualLedger_i ResidualLedger_j)
}
```

Formation checks the boundary equation represented by

\[
T_{i\to j}=g_j\circ r_i.
\]

A free primitive `traverse` with no retraction/generation record is not a
Bootstrap Zero form.

---

## 10. Multi-hole addition, multiplication, and history

The pure finite expression grammar is

```text
AMExpr ::=
    atom AMAtomName : TypeName
  | hole HoleName : TypeName
  | use SourceName OccurrenceName : TypeName
  | plus AMExpr AMExpr
  | tensor AMExpr AMExpr
```

`plus` is ordered juxtaposition. `tensor` is ordered structural substitution
or generative product. Neither constructor is assumed associative,
commutative, distributive, or evaluated.

Historical composition belongs to the morphism grammar:

```text
History ::= identity Boundary | compose Morphism Morphism
```

It is not an `AMExpr` constructor.

A distributivity witness is a complete ledger, not an equality token:

```text
DistributivityWitness ::= distribute WitnessName {
  source-expression AMExpr
  target-expression AMExpr
  production-ledger ProductionLedger
  hole-bindings BindingLedger
  thread-ledger ThreadWord
  residuals ResidualLedger
}
```

The source must have shape `tensor(A, plus(B, C))`; the target must have shape
`plus(tensor(A, B), tensor(A, C))`. Formation verifies exact occurrence
production and bindings. It does not evaluate the two expressions.

### 10.1 Noncollapsing zero presentations

```text
ZeroPresentation ::=
    empty-zero WitnessName
  | balanced-zero WitnessName {
      positive AMExpr
      negative PolarDualPresentation
    }
  | observed-zero ExtensionName
```

`empty-zero` is the only hard-kernel zero-shaped atom. `balanced-zero` is a
noncollapsing witness that retains both terms. `observed-zero` occupies the
`interpreter` or `arithmetic` extension slot and has no kernel meaning.

The raw terms `tensor(empty-zero, E)` and `plus(E, E#)` are not rewritten to
`empty-zero`. Absorption and cancellation can only enter through a visible
equation or interpreter extension.

---

## 11. Five interpreter declarations

The declarations share `WholeCut6` as source:

```text
interpreter I_K      : WholeCut6 -> View_K
interpreter I_X      : WholeCut6 -> View_X
interpreter I_t      : WholeCut6 -> View_t
interpreter I_thread : WholeCut6 -> ThreadMachineForm
interpreter I_AM     : WholeCut6 -> AMForm
```

Bootstrap Zero may check a declaration projection only for preservation of:

- type names;
- source and occurrence names;
- port and incidence names;
- ordered boundaries;
- holes and unused alternatives;
- collision members and multiplicities; and
- residual ledgers.

It supplies no interpreter clause and no claim that two projections have the
same denotation.

---

## 12. Derived six-direction calibration

The three undirected role channels and their two orientations form

\[
\Phi=
\{\pm\alpha_{KX},\pm\alpha_{Xt},\pm\alpha_{tK}\}.
\tag{SixDirections}
\]

This is a finite calibration of direction labels over the six-port carrier.
It does not add six independent strands or a scalar energy. A distribution
record may assign the six degree occurrences among the roles while retaining

\[
n_K+n_X+n_t=6
\]

as a metasyntactic ledger check.

Quotienting distributions by role permutation, interpreting the seven
resulting partition types as halting states, or treating predicates on them
as the 128 Boolean supports are separate calibration extensions.

---

## 13. Extension-preservation judgment

An extension declaration is accepted only with the obligation shape

\[
\Sigma\hookrightarrow\Sigma'
\quad\vdash_{\mathsf{ext}}
\mathsf{preserve}(J_1,\ldots,J_k),
\tag{ExtensionObligation}
\]

where each \(J_i\) names an existing raw identity or formation judgment. The
kernel records this obligation; it does not mark it proved merely because the
extension is syntactically declared.

The following families are intentionally open:

- \(F_n\) carriers and nontriadic arities;
- noncyclic and asymmetric connection topologies;
- nonbinary or higher-valent cuts;
- collision and braid equations;
- characteristic, grading, and energy languages;
- observer communication and translation;
- proof, learning, and Omega rules;
- arithmetic, surreal, geometric, and physical interpreters.

Their visibility prevents openness from becoming silent ontology drift.

---

## 14. Finite checker contract

A research-local checker for this proposal must return `Accepted` or one or
more explicit formation failures. It must reject at least:

1. fewer or more than three canonical whole-cut cells in `WholeCut6`;
2. fewer or more than two initial ports per cut;
3. repeated initial port or occurrence names;
4. equal side or polarity marks within one cut;
5. an unaccounted or multiply accounted port;
6. a line or circle view with a changed occurrence ledger;
7. a braid step that alters any field except order;
8. a collision that drops a member or changes total multiplicity;
9. a traversal without exact retraction/generation factorization;
10. a distributivity record with incomplete production or hole bindings;
11. a zero presentation that discards its balanced terms; and
12. an extension that omits preservation obligations and countercases.

Acceptance proves finite formation only. It does not prove execution,
termination, semantic equality, universality, conservation in nature, or
physical realization.

---

## 15. Coordination theorem to be proved

The proposed final Bootstrap Zero theorem is:

> If \(W\) is accepted by `Whole6WF`, every built-in view and morphism form
> preserves the authoritative typed occurrence and multiplicity ledger,
> except for explicitly declared production, copy, discard, collision, or
> forgetting records; collision preserves member multiplicity; traversal has
> a checked retraction/generation factorization; and every open or forgotten
> item remains named in a hole, fibre, alternative, or residual ledger.

This theorem is strong enough to establish syntactic coordination and weak
enough to preserve the visible extension space required by the theory.
