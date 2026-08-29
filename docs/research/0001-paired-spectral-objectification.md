# Paired spectral selection and the objectification boundary

Status: bounded research calibration  
Date: 2026-08-29  
Proposal slice: T0/T3/T4, Gate B/C, and the computation--learning loop  
Executable witness: `tests/python/test_paired_spectral_objectification.py`

## Outcome

The first theory experiment should not attempt a complete Gaussian-optics,
Schrödinger, or Conway-cut implementation. The smallest useful question is:

> Which part of forward execution -> observer pullback -> parameter update ->
> spectral selection -> objectification is representation-independent, and
> where does proof-relevant information necessarily enter?

The answer separates a positive finite-dimensional kernel from two no-go
boundaries.

1. A declared nondegenerate pairing derives the observer pullback and the
   parameter differential from the same scalar evaluation.
2. A simple dominant spectral point selects paired right and left projective
   modes, with a basis-covariant residual and convergence rate.
3. A parameter-dependent chart requires a connection term. Omitting it can
   mistake pure coordinate motion for learning.
4. Value, differential, iterated action, and spectrum are not faithful to
   program history. Spectral convergence therefore supports only weak,
   task-relative objectification. It cannot construct a strong
   `ObjectificationWitness`.

Items 1--2 are classical finite-dimensional mathematics assembled as a bridge
result. Items 3--4 are the decisive semantic constraints for Adva. This
calibration does not add a pullback, spectrum, or objectification operation to
the stable API.

## Why this problem comes first

The research proposal lists several attractive first experiments. They do not
have equal dependency cost.

| Candidate | Immediate value | Present obstruction |
| --- | --- | --- |
| Full Möbius/Riccati normalizer | Exercises T0--T4 directly | Mostly classical until paired with a nontrivial observer or residual |
| Finite Conway cut residual | Closest to the proposed new geometry | Current kernel has no certified objectification or higher-cell checker |
| Gaussian ABCD chain alone | Excellent physical regression oracle | Lossless propagation computes but does not learn or select a mode |
| Paired spectral kernel | Uses checked evaluation, differentiation, source, and history now | Objectification must remain a candidate rather than a stable judgment |

The selected kernel is small enough to compute with the unfinished tool and
large enough to test the proposed universal mechanism. It also produces a
useful failure result rather than treating every numerical convergence as
confirmation.

## Typed setting

Let `A` be a finite real frontier. A parameterized checked endoprocess is

\[
  D_\theta:A\longrightarrow A.
\]

Choose, as additional interpretation data,

\[
  W_A,\qquad L_A,\qquad
  \rho_A:W_A\times L_A\longrightarrow\mathbb R.
\]

In the executable two-dimensional calibration,

\[
  W_A=\mathbb R^2,\qquad
  L_A=(\mathbb R^2)^*,\qquad
  \rho(w,\ell)=\ell^{\mathsf T}w,
\]

and the checked diagram is interpreted by a matrix `G_theta`. The transpose
below is a consequence of this declared coordinate pairing. It is not the
definition of Adva's future general `D*`.

The world action and observer action are

\[
  D_{\theta *}w=G_\theta w,
  \qquad
  D_\theta^*\ell=G_\theta^{\mathsf T}\ell,
\]

and they obey

\[
  \rho(D_{\theta *}w,\ell)
  =
  \rho(w,D_\theta^*\ell).
\]

The executable program evaluates the single scalar

\[
  \mathcal P(G,w,\ell)=\ell^{\mathsf T}Gw.
\]

Its checked forward differential contains both directions:

\[
  d_w\mathcal P=G^{\mathsf T}\ell,
  \qquad
  d_G\mathcal P=\ell w^{\mathsf T}.
\]

Thus a forward differential of the pairing is already a reverse observer
transport with respect to the world input, and an entrywise parameter
gradient with respect to the program action.

## The paired spectral selection theorem

### Theorem (finite paired spectral kernel)

Let `G_theta` be a differentiable family of real `d x d` matrices. Assume at
the parameter under consideration:

1. `lambda_0` is a simple real eigenvalue;
2. every other spectral value has modulus at most `r < |lambda_0|`;
3. the action is diagonalizable over the chosen finite extension, or a
   declared Jordan bound is included in the convergence estimate;
4. right and left eigenvectors are normalized by `v_0^T u_0 = 1`;
5. the initial world and observer have nonzero overlaps with the selected
   left and right modes.

Then:

\[
  \lambda_0^{-n}G_\theta^n w
  \longrightarrow
  (v_0^{\mathsf T}w)u_0,
\]

and

\[
  \lambda_0^{-n}(G_\theta^{\mathsf T})^n\ell
  \longrightarrow
  (u_0^{\mathsf T}\ell)v_0.
\]

