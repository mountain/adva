# Bootstrap Zero: A Geometric Threading Kernel Syntax

Status: pure syntax proposal following
[note 0087](0087-typed-three-domain-threaded-multihole-calculus.md)
and
[note 0094](0094-focused-normal-forms-subformula-decidable-derivability.md).

This note begins Bootstrap Zero by specifying a deliberately small geometric
language before extending the larger computation language of note 0087.  It
defines only lexical classes, raw forms, type forms, threading annotations,
finite incidence diagrams, formation judgements, and five interpreter
declarations.

It defines no evaluation, denotation, truth, entailment, proof rule, learning
rule, differentiation rule, normalization, operational transition, halting
judgement, or interpreter clause.  The words `function`, `characteristic`,
`dual`, `conjugate`, `derivative`, `learning`, and `proof` below are typed
syntax constructors or declaration tags only.

The proposal changes no stable Rust type, parser, operation registry,
`adva.ir` schema, Python facade, or registered claim.  The implemented
binder-free finite PSC0 language remains the semantic authority in its
declared scope.

---

## 0. Design boundary

The kernel package has one object language, one type language, and five
declared interpreters:

\[
\boxed{
\mathcal G_0=
(\mathcal O_0,\mathcal T_0;
\mathcal I_t,\mathcal I_K,\mathcal I_X,
\mathcal I_{\mathrm{thr}},\mathcal I_{\mathrm{AM}}).
}
\tag{G0}
\]

The public surface uses only two visible families:

```text
{}[]()
<L|R>
```

The first is the permanent ordered three-shell boundary.  The second is a
typed through cell with finite ordered left and right frontiers.  Composition
is represented by exact incidence gluing, not by adding an untyped textual
composition operator.

The two proposed syntactic values are geometric shapes:

- a **line**, recording exact identity transport; and
- a **circle**, recording a closed finitely presented threading component.

`circle` means finite presentation and syntactic closure.  It does not mean
termination or finite unfolding.  `line` means exact occurrence identity.
Two occurrences with one source do not form an identity line merely because
their source names or value types agree.

---

## 1. Lexical namespaces

Fix pairwise disjoint countable namespaces:

\[
\begin{aligned}
&a\in\mathsf{TypeName},
&&\kappa\in\mathsf{FunctionName},
&&s\in\mathsf{SourceName},\\
&o\in\mathsf{OccurrenceName},
&&i\in\mathsf{IncidenceName},
&&h\in\mathsf{HoleName},\\
&n\in\mathsf{CutName},
&&c\in\mathsf{CellName},
&&e\in\mathsf{StrandName},\\
&q\in\mathsf{PolicyName},
&&u\in\mathsf{ThreadAtomName},
&&j\in\mathsf{InterpreterName},\\
&\ell\in\mathsf{LearningTagName},
&&\pi\in\mathsf{ProofTagName},
&&m\in\mathsf{AMAtomName},\\
&\chi\in\mathsf{CharacteristicName},
&&\delta\in\mathsf{DerivativeName}.
\end{aligned}
\tag{Names}
\]

Display strings may coincide across namespaces, but typed identities do not.
Alpha-renaming is initially permitted only for locally bound metasyntactic
names.  It does not identify sources, occurrences, incidences, holes, cuts,
cells, or strands.

The reserved domain-role alphabet is

\[
d ::= K\mid X\mid t.
\tag{Domain}
\]

The reserved side and polarity alphabets are

\[
\ell ::= L\mid R,
\qquad
p ::= +\mid -.
\tag{Orientation}
\]

`K`, `X`, and `t` are role annotations under a declared policy.  They are not
value types and are not inferred from values.

For distinct roles, reserve the typed metasyntactic operation

\[
\operatorname{opp}(K,X)=t,
\quad
\operatorname{opp}(X,t)=K,
\quad
\operatorname{opp}(t,K)=X,
\tag{Opp}
\]

together with the reversed pairs.  `opp(d,d)` is undefined.  The spelling
`opp` avoids overloading the recursion binder `mu` used by note 0087.

---

## 2. Type language

### 2.1 Value types and block types

A signature is

\[
\Sigma=(\mathsf{Base},\mathsf{Fn},\mathsf{btype}),
\]

where

\[
A ::= a,
\qquad a\in\mathsf{Base},
\tag{ValueType}
\]

and each declared function name has one ordered block type

