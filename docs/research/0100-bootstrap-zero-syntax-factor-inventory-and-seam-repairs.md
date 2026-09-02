# Bootstrap Zero Syntax-Factor Inventory and Local Seam Repairs

Status: complete finite inventory and local syntax placement following
[note 0095](0095-bootstrap-zero-geometric-threading-syntax.md),
[note 0096](0096-boolean-triangle-placement-language-alignment.md),
[note 0097](0097-threading-syntax-typed-braid-alignment.md),
[note 0098](0098-multihole-am-type-formation-constraints.md), and
[note 0099](0099-axis-circle-pendulum-history-syntax.md).

This note closes an inventory, not a theory.  It records every syntax factor
currently in play, assigns each factor a status, and repairs four local seams.
It introduces no surreal number, evaluator, physical quantity, equality,
coordination theorem, or interpreter body.

---

## 0. Three statuses

Every factor receives exactly one status in this inventory.

| mark | status | authority |
|---|---|---|
| `H` | hard kernel | declared grammar, namespace, or formation datum |
| `C` | finite-calibration constraint | forced by the Boolean, braid, or multi-hole checks |
| `G` | geometric candidate | admitted only inside an optional named profile |

`H` does not mean semantically true.  It means only that a finite parser or
formation checker has an exact place for the datum.  `C` records distinctions
that the finite calibrations show must not be erased.  `G` marks the proposed
axis--circle coupling; it is neither global syntax nor a proved coherence law.

---

## 1. Hard kernel inventory (`H`)

### 1.1 Names, roles, and orientation alphabets

| family | factors |
|---|---|
| typed names | `TypeName`, `FunctionName`, `SourceName`, `OccurrenceName`, `IncidenceName`, `HoleName`, `CutName`, `CellName`, `StrandName` |
| declaration names | `PolicyName`, `ThreadAtomName`, `InterpreterName`, `LearningTagName`, `ProofTagName`, `AMAtomName`, `CharacteristicName`, `DerivativeName`, `CrossingName`, `HistoryName` |
| domain roles | `K`, `X`, `t` |
| derivative indices | `role[d]`, `history[ζ]` |
| side alphabet | `L`, `R` |
| incidence polarity | `+`, `-` |
| crossing sign | `over`, `under` |

All rows are typed and disjoint.  Identical display strings across rows do
not create identity.  In particular `history[t]` and `role[t]` are distinct
derivative indices.

### 1.2 Type and boundary factors

| layer | factors |
|---|---|
| declarations | base value types, function block types, policy source-to-role assignments |
| finite addresses | annotated incidences, ordered incidence frontiers, ordered hole contexts, named cuts and middle interfaces |
| shape types | `Cut_d(F)`, ordered `Through_de^f(F_L,N_f,F_R)`, `Line(i)`, `Circle(γ)`, `Thread(F_L,F_R)` |
| form sorts | `Form_Q`, `View_d`, `ThreadMachineForm`, `AMForm` |
| visible boundary | the three typed shells `{}_K[]_X()_t` |
| visible cell | the decorated form `c:<L|_n R>[τ]`, compactly printed `<L|R>` |
| graph data | strands, ports, incidence table, exposed frontier, retained open incidences |

The shell and cell displays are surfaces, not complete serializations.  Their
fully explicit records retain names, ordering, policy annotations, holes,
thread words, and unused syntax.

### 1.3 Thread factors

| class | raw constructors |
|---|---|
| routing | `crossing[ξ;r;over]`, `crossing[ξ;r;under]` |
| transport | `function[κ:Π]`, `derivative[ι_D,p;δ:Π↝Π']` |
| characteristic | `characteristic[χ;d;Π]` |
| orientation | `dual[⋆]`, `conjugate[...]`, `polarity[p]`, `side[L]`, `side[R]`, `cut[n;d]` |
| reading | `learning[ℓ;Π]`, `proof[π;Π]` |
| words | finite thread words, finite braid blocks, named strands, formal syntactic braid inverse |

A crossing routes complete incidences.  A function gate may change arity only
when its block type is declared.  A derivative is one constructor with a
tagged index; neither derivative variant computes.

### 1.4 Pure multi-hole add--multiply factors

The complete raw tree grammar is

