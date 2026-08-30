# Optical Closure and the Observer Tower

Status: bounded Python research intertwiners between two previously checked
calibrations. This is not a stable observer, quotient, pullback, or physical
objectification API.

## Question

The local causal-cut experiment derived the six-state action

$$
\Omega(T,S,R,SR,RT,TS)
=
(-SR,-RT,-TS,T,S,R).
$$

The first optical simulation independently constructed a checked real device
chain

$$
F=P(1)L(1)P(1)
$$

with numerical action

$$
F(x,s)=(s,-x).
$$

Both square to $-I$ up to the chosen orientation. Their similarity was only a
calibration match. The missing bounded question was:

> Is there an explicit closure from the six-state carrier to the physical
> optical two-port presentation that commutes with the two actions?

A second question is forced by the first optical residual:

> Which observation level distinguishes a direct expression from a physical
> device history, and which level identifies the two?

## Three aspect-plane closures

The six-state carrier has three invariant aspect--opposite-face planes:

$$
(T,SR),
\qquad
(S,RT),
\qquad
(R,TS).
$$

For any one of these pairs $(A,A^\perp)$, define the research closure

$$
\operatorname{ev}_A(v)
=
\bigl(v_A,-v_{A^\perp}\bigr).
$$

For example,

$$
\operatorname{ev}_T(T)= (1,0),
\qquad
\operatorname{ev}_T(SR)= (0,-1),
$$

and the other four basis states are sent to zero. Therefore each closure is
onto the optical two-port carrier and has a four-state kernel.

The minus sign is not arbitrary decoration. It aligns the already derived
orientation convention

$$
\Omega(T)=SR,
\qquad
\Omega(SR)=-T
$$

with the checked optical device orientation

$$
F(1,0)=(0,-1),
\qquad
F(0,-1)=(-1,0).
$$

The executable test verifies on all six basis states and for all three pairs:

$$
\boxed{
\operatorname{ev}_A\Omega
=
F\operatorname{ev}_A
}.
$$

This is the first explicit commuting bridge between the local six-state
calibration and the physical optical simulation.

## What kind of bridge this is

The result is stronger than noticing that two coordinate arrays look alike:
the closure is stated explicitly, its kernel is known, and commutation is
checked exhaustively.

It is still weaker than a semantic derivation of optics from program geometry:

- the six-state action is reused as a prior bounded Python witness;
- the optical action comes from a separate Rust-checked device program;
- choosing one aspect plane is chart data, not a derived physical law;
- choosing the optical orientation fixes the sign;
- the four-state kernel has not been certified as physically irrelevant;
- no Rust type represents the closure or its commutation certificate.

There are three possible aspect-plane closures, and reversing the optical
orientation gives the corresponding inverse convention. Existence is
verified; uniqueness and canonicity are not.

## The observer tower

The direct quarter-turn

$$
D(x,s)=(s,-x)
$$

and the factorized physical history

$$
F=P(1)L(1)P(1)
$$

have the same numerical action but different program geometry. The forward
and inverse physical histories have different oriented actions but the same
projective action. These two facts define three strictly different observation
levels.

### Level 1: program-aware optical observation

The finest research observation records:

1. the realized two-port action;
2. the output-to-source incidence pattern;
3. the sequence of checked history-event kinds.

It distinguishes $D$ from $F$. Their source-incidence tables are

$$
I_D=
\begin{pmatrix}
1&0\\
0&1
\end{pmatrix},
\qquad
I_F=
\begin{pmatrix}
2&2\\
2&2
\end{pmatrix}.
$$

Here the diagonal entries count sources supporting each output, and the
off-diagonal entries count shared supporting sources. The labels of the
sources are not used, so the comparison is invariant under deterministic
source renaming.

### Level 2: oriented numerical observation

Forgetting source incidence and history leaves the exact realized action.
At this level,

$$
D=F,
$$

but

$$
F\ne F^{-1}=-F.
$$

Thus this observer forgets device construction while retaining the direction
of the lift.

### Level 3: projective numerical observation

Quotienting the determinant-one lift by its central sign gives

$$
[F]=\{F,-F\}.
$$

At this level,

$$
[D]=[F]=[F^{-1}],
$$

and all three induce

$$
z\longmapsto-\frac1z.
$$

The two forgetful steps are therefore

$$
\mathcal O_{\mathrm{prog}}
\longrightarrow
\mathcal O_{\mathrm{or}}
\longrightarrow
\mathcal O_{\mathrm{proj}}.
$$

The first forgets construction and source residual. The second forgets
chirality or central lift sign.

## Consequences for spectrum and closure

The fixed points $\{\pm i\}$ live at the coarsest projective level. They do
not remember whether the action was implemented directly or through a
physical device chain, and they do not distinguish the two oriented lifts.

This sharpens the earlier statement that a scalar spectrum is not its full
carrier:

$$
\text{projective spectral data}
\subsetneq
\text{oriented action data}
\subsetneq
\text{program-aware data}.
$$

The inclusions describe information content, not stable subtypes in Adva.
They also explain why equal spectrum cannot authorize history contraction or
an equation cell.

## Relation to the three properties

Each closure chooses one property and the oriented relation of the other two:

| chosen plane | direct property | opposite relation |
|---|---|---|
| temporal chart | $T$ | $SR$ |
| spatial chart | $S$ | $RT$ |
| relational chart | $R$ | $TS$ |

Every plane produces the same optical order-four shadow after the appropriate
orientation choice. This is a precise bounded realization of the intuition
that each property may be presented through the relation of the other two.

It does not show that the three physical interpretations are interchangeable.
The closures have different kernels, and no physical experiment has selected
one of them as canonical.

## Executable certificate

The extended real paraxial optics test verifies:

1. all three closures are onto the two-port presentation;
2. each closure forgets exactly the other four basis states;
3. the commuting law holds on every basis state;
4. program-aware observation distinguishes direct and factorized programs;
5. forgetting program geometry identifies their oriented actions;
6. oriented observation distinguishes forward and inverse lifts;
7. projectivization identifies the two central-sign lifts;
8. source incidence is compared by shape rather than source names.

Rust remains authoritative for the optical programs, source and occurrence
lineage, histories, validation, and execution. Python defines the bounded
six-state closures and observer tower as research witnesses.

## No-go boundaries

The result does not provide:

- a canonical choice among the three aspect planes;
- a proof that the four-state kernel is unobservable in physics;
- a stable ObservationPolicy or PredicateRegion;
- a contravariant observer pullback;
- an equation or coherence cell between $D$ and $F$;
- an internal-Hom or exponential object;
- a Gaussian beam state space or upper-half-plane derivation;
- parameter learning or mode objectification.

In particular,

$$
\mathcal O_{\mathrm{or}}(D)=\mathcal O_{\mathrm{or}}(F)
$$

does not imply a checked cell $D\Rightarrow F$. It says only that one declared
research observer cannot distinguish them.

## Next obligation

The next experiment can now introduce one tunable focusing parameter
$\kappa$ without confusing numerical equality, projective equality, and
program equality.

The minimal target is:

1. construct a checked real program $p_\kappa$;
2. choose an oriented optical output objective;
3. use the existing Rust forward differential to compute
   $d_\kappa\mathcal L$;
4. compare it with a classical finite-difference or symbolic oracle;
5. state explicitly that this is parameter sensitivity, not yet an adjoint
   pullback or learning;
6. determine which level of the observer tower the objective factors through.

Only after that result should a reverse observation action be proposed.
