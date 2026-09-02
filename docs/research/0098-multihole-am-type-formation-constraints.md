# Multi-Hole A/M Constraints on Bootstrap Zero Type Formation

Status: syntax-factor placement following
[note 0095](0095-bootstrap-zero-geometric-threading-syntax.md),
[note 0096](0096-boolean-triangle-placement-language-alignment.md), and
[note 0097](0097-threading-syntax-typed-braid-alignment.md).

This note corrects an earlier staging error.  Recursive formulas previously
used to motivate this layer belong to a later equality or semantic inquiry.
Bootstrap Zero does not need surreal numbers, numerical objectification,
option order, or arithmetic equality in order to expose the finite syntax
required by multi-hole addition and multiplication programs.

Only raw program shapes are retained here.  They constrain hole order,
source and occurrence identity, grafting, explicit structural operations,
thread routing, and residual data.  They do not assert that two programs have
the same value or that any displayed program computes arithmetic.

---

## 0. Exact correction

The syntax-only input consists of two declared A/M kernels:

```text
AddKernel[x,y] ::= add(use[x], use[y])

ProductKernel[a,x,b,y] ::=
  add(
    add(mul(use[a], use[y]), mul(use[x], use[b])),
    neg(mul(use[a], use[b])))
```

These are expression-tree templates.  They are not equations and they carry
no distinguished result value.  In particular this note introduces no:

- surreal cut or number;
- left/right option family;
- predecessor or birthday order;
- numerical equality or inequality;
- objectification map; or
- semantic interpretation of `add`, `mul`, or `neg`.

The only conclusion is a formation package:

\[
\boxed{
\mathsf{AMPackage}_Q(A)
=
(H,E,\sigma,G,\tau,R).
}
\tag{AMPackage}
\]

Here \(H\) is an ordered hole context, \(E\) a finite A/M tree,
\(\sigma\) an exact binding, \(G\) an occurrence and graft record,
\(\tau\) a typed mixed thread word, and \(R\) the retained unused or
unprojected syntax.

---

## 1. Raw A/M terms

Let the expression grammar be the one declared in note 0095, extended only by
an explicitly declared negative operation when needed:

\[
\begin{aligned}
E ::= {}&\mathsf{atom}[m:A]
\mid \mathsf{hole}[h:A]
\mid \mathsf{use}[s,o:A]\\
&\mid \mathsf{add}[E,E]
\mid \mathsf{mul}[E,E]
\mid \mathsf{neg}[E].
\end{aligned}
\tag{AMTerms}
\]

`neg` is admitted only when its block type is declared.  It is not supplied
by right side, negative incidence polarity, `under`, duality, or conjugation.

The formation judgement is unchanged in kind:

\[
\Sigma_{\mathrm{AM}};H
\vdash_{\mathsf{AM}}E:A.
\tag{AMWF}
\]

It checks a finite typed tree.  It performs no evaluation and proves no law.

### 1.1 Ordered holes

The two kernel boundaries are

\[
H_+=\langle x:A,y:A\rangle,
\qquad
H_\times=\langle a:A,x:A,b:A,y:A\rangle.
\tag{KernelHoles}
\]

Reversing a hole word creates a different raw context.  A braid may route a
frontier into the reversed order, but it does not identify the two kernels or
prove commutativity.

### 1.2 Source and occurrence

Every use is indexed by both a source and an occurrence:

\[
\mathsf{use}[s,o:A].
\]

The product template has the occurrence pattern

\[
a_1y_1+x_1b_1-a_2b_2.
\tag{ProductOccurrences}
\]

Thus the source census is

\[
a:2,\qquad x:1,\qquad b:2,\qquad y:1,
\]

while all six occurrence names remain distinct.  Common source spelling does
not create the second occurrences.  They require an explicit `copy` or
shared-DAG witness in \(G\).

### 1.3 Capabilities are declarations

The addition template requires

\[
\mathsf{add}_A:A,A\Rightarrow A.
\]

The product template additionally requires

\[
\mathsf{mul}_A:A,A\Rightarrow A,
\qquad
\mathsf{neg}_A:A\Rightarrow A.
\]

Naming a value type \(A\) supplies none of these operations automatically.

---

## 2. Binding and grafting

Let an ordered argument configuration expose a frontier

\[
F_E=\langle i_1:(A_1,s_1,o_1),\ldots,i_n:(A_n,s_n,o_n)\rangle.
\]

A kernel instantiation retains an order-preserving typed binding

\[
\sigma:F_E\longrightarrow H
\tag{Binding}
\]

and a graft record

\[
G=(\mathsf{bindings},\mathsf{frames},\mathsf{renamings},
\mathsf{copies},\mathsf{discards}).
\tag{GraftRecord}
\]

The following distinctions are compulsory:

| datum | what formation checks | what it does not imply |
|---|---|---|
| hole order | exact typed position | commutativity |
| binding | argument occurrence to hole | evaluated substitution |
| copy witness | production of fresh occurrences | source equality |
| discard witness | retained unused input | permission to forget provenance |
| graft record | frame and renaming lineage | equality with another graft |

An unused argument remains named in \(R\).  A partially filled context keeps
its ordered complement open.

---

## 3. Alignment with triangle placement

The triangle grammar and the A/M grammar contribute different syntax.