```text
E ::= atom[m:A]
    | hole[h:A]
    | use[s,o:A]
    | add[E,E]
    | mul[E,E]
```

There is no primitive `neg` node.  A negative position is spelled with a
declared atom such as `atom[negUnit_A:A]` and `mul`.  Formation does not assert
that this atom denotes \(-1\).

The associated hard data are an ordered hole context, source-use occurrences,
an exact occurrence-to-hole binding, a graft record, a routed frontier, and a
residual.  `source`, `occurrence`, `hole`, and `incidence` are four different
syntactic kinds.

### 1.5 Judgements and declaration-only interpreters

The kernel contains finite formation judgements for types, frontiers, braid
blocks, thread words, through cells, complete forms, and A/M trees.  It also
contains five interpreter signatures:

```text
I_t    : Form_Q -> View_t
I_K    : Form_Q -> View_K
I_X    : Form_Q -> View_X
I_thr  : Form_Q -> ThreadMachineForm
I_AM   : Form_Q -> AMForm
```

These are declarations only.  No interpreter application, evaluation, or
agreement judgement is present.

---

## 2. Finite-calibration constraints (`C`)

The calibrations do not add meanings; they prevent destructive identifications.

| source | constrained syntax factor |
|---|---|
| 128 Boolean supports | domain vertices, unordered and ordered edge placement, support polarity, achiral/chiral triadic labels |
| triangle alignment | `Through_de^f` and `Through_ed^f` remain distinct; side, polarity, direction, and chirality remain separate |
| signed braid calibration | `over` and `under` are distinct routing atoms with the same endpoint permutation |
| braid history | formal inverse reverses a word without installing an equality; mixed-word braid blocks retain non-routing separators |
| closed routing | endpoint return is not closure; a circle retains explicit cyclic incidence and closure data |
| multi-hole kernels | hole order, exact bindings, frames, renamings, copy/share production, discard, and residual are explicit |
| typed capabilities | `add`, `mul`, structural gates, and required atoms must be declared at exact types |

The seven-bit Boolean support mask and all Boolean connectives remain external
calibration data.  They are not object-language constructors and do not turn
`add` or `mul` into logical conjunction or disjunction.

---

## 3. Geometric candidate profile (`G`)

`PendForm_Q(A)` is an optional subprofile of `Form_Q`.  A general Bootstrap
Zero form is not required to be a pendulum form.

The profile combines already declared kernel nodes with these candidate
records:

| factor | retained raw datum |
|---|---|
| axis | one exact `Line(i)` with ordered `empty`/`universal` tags and a named dual atom |
| circle | one `Circle(γ)` and one named `pierce[z;a,γ]` relation |
| history | one `HistoryName` and one core `derivative[history[ζ],p;...]` atom |
| disturbance | one `EnergyTagName`, provenance, and named perturbation joining energy, axis, and history |
| characteristic | a named raw pair of pure A/M trees, separated without equality |
| repeated uses | six source-use occurrences with census `Y:2`, `U:3`, `E:1` |
| domain cycle | one three-through-cell word ordered `KX`, `Xt`, `tK` with three connectors |
| observation | one forgetting record with a nonempty fibre and residual when distinctions are removed |
| closure | one explicit closure witness with incidence and connector ledgers |
| debt | one retained residual naming all unproved coordination |

The geometric guess lies principally in the coupling matrix among these
records, not in the mere existence of lines, circles, trees, or thread atoms.

---

## 4. The six occurrences, placed exactly

For the raw characteristic display

\[
Y^2\;\bowtie_\chi\;2(E-U)(1-U^2),
\]

the count concerns variable source uses only.  Constants, A/M operation
nodes, and `negUnit_A` atoms are not counted.

| source | occurrence | hole | tree position |
|---|---|---|---|
| `Y` | `o_Y1` | `h1` | left tree, first input |
| `Y` | `o_Y2` | `h2` | left tree, second input |
| `E` | `o_E1` | `h3` | right tree, first difference, left input |
| `U` | `o_U1` | `h4` | right tree, first difference, negative-unit position |
| `U` | `o_U2` | `h5` | right tree, second difference, inner product left |
| `U` | `o_U3` | `h6` | right tree, second difference, inner product right |

Thus

