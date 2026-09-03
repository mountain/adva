# Cell--Carrier--View Relation Machines

Status: syntax-only refinement of
[note 0101](0101-six-port-whole-cut-theory.md) and
[note 0102](0102-bootstrap-zero-whole-cut-grammar.md), calibrated against the
history distinctions of [note 0093](0093-beta-history-local-confluence-audit-2-cells.md)
and the signed routing boundary of
[note 0097](0097-threading-syntax-typed-braid-alignment.md).

This note keeps the public

```text
cell -> carrier -> views
```

spine while making every arrow typed and extensible. It introduces no stable
Rust type, Lisp constructor, proof equality, braid quotient, surreal
interpretation, or physical reading. Its executable companion is
`test_bootstrap_zero_cell_carrier_views.py`, a self-contained Python research
calibration rather than semantic authority.

---

## 0. Correction and result

The earlier formulation made two useful but insufficient commitments:

1. one atomic `<L|R>` cell has two typed ports; and
2. line and circle are checked projections of one six-occurrence ledger.

The refined spine is

\[
\boxed{
\mathsf{TypedCellSignature}
\xrightarrow{\mathsf{assemble}_\rho}
\mathsf{StratifiedCarrier}
\xrightarrow{V_\nu}
\mathsf{PresentedView}_\nu .
}
\tag{CCV}
\]

The assembly law \(\rho\) is now explicit. It decides how cell occurrences
meet, which parallel paths form a relation boundary, and which boundaries
remain open or receive a named filler. A view \(V_\nu\) is not a picture or
an arbitrary projection: it declares a target syntax, retained structure,
forgotten structure, and a kernel of distinctions made observationally zero.

Two finite rank-two machines become sibling instances:

\[
\partial\mathsf{InterchangeCell}=Q_4,
\qquad
\partial\mathsf{BraidCell}=M_6.
\tag{RelationBoundaries}
\]

The four-port machine witnesses independent interchange. The six-port machine
witnesses braid-shaped reorganization. Neither relation identifies its two raw
histories.

---

## 1. Dimension-indexed cells

A cell signature records at least

\[
C=(\dim C,\partial C,\mathsf{ports}(C),
   \mathsf{polarity}(C),\mathsf{label}(C)).
\tag{TypedCell}
\]

The initial stratification is:

| dimension | role | current examples |
|---|---|---|
| 0 | named state or port occurrence | six members of the authoritative ledger |
| 1 | typed step occurrence | whole cut, thread step, signed routing atom |
| 2 | relation between parallel threads | interchange cell, braid cell |
| 3 | coherence among relation cells | truncated-octahedral envelope candidate |

This is a syntactic dimension. It does not assert that the denoted world is a
CW complex, manifold, or Euclidean space.

For one carrier write

\[
\mathcal C=(C_0,C_1,C_2,\ldots;
            s,t,\partial,\lambda,\mathsf{Inc},\mathsf{Open}).
\tag{StratifiedCarrier}
\]

The carrier retains every occurrence. Attaching a higher cell adds a witness;
it does not delete its boundary histories.

---

## 2. Relation boundary constructor

Let \(u\) and \(v\) be two well-typed threads with the same source and
target and with equal positive length \(m\):

\[
s(u)=s(v),\qquad t(u)=t(v),\qquad |u|=|v|=m.
\]

If their internal state occurrences are disjoint, their union has

\[
2(m+1)-2=2m
\]

state occurrences and presents a cyclic relation boundary \(C_{2m}\).
Define

\[
\mathsf{RelBoundary}[u\Rightarrow v]
\quad\text{with}\quad
\partial=C_{2m}.
\tag{RelBoundary}
\]

The unfilled boundary and its filler are different objects:

\[
C_{2m}^{\partial}
\qquad\text{and}\qquad
C_{2m}^{\omega}
=
(C_{2m}^{\partial},\omega:u\Rightarrow v).
\tag{OpenFilled}
\]

Here \(\omega\) is an ordinary witness name, not the project's
\(\Omega\)-boundary.

### 2.1 Interchange machine

For independent operations \(a,b\),

\[
\chi_{a,b}:ab\Longrightarrow ba,
\qquad
\partial\chi_{a,b}=Q_4.
\tag{Q4}
\]

The four state occurrences are the two common endpoints and the two distinct
intermediate occurrences.

