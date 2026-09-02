# Surreal Arithmetic Constraints on Bootstrap Zero Type Formation

Status: finite syntax derivation following
[note 0021](0021-surreal-cut-objectification-no-go.md),
[note 0037](0037-finite-observer-tricusp-surreal-reduction.md),
[note 0070](0070-typed-surreal-through-forms.md),
[note 0075](0075-grounded-multi-hole-through-adapter-v0.md),
[note 0079](0079-typed-hole-open-close-calibration-v0.md),
[note 0095](0095-bootstrap-zero-geometric-threading-syntax.md),
[note 0096](0096-boolean-triangle-placement-language-alignment.md), and
[note 0097](0097-threading-syntax-typed-braid-alignment.md).

This note asks whether the triangle placement grammar and the threading
grammar determine well-defined construction syntax for every Bootstrap Zero
type once they are constrained by the recursive addition and multiplication
forms of surreal arithmetic.

The answer is partial.

- They determine necessary formation coordinates and two finite constructor
  schemas.
- They do not yet determine all required constructors.
- The first missing layer is an integrated multi-hole option space with exact
  graft, occurrence, and alternative-family syntax.
- Even after that finite repair, objectification and the Omega boundary remain
  separate obstructions.

No new stable type, equality, interpreter, surreal-number semantics, or Omega
rule is introduced here.

---

## 0. Exact conclusion

Three independent obligations meet in a constructed type:

\[
\boxed{
\text{construction body }K
\quad+
\text{side and placement }X
\quad+
\text{predecessor order }t.
}
\tag{KXt-Formation}
\]

The triangle grammar supplies the three addresses and their ordered
interfaces.  The threading grammar supplies typed transport history between
ordered incidence frontiers.  Surreal arithmetic supplies recursive option
schemas that say which multi-hole arithmetic programs must populate the two
sides.

None of the three subsystems can replace the others:

- triangle placement does not construct an arithmetic term;
- a braid can route occurrences but cannot copy them;
- an AM expression does not by itself say whether it is a left or right
  option, or whether its recursive dependencies are earlier; and
- equal arithmetic values do not identify their ordered program forms.

Consequently a type constructor needs a package, not a single glyph.

---

## 1. The two surreal arithmetic constraints

Let

\[
x=\{X^L\mid X^R\},
\qquad
y=\{Y^L\mid Y^R\}.
\]

Here \(X^L,X^R,Y^L,Y^R\) are option families.  They are not the L/R
frontiers of a through cell and are not incidence polarities.

### 1.1 Addition

The recursive sum constraint is

\[
\boxed{
x+y
=
\{
x^L+y,\ x+y^L
\mid
x^R+y,\ x+y^R
\}.
}
\tag{Surreal-Add}
\]

Each option changes one operand to one earlier option and retains the other
operand.  At the raw-program level this is one two-hole context

```text
AddKernel[a,b] ::= add(use[a], use[b])
```

instantiated by four different ordered configurations:

| result side | first hole | second hole |
|---|---|---|
| L | \(x^L\) | \(y\) |
| L | \(x\) | \(y^L\) |
| R | \(x^R\) | \(y\) |
| R | \(x\) | \(y^R\) |

The comma between options is option-family concatenation.  It is not the
arithmetic `add` constructor.

### 1.2 Multiplication

Write

\[
M(a,x;b,y)=ay+xb-ab.
\tag{ProductKernel}
\]

Then the recursive product constraint is

\[
\boxed{
xy
=
\{
M(x^L,x;y^L,y),\ M(x^R,x;y^R,y)
\mid
M(x^L,x;y^R,y),\ M(x^R,x;y^L,y)
\}.
}
\tag{Surreal-Mul}
\]

An add--multiply spelling with explicit negation is

```text
ProductKernel[a,x,b,y] ::=
  add(
    add(mul(use[a], use[y]), mul(use[x], use[b])),
    neg(mul(use[a], use[b])))
```

If the AM language insists on `add` and `mul` alone, `neg(z)` must be spelled
as a declared multiplication by a typed negative unit.  The thread tag
`polarity[-]`, the crossing sign `under`, and the interface side `R` cannot be
used as arithmetic negation.

The four option pairs obey one exact side rule:

\[
\boxed{
\operatorname{side}(a,b)=L
\iff
\operatorname{side}(a)=\operatorname{side}(b).
}
\tag{ProductParity}
\]

