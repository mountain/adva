# Independent longitudes confirm the corrected triple-linking calculation

Date: 2026-09-11. Direction and question: Mingli Yuan / 苑明理.
Analysis, implementation and writing: ChatGPT (OpenAI), submitted through
Mingli Yuan's GitHub account as an authorized proxy. Account use is not
endorsement, review or a correctness guarantee.

Status: executed external exact finite cross-check; no native admission.
Base main: `dbfea1b521caf45f737569f760132827f1849b55`.

## Result

The preferred-longitude calculation agrees with the complete surface answer
on every declared input. In particular, it distinguishes the golden rectangles
from the concentric-square counterexample without counting surface triple
points. The two fixed projection directions give different diagrams:

| Configuration | Crossings along (7,11,19) | Crossings along (13,5,23) | Longitude mu, both views | Prior surface mu |
| --- | ---: | ---: | ---: | ---: |
| Golden rectangles | 12 | 8 | -1 | -1 |
| Uniform scale by two | 12 | 8 | -1 | -1 |
| Common translation by (1,2,3) | 12 | 8 | -1 | -1 |
| Rational aspect ratio two | 12 | 12 | -1 | -1 |
| Concentric orthogonal squares, half-widths 3,2,1 | 8 | 4 | 0 | 0 |
| Third golden component separated at y=10 | 4 | 0 | 0 | 0 |

The ordering is (z0,x0,y0), with the oriented boundaries specified in the
[surface correction](borromean-boundary-word-correction.md). Writing
i=z0, j=x0, k=y0, both golden diagrams yield

\[
E(\lambda_k)=1-X_iX_j+X_jX_i+O(3).
\]

The coefficient of X_i X_j is -1. The other two longitudes give the same value
under cyclic relabelling. All their linear coefficients vanish. For the
concentric squares and separated component, all three longitude expansions
equal 1 through degree two. This last observation alone would not identify an
arbitrary link as the unlink.

## Independent route and its shared boundary

The new [checker](../../experiments/borromean_longitude_audit/check.py) reads the
18 admitted inputs from the byte-pinned previous report. A small adapter turns
each oriented rectangle into four ordered vertices. The diagram and longitude
functions receive only these polygons and a projection direction. They never
receive a filled surface, surface-intersection events, surface boundary words,
m, t or a predicted mu. The harness reads the predicted invariant only after
each longitude result has been computed.

Only the exact quadratic-field class Q is reused from the pinned surface
checker. The old field module's surface routines are never called. Thus the
geometric and topological algorithms are separate, while coordinate inputs,
arithmetic implementation, Python host and mathematical trust remain shared.
This is an independent method comparison, not two independent proof kernels.

The calculation imports the preferred-longitude/Magnus interpretation from
Mellor and Melvin, *A geometric interpretation of Milnor's triple linking
numbers*, AGT 3 (2003), section 1, pp. 557-558:
<https://arxiv.org/pdf/math/0110001>. When pairwise linking numbers vanish,
the degree-two coefficient in a preferred longitude gives an integer triple
invariant. Abelianizing the conjugating prefixes is sufficient at this degree.
The general theorem is not reproved here.

The diagram convention and recursive substitution are also checked against
Audoux, Meilhan and Yasuhara, *Milnor-type invariants for surface-links and
cut-diagrams*, sections 1.3, 2.2 and 2.5:
<https://arxiv.org/pdf/2109.14578>. Its one-dimensional construction labels
signed undercrossings with their overpassing arcs. With a^b=b^-1 a b, the
ordered signed prefix conjugates the starting meridian; the normalized loop
word supplies the longitude. We use precisely the rectangle profile with
zero self-writhe, so its framing normalization is trivial.

## Diagram, meridians and longitude witnesses

For each fixed direction d, e1=d cross e_x and e2=d cross e1 orient the image
plane towards d. Dot products with these two vectors give exact projected
coordinates; the greater dot product with d identifies the overpass.
At a crossing, epsilon is sign(det(t_over,t_under,d)); its agreement with the
two-dimensional determinant is checked. The relation is

\[
a_{out}=b^{-\epsilon}a_{in}b^{\epsilon}.
\]

Each component is cut only at undercrossings. Its initial arc wraps around
the chosen starting vertex; numeric exact edge parameters locate overpasses
in the correct cyclic arc. Walking around the component gives the longitude
word as the ordered product of b^epsilon at those undercrossings. Self-crossings
are absent because the admitted input is an embedded rectangle whose plane
projects injectively. The checker enforces that condition.

