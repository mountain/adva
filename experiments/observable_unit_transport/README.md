# Observable units: means, variances, and complete-carrier transport

One finite part of priority 1 of the applied-mathematics work is now witnessed by a bounded
mathematical contract: changing compatible linear units multiplies observable
means by `a` and observable variances by `a²`, while preserving the finite
probability and observation problem. The earlier storage holder-exit obligation
remains open on its separate engineering track; it was not executed here.

Author: ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy; account
use is not his review, endorsement, or correctness guarantee. Code, synthetic
fixtures, report, and generated evidence are original work under Unknown v0.3.

## Frozen scope and elementary argument

[contract.json](contract.json) was frozen before execution against base
`f8722a5fd29b04571a2d54b54e1e6d3c17563101`. The profile is
`adva.research.observable-unit-transport.v0`. Its receiver directly reuses the
unchanged `probability_receipt` checker. This is a finite formal unit registry,
not a physical calibration certificate, native dimension type, or unit authority.

| Unit | Declared dimension | Scale against that dimension's reference |
| --- | --- | --- |
| `m` | `Length` | 1 |
| `cm` | `Length` | 1/100 |
| `s` | `Time` | 1 |
| `ms` | `Time` | 1/1000 |

For fixed finite probabilities `p_i` and values `x_i`, let `y_i = a x_i`.
Then, with `μ = Σ p_i x_i`, exact finite arithmetic gives

\[
 E[Y]=\sum_i p_i(ax_i)=a\mu,\qquad
 \operatorname{Var}(Y)=\sum_i p_i(ax_i-a\mu)^2
 =a^2\operatorname{Var}(X).
\]

The same calculation applies on every observation event of positive probability:
its conditional law stays fixed, its mean scales by `a`, and its variance by
`a²`. Averaging these conditional means gives the scaled tower expectation.
Averaging conditional variances gives the scaled within variance; squared
differences between conditional and overall means give the scaled between
variance. Zero-probability conditionals stay null: this argument does not define
a conditional law on such events.

The density `p_i/reference_i` uses unchanged probability and reference weights.
Its mean, energy, variance, observed energy, and hidden residual therefore remain
dimensionless and unchanged. This is an observable-value conversion on a fixed
finite carrier, not a transformation of a continuous density by a Jacobian.

## Receiving contract

The request has exactly `source`, `source_quantity`, `target_quantity`, and
`step`. Each quantity has exactly `dimension`, `unit`, and canonical rational
zero `origin`. The receiver checks both quantities against its registry, binds
the source quantity to the source observable's unit, and derives
`a = source_scale / target_scale`; the caller cannot redefine a unit or factor.

The complete target context copies the source, scales only `observable.values`,
changes the observable unit, and appends exactly the requested history step.
Source and derived target must both fit the unchanged parent limits before any
candidate evidence is checked. The candidate has exactly `profile`, `request`,
`source_receipt`, `target_receipt`, and `transport`. Transport has exactly
`factor`, `expectation_unit`, and `variance_unit`; the latter annotations each
contain `unit` and a true integer `power`, respectively 1 and 2.

Verification checks the source against the fixed request, checks the target
against its own context, and then binds the target to the complete requested
conversion. Only afterward are the factor, unit powers, and all moment and
conditional relations accepted. `endpoint_arithmetic_checked` remains diagnostic:
two correct endpoints do not themselves certify the requested relation.
`accepted_target` and `transport` are returned only on full success; refusals
return both as null and retain no accepted semantic delta.

## Finite results and counterexamples

The first campaign passed all **397 assertions in 37 fresh receiver processes**:
five accepted requests, 23 evidence refusals, and nine unsupported contexts.
No implementation correction or second campaign replay was needed.

| Accepted case | Factor | Source mean → target mean | Source variance → target variance |
| --- | ---: | --- | --- |
| Primary `m → cm` | 100 | 3/4 m → 75 cm | 11/16 m² → 6875 cm² |
| Inverse `cm → m` | 1/100 | 75 cm → 3/4 m | 6875 cm² → 11/16 m² |
| Fresh reuse `s → ms` | 1000 | 5/16 s → 625/2 ms | 11/256 s² → 171875/4 ms² |
| Constant primary observable | 100 | 2 m → 200 cm | 0 m² → 0 cm² |
| Identity `m → m` | 1 | 3/4 m → 3/4 m | 11/16 m² → 11/16 m² |