\[
\kappa:\mathbf A\Rightarrow\mathbf B.
\tag{FunctionBoundary}
\]

An ordered value frontier is

\[
\mathbf A ::= \epsilon
\mid \langle i:A\rangle\mathbf A.
\tag{Frontier}
\]

Concatenation is metasyntactically written \(\mathbf A\mathbf B\).  It does
not introduce an implicit product, exchange, copy, merge, or discard.

A block type is

\[
\Pi ::= \mathbf A\Rightarrow\mathbf B.
\tag{BlockType}
\]

### 2.2 Roles are indices, not value types

A policy declaration has the raw form

\[
Q:q\{s_1\mapsto d_1,\ldots,s_m\mapsto d_m\}.
\tag{PolicyDecl}
\]

The annotation

\[
i:(A,s,o)@_Q d^p
\tag{AnnotatedIncidence}
\]

records a value type, source, occurrence, policy role, and polarity.  Its
underlying value type remains \(A\).  The expression \(A@_Qd^p\) is therefore
an indexed incidence form, not a new member of `ValueType`.

### 2.3 Frontier, cut, through, and shape types

An incidence frontier is a finite ordered word

\[
F ::= \epsilon
\mid \langle i:(A,s,o)@_Qd^p\rangle F.
\tag{IncidenceFrontier}
\]

A syntax-hole context and a named middle-interface form are

\[
H ::= \epsilon_H
\mid \langle h:A\rangle H,
\qquad
N_f ::= \mathsf{middle}[n;f].
\tag{HoleAndMiddle}
\]

The remaining type forms are

\[
\begin{aligned}
T ::= {}&\mathsf{Cut}_d(F)
\mid \mathsf{Through}_{de}^{f}(F_L,N_f,F_R)\\
&\mid \mathsf{Line}(i)
\mid \mathsf{Circle}(\gamma)
\mid \mathsf{Thread}(F_L,F_R)\\
&\mid \mathsf{Form}_Q
\mid \mathsf{View}_d
\mid \mathsf{ThreadMachineForm}
\mid \mathsf{AMForm},
\end{aligned}
\tag{TypeForms}
\]

where \(d\ne e\), \(f=\operatorname{opp}(d,e)\), \(N_f\) is a named
middle-interface declaration, \(\gamma\) is a finite cyclic incidence word,
and \(H\) is an ordered hole context.

These are syntactic type constructors.  `Cut`, `Through`, `Line`, and
`Circle` have no set-theoretic, topological, operational, or logical
interpretation in this note.

---

## 3. The two visible object forms

### 3.1 The permanent three-shell boundary

The only public shell word is

\[
\boxed{B_\partial:={}_K[]_X()_t.}
\tag{ShellBoundary}
\]

The three atoms have the spellings

\[
b_K:=\{\},
\qquad
b_X:=[],
\qquad
b_t:=().
\tag{Shells}
\]

They are empty atomic shells.  Mixed or same-role nesting is absent from
\(\mathcal O_0\):

```text
{[]}, [()], ({}), {{}}, [[]], (())
```

are not raw forms.  Role permutations may occur in auxiliary typed data but
are not additional public boundaries.

### 3.2 Through cells

A raw through cell is

\[
c:\left\langle L\middle|_n R\right\rangle[\tau],
\tag{Cell}
\]

where:

- \(L\) and \(R\) are finite ordered incidence frontiers;
- \(n\) is one named cut or middle-interface occurrence; and
- \(\tau\) is one finite thread word.

Its compact printed surface may erase the decorations and show only

```text
<L|R>
```

but the typed form retains `c`, `n`, `L`, `R`, and `tau`.  Equality of the
compact printout is not raw-syntax identity.

The two frontiers may have different lengths, including zero.  Arity alone
does not authorize structural computation.  A one-to-many cell is accepted
as `copy` only when its thread word contains an exact function declaration
whose registered block type has that boundary.  The same requirement applies
to discard, swap, merge, addition, multiplication, and every other named
operation.

---

## 4. Thread alphabet

The threading vocabulary is separated into typed lexical classes rather than
placed in one untyped token set.

### 4.1 Transport atoms