### 2.2 Braid machine

For adjacent or overlapping operations \(a,b\),

\[
\beta_{a,b}:aba\Longrightarrow bab,
\qquad
\partial\beta_{a,b}=M_6.
\tag{M6}
\]

The six state occurrences are the two common endpoints and four distinct
intermediate occurrences. The source and target histories remain unequal:

\[
aba\ne bab
\quad\text{in raw syntax}.
\tag{HistoryDistinct}
\]

The witness \(\beta\) relates them at dimension two.

---

## 3. Coxeter shadow versus signed braid data

The finite hexagonal carrier uses the Coxeter shadow

\[
a^2=b^2=1,
\qquad
aba\Rightarrow bab.
\tag{CoxeterShadow}
\]

The signed routing language of note 0097 instead retains
\(\sigma_i\) and \(\sigma_i^{-1}\) as distinct crossing histories. It does
not impose \(\sigma_i^2=1\). Therefore a finite \(M_6\) face is not the
whole braid group. It is the boundary of one admitted braid-shaped coherence
after an explicitly declared forgetting of crossing winding.

This gives three separate operations:

1. signed routing: \(\sigma_i\) or \(\sigma_i^{-1}\);
2. retraction witness:
   \(\sigma_i\sigma_i^{-1}\Rightarrow 1\);
3. braid witness:
   \(\sigma_i\sigma_{i+1}\sigma_i
     \Rightarrow
     \sigma_{i+1}\sigma_i\sigma_{i+1}\).

Retraction cancels an inverse pair. A braid cell reorganizes crossings and is
not itself dissipation.

---

## 4. View contracts

A view declaration has the form

\[
V_\nu=
(\mathsf{name},\mathsf{target},
 \mathsf{preserves},\mathsf{forgets},\ker V_\nu).
\tag{ViewContract}
\]

The initial well-formedness conditions are:

1. the view name and target syntax are explicit;
2. retained and forgotten coordinates are disjoint;
3. every declared kernel distinction is among the forgotten coordinates;
4. the authoritative occurrence ledger is reused literally; and
5. boundary formation is respected:

\[
V_\nu(\partial c)=\partial V_\nu(c).
\tag{ViewBoundary}
\]

The initial core views are:

| view | retained structure | characteristic forgetting |
|---|---|---|
| line | occurrence ledger, typed endpoints, selected linear paths | cyclic root and higher filler |
| circle | occurrence ledger, cyclic incidence and closure | chosen seam |
| thread | occurrence ledger, ordered operations and history identity | geometric embedding |
| logic | judgments, inference edges, parallel derivations, open obligations and fillers | metric and embedding |

The set of view names is deliberately open. Arithmetic, characteristic,
energy, observer, braid, surreal, or geometric views may be added only by a
new contract; they are not new fields silently appended to the kernel.

---

## 5. Logic view of \(Q_4\) and \(M_6\)

The logic view is proof-relevant. It does not assign truth values.

For \(Q_4\), it presents the independent critical-pair obligation

\[
ab\overset{?}{\Longrightarrow}ba.
\]

For \(M_6\), it presents

\[
\mathcal D_L:
\Gamma_0\xrightarrow a\Gamma_1
\xrightarrow b\Gamma_2
\xrightarrow a\Gamma_3,
\]

\[
\mathcal D_R:
\Gamma_0\xrightarrow b\Gamma'_1
\xrightarrow a\Gamma'_2
\xrightarrow b\Gamma_3.
\]

An open \(M_6^\partial\) projects to a proof obligation. A filled
\(M_6^\beta\) projects to

\[
\beta:\mathcal D_L\Longrightarrow\mathcal D_R.
\tag{LogicBraid}
\]

The six occurrences are intermediate judgments, not six logical values.
The logic view proves no soundness merely by existing. A later interpreter
must still check:

- each state judgment is well formed;
- every edge rule is admissible;
- both paths have exactly the declared typed endpoints;
- the filler is a valid witness rather than a name alone; and
- witnesses remain compatible under later composition and whiskering.

Proof irrelevance is a further forgetting view. It must not be built into
\(V_{\mathsf{logic}}\).

---

## 6. Truncated-octahedral coherence envelope