For every arc, the abelianized signed prefix V produces the explicit word
V^-1 m_i V. Substitution gives a representative longitude in three component
meridians. The records retain both levels of words, their expansions and the
crossing relations, rather than retaining only the final coefficient. An
additional Chen iteration must give the same arc series through degree two.
Every Wirtinger relation, including the relation closing each component,
is checked at that degree. Agreement here does not verify the full link group
or any higher-degree quotient.

The geometry stage rejects edge-on projections, overlapping projected edges,
vertex crossings, triple projected crossings and actual boundary contacts.
All admitted crossings are transverse double events strictly inside edges;
the remaining PL corners can be rounded without changing the diagram.
No floating-point tolerance decides any incidence or crossing order.

## Checks, retained evidence and costs

The [contract](../../experiments/borromean_longitude_audit/contract.json) was
frozen before execution. Its two fixed directions were not changed or selected
after seeing results. There was no failed mathematical attempt, implementation
correction or budget increase.

- 18 admitted inputs: six configurations, seven further orientation-sign
  choices and five further component orders.
- Each input is computed in both fixed projections, then recomputed after
  rotating the starting vertex on all components: 72 accepted calculations.
- Three independent readings of pairwise linking agree: each ordered
  undercrossing sum and half the total crossing-sign sum. Only zero pairwise
  linking is admitted for the integer triple judgment.
- Explicit-word series multiplication agrees with signed ordered-pair
  counting. Cyclic longitude coefficients agree, diagonal coefficients
  vanish and off-diagonal coefficients are antisymmetric.
- Four inherited controls give UnknownCoverage, RefusedLinkContact,
  RefusedPairwiseNonzero and InvalidDomain, respectively. An additional
  edge-on direction is refused. The nonzero-linking control reaches longitude
  construction but is stopped before an integer triple judgment.
- A fresh process compares the full mathematical records, including words,
  crossings and moved-basepoint results, with the first process.

| Measurement | First process | Fresh replay |
| --- | ---: | ---: |
| Assertions | 3,659 | 3,660 |
| Diagram calls including controls | 75 | 75 |
| Longitude calls including one refusal | 73 | 73 |
| Counted work units | 200,445 | 200,446 |
| Child seconds including report publication | 0.705479 | 0.894681 |
| Supervisor seconds through measured ledger checkpoint | 0.744550 | 0.946950 |
| Child peak RSS, KiB | 19,072 | 25,320 |

Both processes installed Linux address-space and CPU limits. Each had a
20-second mathematical deadline, 25-second alarm and 26-second subprocess
timeout; the session allowed at most three attempts and used two. The last
fixed-size supervisor ledger replacement is outside its reported checkpoint
timing. Research, coding, network and integration costs are not measured here;
no speedup is claimed.

Retained files:
[first report](../../experiments/borromean_longitude_audit/attempt-01.json),
[fresh replay](../../experiments/borromean_longitude_audit/replay-01.json),
[session ledger](../../experiments/borromean_longitude_audit/execution.json),
and [finite session supervisor](../../experiments/borromean_longitude_audit/run_session.py).
Source, input and contract digests bind the results to their bytes. Reports
are intentionally complete; all three longitudes and alternate basepoints
remain available even when their coefficients agree.

For one separately bounded verification from a checkout, choose a fresh
output path and compare with the retained first report:

```sh
timeout 26s python -B -S experiments/borromean_longitude_audit/check.py \
  --compare experiments/borromean_longitude_audit/attempt-01.json \
  --output /tmp/borromean-longitude-verification.json
```

This is a single replay, not authorization for an automatic retry loop. The
committed session ledger is historical and must not be overwritten.

## What is completed, and what is still open

The finite complement-side question is now answered: properly extracted
preferred longitudes agree with the corrected surface formula on the golden
example, the zero-value counterexample and the declared controls/transports.
The older queue remains byte-identical as a historical record. This note is
its separately contracted successor, not a retroactive assertion that its
old executable already implemented the extraction.

Two details of that handoff must not be carried forward. Its recipe inserted
a factor at every crossing and inverted factors at overpasses; this successor
uses the correctly framed undercrossing word. Its agreement target was the
raw triple count; the target here is the full m-t expression. The concentric
squares show why that change matters. The signed crossing relations are
rebuilt instead of reusing historical unsigned relation words.

No arbitrary polygon-link verifier, general framing algorithm, higher Milnor
invariant, knot classification or ambient isotopy is implemented. The shared
field code has not received a separate formal proof. The Pascal-rooted
geometry obligation, native importer and catalog admission remain Open;
no native identity, Seal, free, new word or physical interpretation follows.
