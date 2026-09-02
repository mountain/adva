# Axis--Circle Pendulum History Syntax

Status: syntax-factor placement following
[note 0079](0079-typed-hole-open-close-calibration-v0.md),
[note 0081](0081-relative-halt-exploration-threaded-compactification.md),
[note 0087](0087-typed-three-domain-threaded-multihole-calculus.md),
[note 0095](0095-bootstrap-zero-geometric-threading-syntax.md), and
[note 0098](0098-multihole-am-type-formation-constraints.md).

This note asks whether the formal factors of a pendulum equation can impose a
new syntax-only restriction on Bootstrap Zero.  The answer is yes, provided
that the equation is treated as a finite constraint record rather than as a
physical or numerical assertion.

The motivating picture is a line passing through a circle.  The line carries
the empty/universal dual aspect; the circle carries finite closure; a named
contingency or energy perturbation is attached to a history threaded around
the circle.  This motivation is philosophical.  The grammar below neither
explains contingency nor asserts that forgetting, energy, a pendulum,
hyperbolic compactification, three cusps, and an Omega boundary are the same
thing.

No coordination or consistency theorem is proved here.  The purpose is only
to put every required syntax factor in a distinct place.

---

## 0. Result

A finite axis--circle pendulum presentation must retain one package:

\[
\boxed{
\mathsf{PendForm}_Q(A)
=
(a,\gamma,z;\zeta,\delta;\varepsilon,\chi;
H,E,\sigma,G;W_\Omega;F,C,R).
}
\tag{PendPackage}
\]

Its fields are:

| field | raw syntax role |
|---|---|
| \(a\) | one exact line with ordered empty/universal aspect tags |
| \(\gamma\) | one finite circle name and cyclic incidence word |
| \(z\) | a named `pierce` relation between \(a\) and \(\gamma\) |
| \(\zeta\) | a history-parameter name, not the domain role \(t\) |
| \(\delta\) | a history-indexed derivative atom |
| \(\varepsilon\) | a named energy/contingency tag with provenance |
| \(\chi\) | a constraint-cell name retaining two A/M trees |
| \(H,E,\sigma,G\) | ordered holes, trees, bindings, and occurrences |
| \(W_\Omega\) | the explicit three-through-cell circular word |
| \(F\) | a forgetting record with fibre and residual |
| \(C\) | an explicit closure witness |
| \(R\) | every unused alternative and unproved comparison |

The central restriction is:

> The derivative, energy tag, A/M occurrence tree, axis--circle relation,
> three-domain cycle, forgetting record, and closure witness must refer to
> the same named finite presentation.  None may be reconstructed from a later
> value or inferred from another field.

This is a formation requirement, not a claim that the fields are coherent.

---

## 1. The motivating diagram and its syntactic reading

The ideal picture contains:

1. one vertical axis;
2. one circle around the axis;
3. one perturbation that marks a departure from the unperturbed display; and
4. one history following the resulting swing and returning to the circle.

Only three parts survive into raw syntax.

| picture word | retained syntax | deliberately absent |
|---|---|---|
| vertical line | \(\mathsf{Axis}(a;\mathsf{Line}(i))\) | metric verticality |
| circle | \(\mathsf{Circle}(\gamma)\) | topological or dynamical periodicity |
| line through circle | \(\mathsf{pierce}[z;a,\gamma]\) | intersection number or linking theorem |
| empty/universal ends | ordered tags \(\langle\mathsf{empty},\mathsf{universal}\rangle\) | metaphysical interpretation |

`pierce` is a relation name in a finite record.  It does not say whether a
Euclidean line meets the circumference at two points, passes through a disk,
or links a ring in three-space.  Choosing among those geometries belongs to a
later interpreter.

The axis line remains an exact identity line in the sense of note 0095.  The
two aspect tags decorate its oppositely exposed ends; they do not turn the
ends into different source or occurrence identities.

---

## 2. Namespace correction

The pendulum notation collides with three existing Bootstrap Zero spellings.
Formation must separate them before any equation is written.