Let \(s_1,s_2,s_3\) be adjacent transpositions acting on four ordered
symbols. Their finite Coxeter presentation is

\[
S_4=
\langle s_1,s_2,s_3
\mid
s_i^2=1,,
(s_1s_3)^2=1,,
(s_1s_2)^3=1,,
(s_2s_3)^3=1
\rangle.
\tag{S4}
\]

The 24 permutations are the vertices of the fourth permutohedron, the
truncated octahedron denoted here by \(TO_{24}\). Its rank-two cosets give

\[
6Q_4+8M_6
\tag{TOFaces}
\]

as its fourteen faces:

\[
[S_4:\langle s_1,s_3\rangle]=24/4=6,
\]

\[
[S_4:\langle s_1,s_2\rangle]
+[S_4:\langle s_2,s_3\rangle]
=24/6+24/6=8.
\]

Every vertex is incident to one square and two hexagons, the local pattern
\(4.6.6\). The executable fixture enumerates the full 24-state graph and its
fourteen rank-two face occurrences. It does not construct a certified
3-cell filler. Thus \(TO_{24}\) is currently a finite coherence envelope,
not an established coherence theorem.

---

## 7. Typed zero and generative relations

Three zeros must remain typed:

1. the empty raw form \(0_{\varnothing}\);
2. the identity operation \(1_A:A\to A\); and
3. zero in an additive chain or observation target.

The Coxeter carrier illustrates a precise generative scheme. Starting from a
chosen identity state and freely applying \(s_1,s_2,s_3\) gives an infinite
word tree. Nonempty words that return to the same finite state form relation
boundaries:

\[
(s_1s_3)^2\leadsto Q_4,
\qquad
(s_1s_2)^3\leadsto M_6,
\qquad
(s_2s_3)^3\leadsto M_6.
\]

Hence

\[
\boxed{
\mathsf{generation}
=\text{free histories from a chosen zero},
\qquad
\mathsf{geometry}
=\text{typed relations among returning histories}.
}
\tag{GenerativeZero}
\]

Endpoint return is not raw-history erasure. A nonempty loop and the empty
history remain different syntax. A filler records why a declared observation
may treat their boundary difference as zero.

This distinction is essential for a later braid extension: a braid may induce
the identity permutation while retaining nontrivial pure-braid history.

---

## 8. Executable calibration

The companion test checks:

1. generic relation boundaries require parallel, well-typed threads;
2. \(Q_4\) has four occurrences and records \(ab\Rightarrow ba\);
3. \(M_6\) has six occurrences and records \(aba\Rightarrow bab\);
4. open and filled relation carriers remain distinct;
5. line, circle, thread, and logic views reuse one literal occurrence ledger;
6. logic view retains unequal histories and a named witness without creating
   a truth valuation;
7. malformed view contracts and forged relation boundaries are rejected;
8. a new view name can be introduced without changing a closed enum;
9. the \(TO_{24}\) enumeration has 24 vertices, 36 edges, six square faces,
   eight hexagonal faces, and local incidence \(4.6.6\); and
10. nonempty Coxeter relation words may return to the identity state without
    becoming the empty history.

These are finite syntax calibrations. They do not establish general
confluence, braid-group faithfulness, higher coherence, logic soundness,
surreal adequacy, or an implementation in the stable Adva kernel.

---

## 9. Revised spine and open frontier

The current research spine is

\[
\mathsf{AtomicCut}_1
\longrightarrow
\begin{cases}
\mathsf{InterchangeCell}_2(Q_4),\\
\mathsf{BraidCell}_2(M_6)
\end{cases}
\longrightarrow
\mathsf{CoherenceEnvelope}_3(TO_{24})
\longrightarrow
\{V_{\mathsf{line}},
V_{\mathsf{circle}},
V_{\mathsf{thread}},
V_{\mathsf{logic}},\ldots\}.
\tag{RevisedSpine}
\]

The hard conclusion is structural: cells are typed local generators, the
carrier is the authoritative stratified occurrence ledger, and a view is a
declared partial observation with an auditable kernel.

The next proof obligation is to connect the three original whole-cut pairings
of \(\mathbb W_6\) to the six-step boundary of one \(M_6\) relation cell
without conflating ports, states, and step occurrences. Only after that bridge
is explicit may the braid filler be proposed as part of the Bootstrap Zero
completion theorem.