Equal option polarities produce a left option; mixed polarities produce a
right option.  In the Boolean edge classification of note 0096, these are the
symmetric equivalence/parity pair.  The product formula therefore does not by
itself introduce a directed edge or a chiral braid history.

---

## 2. What the formulas force into the multi-hole grammar

The independent `AMForm` grammar in note 0095 can spell an expression tree,
but the two schemas require five further distinctions.

### 2.1 Ordered contexts and simultaneous grafting

The kernels have ordered hole boundaries:

\[
H_+=\langle a:A,b:A\rangle,
\qquad
H_\times=\langle a:A,x:A,b:A,y:A\rangle.
\]

An instantiation must retain an order-preserving binding

\[
\sigma:\operatorname{out}(\vec E)\longrightarrow H
\]

and a graft certificate.  Substitution is not recoverable from the evaluated
result.

### 2.2 Option families are not arithmetic sums

The left and right sides are finite ordered families

\[
\Lambda_L=\langle E_1,\ldots,E_m\rangle,
\qquad
\Lambda_R=\langle F_1,\ldots,F_n\rangle.
\]

The grammar needs a family constructor or record field.  Reusing `add` here
would confuse the branching space of possible options with addition inside
one option.

### 2.3 Source and occurrence remain different

In \(M(a,x;b,y)\), sources \(a\) and \(b\) each occur twice.  A tree spelling
therefore contains six uses:

\[
a_1y_1+x_1b_1-a_2b_2.
\]

The two uses of \(a\) and the two uses of \(b\) need distinct occurrence
names and an explicit copy or sharing certificate.  A braid permutation
preserves the incidence multiset and cannot discharge this obligation.

### 2.4 Arithmetic capabilities are type-indexed

The addition schema requires a declared operation

\[
\mathsf{add}_A:A,A\Rightarrow A.
\]

The product schema additionally requires

\[
\mathsf{mul}_A:A,A\Rightarrow A,
\qquad
\mathsf{neg}_A:A\Rightarrow A
\]

or an equivalent typed negative-unit spelling.  Hence the product constructor
cannot be generated uniformly for every declared value type merely because
the type is named \(A\).

### 2.5 Equation witnesses are not raw constructors

The displayed surreal formulas constrain a later equality or objectification
judgment.  They do not make the constructed left and right option records
literally equal to an existing raw term named `add(x,y)` or `mul(x,y)`.

The repository's finite no-go already gives the warning:

\[
\operatorname{Obj}(0\mid2)
=
\operatorname{Obj}(0\mid3)
=1
\]

although the two cut presentations are distinct.  Likewise, `add(x,y)` and
`add(y,x)` may evaluate to the same scalar while retaining different ordered
hole programs.

---

## 3. Triangle alignment

The three domains now receive a sharper syntax-only reading.

| domain | formation datum | finite question |
|---|---|---|
| \(K\) | AM kernel, hole binding, graft and copy structure | was an option program constructed legally? |
| \(X\) | L/R option family, cut placement and order certificate | on which side may the option be placed? |
| \(t\) | recursive dependency or birthday predecessor | was every referenced option available earlier? |

This does not define the domains semantically.  It identifies the three
independent certificates demanded by the surreal schemas.

The opposite-domain interfaces can consequently be read as proof
obligations:

| endpoint data | opposite interface | missing certificate |
|---|---|---|
| construction \(K\) plus placement \(X\) | \(t\) | well-founded predecessor evidence |
| placement \(X\) plus predecessor \(t\) | \(K\) | typed AM construction and graft evidence |
| predecessor \(t\) plus construction \(K\) | \(X\) | side and cut-admissibility evidence |

This is a derived alignment, not an identification of a triangle edge with a
surreal operation.

Two additional consequences follow.

First, the multiplication side rule is symmetric Boolean parity on the two
option-side inputs.  It is not `over` versus `under`.

Second, the order of the kernel holes remains raw syntax even when a later
arithmetic equality is commutative.  Reversing the holes may require a braid
block to route incidences, but the braid alone does not prove commutativity of
the gate.

---

## 4. Threading alignment

Let \(F_H\) be the occurrence frontier demanded by a kernel and let \(F_E\)
be the frontier delivered by an ordered configuration.  A construction may
contain a judgment