| overloaded display | existing role | corrected pendulum role |
|---|---|---|
| \(t\) | reserved domain role in \(\{K,X,t\}\) | never used as the history parameter |
| \(d\) | domain metavariable in note 0095 | never used as the derivative operator |
| \(\omega,\Omega\) | commonly rate, one-form, period, or boundary | \(\Omega\) is reserved for the circular boundary only |
| \(s\) | source-name metavariable | not used for history |
| \(h\) | hole-name metavariable | not used for history |

Introduce pairwise disjoint namespaces

\[
\zeta\in\mathsf{HistoryName},
\qquad
\varepsilon\in\mathsf{EnergyTagName},
\qquad
z\in\mathsf{PiercingName},
\qquad
\varphi\in\mathsf{ForgettingName},
\qquad
\kappa_C\in\mathsf{ClosureName}.
\tag{NewNames}
\]

The display \(\zeta\) is the parameter formerly written \(t\) in a
differential equation.  It denotes the ordered history carried by the thread,
not physical time and not the domain role `t`.

The derivative is written \(D_\zeta\).  The capital \(D\) is a constructor
tag indexed by a `HistoryName`; it is not the domain metavariable \(d\) and it
does not compute differentiation.

---

## 3. A pendulum equation as a raw constraint

The familiar second-order spelling becomes

\[
D_\zeta^2\theta
+\kappa\,\mathsf{restore}(\theta)
\;\bowtie_{\chi_p}\;0.
\tag{RawPendulumODE}
\]

Here:

- \(D_\zeta^2\) is two ordered derivative atoms;
- `restore` is a declared unary function name, not an installed sine;
- \(\kappa\) is an atom or supplied hole;
- \(\bowtie_{\chi_p}\) is a constraint-cell separator; and
- the two sides are retained and are not declared equal.

This spelling exposes derivative order but does not place the energy tag
inside the path record.  The prior pendulum work supplies a more useful
finite first-history template:

\[
D_\zeta U\;\bowtie_{\delta}\;Y,
\qquad
Y^2\;\bowtie_{\chi}\;2(E-U)(1-U^2).
\tag{RawFirstHistory}
\]

These are again raw paired records, not equations.  They are selected because
the second pair can be written entirely in the multi-hole A/M grammar while
mentioning the energy source explicitly.

### 3.1 Exact A/M spelling

Use the ordered hole context

\[
H_{\mathrm{pend}}
=\langle
y_1:A,y_2:A,
e_1:A,
u_1:A,u_2:A,u_3:A
\rangle.
\tag{PendHoles}
\]

The two sides of the characteristic cell are

```text
lhs := mul(use[Y,y1], use[Y,y2])

rhs := mul(
  atom[2:A],
  mul(
    add(use[E,e1], neg(use[U,u1])),
    add(atom[1:A], neg(mul(use[U,u2], use[U,u3])))
  )
)
```

The occurrence census is exact:

\[
Y:2,\qquad U:3,\qquad E:1.
\tag{PendOccurrenceCensus}
\]

All six occurrence names are distinct.  Consequently the constraint forces
copy or sharing evidence for \(Y\) and \(U\).  A braid can reorder those
occurrences but cannot create them.

### 3.2 Energy is a tag attached to an occurrence

The raw form is

\[
\mathsf{energy}[\varepsilon;
\mathsf{use}[E,e_1:A];\mathsf{provenance};R_\varepsilon].
\tag{EnergyTag}
\]

It says only that the same occurrence \(e_1\) appears in the characteristic
cell and in the perturbation record.  It does not say that \(E\) is real,
positive, conserved, dimensional, random, or capable of producing motion.

The requested connection between energy disturbance and path is therefore
syntactic and exact: the energy occurrence is literally one input of the
same constraint cell whose other inputs are the history derivative
occurrences.

---

## 4. The history derivative

Add the candidate transport atom

\[
\mathsf{historyDerivative}
[\delta;\zeta;p;
\mathsf{use}[U,u_0:A]
\rightsquigarrow
\mathsf{use}[Y,y_0:A]].
\tag{HistoryDerivative}
\]

Its formation checks:

1. \(\zeta\) belongs to `HistoryName`;
2. the input and output have declared value type \(A\);
3. \(u_0\) and \(y_0\) are fresh occurrences with sources \(U\) and \(Y\);
4. the atom occupies a named position in one finite thread word; and
5. the characteristic cell cites the same source names \(U,Y\).

