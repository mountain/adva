# Finite Triadic Satisfaction Logic

Status: exploratory finite calibration extending
[`0038-triadic-characteristic-inference-calibration.md`](0038-triadic-characteristic-inference-calibration.md)
and
[`0042-atiyah-legendre-triadic-crossing.md`](0042-atiyah-legendre-triadic-crossing.md).

This note studies one deliberately small question:

> After a finite observer has inferred individual characteristics, is the next
> computable characteristic an order of entailment induced by one typed
> three-domain satisfaction form?

The proposed finite object is

\[
\Lambda_Q:
\mathcal T_Q\times\mathcal X_Q\times\mathcal K_Q
\longrightarrow
\mathbb S,
\]

where \(\mathbb S\) is read as a Sierpinski observation: positive finite
evidence can be returned, while failure to observe evidence is not promoted
to a general proof of negation.

The Legendre three-cusp closure from note 0042 supplies the bounded carrier.
The selected positive-unipotent lifts close to \(-I\), the compatible
monodromy convention closes to \(I\), and a two-cusp prefix is noncentral.
A projective observer identifies \(I\) and \(-I\).  The finite fixture computes
that observer quotient, retains its exact fine preimages as a residual, takes
all three kinds of opposite-pair section, and derives an entailment preorder
from inclusion of proposition supports.

This is not a stable logic, proposition, topology, observer, quotient, or
learning API.  It is a research-local finite algorithm and executable
calibration.  Rust remains the authority for checked Adva program histories;
Python owns only the finite research relation and exact external matrix
oracle.  The active `ProgramSlice` priority remains unchanged.

## 0. Executive result

The finite calibration supports the chain

\[
\boxed{
\text{triadic satisfaction}
\longrightarrow
\text{opposite-pair sections}
\longrightarrow
\text{observer quotient}
\longrightarrow
\text{entailment by support inclusion}.
}
\]

The first object characteristic is a proposition-like observed support.  The
first relational characteristic is its refinement or entailment order.

For the lifted Legendre observer, the finite accepted points are

\[
\ell_I=(t_I,x_I,k_I),
\]

\[
\ell_{-I}=(t_{-I},x_{-I},k_{-I}),
\]

and

\[
\ell_{\mathrm{open}}=(t_o,x_o,k_o).
\]

The projective observer quotient sends

\[
\ell_I,\ell_{-I}
\longmapsto
\ell_{[I]},
\]

while

\[
\ell_{\mathrm{open}}
\longmapsto
\ell_{\mathrm{open}}^{\mathrm{proj}}.
\]

The quotient does not delete the distinction silently.  Its residual records

\[
q^{-1}(\ell_{[I]})
=
\{\ell_I,\ell_{-I}\}.
\]

Define the fine propositions

\[
P_I=\{\ell_I\},
\qquad
P_{-I}=\{\ell_{-I}\},
\]

and

\[
P_{\mathrm{proj}}
=
\{\ell_I,\ell_{-I}\}.
\]

Then the finite entailment calculation gives

\[
P_I\preceq P_{\mathrm{proj}},
\qquad
P_{-I}\preceq P_{\mathrm{proj}},
\]

but neither reverse entailment, and

\[
P_{\mathrm{proj}}
=
P_I\lor P_{-I}
\]

as a union of finite supports.

This is the precise sense in which projective logical closure is a stable
shadow of two finer lifted outcomes.

---

# Part I. From a characteristic to a logical relation

## 1. The first object characteristic

A finite observer may begin with a one-bit distinction

\[
\chi_U:X\longrightarrow\mathbb S.
\]

The observed truth region is

\[
U=\chi_U^{-1}(1).
\]

This forgets almost everything about points inside \(U\): their histories,
geometry, construction provenance, cost, and future transport can all differ
while the characteristic returns the same positive reading.

The use of \(\mathbb S\) rather than an automatically discrete Boolean object
is intentional.  Positive evidence may be finitely witnessed while its
complement is not finitely decidable.  A classical Boolean reading requires a
stronger observer contract, a decidable or clopen region, or a declared
Booleanization that records what it forgets.

## 2. The first relational characteristic

One proposition alone does not constitute a logic.  Given two observed
supports \(P\) and \(R\), the first canonical comparison is inclusion:

\[
P\preceq_Q R
\quad\Longleftrightarrow\quad
\operatorname{supp}_Q(P)
\subseteq
\operatorname{supp}_Q(R).
\]

This relation is reflexive and transitive.  It is therefore a preorder before
any claim of antisymmetry, syntax, proof normalization, or canonical
proposition identity.