\[
\Sigma;Q\vdash_{\mathsf{thread}}
\tau:F_E\rightsquigarrow F_H.
\]

The judgment is useful only after occurrence production has been checked.

| need | supplying syntax | braid authority |
|---|---|---|
| reorder holes | signed crossing block | may permute complete incidences |
| duplicate \(a,b\) in \(M\) | explicit copy or shared-DAG occurrence witness | cannot supply |
| omit an unused argument | explicit discard | cannot supply |
| compute `add`, `mul`, `neg` | declared function atoms | crossings remain separators |
| identify two program orders | equation/coherence witness | same routing is insufficient |
| combine alternatives | option-family constructor | sequential thread is insufficient |

The product kernel therefore has the schematic mixed word

```text
copy/share
:: braid-block
:: mul/add/neg gates
:: braid-block
```

Its exact spelling depends on the integrated multi-hole compiler.  Bootstrap
Zero currently has no rule that derives this word from the AM tree.

---

## 5. Candidate construction package

A finite presented-cut constructor must retain at least

\[
\mathsf{Ctor}_Q(A)=
(H,\Lambda_L,\Lambda_R,\sigma,G,\tau,
\delta_t,\delta_X,R),
\tag{CtorPackage}
\]

where:

- \(H\) is an ordered typed hole context;
- \(\Lambda_L,\Lambda_R\) are ordered option families of typed AM terms;
- \(\sigma\) is the exact argument-to-hole binding;
- \(G\) retains graft, source, occurrence, copy, and discard data;
- \(\tau\) is the typed mixed routing and gate word;
- \(\delta_t\) certifies recursive predecessor descent;
- \(\delta_X\) records side placement and, when claimed, cut order evidence;
  and
- \(R\) retains alternatives and failed equality or objectification squares.

This yields three different formation levels.

### 5.1 Presented cut

\[
\frac{
\Sigma;H\vdash_{\mathsf{AM}}\Lambda_L:A
\qquad
\Sigma;H\vdash_{\mathsf{AM}}\Lambda_R:A
\qquad
\mathsf{occurs}(G,\sigma,\tau)
}{
\Sigma;Q\vdash_{\mathsf{form}}
\{\Lambda_L\mid\Lambda_R\}:\mathsf{PresentedCut}_Q(A)
}.
\tag{PresentedCut}
\]

This rule needs no numerical-order claim.

### 5.2 Well-founded option form

\[
\frac{
C:\mathsf{PresentedCut}_Q(A)
\qquad
\delta_t:\operatorname{deps}(C)\prec C
}{
C:\mathsf{WFOptionForm}_Q(A)
}.
\tag{WFOptionForm}
\]

For addition and multiplication, the recursive call measure is the ordered
pair of operand construction ranks.  Every recursive call lowers at least one
coordinate and raises neither.

### 5.3 Number-admissible form

\[
\frac{
C:\mathsf{WFOptionForm}_Q(A)
\qquad
\delta_X:\forall \ell\in L_C,\forall r\in R_C,\ \ell<r
}{
C:\mathsf{NumberAdmissibleForm}_Q(A)
}.
\tag{NumberAdmissible}
\]

Bootstrap Zero has no order or simplest-object judgment, so the last premise
is presently only the required shape of a future certificate.  Objectifying a
number from this form is a later operation and must retain a residual.

---

## 6. Candidate finite constructor rules

The two formulas do justify conditional constructor rules.

### 6.1 Sum-form constructor

If \(x\) and \(y\) have well-founded option forms, the required arithmetic
signature contains `add_A`, all four ordered grafts type-check, and every use
has certified lineage, then the option families generated by
`Surreal-Add` form a candidate

\[
\mathsf{sumForm}[x,y]:\mathsf{WFOptionForm}_Q(A).
\]

The rule does not prove the number condition or commutativity.

### 6.2 Product-form constructor

If the corresponding premises hold for `add_A`, `mul_A`, and `neg_A`, all
four product-kernel grafts type-check, repeated option occurrences are
explicitly produced, and every recursive call lowers the operand-rank pair,
then `Surreal-Mul` forms a candidate

\[
\mathsf{productForm}[x,y]:\mathsf{WFOptionForm}_Q(A).
\]

The rule does not prove distributivity, the number condition, or that its
objectification equals a semantic product.

These rules are conditional because their multi-hole premises are not yet
constructors of \(\mathcal G_0\).