\[
F_{\mathrm{use}}
=\langle o_{Y1},o_{Y2},o_{E1},o_{U1},o_{U2},o_{U3}\rangle,
\qquad
H_{\mathrm{pend}}=\langle h_1{:}A,\ldots,h_6{:}A\rangle,
\]

and the total typed binding is

\[
\sigma(o_{Y1},o_{Y2},o_{E1},o_{U1},o_{U2},o_{U3})
=(h_1,h_2,h_3,h_4,h_5,h_6).
\]

The production ledger must create the two `Y` occurrences and three `U`
occurrences explicitly.  The braid layer begins only after that frontier
exists and therefore cannot manufacture any of the six uses.  Incidence
names are added by geometric placement and are not aliases for holes or
occurrences.

---

## 5. Local seam repairs

### 5.1 Pure A/M syntax

The accidental unary `neg` extension has been removed.  Both note 0098 and
the pendulum characteristic now use only `atom`, `hole`, `use`, `add`, and
`mul`.  Negative-unit positions cite a declared `AMAtomName`.

### 5.2 One derivative family

The earlier role-indexed derivative and the later history derivative are now
one constructor:

```text
derivative[index, polarity; name : input ↝ output]
index ::= role[d] | history[ζ]
```

This is a tagged syntactic sum, not a conversion between history and the
three domain roles.

### 5.3 Four namespaces at the multi-hole seam

`SourceName`, `OccurrenceName`, `HoleName`, and `IncidenceName` are never
identified.  An explicit production record relates a source to its uses;
`σ` binds uses to holes; the incidence table later places complete typed
uses in a diagram.

### 5.4 Cross-reference repair

The threading note now points to the syntax-only multi-hole A/M note.  It no
longer describes note 0098 as a surreal or option-semantic construction.

---

## 6. The coupling matrix is still a conjecture

Within `PendForm_Q(A)`, literal shared names are proposed as follows:

| shared name | candidate records that cite it |
|---|---|
| axis `a` | axis line, piercing, perturbation |
| cycle `γ` | `Circle`, piercing, history carrier, Omega word, forgetting, closure witness |
| history `ζ` | history-indexed derivative, perturbation, history carrier |
| energy occurrence `o_E1` | characteristic tree, energy tag |
| sources `U,Y` | derivative endpoints, characteristic source census |

Literal agreement is checkable, but it proves no commutation, preservation,
periodicity, compactification, or common interpretation.

The essential unresolved seam is deliberately left visible:

\[
\mathsf{Circle}(\gamma),
\qquad
\mathsf{circle}_\Omega(\gamma),
\qquad
\mathsf{ClosureWitness}(\gamma)
\]

currently share a name but do not yet arise from one common formation and
coherence theorem.  Renaming the three records would not solve this problem.

---

## 7. Deferred coordination proof obligations

A later proof layer must establish, separately:

1. preservation of value types from A/M uses through `σ` into routed
   incidences;
2. preservation of occurrence production and source lineage under braids;
3. compatibility of graft renaming with incidence gluing;
4. stability of the derivative-index distinction under substitution;
5. agreement of the `Circle(γ)` cyclic word with the Omega incidence and
   connector ledgers;
6. independence and compatibility of forgetting and closure evidence;
7. preservation of every open hole, unused alternative, fibre, and residual;
8. any common observation made by the five declared interpreters.

None is a premise silently added to the present grammar.

---

## 8. Executable finite inventory

The companion test checks that:

1. the `H`, `C`, and `G` inventories are finite and disjoint;
2. `role[t]` and `history[t]` remain different derivative indices;
3. the A/M term algebra contains no `neg` constructor;
4. six fresh uses bind totally and bijectively to six distinct holes;
5. the production ledger has exact census `Y:2,U:3,E:1`;
6. `PendForm` is candidate and optional rather than hard and global; and
7. the circle/Omega/closure seam remains an explicit unproved obligation.

The executable fixture contains no evaluator, scalar, equality checker, or
semantic interpretation.

---

## Conservative conclusion

The finite syntax picture is now closed as an inventory.  Its factors have
places, typed seams, and explicit status labels.  The inventory does not
claim that those factors agree.

The next legitimate step is therefore a coordination proof, beginning with
the shared-cycle seam rather than hiding that seam behind a new name.