In the diagonalizable case the projective error is bounded by a
condition-number factor times `(r/|lambda_0|)^n`. The selected eigenvalue
sensitivity is

\[
  \frac{d\lambda_0}{d\theta}
  =
  v_0^{\mathsf T}
  \frac{dG_\theta}{d\theta}
  u_0.
\]

### Proof

Write

\[
  G_\theta
  =
  S\,\mathrm{diag}(\lambda_0,\lambda_1,\ldots)S^{-1}.
\]

The first column of `S` is `u_0`; the first column of `S^{-T}` is `v_0`.
Expanding `w` in the right eigenbasis proves the first limit, and applying the
same argument to `G^T` proves the second. The rate follows by bounding the
remaining diagonal powers through `S` and `S^{-1}`.

Differentiate

\[
  G_\theta u_0=\lambda_0u_0
\]

and left-multiply by `v_0^T`. The differentiated eigenvector terms cancel
because `v_0^T G=lambda_0 v_0^T` and `v_0^T u_0=1`, giving the sensitivity
formula.

The pairing identity and its differential follow from bilinearity. For a
composition `G=G_m...G_1`, repeated use of the pairing transports the
observer in the opposite order, which is the finite program chain rule.

### Status

The linear-algebraic statements are classical. Their role here is a bridge
theorem: one declared pairing simultaneously organizes forward execution,
observer transport, parameter sensitivity, spectral selection, and the two
projective modes. The bridge is only a candidate interpretation of checked
Adva diagrams; it is not a general theorem about all `ProgramTerm` values.

## Basis covariance and the chart connection

For a parameter-independent change of basis `T`, set

\[
  \widetilde G=TGT^{-1},\qquad
  \widetilde w=Tw,\qquad
  \widetilde\ell=T^{-\mathsf T}\ell.
\]

Then

\[
  \widetilde\ell^{\mathsf T}\widetilde G\widetilde w
  =
  \ell^{\mathsf T}Gw.
\]

Right modes transform by `T`, left modes by `T^{-T}`, and the spectrum and gap
ratio are unchanged. This is the correct finite meaning of representation
independence for the calibration.

If `T=T_theta` depends on the optimized parameter, define

\[
  A_\theta=T_\theta'T_\theta^{-1}.
\]

Then

\[
  \widetilde G_\theta'
  =
  T_\theta G_\theta'T_\theta^{-1}
  +
  [A_\theta,\widetilde G_\theta].
\]

The commutator is not an optional numerical correction. It is the
Maurer--Cartan connection term that distinguishes physical program change
from chart motion.

For a pure chart family

\[
  \widetilde G_\theta=T_\theta G T_\theta^{-1},
\]

the scalar pairing stays constant only if world and observer representatives
are transported as well:

\[
  \widetilde w_\theta=T_\theta w,
  \qquad
  \widetilde\ell_\theta=T_\theta^{-\mathsf T}\ell.
\]

Holding those coordinate representatives fixed while differentiating only
`widetilde G_theta` generally gives a nonzero number. Such a number is a
coordinate gradient, not evidence that the system learned. A future
`ActionPresentation` must therefore declare whether a parameter is physical,
a chart coordinate, or both, and must carry the corresponding connection
rule.

## No-go: spectral closure is not history-faithful

Consider the two checked scalar programs

\[
  p_{\mathrm{share}}(x)=\operatorname{add}(\operatorname{copy}(x)),
  \qquad
  p_{\mathrm{scale}}(x)=\operatorname{scale}_2(x).
\]

For every real input,

\[
  p_{\mathrm{share}}(x)=p_{\mathrm{scale}}(x)=2x.
\]

They also have the same derivative, every finite iterate has the same value
and derivative, and their one-dimensional action presentations have the same
spectrum `{2}`.

Adva nevertheless records different operation graphs, copy histories,
occurrence paths, source partitions, and differential rule certificates.

### Proposition (spectrum/history non-faithfulness)

No observer that factors only through realized linear action, its ordinary
differential, its finite powers, and its matrix spectrum can be faithful on
the fragment containing `p_share` and `p_scale`.

### Proof

Every listed observation is a function of the common linear map `x -> 2x`, so
it assigns equal observations to both programs. The checked IR and histories
are unequal. Hence the observer does not separate the two programs.

### Consequence for the proposed universal mechanism

The following part can be universal under declared finite assumptions:

\[
  \text{execution}
  \to
  \text{pairing}
  \to
  \text{pullback/differential}
  \to
  \text{spectral selection}.
\]

The final arrow

\[
  \text{spectral selection}
  \to
  \text{strong objectification}
\]

