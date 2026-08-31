# Triadic Characteristic Inference: A Finite Calibration

Status: exploratory research calibration extending
[`0036-triangular-symbolic-interpretation-learning-calculus.md`](0036-triangular-symbolic-interpretation-learning-calculus.md).

This note isolates one deliberately small question from the larger
three-computer programme:

> Can temporal, spatial, and constructive observations infer one finite
> characteristic through a common syntax and a common algorithmic skeleton?

The answer is positive for the two bounded affine calibrations studied here,
but only after weakening “the same algorithm” to a precise typed statement:

> The three domains share one finite characteristic algebra and one
> constraint-intersection procedure. They do not share one untyped decoder.
> Temporal and constructive interpretations are covariant, while the spatial
> interpretation is contravariant through inverse image.

The resulting variance signature is

\[
(+,-,+).
\]

This note is not a stable Adva API, a general characteristic-factorization
theorem, an implementation of observer pullback, a claim in `claims.toml`, or
a solution to the full left/right surreal reduction problem. In particular,
`rho_X` below is mathematical notation for inverse-image transport on a
finite family of intervals. It is not the reserved `D*`, a `ProgramTerm`, a
boundary swap, or a certified pullback in the current Rust core. The active
`ProgramSlice` priority and Rust semantic authority remain unchanged.

The note follows the project research format: intuition, finite evidence and
formalization, conservative conclusion, and red-team opinion.

## 1. Intuition

### 1.1 Calibrate one process through three observations

The weakest experimental method would choose three unrelated examples and
then describe them by analogy. That would not test a common characteristic
language. The stronger method is:

1. choose one finite program fragment;
2. give it temporal, spatial, and constructive interpretations;
3. expose finite observations in all three domains; and
4. ask whether the observations recover the same characteristic.

The first calibration uses one scale generator,

\[
D(x)=2x.
\]

The second uses two noncommuting generators,

\[
S(x)=x+1,
\qquad
D(x)=2x.
\]

The second example is the first one that can detect order rather than merely
repeated scale.

### 1.2 Three meanings of “characteristic” must be separated

The discussion uses three distinct levels.

A **local characteristic factor** explains one adjacent transition:

\[
b_{i-1}\xrightarrow{\lambda_i}b_i.
\]

A **cumulative characteristic** is the ordered fold of local factors:

\[
\chi_n
=
\lambda_n\odot\cdots\odot\lambda_2\odot\lambda_1.
\]

A **stationary characteristic** is a local factor that repeats throughout the
observed finite boundary:

\[
\lambda_1=\lambda_2=\cdots=\lambda_n=c.
\]

For example, in

\[
1\longrightarrow2\longrightarrow4\longrightarrow8,
\]

the stationary local factor is multiplication by `2`, while the cumulative
three-step characteristic is multiplication by `8`.

This distinction is structural. “Find a repeated law” and “compress the whole
finite program” are different inference tasks. A usable calculus needs both a
local `factor` operation and an ordered `fold` operation.

### 1.3 A finite observation never identifies a law without a hypothesis class

The observation

\[
1\longmapsto2
\]

is compatible with both `x mapsto 2x` and `x mapsto x+1`, as well as
infinitely many other functions. Characteristic inference is therefore
relative to an observer contract `Q`. At minimum, `Q` specifies:

- a bounded candidate characteristic language;
- an observational equivalence relation;
- the probes or boundary objects that are visible; and
- finite time, space, construction, and search budgets.

A characteristic is never inferred “from the data alone”. It is inferred
within the distinctions and candidate language declared by a finite
observer.

### 1.4 One characteristic algebra, three typed interpretations

Let

\[
(\mathcal F_Q,\odot,1)
\]

be a finite or finitely bounded characteristic algebra. A candidate
`f in F_Q` has three typed interpretations:

\[
\rho_t(f),
\qquad
\rho_X(f),
\qquad
\rho_K(f).
\]

The intended types are

\[
\rho_t:\mathcal F_Q\longrightarrow\operatorname{End}(T_Q),
\]

\[
\rho_X:\mathcal F_Q^{\mathrm{op}}
\longrightarrow
\operatorname{End}(\mathsf{Open}(X_Q)),
\]

and

\[
\rho_K:\mathcal F_Q
\longrightarrow
\operatorname{End}(K_{\mathrm{can},Q}).
\]

