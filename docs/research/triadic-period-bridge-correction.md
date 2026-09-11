# Separate quotient descent, role cycling and interval period three

Date: 2026-09-11. Direction: Mingli Yuan / 苑明理.
Correction, implementation and writing: ChatGPT (OpenAI), through Mingli Yuan's
GitHub account as an authorized proxy. Authorization and mutual trust are not
endorsement, review or correctness guarantees.

Status: external exact finite correction with a separate real-order argument.
No native semantic change, geometry admission or entropy computation.

## Correction and preserved history

This corrects the dynamical bridge in Research 0168 at
[`8930407`](https://github.com/mountain/adva/blob/8930407e7502ef58c62dd6a82a7517a897cd60fb/docs/research/0168-triadic-cycle-and-continuation-discipline.md),
whose SHA256 is
`b29d26991d56f69b0463b68e0782c25bd7ff18e07e8bfe6ebebd0942f88ecb69`.
The original wording remains in that commit. The revised
[0168](0168-triadic-cycle-and-continuation-discipline.md) records this correction
at its entrance and replaces the faulty implications where they occurred.

| Previous inference | Corrected boundary |
| --- | --- |
| Projecting away a layer gives a self-map automatically | The next observation must be constant on each observation fibre |
| Three role stages give a period-three return map | The phase-tagged stage map and the full-cycle return map are different maps |
| A fixed point of F cubed has least period three | Earlier returns must be excluded; a fixed point also satisfies F cubed(x)=x |
| Non-injectivity or folding on an ordered base forces period three | A continuous non-injective interval map can have no period-three point |
| Retaining a layer makes the dynamics invertible and nonchaotic | A transition law and its injectivity, surjectivity and dynamical properties need separate evidence |
| The finite matrix checker derived an entropy lower bound | It checked finite matrix identities and orbit counts; the graph-to-entropy theorem and its application are separate obligations |

The signed longitude and surface-system experiments remain unchanged. So do
the source, contract and evidence of the 0167 matrix experiment. Its claim
entry now explicitly leaves entropy bounds outside its executable certificate
and withdraws the suggestion that folding by itself supplies a general
dynamical criterion. No existing exact matrix identity is retracted.

## An interval counterexample without a numerical scan

Let f(x)=x squared on [-1,1]. It is continuous, maps into [0,1], and identifies
-1/2 and 1/2. Its third iterate is x to the eighth power. Exact polynomial
composition and multiplication verify

\[
f^3(x)-x=x^8-x=x(x-1)(1+x+x^2+x^3+x^4+x^5+x^6).
\]

For negative x, x^8-x is strictly positive. On [0,1], the last factor is
strictly positive because its constant coefficient is 1 and every other
coefficient is nonnegative. Consequently the only roots on [-1,1] are 0 and 1,
both fixed by f. There is no point of least period three.

The checker verifies the coefficient identity, even exponent, positive-factor
coefficients, the collision and the fixed endpoints. The zero-exclusion step
uses the stated elementary real-order rules; it is written out above, not
inferred from sampled rational points. This is an external algebraic
certificate and argument, not a formal real-arithmetic proof kernel. A changed
constant coefficient in the factor is an explicit failing-identity control.

## A positive interval witness remains available

Use T(x)=2x on [0,1/2] and T(x)=2-2x on [1/2,1]. The two affine pieces meet
at 1 and map their endpoint pairs to [0,1], so this is a continuous interval
self-map. The exact orbit is

\[
2/7\longmapsto4/7\longmapsto6/7\longmapsto2/7.
\]

The checker verifies its distinct points and d=a<b<c, as well as refusal of
the fixed-point control a=2/3. This satisfies the hypothesis of Li and Yorke,
*Period Three Implies Chaos*, American Mathematical Monthly 82(10), 1975,
Theorem 1, p. 987: <https://www.its.caltech.edu/~matilde/LiYorke.pdf>.
That theorem supplies the all-periods and uncountable-set conclusions; this
experiment does not enumerate infinitely many periods or construct that set.
No finite-set cycle is admitted through this interval boundary.

## Construct the quotient before reading its dynamics

For a finite total map F on S and a surjection q:S -> Y, a map g satisfying
qF=gq exists exactly when

\[
q(s)=q(t)\quad\Longrightarrow\quad q(F(s))=q(F(t)).
\]

Necessity follows from the commuting equation. For sufficiency choose any
representative of each fibre and use its next observation: the condition makes
the choice independent of the representative. The checker enumerates every
pair, constructs g only after this check and verifies the equation at every
state. A failed descent keeps the conflicting state pair instead of inventing
a next observation.

| Fixture | Source F table | Observation q table | Result |
| --- | --- | --- | --- |
| Failed descent | [0,2,2,3] | [0,0,1,1] | States 0 and 1 both observe 0, then observe 0 and 1 |
| Non-injective quotient | [2,3,2,3] | [0,0,1,1] | g=[1,1]; only least period 1 occurs |
| Two-cycle quotient | [2,3,0,1] | [0,0,1,1] | g=[1,0]; least period 2 |
| Finite three-cycle quotient | [2,3,4,5,0,1] | [0,0,1,1,2,2] | g=[1,2,0]; least period 3, but not a real-interval witness |

These are mathematical set elements local to this experiment. They neither
allocate Adva identities nor authorize merging native histories.

## Role cycling and history retention

On the six states (r,x), r in {0,1,2} and x in {0,1}, define
S(r,x)=(r+1 modulo 3,x). Every state has least period three for S. The full-cycle
return on phase zero is S cubed, which is identity and has least period one.
Forgetting the phase also gives the identity map on {0,1}. All six states and
all quotient fibres are checked. Thus the choice of what counts as one step
matters before a period can be interpreted.

For the constant base map F(0)=F(1)=0, retain the entire history and append the
next value. All valid histories of lengths 1 through 5 are checked: deleting
the last entry recovers the input, and endpoint projection commutes with F.
This gives injectivity on the finite profile. On the space of all nonempty
valid histories, append is not surjective because every image has length at
least two and a singleton has none. This length argument is not a claim about
two-sided infinite-history completions. No topology or chaos verdict is
inferred for this history space or for Adva.

## Contract, results and replay

The [contract](../../experiments/triadic_period_bridge/contract.json) was
written before execution and allowed one initial child and one fresh replay,
with zero corrections. Both passed, with the full mathematical witnesses
identical after JSON serialization and fresh-process comparison.

| Measurement | First child | Replay child |
| --- | ---: | ---: |
| Assertions | 94 | 95 |
| Counted work units | 301 | 302 |
| Seconds before report publication | 0.000510 | 0.000574 |
| Peak RSS, KiB | 12,288 | 12,288 |

The supervisor took 0.074351 seconds through its final checkpoint. Linux
address-space, CPU and file-size limits were mandatory and installed in the
supervisor and both children. Child timeouts, the supervisor alarm and an
enclosing 14-second timeout include checking, replay and checkpointing. The
run stops on the first failed or unknown child, and an existing session ledger
cannot be overwritten or automatically resumed. No failed mathematical attempt
occurred. Authoring, literature reading, network and integration time are not
part of these process measurements; no performance improvement is claimed.

An integration-only registry check also tried requiring every dependency string
to name a registered claim. It failed on a pre-existing reference from
`adva.bounded-verified.symbolic-probe-matrix-shadow.v0` to the absent
`adva.exact.structural-forward-differential.v1`; the same reference is present
in the pinned base. This correction does not guess a replacement for it. TOML
parsing, claim-ID uniqueness and the dependencies of both affected entries are
checked separately. The registry is not reported as globally dependency-clean.

Retained: [checker](../../experiments/triadic_period_bridge/check.py),
[first report](../../experiments/triadic_period_bridge/attempt-01.json),
[replay](../../experiments/triadic_period_bridge/replay-01.json), and
[execution ledger](../../experiments/triadic_period_bridge/execution.json).
To reproduce this finite two-child session, choose a fresh directory:

```sh
timeout 14s python -B -S experiments/triadic_period_bridge/check.py \
  --session /tmp/triadic-period-bridge-verification
```

## Next admissible bridge

The abstract finite quotient criterion is now executable. Applying it to an
Adva example still needs a declared checked carrier, one-step transition,
observation q, reachable domain and explicit forgotten residual. Those bindings
are not supplied by this experiment. A successful finite descent would then
justify its own observed transition table; an interval interpretation would
remain an additional construction. Transport, holonomy, entropy and native
geometry admission are not closed by adding fields to that table.