The last condition is source linkage, not an equality between occurrences.
If the characteristic needs additional uses, \(G\) must contain their copy or
sharing lineage.

No linearity, chain rule, Leibniz rule, second derivative, integration, clock,
or equation-solving rule is installed.

---

## 5. One circle, named once

The presentation uses one cycle name \(\gamma\), not three circles silently
identified after the fact.  The same \(\gamma\) must be referenced by:

\[
\mathsf{Circle}(\gamma),
\qquad
\mathsf{pierce}[z;a,\gamma],
\qquad
\mathsf{history}[\zeta;\gamma;w],
\qquad
\mathsf{close}[\kappa_C;\gamma].
\tag{SharedCycleName}
\]

Its three-domain decomposition is the existing Omega threading form:

\[
W_\Omega(\gamma)=
\circlearrowleft_\Omega
\bigl(
T^t_{KX},k_X,
T^K_{Xt},k_t,
T^X_{tK},k_K
\bigr).
\tag{OmegaWord}
\]

Formation requires all three through cells and all three connectors to
type-check and their ordered cyclic incidence word to be literally
\(\gamma\).  This gives a syntax-level identification: the displayed circle,
the history carrier, and the three-computer loop share one named finite graph.

It does not establish that a physical pendulum orbit, an \(H^2\) boundary,
three cusps, a Chaitin constant, or an analytic period has been constructed.

### 5.1 Closure is independent data

Neither the derivative atom nor the characteristic cell derives closure.
The package must contain

\[
C=\mathsf{close}[\kappa_C;
\gamma;\mathsf{incidenceTable};\mathsf{connectorLedger}].
\tag{ClosureWitness}
\]

Without \(C\), the same derivative and A/M records form an open history but
not a `Circle`.  Endpoint-type agreement is insufficient, and return to the
same visible frontier is not raw identity of the history word.

---

## 6. Forgetting and the small unseen circle

The philosophical claim that a finite observer sees a small circle because
information has been forgotten is represented only by an explicit record:

\[
F=
\mathsf{forget}
[\varphi;Q;
F_{\mathrm{fine}}\rightsquigarrow F_{\mathrm{seen}};
\mathsf{fibre};R_F].
\tag{ForgetRecord}
\]

Formation requires the forgotten fibre and residual \(R_F\) to be nonempty
records whenever the fine and seen frontiers differ.  The record may be
attached to \(\gamma\), but it cannot construct the closure witness \(C\).

This separates three claims:

| claim | syntax status |
|---|---|
| distinctions were projected away | explicit `forget` record |
| a finite cyclic incidence word exists | explicit `Circle(γ)` derivation |
| forgetting caused that closure | no rule; later interpretation only |

The initial circle may be opaque to a declared observer, but opacity is not
absence and does not turn the circle into a point.

---

## 7. Candidate formation rule

The complete raw judgement is

\[
\frac{
\begin{array}{c}
a:\mathsf{AxisLine}
\qquad
\gamma:\mathsf{Circle}
\qquad
z:\mathsf{Pierce}(a,\gamma)\\
\delta:\mathsf{HistoryDerivative}(\zeta;U,Y)
\qquad
\varepsilon:\mathsf{EnergyTag}(E,e_1)\\
\Sigma_{\mathrm{AM}};H_{\mathrm{pend}}
\vdash_{\mathsf{AM}}(E_L,E_R):A\\
\mathsf{occurs}(G;Y^2,E,U,1,2)
\qquad
W_\Omega:\mathsf{Cycle}(\gamma)\\
F:\mathsf{ForgetRecord}(Q,\gamma)
\qquad
C:\mathsf{ClosureWitness}(\gamma)
\end{array}
}{
\Sigma;Q\vdash_{\mathsf{form}}
\mathsf{pend}
[a,\gamma,z;\zeta,\delta;\varepsilon,\chi;
H,E,\sigma,G;W_\Omega;F,C,R]
:
\mathsf{PendForm}_Q(A)
}.
\tag{PendFormation}
\]

The rule enforces only the following literal agreements:

- one line name in the axis and piercing records;
- one cycle name in `Circle`, `pierce`, history, Omega word, forgetting, and
  closure records;