cannot be universal in the same extensional sense. It must name an observation
policy `Q`, state which history information may be forgotten, and provide a
proof-relevant lift or cell. Spectral convergence alone gives at most weak
objectification of a task-relative mode.

This agrees with the universal-history draft: the large representable-history
semantics is faithful, while finite observers are compressions whose
faithfulness must be proved on a declared fragment.

## The executable two-mode calibration

Choose

\[
  D=\begin{pmatrix}1&0\\0&\rho\end{pmatrix},
  \qquad 0<\rho<1,
\]

and

\[
  S_\theta
  =
  R_\theta
  \begin{pmatrix}1&\sigma\\0&1\end{pmatrix},
  \qquad
  G_\theta=S_\theta D S_\theta^{-1}.
\]

For nonzero `sigma`, `G_theta` is non-normal. Its right and left selected modes
differ, so an accidental identification of pullback, inverse, and transpose
is easier to detect. The test uses Adva to:

1. compile the generic two-by-two world action;
2. compile the scalar pairing `ell^T G w`;
3. evaluate the action through checked Rust IR;
4. obtain `G^T ell` and `ell w^T` from the checked differential;
5. iterate both the world action and the derived observer action;
6. retain the K2 history counterexample.

NumPy supplies candidate matrix products, eigenvectors, basis changes, and
finite-difference data. Those values are regression oracles, not semantic
authority.

## Cross-domain interpretation

| Formal role | Lossy optical resonator | Imaginary-time spectral evolution | Learning/control reading |
| --- | --- | --- | --- |
| `w` | modal amplitude | trial state | state or representation |
| `G_theta` | round-trip operator including loss/gain | `exp(-tau(H_theta-E_0))` | parameterized transition |
| `ell` | target/adjoint field | measurement covector | objective/costate |
| `G_theta^T ell` | adjoint round trip under declared real pairing | backward observable action | credit assignment |
| dominant right mode | least-loss mode | ground-state ray | retained feature/state |
| dominant left mode | receptive/adjoint mode | same ray in self-adjoint case | sensitivity mode |
| spectral gap | mode discrimination | energy gap after exponentiation | selection rate |
| strong objectification | certified reusable cavity mode | certified spectral projector | certified reusable program unit |

The optical interpretation requires loss, gain, aperture, measurement, or
feedback. A fixed ideal lossless cavity has unit-modulus elliptic spectrum and
does not satisfy the contraction hypothesis. It computes and preserves phase;
it does not learn merely by repeated propagation.

The imaginary-time self-adjoint case is the normal subcase `sigma=0`. The
non-normal optical case is useful precisely because its left and right modes
differ. The common theorem is the paired spectral kernel, not an identification
of the physical systems.

## What the computation can and cannot certify

The current tool can certify, within its finite declared scope:

- parsing, typing, linking, and explicit linear use;
- source and occurrence history of the executable diagrams;
- scalar evaluation and structural forward differentials;
- the exact versioned operation rules used by the differential;
- separation of equal values from unequal checked histories.

The research test can additionally verify numerically:

- the bilinear pairing law in the chosen representation;
- the transpose pullback induced by that pairing;
- entrywise parameter gradients;
- paired projective convergence under a declared gap;
- fixed-basis covariance and the parameter-dependent chart correction.

It does not certify:

- a general Adva observer pullback;
- an intrinsic spectrum of arbitrary programs;
- a proof cell from numerical convergence;
- canonicity of an objectified mode;
- cross-domain physical equivalence;
- a general faithfulness or universality theorem.

## Next theorem forced by this calibration

The next positive target should be a **typed spectral objectification interface
theorem**, not a generic spectrum API. Its input data should be:

1. a checked endodiagram;
2. a declared world/observer pairing;
3. an `ActionPresentation` with replay certificate;
4. a task observer `Q`;
5. right/left residual bounds and a spectral-gap bound;
6. explicit history-forgetting and chart-transport policies.

Its output should first be candidate data for a lifting problem:

\[
  \text{spectral candidate}
  \longrightarrow
  \mathsf{Obj}_Q(D).
\]

Only after a Rust checker can verify the lift and its coherence should the
result become an `ObjectificationWitness`. The immediate mathematical task is
to characterize when two action presentations with the same paired spectral
data admit the same task-relative lift, and when the fibre of that lift remains
non-contractible because of history.

## Brief assessment

The computation--learning intuition survives, but in a more precise form.
Forward execution, dual observation, differentiation, and spectral selection
do form a portable mathematical kernel. The genuinely difficult point is the
last one: turning a selected mode into a reusable unit without erasing
proof-relevant history. Chart covariance and history faithfulness are not
decorations around the mechanism; they are its two main correctness
conditions.