---

## 7. Construction status of the existing types

| existing type form | raw formation status after this alignment | unresolved constructor data |
|---|---|---|
| value type \(A\) | declared | operation capabilities and laws |
| ordered frontier | formed | none at raw list level |
| \(\mathsf{Line}(i)\) | formed by exact incidence identity | no arithmetic equality follows |
| \(\mathsf{Thread}(F_L,F_R)\) | formed by checked atoms and braid blocks | no compiler from AM trees |
| \(\mathsf{Through}_{de}^{f}\) | formed from typed incidences | no general arithmetic grounding rule |
| \(\mathsf{Circle}(\gamma)\) | formed by finite incidence closure | not a well-founded surreal form |
| \(\mathsf{AMForm}\) | local expression grammar exists | option families, graft and occurrence proof |
| \(\mathsf{ThreadMachineForm}\) | package syntax exists | no execution or AM lowering |
| \(\mathsf{Form}_Q\) | finite record can be checked | constructor synthesis remains partial |
| \(\mathsf{View}_d\) | target sort only | no interpreter clauses or inhabitants |

Thus the answer to “does every type already have a well-defined construction
syntax?” is **no**.  Line, finite thread, finite circle, and raw AM terms do.
The integrated arithmetic cut type and the three views do not.

---

## 8. Obstructions before the Omega boundary

There are three finite obligations that must not be hidden inside Omega.

1. **Multi-hole integration.** Option families, simultaneous grafting, and
   occurrence accounting are not connected to the thread checker.
2. **Equality authority.** The recursive formulas constrain a future
   definitional or semantic equality but do not create raw equation cells.
3. **Objectification non-naturality.** Acting on a decorated form and then
   objectifying need not equal acting on the objectified number.  Exact program
   reconstruction must retain the failed square.

These are finite structural problems.  Solving or isolating them is a
precondition for knowing what remains genuinely Omega-specific.

---

## 9. The Omega boundary left open

The current repository uses several distinct Omega spellings.  Only two
well-foundedness contrasts are needed here.

### 9.1 A cyclic program is finitely writable but not a Conway predecessor DAG

The term

\[
\Omega_\Pi=\mu r:\Pi.r
\]

is legal recursive program syntax.  Its self-dependency cannot satisfy the
strict predecessor premise of `WFOptionForm`.  This separates program typing
from surreal-form well-foundedness.

### 9.2 Conway \(\omega\) is well founded but not a finite explicit option list

The presentation

\[
\omega=\{0,1,2,\ldots\mid\}
\]

has an infinite option family.  It needs a generator, lazy frontier, ordinal
rank, or another effective presentation.  A cyclic finite word is not
automatically such a certificate.

These two failures point in different directions: one lacks well-foundedness;
the other lacks finite enumeration.  This note does not identify either with
the circular threading decoration, an observer-relative halting mass, or a
geometric singularity.  The intended Omega construction rule remains open.

---

## 10. Executable finite calibration

The companion test checks:

1. the addition schema produces exactly two options on each side;
2. addition changes one operand option at a time;
3. the multiplication schema produces the four standard option kernels;
4. equal option polarities map left and mixed polarities map right;
5. every recursive arithmetic call lowers at least one operand rank;
6. the product kernel demands repeated option occurrences;
7. adjacent routing preserves the occurrence multiset and cannot implement
   those copies;
8. arithmetic negation, option side, incidence polarity, and crossing sign
   remain distinct;
9. the product rule is unavailable without a typed negation capability; and
10. a self-dependency fails the finite predecessor check.

The fixture validates the necessary finite shape only.  It does not implement
surreal objectification, prove the recursive equations, or solve Omega.

---

## Conservative conclusion

The two surreal arithmetic formulas do more than provide examples.  They
force a type constructor to retain, simultaneously:

\[
\boxed{
\text{ordered holes}
+\text{option families}
+\text{occurrence lineage}
+\text{thread history}
+\text{side placement}
+\text{predecessor evidence}
+\text{residual}.
}
\]

This yields conditional construction rules for finite well-founded sum and
product forms.  It does not yet yield construction rules for every Bootstrap
Zero type.

The next finite task is now exact: connect the multi-hole AM grammar to option
families, graft certificates, and the thread checker.  Once that bridge is
made, the remaining failure can be tested rather than merely named Omega.