\[
u_{\mathrm{tr}} ::= 
\mathsf{function}[\kappa:\Pi]
\mid
\mathsf{derivative}[d,p;\delta:\Pi\rightsquigarrow\Pi'].
\tag{TransportAtoms}
\]

`derivative` is a domain- and polarity-indexed constructor.  It neither
computes a derivative nor satisfies linearity, Leibniz, chain, nilpotence, or
commutation laws here.

### 4.2 Characteristic atoms

\[
u_{\mathrm{char}} ::= 
\mathsf{characteristic}[\chi;d;\Pi].
\tag{CharacteristicAtom}
\]

This constructor names a characteristic position in a thread.  It does not
assert invariance, eigenform, quotient stability, or successful learning.

### 4.3 Orientation atoms

\[
u_{\mathrm{ori}} ::= 
\mathsf{dual}[\star]
\mid
\mathsf{conjugate}[\overline{\phantom{x}}]
\mid
\mathsf{polarity}[p]
\mid
\mathsf{side}[L]
\mid
\mathsf{side}[R]
\mid
\mathsf{cut}[n;d].
\tag{OrientationAtoms}
\]

No equation identifies duality, conjugation, polarity reversal, side
reversal, or cut reversal.  In particular, involution and contravariant
composition laws are not part of raw syntax.

### 4.4 Learning and proof atoms

\[
u_{\mathrm{read}} ::= 
\mathsf{learning}[\ell;\Pi]
\mid
\mathsf{proof}[\pi;\Pi].
\tag{ReadoutAtoms}
\]

These are distinct readout tags.  `proof` does not contain a derivation and
`learning` does not create a vocabulary item in this note.  Their eventual
codomains and any duality between them are deliberately unspecified.

### 4.5 Thread words

Let

\[
u ::= u_{\mathrm{tr}}
\mid u_{\mathrm{char}}
\mid u_{\mathrm{ori}}
\mid u_{\mathrm{read}}.
\]

A thread word is a finite ordered word

\[
\tau ::= \epsilon_\tau
\mid u::\tau.
\tag{ThreadWord}
\]

The order and every repeated occurrence are retained.  A thread word is not
an execution trace.  A future threading-machine interpreter may interpret
it, but this note declares no transition relation.

A threading-machine form packages a left frontier, a thread word, and a right
frontier:

```text
ThreadMachineForm ::= pack_thr(F_L, tau, F_R)
```

This is only target-language syntax.  No transition relation, machine state,
execution order, or halting predicate is introduced here.

---

## 5. Strands and finite incidence diagrams

### 5.1 Strands

A strand declaration is

\[
e:i^-\xrightarrow{\tau}j^+.
\tag{Strand}
\]

It records two named incidences and a finite thread word.  Formation requires
literal agreement of their underlying value types and declared compatibility
of their policy roles.  It does not identify their source or occurrence
names.

An exact identity strand is written

\[
\mathsf{idLine}[i]:i^-\longrightarrow i^+.
\tag{IdentityLine}
\]

Both ends refer to the same incidence, source, and occurrence names.  A
strand between distinct copy siblings must instead carry an explicit
function, comparison, or other future connector tag.  It is not an identity
line.

### 5.2 Diagrams

A raw geometric form is a finite record

\[
P=operatorname{diagram}
(B_\partial;\mathcal C,\mathcal E;\partial^-P,\partial^+P),
\tag{Diagram}
\]

where:

- \(\mathcal C\) is a finite name-indexed family of through cells;
- \(\mathcal E\) is a finite name-indexed family of strands;
- cell incidences and strand endpoints are related by an explicit finite
  incidence table;
- \(\partial^-P\) and \(\partial^+P\) are ordered exposed frontiers; and
- every name and every unused incidence remains in the record.

Sequential and parallel arrangement are derived graph shapes:

- gluing a positive exposed incidence to a compatible negative incidence
  produces adjacency; and
- disjoint union produces juxtaposition.

This paragraph defines only raw graph formation.  It introduces no
associativity equation, interchange law, evaluator, or categorical semantics.

### 5.3 Line and circle values

A **line value** is a finite connected diagram component generated by one
exact identity strand and having exactly its two oppositely polarized exposed
ends:

\[
\Sigma;Q\vdash_{\mathsf{shape}}P:\mathsf{Line}(i).
\tag{LineValue}
\]

A **circle value** is a finite nonempty connected diagram component whose
incidence table forms one cyclic word and has no exposed end:

\[
\Sigma;Q\vdash_{\mathsf{shape}}P:\mathsf{Circle}(\gamma).
\tag{CircleValue}
\]

The judgement checks only finite presentation, incidence closure, and type
matching.  It does not assert that a represented process terminates, returns,
repeats, normalizes, or has finite semantic extent.

Branching through cells make a general program a finite stratified
one-complex rather than a one-manifold.  `Line` and `Circle` are the two
distinguished value shapes, not an assertion that every connected program
has one of those shapes.

---

## 6. Object-language formation judgements

The primary judgements are

\[
\Sigma\vdash_{\mathsf{type}}A,
\qquad
\Sigma;Q\vdash_{\mathsf{frontier}}F,
\tag{TypeJudgements}
\]

\[
\Sigma;Q\vdash_{\mathsf{thread}}
\tau:F_L\rightsquigarrow F_R,
\tag{ThreadJudgement}
\]

\[
\Sigma;Q\vdash_{\mathsf{cell}}
c:\langle L\mid_nR\rangle[\tau]:
\mathsf{Through}_{de}^{f}(F_L,N_f,F_R),
\tag{CellJudgement}
\]

and

\[
\boxed{
\Sigma;Q;H\vdash_{\mathsf{syn}}
P:\mathbf A\Rightarrow\mathbf B.
}
\tag{WF}
\]

The final judgement says only that \(P\) is a finite well-formed geometric
program form with the displayed value frontier, policy annotations, and open
hole context.

Its checker must enforce at least:

1. finite names, cells, strands, thread words, and incidence tables;
2. pairwise namespace and local-name discipline;
3. ordered left, right, input, output, and hole frontiers;
4. literal value-type agreement at every glued incidence;
5. policy roles as annotations rather than value types;
6. distinct endpoint roles and the declared opposite middle role for each
   through cell;
7. explicit function names for every structural arity change;
8. exact occurrence identity for every identity line;
9. explicit retention of open and unused incidences; and
10. exact closure of a syntactic circle.

It must not inspect a scalar value, run an operation, solve an equation,
differentiate a function, close a hole, choose a filling, or decide a logical
claim.

---

## 7. Multi-hole add--multiply expression syntax

The add--multiply target language is independently generated by

\[
E ::= 
\mathsf{atom}[m:A]
\mid
\mathsf{hole}[h:A]
\mid
\mathsf{use}[s,o:A]
\mid
\mathsf{add}[E,E]
\mid
\mathsf{mul}[E,E].
\tag{AMGrammar}
\]

Its hole context is an ordered word

\[
H=\langle h_1:A_1,\ldots,h_m:A_m\rangle.
\]

`use[s,o:A]` separates one source from one of its occurrences.  Repeating a
source name does not repeat an occurrence name.  An eventual interpreter must
account for any required copy, but no such clause is defined here.

The sole formation judgement is

\[
\Sigma_{\mathrm{AM}};H
\vdash_{\mathsf{AM}}E:A.
\tag{AMWF}
\]

A packaged multi-hole expression is the syntax record

\[
\mathsf{pack}_{\mathrm{AM}}(H,E:A):\mathsf{AMForm}.
\tag{AMPack}
\]

`add` and `mul` are binary constructors declared by
\(\Sigma_{\mathrm{AM}}\).  This grammar supplies no arithmetic values,
identities, associativity, commutativity, distributivity, simplification,
evaluation, or equality.

---

## 8. Five interpreter declarations

Interpreter signatures belong to a separate declaration language:

```text
interpreter I_t      : Form_Q -> View_t
interpreter I_K      : Form_Q -> View_K
interpreter I_X      : Form_Q -> View_X
interpreter I_thread : Form_Q -> ThreadMachineForm
interpreter I_AM     : Form_Q -> AMForm
```

Abstractly,

\[
\begin{aligned}
\mathcal I_t&:\mathsf{Form}_Q\Rightarrow\mathsf{View}_t,\\
\mathcal I_K&:\mathsf{Form}_Q\Rightarrow\mathsf{View}_K,\\
\mathcal I_X&:\mathsf{Form}_Q\Rightarrow\mathsf{View}_X,\\
\mathcal I_{\mathrm{thr}}
&:\mathsf{Form}_Q\Rightarrow\mathsf{ThreadMachineForm},\\
\mathcal I_{\mathrm{AM}}
&:\mathsf{Form}_Q\Rightarrow\mathsf{AMForm}.
\end{aligned}
\tag{InterpreterDeclarations}
\]

The declaration-formation judgement is

\[
\Sigma\vdash_{\mathsf{idecl}}
\mathcal I_j:S\Rightarrow T.
\tag{InterpreterDeclWF}
\]

It checks only that the interpreter name is fresh and its source and target
sorts are declared.  There is no interpreter application judgement and no
clause of the form

\[
\mathcal I_j(P)=M
\]

in Bootstrap Zero syntax.

In particular:

- the temporal, constructive, and spatial declarations do not assign
  meanings to the three shells;
- the threading-machine declaration does not execute a thread word; and
- the add--multiply declaration does not evaluate, encode, or decode an
  expression.

Interpreter bodies, correctness relations, residuals, and coherence among
the five interpretations are later metatheory.

---

## 9. Surface and fully explicit forms

The compact surface

```text
{}[]()
<L|R>
```

is intentionally not a complete serialization.  Its fully explicit syntax
record is schematically

```text
form P under policy Q
  boundary {}[]()
  holes (h1:A1, ..., hm:Am)
  cell c : <L |n R> [thread tau]
  strands (e1, ..., ek)
  incidence (...)
  exposed (input ..., output ...)
```

The compact printout may be used only together with the explicit record or a
certificate that reconstructs it without ambiguity.  Surface equality alone
does not identify programs.

---

## 10. Relationship to note 0087

Note 0087 remains the larger constructor-complete computation-syntax
proposal.  The present kernel is smaller in three ways:

1. it uses finite incidence gluing rather than taking serial, tensor, graft,
   threading, and recursive forms as one flat term grammar;
2. it records thread vocabulary as typed annotations without interpretation;
   and
3. it declares interpreters without supplying any clause or semantic result.

The present note does not yet prove that every note-0087 term elaborates into
\(\mathcal G_0\), or conversely.  In particular, recursion variables,
`mu`, one-step unfolding, grounded filling, connector authority, and the
Omega circle require later conservative extensions or explicit failures.

The implemented PSC0 carriers may serve as independent finite checks for a
future elaboration.  They do not become definitions of the new syntax merely
because their names are reused.

---

## 11. Bootstrap Zero proof obligations

The first metatheorems should remain syntactic.

### B0.1 Decidable formation

For finite input records, each formation judgement above is decidable.

### B0.2 Generation--derivation correspondence

Let \(\mathsf{Gen}_{\mathcal G_0}(\Pi)\) be the raw forms generated by the
grammar and \(\mathsf{Der}_{\mathcal G_0}(P:\Pi)\) their finite formation
derivations.  Target

\[
P\in\mathsf{Gen}_{\mathcal G_0}(\Pi)
\quad\Longleftrightarrow\quad
\mathsf{Der}_{\mathcal G_0}(P:\Pi)\ne\varnothing.
\tag{SyntaxCompleteness}
\]

### B0.3 Exact line criterion

An identity-line derivation exists exactly when both displayed endpoints
reuse the same typed incidence, source, and occurrence names.

### B0.4 Finite circle criterion

A circle derivation exists exactly when the finite incidence word is
nonempty, cyclically type-compatible, and has no exposed endpoint.

### B0.5 Interpreter-declaration conservativity

Adding a well-formed interpreter declaration does not create a new object,
thread, AM-expression, line, or circle derivation.

No completeness, soundness, adequacy, normalization, evaluation, learning,
proof, differentiation, or halting theorem is included in these obligations.

---

## Conservative conclusion

Bootstrap Zero starts with one finite typed geometric record:

\[
\boxed{
\Sigma;Q;H\vdash_{\mathsf{syn}}
P:\mathbf A\Rightarrow\mathbf B.
}
\]

Its public surface is generated by the three-shell boundary and through
cells:

\[
\boxed{{}_K[]_X()_t}
\qquad
\boxed{\langle L\mid R\rangle}.
\]

Lines and circles are distinguished finite graph shapes.  Function,
characteristic, duality, conjugation, polarity, derivative, left/right, cut,
learning, and proof are typed thread syntax.  The three domain interpreters,
the threading-machine interpreter, and the multi-hole add--multiply
interpreter are declarations only.

The absence of semantics is deliberate.  The first task is to prove that the
language can say exactly which finite forms are syntactically legal before it
tries to say what any legal form means.