| factor | triangle contribution | A/M contribution |
|---|---|---|
| \(K\) role | one construction address | kernel, tree, holes, graft record |
| \(X\) role | one placement address | explicit placement of incidences and cuts |
| \(t\) role | one domain address in an ordered through word | no predecessor or physical-time meaning |

The correction in the last row is essential.  Nothing in a finite A/M tree
turns the domain role \(t\) into a birthday, recursion rank, or clock.  Those
would be later declarations.

The ordered through type

\[
\mathsf{Through}_{de}^{f}
\]

may carry an A/M occurrence frontier, but it does not evaluate the tree.
Reversing \(de\) changes raw placement even if the A/M tree later receives a
commutative interpretation.

---

## 4. Alignment with threading

Let \(F_E\) be the occurrence frontier produced by the graft record and
\(F_H\) the frontier demanded by the ordered holes.  Routing is recorded by

\[
\Sigma;Q\vdash_{\mathsf{thread}}
\tau:F_E\rightsquigarrow F_H.
\tag{AMThread}
\]

Its authority is deliberately small:

| required act | syntax that supplies it | braid authority |
|---|---|---|
| reorder complete incidences | signed crossing block | sufficient for routing only |
| make repeated occurrences | explicit copy/share record | cannot be supplied by a braid |
| drop an occurrence | explicit discard record | cannot be supplied by a braid |
| apply a gate | declared function atom | not a crossing |
| compare two trees | future comparison/equality cell | not endpoint coincidence |

Consequently a product spelling has the mixed shape

```text
copy/share :: braid-block :: mul/add/neg gates :: braid-block
```

but note 0095 still has no compiler that derives this word from an A/M tree.
The shape is an obligation, not an interpreter clause.

---

## 5. Raw formation rule

A packaged expression is formed only when all syntax records agree:

\[
\frac{
\begin{array}{c}
\Sigma_{\mathrm{AM}};H\vdash_{\mathsf{AM}}E:A
\qquad
\sigma:F_E\to H\\
\mathsf{occurs}(G,E,F_E)
\qquad
\Sigma;Q\vdash_{\mathsf{thread}}\tau:F_E\rightsquigarrow F_H
\end{array}
}{
\Sigma;Q\vdash_{\mathsf{form}}
(H,E,\sigma,G,\tau,R):\mathsf{AMPackage}_Q(A)
}.
\tag{AMPackageFormation}
\]

The premise `occurs` checks at least:

1. every expression occurrence has one declared source and a fresh occurrence
   name;
2. every repeated source use has an explicit production witness;
3. binding and hole orders are total on the filled subcontext;
4. routing preserves complete incidence records;
5. unused arguments, holes, alternatives, and failed comparisons stay in
   \(R\); and
6. each gate name has the exact declared block type.

No premise checks a value, numerical equality, algebraic law, or option order.

---

## 6. What is and is not constrained

The raw kernels force the following finite vocabulary into any future
multi-hole interpreter:

\[
\boxed{
\text{ordered holes}
+\text{typed gates}
+\text{source/occurrence lineage}
+\text{copy/discard witnesses}
+\text{graft record}
+\text{thread routing}
+\text{residual}.
}
\]

They do not yet give construction rules for every Bootstrap Zero type.

| type form | raw status | open syntax |
|---|---|---|
| \(\mathsf{Line}(i)\) | independently formed | no arithmetic claim |
| \(\mathsf{Circle}(\gamma)\) | independently formed | no periodicity claim |
| \(\mathsf{Thread}(F_L,F_R)\) | independently formed | no A/M lowering |
| \(\mathsf{AMForm}\) | finite tree can be checked | no integrated compiler |
| \(\mathsf{Form}_Q\) | finite record can be checked | synthesis remains partial |
| \(\mathsf{View}_d\) | target sort only | no interpreter clauses |

In particular, the finite A/M template does not close a circle and does not
explain an Omega boundary.  Those require independent syntax.

---

## 7. Deferred coordination obligations

This note places factors but proves no mutual coherence.  A later stage must
separately establish:

1. type preservation from A/M occurrence frontiers to thread frontiers;
2. invariance of source lineage under braid routing;
3. compatibility of graft renaming with incidence gluing;
4. exact accounting of copy and discard across interpreter output;
5. preservation of open holes and residuals; and
6. any claimed comparison or equality between differently ordered programs.

These obligations are not failures of the raw grammar.  They mark the next
proof layer.

---

## 8. Executable finite calibration

The companion test checks:

1. the addition and product templates have fixed ordered hole boundaries;
2. the product template contains six fresh occurrences with source census
   \(a:2,x:1,b:2,y:1\);
3. routing preserves the occurrence multiset and cannot manufacture copies;
4. arithmetic negation, incidence polarity, crossing sign, and L/R side are
   distinct alphabets;
5. the product template is unavailable without declared `add`, `mul`, and
   `neg` operations;
6. swapped hole orders remain different raw terms;
7. option-family concatenation is not the `add` constructor; and
8. a constraint record retains both trees without equating them.

The fixture contains no surreal values, option recursion, evaluator, or
equality checker.

---

## Conservative conclusion

Multi-hole addition and multiplication already impose a strong syntax-only
restriction.  A legal expression is not merely an A/M tree: it is a tree
together with ordered holes, occurrence production, exact binding, routing,
and residual data.

This is the right boundary for Bootstrap Zero at the present stage.  It keeps
the finite construction factors visible while leaving arithmetic meaning and
all coordination theorems for later work.