In a spatial interpretation it is inclusion of truth regions.  In a
constructive interpretation it asks for proof or witness transport.  In a
temporal interpretation it asks whether successful histories for the premise
remain successful histories for the conclusion.

The important claim is not that these three descriptions are equal as
untyped values.  The research target is that they are typed realizations of
one entailment characteristic with explicit comparison certificates.

## 3. A three-domain satisfaction form

Let

\[
\mathcal T_Q
\]

be a finite set of temporal histories,

\[
\mathcal X_Q
\]

a finite set of spatial readings, and

\[
\mathcal K_Q
\]

a finite set of constructive witnesses.

A finite triadic form is a relation

\[
\Lambda_Q
\subseteq
\mathcal T_Q\times\mathcal X_Q\times\mathcal K_Q.
\]

Its Sierpinski-valued presentation is

\[
\Lambda_Q(t,x,k)
=
\begin{cases}
1,&(t,x,k)\text{ is accepted},\\
0,&\text{no positive evidence is present in the finite relation}.
\end{cases}
\]

Because the entire fixture is finite and explicitly enumerated, its negative
queries are decidable inside this calibration.  That finite fact must not be
extrapolated to an unrestricted program or universal-machine form.

## 4. Opposite-pair sections

Fixing two coordinates gives a characteristic on the third.

The temporal section is

\[
\Lambda_Q(-,x,k)
=
\{t\mid\Lambda_Q(t,x,k)=1\}.
\]

The spatial section is

\[
\Lambda_Q(t,-,k)
=
\{x\mid\Lambda_Q(t,x,k)=1\}.
\]

The constructive section is

\[
\Lambda_Q(t,x,-)
=
\{k\mid\Lambda_Q(t,x,k)=1\}.
\]

This is the finite computational form of the triangle principle: the
opposite pair supplies the vocabulary with which one vertex is read.

The fixture also checks incompatible mixed pairs.  A temporal history from
the \(-I\) lift and a construction witness from the \(I\) convention produce
an empty spatial section rather than a fabricated reconciliation.

---

# Part II. Legendre closure as the finite carrier

## 5. Three exact lifted outcomes

Use the vanishing directions

\[
\delta_0=a,
\qquad
\delta_1=b,
\qquad
\delta_\infty=-a-b
\]

and the positive primitive transvections from note 0042.  Their squared cusp
lifts are

\[
U_0=
\begin{pmatrix}
1&2\\
0&1
\end{pmatrix},
\]

\[
U_1=
\begin{pmatrix}
1&0\\
-2&1
\end{pmatrix},
\]

and

\[
U_\infty=
\begin{pmatrix}
-1&2\\
-2&3
\end{pmatrix}.
\]

The finite fixture uses three outcomes.

### Compatible monodromy history

\[
U_0U_1(-U_\infty)=I.
\]

This produces the point

\[
\ell_I
=
(
\text{compatible history},
\text{lifted identity},
\text{compatible word}
).
\]

### Positive-unipotent history

\[
U_0U_1U_\infty=-I.
\]

This produces

\[
\ell_{-I}
=
(
\text{positive-unipotent history},
\text{central minus identity},
\text{positive-unipotent word}
).
\]

### Open two-cusp prefix

\[
U_0U_1\notin\{I,-I\}.
\]

This produces

\[
\ell_{\mathrm{open}}
=
(
\text{two-cusp prefix history},
\text{noncentral lift},
\text{two-cusp prefix word}
).
\]

The three points form the complete accepted support of the bounded lifted
form.  They are not proposed as a complete state space of Legendre
monodromy.

## 6. Why these are genuinely typed coordinates

The temporal labels record which ordered continuation convention was used.
The spatial labels record the resulting action on the lifted rank-two
carrier.  The constructive labels record the chosen word or presentation.

The relation accepts only the declared compatible triples:

\[
\Lambda_Q(\ell_I)=
\Lambda_Q(\ell_{-I})=
\Lambda_Q(\ell_{\mathrm{open}})=1.
\]

A coordinate permutation or arbitrary recombination is not accepted merely
because its strings or scalar values look related.

This discipline is weaker than a general comparison theorem but stronger than
placing three annotations in adjacent columns.

---

# Part III. Observer quotient and accountable forgetting

## 7. Fine and coarse observers

Let \(Q_{\mathrm{lift}}\) retain:

- exact \(I\) versus \(-I\);
- the compatible versus positive-unipotent temporal convention; and
- the corresponding construction word.

Let \(Q_{\mathrm{proj}}\) forget:

- the central sign;
- which full-circuit convention supplied closure; and
- which of the two full construction words was used.

It retains only:

- closed circuit versus open prefix;
- projective identity versus projective nonidentity; and
- closed word versus prefix word.