The spatial interpretation is contravariant because a temporal function acts
on observable regions by inverse image. The constructive interpretation is
stated on canonical construction forms; raw construction history requires a
separate carrier and a quotient map.

The shared syntax is therefore not “all domains perform the same primitive
operation”. It is:

\[
\boxed{
\text{one characteristic algebra}
+
\text{three typed interpretations}
+
\text{one constraint solver}.
}
\]

### 1.5 Characteristic inference is intersection of observation fibres

For a typed observation `o_D` in domain `D`, define its characteristic fibre
by

\[
\operatorname{Fib}_{D,Q}(o_D)
=
\{f\in\mathcal F_Q:
\rho_D(f)\equiv_Q o_D\}.
\]

The joint candidate set is

\[
\boxed{
\operatorname{Char}_Q(o_t,o_X,o_K)
=
\operatorname{Fib}_{t,Q}(o_t)
\cap
\operatorname{Fib}_{X,Q}(o_X)
\cap
\operatorname{Fib}_{K,Q}(o_K).
}
\]

Thus the common algorithm is not a common low-level decoding formula. It is a
common operation in characteristic space: each typed interpreter contributes
constraints, and the constraints are intersected.

### 1.6 Finite representation requires a quotient and an accountable residual

Different raw construction histories may have the same temporal function and
the same spatial inverse-image action. A finite characteristic can compress
those histories only by identifying them in an observational quotient.

The correct shape is therefore

\[
K_{\mathrm{raw}}
\xrightarrow{\chi_K}
\mathcal F_Q
\xrightarrow{\operatorname{NF}}
K_{\mathrm{can}},
\]

supplemented by a certificate or residual that retains distinctions forgotten
by `chi_K`. The characteristic is an operational quotient, not a lossless
copy of the source history.

## 2. Finite evidence and structural formalization

### 2.1 The observer contract

For this note, write

\[
Q
=
(\mathcal F_Q,\equiv_Q,\Pi_Q,B_Q),
\]

where:

- `F_Q` is the bounded candidate characteristic space;
- `equiv_Q` is exact equality or another explicitly declared observation
  relation;
- `Pi_Q` is the finite family of probes, states, intervals, or syntax
  boundaries; and
- `B_Q` is the finite resource budget.

Every uniqueness statement below is relative to such a `Q`. Enlarging the
candidate language or weakening the observations can turn a unique result
into an ambiguous one.

For an exact finite candidate set, the inference result should distinguish
four states:

```text
Unique(feature, certificate)
Ambiguous(candidates, separating_observations)
Inconsistent(countercertificate)
Unknown(search_residual)
```

`Inconsistent` is justified only when the candidate space has been exhausted
or exclusion is otherwise certified. Search timeout or incomplete enumeration
returns `Unknown`, never a proof of nonexistence.

### 2.2 Local factors and cumulative folding

For the `i`-th adjacent triadic observation, let

\[
C_i^t,
\qquad
C_i^X,
\qquad
C_i^K
\]

be the candidate sets returned by the temporal, spatial, and constructive
decoders. Their common local-factor set is

\[
C_i=C_i^t\cap C_i^X\cap C_i^K.
\]

When `C_i={lambda_i}`, the cumulative characteristic is

\[
\chi_n
=
\lambda_n\odot\cdots\odot\lambda_1.
\]

The stationary test is separate:

\[
\operatorname{stationary}
\Longleftrightarrow
\lambda_1=\cdots=\lambda_n.
\]

The spatial decoder must carry its own arrow orientation. If a temporal step
is

\[
x_i=g_i(x_{i-1}),
\]

then the corresponding region relation is

\[
U_{i-1}=g_i^{-1}(U_i).
\]

A uniform implementation may share the outer inference loop, but it must not
erase this typed reversal.

### 2.3 Calibration I: one scale generator

Let the candidate language consist of positive rational scale contexts

\[
c_a[\square]=a\cdot\square,
\qquad
a\in\mathbf Q_{>0}.
\]

The temporal interpretation is

\[
\rho_t(c_a)(x)=ax.
\]

For the observed chain

\[
1\longrightarrow2\longrightarrow4\longrightarrow8,
\]

each local temporal factor is `c_2`.

For the spatial interpretation, let

\[
I_r=(-r,r)
\]

and act by inverse image:

\[
\rho_X(c_a)(I_r)
=
\{x:ax\in I_r\}
=
I_{r/a}.
\]

Repeated inverse-image transport gives

\[
I_1
\longmapsto
I_{1/2}
\longmapsto
I_{1/4}
\longmapsto
I_{1/8}.
\]

The visible radius is multiplied by `1/2`, but the inferred program
characteristic is still `c_2`. Without the contravariant type, the spatial
observation would be misread as the opposite scale.

For the constructive interpretation, retain the uncontracted contexts

\[
x
\longrightarrow
2x
\longrightarrow
2(2x)
\longrightarrow
2(2(2x)).
\]

Every step adds the same one-hole context `c_2`. Thus all three domains recover
one stationary local factor,

\[
c_2,
\]

and the cumulative three-step characteristic is `c_2^3`.

This calibration establishes typed agreement for repeated scale. It does not
yet test order, noncommutation, branching, or information loss.

### 2.4 Two basic compatibility laws

The scale calibration satisfies two commuting conditions.

Evaluation compatibility is

\[
\operatorname{eval}(\rho_K(f)(e))
=
\rho_t(f)(\operatorname{eval}(e)).
\]

Open-set compatibility is

\[
x\in\rho_X(f)(U)
\Longleftrightarrow
\rho_t(f)(x)\in U.
\]

The second equation defines inverse-image transport. It is the reason that the
spatial interpretation reverses composition.

### 2.5 Calibration II: two noncommuting generators

Define

\[
S(x)=x+1,
\qquad
D(x)=2x.
\]

Use chronological notation: `p;q` means first execute `p`, then execute `q`.
Therefore

\[
\llbracket p;q\rrbracket
=
\llbracket q\rrbracket\circ\llbracket p\rrbracket.
\]

The two minimal words differ:

\[
\llbracket S;D\rrbracket(x)=2x+2,
\]

\[
\llbracket D;S\rrbracket(x)=2x+1.
\]

Hence

\[
S;D\not\equiv D;S.
\]

This is the first calibration in which the characteristic must retain order.

### 2.6 The binary affine characteristic monoid

Every word generated by `S` and `D` denotes a unique affine map

\[
x\longmapsto2^k x+b,
\qquad
(k,b)\in\mathbf N\times\mathbf N.
\]

Define

\[
\chi(p)=(k,b).
\]

The generator characteristics are

\[
\chi(S)=(0,1),
\qquad
\chi(D)=(1,0).
\]

A chronological scan updates the pair by

\[
(k,b)\xrightarrow{S}(k,b+1),
\]

\[
(k,b)\xrightarrow{D}(k+1,2b).
\]

Therefore

\[
\chi(S;D)
:
(0,0)\xrightarrow{S}(0,1)\xrightarrow{D}(1,2),
\]

while

\[
\chi(D;S)
:
(0,0)\xrightarrow{D}(1,0)\xrightarrow{S}(1,1).
\]

Thus

\[
\chi(S;D)=(1,2),
\qquad
\chi(D;S)=(1,1).
\]

Let `f_1=(k_1,b_1)` be executed first and `f_2=(k_2,b_2)` second. Their
characteristic product is

\[
\boxed{
f_2\odot f_1
=
(k_1+k_2,\;2^{k_2}b_1+b_2).
}
\]

Indeed,

\[
(2^{k_2}x+b_2)\circ(2^{k_1}x+b_1)
=
2^{k_1+k_2}x+2^{k_2}b_1+b_2.
\]

The identity is `(0,0)`. This finite algebra is the binary affine monoid used
in the rest of the calibration.

### 2.7 Order reduction is a deformed crossing, not a swap

The generators satisfy the extensional relation

\[
\boxed{
S;D\equiv D;S;S.
}
\]

Moving `D` leftward across `S` duplicates the translation generator. The
operation is not a commutative swap:

\[
S;D\not\equiv D;S.
\]

Every characteristic pair has the canonical representative

\[
\operatorname{NF}(k,b)=D^k;S^b,
\]

whose denotation is `2^k x+b`.

The safe engineering route is to compute `(k,b)` by the linear scan above and
materialize the canonical word only when needed. This note does not prove that
an abstract presentation using only the rewrite `S;D -> D;S^2` is terminating
and confluent under every rewriting strategy. Uniqueness here is uniqueness of
the affine pair and of the selected canonical section, not a completed general
rewriting theorem.

