# Frame covariance: transport the question with the representation

Date: 2026-09-09. Status: **external finite calibration**, not native admission.
Direction: Mingli Yuan; arithmetic formulation and implementation: ChatGPT.
Base: `b22ff23fa22c3e2b2ce7103e1b54344d540b76a9`, after library PR #1
and Adva PR #166 were merged in dependency order.

## Question, relationship to existing work, and cut

Can a passive rational change of coordinates preserve a decomposition,
observation, energy, and solvability judgment when the frame is transported?
What fails if only the numbers are renamed?

[Research 0135](0135-reunderstanding-resource-frames-and-fuel.md) already binds
reinterpretation to conserved resources and cumulative fuel. [Research
0159](0159-frame-symmetry-triadic-continuation.md) already checks Boolean
question permutations and the transport of an explicit selection order. This
round does not repeat those experiments. It adds a nonorthogonal rational
coordinate example where the metric and observation map must change as well.
It follows the discussion of a canonical metric versus a noncanonical
eigenbasis motivated by the Yau text. No identification of this finite vector
space with a Calabi-Yau manifold, Teichmueller space, three native machines,
or physical substrates is made.

The [frozen contract](../../experiments/frame_covariance/contract.json) states
the exact domain, syntax, quantifiers, input family, controls and resources.
Only Python standard-library rational arithmetic is used. Rust-owned semantic
identities, histories, cells and certificates are untouched. The geometry
growth obligation stays Open; this is not an admitted Pascal descendant.

## Exact arithmetic model

Work in the externally named ordered space V = Q^3. Write C(x,y,z)=(y,z,x),
P=J/3 for averaging, Q=I-P, Delta=3Q, and L=(2I+C)/3. The metric is G=I.
Here Q is a projection matrix, not the rational number field or a native
observer. The observation map O=I reads three fixed, labelled outputs.

The exact identities are P^2=P, Q^2=Q, PQ=0, P+Q=I,
L^-1=(4I-2C+C^2)/3, L^T L=P+Q/3, and L^6=P-Q/27.
Thus splitting x into (Px,Qx) and retaining both parts permits exact merging.
The residual energy ||Q L^k x||^2 equals ||Qx||^2/3^k. After six steps a
nonzero residual remains nonzero; small observation does not authorize zero.

The selected problem is Delta phi=b with a phi=0, where a=(1,1,1).
It is solvable exactly when ab=0, and then phi=b/3 is the unique solution in
the declared gauge. Indeed, a Delta=0 proves necessity; on ker(a), Delta=3I
proves existence and uniqueness. Without the gauge, adding any constant
vector preserves Delta phi. This is a written elementary argument; the
matrix equalities are machine checked with Fraction, not a formal proof kernel.

For an invertible rational T put y=Tx and transport:

| Frame data | Target representation |
| --- | --- |
| P, Q, Delta, L | T A T^-1 for each operator A |
| Metric G | T^-T G T^-1 |
| Fixed-output observer O | O T^-1 |
| Gauge/compatibility covector a | a T^-1 |
| Load and selected solution | Tb and T phi |
| Source labels, history and resource account | Retained separately; no identity inferred from values |

Then O' y=Ox, y^T G' y=x^T Gx, A' y=T Ax and a' y=ax.
These identities explain covariance for every rational input under the stated
matrix hypotheses. Our finite enumeration is a calibration of their
implementation, not an enumeration of Q^3. The inverse and ordinary matrix
transpose here do not implement Adva's reserved future D* operation.

## Witnesses and refusal conditions

With T=diag(1,2,3) and x=(1,-1,0), y=(1,-2,0):

- Energy is 2 in the source and transported metric. Keeping the old I instead
  reports 5.
- The source load has zero sum and a solution. The old target sum is -1 and
  falsely rejects this same problem. The transported covector (1,1/2,1/3)
  gives zero and preserves the selected solution (1/3,-2/3,0).
- For v=(1,1,-2), direct coordinates group the first two equal values.
  The encoded vector (1,2,-6) has three distinct coordinates. Reading it
  through O'=T^-1 restores the original grouping. A coordinate partition and
  an observed-output partition are different objects.