The quotient acts on all three coordinates:

\[
q_t:\mathcal T_{\mathrm{lift}}\to\mathcal T_{\mathrm{proj}},
\]

\[
q_X:\mathcal X_{\mathrm{lift}}\to\mathcal X_{\mathrm{proj}},
\]

and

\[
q_K:\mathcal K_{\mathrm{lift}}\to\mathcal K_{\mathrm{proj}}.
\]

The coarse form is the image relation

\[
\Lambda_{\mathrm{proj}}
=
(q_t\times q_X\times q_K)(\Lambda_{\mathrm{lift}}).
\]

## 8. Quotient residual

The quotient result stores the complete finite preimage of every accepted
coarse point.

For projective closure,

\[
q^{-1}
(
\text{closed},
[I],
\text{closed word}
)
=
\{\ell_I,\ell_{-I}\}.
\]

For the open prefix,

\[
q^{-1}
(
\text{open},
\text{nonidentity},
\text{prefix word}
)
=
\{\ell_{\mathrm{open}}\}.
\]

Thus the operation reduces three accepted fine points to two accepted coarse
points while preserving an exact account of the merged distinction.

This is the first finite implementation of the pattern

\[
\boxed{
\text{observer quotient}
=
\text{coarse characteristic}
+\text{forgotten-preimage residual}.
}
\]

It is not yet an Adva semantic transformation.  The quotient is a Python
research fixture over a declared finite set.

## 9. Learning and forgetting directions

Learning moves from the coarse projective observer toward the finer lifted
observer:

\[
Q_{\mathrm{proj}}
\preceq
Q_{\mathrm{lift}}.
\]

Auditable forgetting points in the reverse direction:

\[
\Lambda_{\mathrm{lift}}
\longrightarrow
\Lambda_{\mathrm{proj}}.
\]

The coarse closure proposition is stable under learning because pulling it
back to the fine observer gives

\[
q^{-1}(P_{\mathrm{closed}})
=
P_I\lor P_{-I}.
\]

The fine observer does not refute projective closure.  It refines the single
coarse truth into two lifted alternatives.

This is the proposed local meaning of logical stability under learning:

> a coarse proposition remains the image of the refined proposition system,
> while distinctions that were previously invisible become explicit
> residual-bearing alternatives.

---

# Part IV. Entailment computation

## 10. Propositions as finite supports

Inside the fixture, a proposition is a named subset of the accepted triadic
support.

The four propositions used are:

\[
P_I=\{\ell_I\},
\]

\[
P_{-I}=\{\ell_{-I}\},
\]

\[
P_{\mathrm{proj}}
=
\{\ell_I,\ell_{-I}\},
\]

and

\[
P_{\mathrm{any}}
=
\{\ell_I,\ell_{-I},\ell_{\mathrm{open}}\}.
\]

Each proposition is checked to be well typed:

\[
\operatorname{supp}(P)
\subseteq
\operatorname{supp}(\Lambda_Q).
\]

## 11. Entailment by inclusion

The bounded entailment judgment is

\[
P\vdash_Q R
\quad\Longleftrightarrow\quad
\operatorname{supp}(P)
\subseteq
\operatorname{supp}(R).
\]

The fixture proves:

\[
P_I\vdash_Q P_{\mathrm{proj}},
\]

\[
P_{-I}\vdash_Q P_{\mathrm{proj}},
\]

and

\[
P_{\mathrm{proj}}\vdash_Q P_{\mathrm{any}}.
\]

It refutes the reverse support inclusions:

\[
P_{\mathrm{proj}}\nvdash_Q P_I,
\]

and

\[
P_I\nvdash_Q P_{-I}.
\]

The conclusion is deliberately narrow:

> after one-bit characteristics exist, support inclusion supplies a first
> computable relational characteristic.

This does not yet supply implication syntax, proof terms for entailment,
Heyting adjoints, Boolean complement, modalities, quantifiers, or a complete
proof calculus.

## 12. Why this is not merely three-valued logic

The three lifted points are not three truth values.  They are three compatible
triples in a typed relation.  A proposition still receives a finite observed
or unobserved reading at each triple.

The word “triadic” refers to the arity and coordination of satisfaction:

\[
\text{time}\times\text{space}\times\text{construction}
\longrightarrow
\mathbb S.
\]

It does not refer to replacing true and false by a third scalar truth value.

---

# Part V. Checked construction witness

## 13. A minimal Adva sign calibration

The executable fixture defines three checked one-input programs:

\[
\operatorname{id}(x)=x,
\]

\[
\operatorname{central}(x)=-x,
\]