### 2.8 Temporal recovery of `(k,b)`

The temporal interpretation is

\[
\rho_t(k,b)(x)=2^k x+b.
\]

Under the declared affine hypothesis class, exact probes at `0` and `1`
suffice:

\[
y_0=\rho_t(k,b)(0)=b,
\]

\[
y_1=\rho_t(k,b)(1)=2^k+b.
\]

Hence

\[
b=y_0,
\qquad
2^k=y_1-y_0.
\]

For `S;D`, the probe table is

\[
0\mapsto2,
\qquad
1\mapsto4,
\]

which recovers `(1,2)`. For `D;S`, it is

\[
0\mapsto1,
\qquad
1\mapsto3,
\]

which recovers `(1,1)`.

A single probe need not identify the generator. At `x=1`, both `S` and `D`
produce `2`. The second probe is a separating observation supplied by `Q`, not
by the raw value alone.

### 2.9 Spatial recovery of `(k,b)`

Write an open interval as

\[
I(m,r)=(m-r,m+r),
\qquad r>0.
\]

For

\[
f_{k,b}(x)=2^k x+b,
\]

the inverse image is

\[
\boxed{
\rho_X(k,b)(I(m,r))
=
f_{k,b}^{-1}(I(m,r))
=
I\left(\frac{m-b}{2^k},\frac{r}{2^k}\right).
}
\]

Suppose the observer records

\[
I(m,r)\longmapsto I(m',r').
\]

Within the exact binary affine language,