The primary carrier has probabilities `(1/2,1/4,1/4,0)`, uniform reference,
values `(0,1,2,3)`, and observation `(a,a,b,b)`. Reuse has probabilities
`(1/4,1/4,1/2,0)`, values `(0,1/4,1/2,1)`, and observation `(a,a,b,void)`.
Density energy remains `3/2` in both families; hidden residual remains `1/4`
in the primary and `0` in the reuse family. Independent observations compute
variance by the raw-second-moment expression `E[X²] - E[X]²`, separately from
the receiver's centered-square check.

The inverse takes its source from the actual `accepted_target` returned by a
fresh forward receiver. It restores the numerical observable and retains both
forward and inverse history entries. Identity conversion also retains its step.

Each primary/reuse family has 11 evidence mutations: wrong factor, linear rather
than quadratic variance scaling, unsquared variance unit, scaled density energy,
recomputed changed probability, observation, observable, or history, a changed
request, an invented native-authority field, and a missing density coordinate.
Another reuse mutation invents a conditional on the zero-probability `void`
event. All 23 are refused; **12 reach both local endpoint checks** before refusal.

Two controls deserve a precise distinction: changing only the final, zero-mass
observable coordinate from 300 to 301 cm, or from 1000 to 1001 ms, leaves
**every reported claim identical** after recomputation. The resulting observables
are equal `P`-almost surely. This is neither a contradiction in probability nor
a statistical distinction. The selected contract nevertheless requires the
entire declared carrier map, including zero-probability coordinates, so its
complete-context binding refuses these changes. An almost-sure quotient would
require a different explicitly stated contract.

Nine contexts are unsupported: cross-dimension conversion, forged dimension,
unknown unit, nonzero origin, noncanonical zero, Boolean numerator, source-unit
mismatch, derived value outside the parent's bound, and already-full history.
These return `InvalidContext`, not a failed physical measurement.

## Costs, evidence, and continuation

| Measurement | Value |
| --- | ---: |
| Campaign wall time | 7.183338336 seconds |
| Instrumented construction | 0.034257004 seconds |
| Fresh receiving, including process overhead | 6.878903244 seconds |
| Instrumented JSON serialization | 0.104429697 seconds |
| Independent observations | 0.005693741 seconds |
| Subsequent archive creation and hash validation | 0.105465112 seconds |
| Cumulative counted receiver work | 4,920 units |
| Largest child RSS | 11,776 KiB = 11.5 MiB |
| Supervisor peak RSS | 13,952 KiB = 13.625 MiB |

Search candidates: zero. Memory uses Linux `ru_maxrss`, not simultaneous aggregate
RSS or file size. Per-case reuse costs are retained in `execution.json`; no
speedup is claimed. Archive timing was measured separately after the campaign.
Final report encoding, uninstrumented bookkeeping, research, review, and network
costs are not separately measured.

Frozen limits are 30 seconds and at most 40 receiving processes; each receiver
has three seconds wall/CPU, 128 MiB address space, 32 KiB per wire, and one
cumulative 10,000-unit budget across both parent calls. Parent limits remain
one through six carrier elements, input rational components at most 1024,
claim components at most 10⁹, and four history entries. No square-root operation,
affine origin change, general dimension algebra, or capacity increase was added.

From the repository root, replay into a fresh directory:

```bash
python3 -B -S experiments/observable_unit_transport/run.py --output /tmp/adva-observable-unit-replay
```

See [execution.json](evidence/execution.json), [manifest.json](evidence/manifest.json),
and [attempt-1.tar.gz](evidence/attempt-1.tar.gz). The archive retains exact inputs,
outputs, commands, independent observations, and source hashes. Its recorded
environment is Python 3.12.14. It contains 192 members and occupies 17,165 bytes;
SHA-256: `a8c312bc306a9b55c408855a0ca3e694436e38276934624d0a80771fd488c662`.
Evidence is finite and reproducible; no native
word, `Close`, `free`, M6 filler, universality, learning, or practical user benefit
is claimed. It helps people and agents keep probability normalization distinct
from observable units and detect a correct calculation of the wrong conversion.

Priority 2 is a separately frozen typed 2×2 transition-kernel composition with
the complete middle marginal bound to both interfaces. A three-stage binary
joint has eight atoms, exceeding the current probability receiver's six-atom
cap. The next step must choose an explicit compatible representation or a
separately reviewed profile; it must not silently widen that cap.