Delta has eigenvalues 0,3,3. Both u=(1,-1,0) and v=(1,1,-2) have eigenvalue
3, but their equal-value partitions differ. The positive eigenspace is fixed;
an individual eigenvector and its level partition require further selection.
This rules out using a repeated eigenvalue alone as an operational direction.

A singular T is rejected. Zero trial fuel returns Unknown:Fuel without
solving. A compatible load with no gauge returns Unknown:NonUnique. These
are external fixture statuses, not new Rust judgments. Changing O deliberately
can be a legitimate new question, but it is not passive representation change.

## Finite execution and costs

The producer and checker share Python/Fraction and elementary matrix routines;
there is no independent trusted kernel. Fixed matrix equalities and negative
controls supplement per-instance checks. The full exact inputs, transported
frames, split parts, judgments and six-step histories are in
[evidence.json](../../experiments/frame_covariance/evidence.json).

- 27 inputs in {-1,0,1}^3 for each of a cyclic permutation, diagonal scaling
  and a fresh shear; all 81 cases pass.
- Fresh vector (2,-3,1), outside the grid, reused in each frame; all three
  additional cases pass. Total 84, with 504 retained six-step events.
- 22 exact matrix identity checks pass; seven controls have expected outcomes.
- Total 1,615 logical checks; zero search candidates; one mathematical route.
- Source and contract hashes are bound in the evidence. File readback and
  JSON equality replay pass; rational scalars serialize as [numerator,denominator].

The final invocation measured 0.131460475 s before writing metrics, including
frame construction 0.002326429 s, matrix checking 0.002625673 s, grid construction
and verification 0.082849879 s, fresh-instance reuse 0.003695542 s, controls
0.000289423 s, evidence serialization/write 0.028367748 s, and readback/JSON
replay 0.003580110 s. Other overhead includes packing and hashing. Peak RSS was
15,180 KiB on Linux. The 491,156-byte evidence size is not a memory measurement.
See [metrics](../../experiments/frame_covariance/evidence.metrics.json).

One initial successful run took 0.193760820 s with peak RSS 15,196 KiB. Ruff
then reported three style issues (non-executable shebang, import order, set
comprehension). Those were fixed, followed by exactly one confirmation replay
whose source-bound evidence is committed. No mathematical failure or search
restart occurred; combined measured invocation time is 0.325221295 s. Ruff now
passes. Research, editing, lint and network/publication time are not included.

Limits: one fixed route, 100,000 logical checks, 10 s wall alarm, 8 s CPU,
256 MiB address space, 1 MiB per output file, six steps per row. Hard OS
termination may prevent checkpointing. A caught time/memory limit records
Unknown; missing partial rows are explicit. No automatic retry or fuel reset
exists. The bounds describe this fixed script, not a hardened arbitrary-input
interpreter. Changing its constants/contract requires a newly reviewed trial.

Reproduce from the repository root on Linux:

```sh
python -I -S experiments/frame_covariance/run.py /tmp/frame-covariance.json
```

This regenerates evidence and a `.metrics.json` sidecar. Timings, platform
metadata and resulting file hashes may vary; rational witnesses should not.
No general performance benefit, expression-power gain, or user-value claim is
made. Keeping and transporting frame data has a positive construction/checking
cost. There is no cost comparison suggesting acceleration.

## Vocabulary and next minimal obligation

No new word is introduced. The existing proposed `frame` is clarified by this
external relation: it carries invariants, allowed transforms, observers and
selection conditions, together with the already required history/fuel binding.
`representation` supplies the encoding; `interpret` reads through the observer;
`split` retains both projections; `merge` reconstructs; `judge` checks the
transported problem; `revise` must record when the question itself changes.
These are working interpretations, not a claim that these words are currently
executable native calls. The replay method expands them into the matrices above.

This helps Mingli and subsequent implementers detect a false ModelGap caused
by an untransported measuring or judging rule. It does not establish a benefit
for Jiamin's real task, solve question generation, or grant native free/Seal.

The next smallest useful obligation is read-only: select one existing
Rust-checked artifact, bind one observation to its actual source/occurrence
identities, and determine whether its current IR can express the corresponding
commuting relation with a retained residual. If the carrier is missing, retain
that precise obstruction. Do not add an eigenvalue or transport API to bypass
the agenda's specialization and certificate dependencies.