\[
2^k=\frac{r}{r'},
\qquad
b=m-2^k m'.
\]

Thus radius contraction recovers the dilation exponent, while centre shift
recovers the translation parameter. Radius alone cannot recover `b`.

Taking the common terminal interval `I(0,1)`, the word `S;D` has inverse image

\[
(-3/2,-1/2)=I(-1,1/2),
\]

which recovers `(1,2)`. The word `D;S` has inverse image

\[
(-1,0)=I(-1/2,1/2),
\]

which recovers `(1,1)`.

### 2.10 Constructive recovery and the raw/canonical split

Let

\[
K_{\mathrm{raw}}=\{S,D\}^*
\]

be the raw construction histories. The scan defines

\[
\chi_K:K_{\mathrm{raw}}\longrightarrow\mathcal F_{\mathrm{aff}}.
\]

Choose the canonical section

\[
\operatorname{NF}:\mathcal F_{\mathrm{aff}}
\longrightarrow K_{\mathrm{can}},
\qquad
\operatorname{NF}(k,b)=D^k;S^b.
\]

Then

\[
\chi_K\circ\operatorname{NF}
=
\operatorname{id}_{\mathcal F_{\mathrm{aff}}},
\]

but generally

\[
\operatorname{NF}\circ\chi_K
\ne
\operatorname{id}_{K_{\mathrm{raw}}}.
\]

For example,

\[
\chi_K(S;D)
=
\chi_K(D;S;S)
=
(1,2),
\]

although the raw histories are distinct.

A canonical constructive interpretation can be written

\[
\rho_K(k,b)(e)
=
S^b[D^k[e]].
\]

It preserves the affine extensional meaning, but it does not reconstruct the
source history. Source, occurrence, scope, sharing, and rewrite provenance
must remain in a separate residual or proof object.

### 2.11 The exact variance law

For characteristics `f_1` and `f_2`, with `f_1` executed first, the three
interpretations obey

\[
\rho_t(f_2\odot f_1)
=
\rho_t(f_2)\circ\rho_t(f_1),
\]

\[
\rho_X(f_2\odot f_1)
=
\rho_X(f_1)\circ\rho_X(f_2),
\]

and

\[
\rho_K(f_2\odot f_1)
\equiv_{\mathrm{can}}
\rho_K(f_2)\circ\rho_K(f_1).
\]

The spatial equation is the general inverse-image law

\[
(g\circ f)^{-1}=f^{-1}\circ g^{-1}.
\]

The triadic composition signature can therefore be summarized as

\[
\boxed{
\mathfrak I(f_2\odot f_1)
=
(T_2\circ T_1,\;X_1\circ X_2,\;K_2\circ K_1\ \mathrm{mod}\ \mathrm{can}).
}
\]

This is the precise content of the variance signature `(+,-,+)` in the finite
affine model.

### 2.12 Finite representation and normalized expansion

Consider

\[
S;D^n.
\]

The scan gives

\[
\chi(S;D^n)=(n,2^n).
\]

Its canonical word is

\[
D^n;S^{2^n}.
\]

Literal materialization of the canonical word requires exponentially many
`S` symbols, while the parameter pair requires only `O(n)` bits: `n` needs
`O(log n)` bits and `2^n` needs `n+1` bits.

This is not a theorem that every characteristic representation is shorter
than every source program. It establishes a narrower point:

> A characteristic normal form should be stored as compressed parameters, not
> as its fully expanded canonical word.

The compression is possible because `chi_K` quotients raw histories by their
common affine action. It is therefore inseparable from controlled information
loss.

### 2.13 Residual and reduction certificate

A complete research result for a raw construction `p` should have the shape

\[
\operatorname{CharacteristicResult}_Q(p)
=
(\chi_K(p),\pi_p,R_{K,Q}(p)),
\]

where:

- `chi_K(p)` is the finite operational characteristic;
- `pi_p` records the checked reduction or correspondence to the selected
  canonical representative; and
- `R_(K,Q)(p)` records intensional distinctions not carried by the
  characteristic.

In the affine calibration, `S;D` and `D;S;S` have the same characteristic but
must remain distinguishable through raw history or residual data. Equal
values and equal inverse-image actions do not authorize source or occurrence
identification.

### 2.14 A bounded triadic characteristic form

The current calibration can be packaged as

\[
\boxed{
\mathfrak C_Q
=
(\mathcal F_Q,\odot,1;
\rho_t,\rho_X,\rho_K;
\chi_K,\operatorname{NF};
\omega_{\mathrm{eval}},\omega_{\mathrm{open}};
R_Q).
}
\]

Here

\[
\omega_{\mathrm{eval}}:
\operatorname{eval}\circ\rho_K(f)
=
\rho_t(f)\circ\operatorname{eval},
\]

and

\[
\omega_{\mathrm{open}}:
 x\in\rho_X(f)(U)
\Longleftrightarrow
\rho_t(f)(x)\in U.
\]

This is a local calibration object, not yet the full opposite-edge
quote--unfold triangle of `0036`. It isolates the smaller question of whether
three typed observations consistently identify one finite characteristic.

### 2.15 One algorithmic skeleton

A bounded implementation can use the following two-stage procedure:

```text
infer_characteristic(Q, triadic_boundaries):
    local_factors = []

    for each adjacent typed triadic boundary:
        candidates = bounded_feature_space(Q)

        candidates &= temporal_constraints(...)
        candidates &= spatial_inverse_image_constraints(...)
        candidates &= construction_constraints(...)

        if search was not exhaustive:
            return Unknown(search_residual)

        if candidates is empty:
            return Inconsistent(countercertificate)

        if candidates has more than one element:
            return Ambiguous(candidates, separating_observations)

        local_factors.append(the unique candidate)

    cumulative = ordered_fold(local_factors)
    stationary = all_equal(local_factors)

    return Unique(
        local_factors,
        cumulative,
        stationary,
        certificates,
        residuals,
    )
```

The outer solver is shared. The three constraint generators are typed and are
not interchangeable.

## 3. Conservative conclusion

### 3.1 What the finite calibration supports

Within the declared deterministic affine model, the two examples support the
following claims:

1. temporal, spatial, and constructive observations can share one finite
   characteristic algebra;
2. characteristic inference can be expressed as intersection of typed
   observation fibres;
3. local factors, cumulative characteristics, and stationary characteristics
   are separate outputs;
4. temporal and constructive interpretations are covariant, while spatial
   inverse-image interpretation is contravariant;
5. noncommuting order can be retained by a finite parameter pair;
6. order reduction may require a deformed crossing law rather than a swap;
7. raw construction history maps to a finite extensional quotient and cannot
   in general be reconstructed from that quotient; and
8. a usable result must combine characteristic, certificate, and residual.

The core finite pattern is

\[
\boxed{
\text{bounded candidate algebra}
\to
\text{three typed observation fibres}
\to
\text{intersection}
\to
\text{ordered fold}
\to
\text{certificate and residual}.
}
\]

### 3.2 What is not established

The note does not establish that:

- arbitrary Adva programs admit finite characteristic normal forms;
- the three domains always identify a unique characteristic;
- the affine crossing law solves the earlier surreal `L/R` reduction problem;
- the startup calibration of the three computers is complete;
- a proper class has a finite global representation;
- contravariant interval transport is already a certified Adva observer
  pullback;
- construction history and extensional function semantics are equivalent;
- the binary affine monoid contains genuine cuts, branches, holes, sharing, or
  nontermination; or
- the full triangular learning cycle has been implemented.

The current evidence comes from finite, deterministic, injective affine maps
with exact arithmetic and a strongly restricted candidate language.

### 3.3 Engineering consequence

No stable type or operation should be added from this note alone. A future
bounded fixture should remain research-local and should preserve the current
ontology discipline:

- Rust owns program, source, occurrence, history, and certificate identity;
- inverse-image observations do not create program identities;
- canonicalization does not mutate or erase raw history;
- equal values do not authorize contraction or sharing; and
- incomplete search returns `Unknown`.

The affine pair `(k,b)` is a candidate research carrier, not a replacement for
`ProgramTerm`, `History`, `CausalCut`, `ProgramSlice`, or any existing
certificate type.

### 3.4 Immediate next calibration

The smallest useful pressure test is

\[
Q(x)=x^2.
\]

It introduces three phenomena absent from the affine examples:

1. **temporal information loss:** `x` and `-x` have the same image;
2. **spatial branching:** the inverse image of a positive interval can split
   into two open components; and
3. **constructive copy discipline:** `e^2` requires two explicit occurrences
   or an explicit copy operation and must not infer sharing from notation,
   value equality, structural hashing, or host-language aliasing.

That calibration can test whether the current characteristic monoid remains
adequate or whether the common carrier must be upgraded to a relation,
correspondence, span, or another branch-aware object. It should also test
whether one finite residual can account simultaneously for lost sign,
spatial branch identity, and constructive occurrence provenance.

## 4. Red-team opinion

### 4.1 The hypothesis class does most of the identification work

Two temporal probes recover `(k,b)` only because the candidate language has
already been restricted to `x mapsto 2^k x+b`. A richer language can fit the
same finite table in many ways. The observation contract is part of the
result, not a footnote.

### 4.2 The spatial observation is unusually informative

An exact interval supplies both centre and radius. That pair contains enough
continuous data to recover both affine parameters. A coarser spatial observer
that records only inclusion, connectivity, or radius would identify fewer
features. The present success should not be generalized to arbitrary open-set
observations.

### 4.3 Contravariance is interpretation-dependent

The `(-)` in `(+,-,+)` follows from choosing inverse image as the spatial
interpretation. Other spatial semantics may use direct image, relations,
measures, or bidirectional correspondences. The signature is established for
this calibration, not declared as a theorem of every future three-domain
model.

### 4.4 The constructive domain is richer than the other two

Temporal and spatial observations in the affine example are extensional. The
raw constructive domain retains intensional order and occurrence history.
Therefore the three carriers are not isomorphic. Their common characteristic
is a quotient visible to all three, not the total information of each domain.

### 4.5 The rewrite relation is not yet a general normalization theorem

The identity `S;D = D;S^2` proves one extensional crossing law. It does not by
itself prove a terminating and confluent rewrite system for arbitrary
extensions of the language. The parameter scan supplies a safe normal-form
algorithm only for the bounded affine monoid.

### 4.6 No genuine cut or branch has been calibrated

Affine bijections send intervals to intervals under inverse image. They do not
split regions, merge histories, encounter critical points, or create
branch-choice residuals. The present note calibrates order reversal, not yet a
spatial cut calculus.

### 4.7 Empty candidate sets require certified exhaustion

For an infinite or lazily generated candidate language, failure to find a
feature is not evidence that none exists. The `Inconsistent` result is valid
only with a finite exhaustive search or a checked exclusion argument.
Otherwise the correct result is `Unknown`.

### 4.8 The next example can expose a false unification

The square map may show that a single endomorphism monoid is too narrow. Its
temporal collapse, spatial two-branch inverse image, and constructive copy
structure may require different carriers connected by a relation rather than
three interpretations of one ordinary function object. A counterexample of
that kind would be progress: it would locate the exact point at which the
current common syntax must be generalized.