- one history name in the derivative and history word;
- one \(E\) source between the energy tag and characteristic tree;
- one \(U,Y\) source pair between the derivative and characteristic tree;
- exact A/M occurrence counts and distinct occurrence names;
- the ordered domain cycle \(KX\), \(Xt\), \(tK\); and
- non-erasure of fibres, unused syntax, and residuals.

These checks make the package well formed.  They do not prove that its
subsystems commute, preserve one another, or admit a common interpretation.

---

## 8. The syntax restriction obtained

The pendulum factors add one finite restriction to Bootstrap Zero:

\[
\boxed{
\begin{gathered}
\text{Every claimed closed axis--circle history must carry}\
\text{a distinct history parameter, an explicit derivative edge,}\
\text{a perturbation occurrence, a finite A/M characteristic tree,}\
\text{a three-domain cyclic word, a forgetting fibre,}\
\text{a closure witness, and a retained residual.}
\end{gathered}
}
\tag{PendulumRestriction}
\]

This restriction connects four previously adjacent layers without collapsing
them:

| layer | supplied factor |
|---|---|
| geometric values | exact line, finite circle, named piercing |
| domain placement | ordered \(KX\to Xt\to tK\) decomposition |
| threading | history name, derivative atom, connectors, retained word |
| multi-hole A/M | energy occurrence and characteristic tree |

The record is a candidate finite closure of the syntax-factor inventory.  It
is not a closure theorem for the language.

---

## 9. What cannot be derived at this stage

The following implications are forbidden:

1. a pendulum equation implies a closed orbit;
2. a closed syntax circle implies a repeated execution;
3. an energy tag implies conservation, motion, or direction;
4. forgetting implies quotient validity or circle formation;
5. `circle_Omega` implies an \(H^2\) compactification or three cusps;
6. a shared cycle name proves agreement of the five interpreters;
7. the characteristic A/M trees are equal, equivalent, or solvable; and
8. \(D_\zeta\) is physical time differentiation.

In particular, the sentence “the observed behavior near Omega comes from the
perturbed axis” remains a proposed interpretation.  The present grammar only
makes it possible to state later what evidence such an interpretation would
have to preserve.

---

## 10. Deferred coordination proofs

Once syntax-factor placement is accepted, the next stage may ask for separate
proofs of:

1. **namespace coherence:** substitutions cannot turn `HistoryName` into the
   domain role `t`;
2. **derivative typing:** history derivative atoms preserve declared source
   and value types;
3. **occurrence coherence:** A/M copies match the thread production ledger;
4. **cycle coherence:** the three through pieces glue to exactly the cyclic
   word named by `Circle(γ)`;
5. **forgetting coherence:** projection retains the declared fibre and
   residual;
6. **closure coherence:** closure is stable under allowed alpha-renaming but
   not inferred from endpoint return; and
7. **interpreter coherence:** the three domain views, threading view, and A/M
   view preserve the shared identifiers required by this package.

None is proved by the current formation checker.

---

## 11. Executable finite calibration

The companion test checks:

1. history names and domain roles remain different typed identities even if
   their display strings coincide;
2. \(D_\zeta\) cites the same \(U,Y\) sources as the characteristic cell;
3. the A/M spelling has exact source census \(Y:2,U:3,E:1\) and six fresh
   occurrences;
4. adjacent routing preserves that occurrence multiset and cannot create the
   required copies;
5. the axis, circle, piercing, history, forgetting, and closure records use
   the same names;
6. the Omega word has exactly the ordered cycle \(KX,Xt,tK\) with three
   explicit connectors;
7. neither a characteristic cell nor endpoint return constructs a closure
   witness;
8. forgetting without fibre or residual is rejected; and
9. the whole finite package forms without evaluating an equation.

---

## Conservative conclusion

The pendulum contributes a useful syntax constraint precisely because its
meaning is withheld.  Its formal skeleton forces a history derivative, an
energy occurrence, repeated A/M uses, a named cyclic carrier, and explicit
closure and forgetting records to coexist without allowing any one of them to
stand in for the others.

Thus the proposed restriction can close the present finite inventory of
syntax factors.  Whether those factors are coordinated is the next question,
not an assumption smuggled into this one.