and

\[
\operatorname{open}(x)=2x.
\]

It then applies the projective sign-forgetting readout

\[
\operatorname{proj}(x)=x^2.
\]

Hence

\[
\operatorname{proj}(\operatorname{id}(x))
=
x^2
\]

and

\[
\operatorname{proj}(\operatorname{central}(x))
=
x^2,
\]

while

\[
\operatorname{proj}(\operatorname{open}(x))
=
4x^2.
\]

The first two projected values agree extensionally, but their checked Adva
histories and IR remain distinct.  The projective observation therefore
forgets the sign without authorizing identification of the construction
histories.

The scalar program is a bounded sign calibration for the matrix quotient.  It
does not claim that Adva currently executes \(SL(2,\mathbb Z)\) matrices,
Legendre monodromy, or a general projective observer.

## 14. Authority boundary

Rust certifies:

- the three scalar program diagrams;
- explicit copy in the square readout;
- their source and occurrence structure;
- the distinct histories; and
- graph validation.

SymPy supplies:

- exact \(2\times2\) Legendre matrix multiplication;
- the external polynomial comparison; and
- no semantic program identity.

Python supplies:

- the finite triadic relation;
- its section and quotient algorithms;
- the support preorder; and
- the explicit residual preimage table.

No Python result is promoted to a stable semantic equality or certificate.

---

# Part VI. The finite algorithm

## 15. Input

The quotient computation receives:

1. three finite carriers
   \(\mathcal T_Q,\mathcal X_Q,\mathcal K_Q\);
2. a finite accepted relation
   \(\Lambda_Q\);
3. one declared map on each carrier,
   \(q_t,q_X,q_K\); and
4. finite proposition supports contained in \(\Lambda_Q\).

## 16. Section algorithm

For an opposite pair, enumerate the remaining carrier and retain exactly the
accepted triples.

For example:

\[
\operatorname{Section}_X(t,k)
=
\{x\in\mathcal X_Q\mid(t,x,k)\in\Lambda_Q\}.
\]

The other two sections are cyclic permutations of the same finite algorithm.

## 17. Quotient algorithm

Map every accepted point:

\[
(t,x,k)
\longmapsto
(q_t(t),q_X(x),q_K(k)).
\]

Deduplicate the mapped points to obtain the coarse relation.  Simultaneously
group every fine point by its coarse image.  The groups are the exact finite
residual.

No tuple is discarded without appearing in one preimage group.

## 18. Entailment algorithm

For finite propositions \(P\) and \(R\), compute

\[
\operatorname{supp}(P)
\setminus
\operatorname{supp}(R).
\]

If the difference is empty, the fixture accepts

\[
P\vdash_QR.
\]

Otherwise it returns a finite counterexample point.  This exact finite
criterion is not a general proof-search algorithm for open or infinite
observers.

## 19. Complexity

For a relation with \(N\) accepted triples:

- constructing all three singleton opposite-pair sections is \(O(N)\) after
  suitable indexing, or \(O(N)\) per unindexed query in the minimal fixture;
- quotient construction is \(O(N)\) expected time with finite hashing; and
- proposition entailment is finite set inclusion.

The point of the experiment is not asymptotic novelty.  It is to expose the
smallest data that an auditable 3-form computation must retain.

---

# Part VII. Relation to singular crossing and Omega

## 20. Crossing transport

At a general cusp, the triadic form should itself be transported:

\[
\Lambda_{Q,-}
\rightsquigarrow
\Lambda_{Q,+}.
\]

The temporal, spatial, and constructive carrier maps need not commute
strictly.  A future crossing computation should compare the two transported
relations and produce

\[
\Theta_{Q,c}
\]

or an accountable residual.

The present fixture does not compute this cube.  It calibrates the simpler
observer quotient at one already-computed closure event.

## 21. No numerical Omega claim

The finite sign quotient is computable and finite.  It is not Chaitin
\(\Omega_U\), a halting domain, or a proof of structural noncompletion.

The possible future connection is through a universal prefix-free machine
whose halting domain is a computably enumerable open set.  Its Sierpinski
characteristic can be positively observed while no total computable discrete
Boolean characteristic decides both halting and nonhalting.

That construction requires an explicit universal interpreter, prefix
weights, observer maps, and three-domain comparison theorem.  None is supplied
by this note.

---

# Part VIII. Conservative conclusion

## 22. What the calibration establishes

Within the declared finite carriers, the fixture establishes:

1. one explicit three-domain satisfaction relation;
2. exact temporal, spatial, and constructive opposite-pair sections;
3. exact rejection of incompatible mixed readings;
4. one three-coordinate observer quotient;
5. an exact preimage residual for every accepted coarse point;
6. projective closure as the merge of \(I\) and \(-I\);
7. a finite entailment preorder by proposition-support inclusion;
8. the decomposition
   \(P_{\mathrm{proj}}=P_I\lor P_{-I}\); and
9. distinct Rust-checked construction histories hidden by one projective
   scalar readout.

## 23. What it suggests

The evidence supports the working ladder

\[
\boxed{
\text{object characteristic}
\to
\text{relational characteristic}
\to
\text{logical order}
\to
\text{transported logic}.
}
\]

It also supports the interpretation:

\[
\boxed{
\text{logical stability under learning}
=
\text{conservative refinement}
+\text{accountable forgetting}.
}
\]

## 24. What is not established

The note does not establish that:

- every finite observer admits a useful triadic satisfaction form;
- the form is unique or canonical;
- support inclusion is the correct constructive entailment;
- every spatial truth region is open;
- every open predicate admits Booleanization;
- the projective quotient is a general learning map;
- the quotient preserves arbitrary logical connectives;
- the three domains contain information irrecoverable from every pair;
- the Legendre sign is an observer-independent anomaly;
- a general crossing coherence cube exists;
- a complete or decidable 3-form proof calculus exists; or
- any \(\Omega\)-type theorem follows.

No stable API or claim registry entry is justified by this calibration alone.

---

# Part IX. Red-team opinion

## 25. The relation may be a hand-written lookup table

The finite accepted triples were chosen from already-understood Legendre
outcomes.  The experiment computes sections and quotients correctly, but it
does not yet infer the relation from raw observations.

The next learning test must reconstruct at least part of \(\Lambda_Q\) from
incomplete fibres and report alternative compatible forms when it is not
identifiable.

## 26. Support inclusion may be too extensional

Two propositions with the same accepted support can have different proof
histories or future crossing behaviour.  A mature entailment judgment may
require a constructive transformer and certificate, not only set inclusion.

The present preorder is therefore the observer-level shadow of entailment,
not its final constructive definition.

## 27. Genuine triadicity is not proved

Every accepted triple in the fixture is diagonal and each opposite pair
determines the third.  This makes the section calculation exact but also means
that pairwise data may reconstruct the whole finite relation.

A genuinely triadic test must exhibit either:

- pairwise-compatible projections with two different global fillings;
- a nontrivial total coherence defect;
- or construction-sensitive future transport not recoverable from the
  temporal and spatial pair.

## 28. Boolean language can conceal semidecidability

The finite fixture can decide membership because its relation is explicitly
enumerated.  A universal or open observer may only enumerate positive
evidence.

Future code must distinguish:

- observed false in a declared finite exhaustive carrier;
- absence of evidence under an incomplete search; and
- certified negation.

Only the first is used here.

## 29. The projective quotient is unusually clean

The central sign gives a two-element fine fibre with a transparent quotient.
General observer forgetting can have nonuniform fibres, partial maps,
relation-valued transport, or no canonical coarse representative.

The algorithm should later be pressure-tested on a region-indexed branch
example such as \(x^3-3x\).

---

# Part X. Next exact questions

## 30. First next question: constructive entailment

Replace support inclusion by an explicit checked transformer

\[
\operatorname{Prf}_Q(P)
\longrightarrow
\operatorname{Prf}_Q(R)
\]

and compare its temporal execution and spatial inclusion readings.

The transformer must preserve source and occurrence identity and return a
certificate.  This belongs downstream of the current stable semantic
priorities.

## 31. Second next question: ambiguous global fillings

Construct two finite triadic relations with identical pairwise projections
but different accepted triple sets.  Ask which additional observation or
coherence condition separates them.

This would be the smallest falsifiable test of genuine three-way information.

## 32. Third next question: crossing transport

Let a parameter path cross a simple discriminant stratum.  Compute the
before-and-after forms

\[
\Lambda_{Q,-},
\qquad
\Lambda_{Q,+},
\]

their three carrier transports, and the total comparison defect.

The result should be strictly coherent, centrally coherent, or `Unknown` with
an explicit residual.

## 33. Immediate working thesis

The most conservative current thesis is:

\[
\boxed{
\begin{aligned}
&\text{a proposition is a finite observed support of a typed 3-form;}\\
&\text{entailment is initially the refinement order of those supports;}\\
&\text{learning refines the form, while observer quotients forget it;}\\
&\text{logical stability requires those two directions to remain
accountably compatible.}
\end{aligned}
}
\]

The next general computation is not yet a universal logic engine.  It is a
finite, certificate-bearing transport of triadic forms and their induced
entailment order.
