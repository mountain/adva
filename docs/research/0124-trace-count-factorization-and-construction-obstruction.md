# Research 0124: Trace count factorization and construction recovery obstruction

Status: scoped mathematical argument with a Rust research witness checker.
This is an additive continuation of Research 0114 and 0117. It does not
reinterpret their frozen artifacts or install a semantic discharge predicate.

## 1. Why this pair

Mingli Yuan asked that the unresolved mathematical questions visible in CI be
examined under finite expression and resource limits. The existing fixture
already separates two questions: which projection can be recovered from the
others, and which proposed recovery is impossible with the available inputs?
The present formalization and implementation were developed with ChatGPT.

The artifact retains both a positive witness and a negative witness. Their
meanings are fixed below, independently of the names used to present them.

## 2. Exact domain and projection types

Use the recorded paths accepted by the existing Rust trace-arithmetic path
validator: a nonempty sequence of distinct frame coordinates, one complete
three-port handoff between every adjacent pair, matching labelled endpoints,
and a mechanism word agreeing with the frames. These are document-local
formation records. They do not certify that a mechanism executed its output.

Write T for `TemporalTraceCodeV0`, S for `SpatialTraceCodeV0`, and C for the
complete `ConstructiveTraceCodeV0`, including its ordered mechanism word.
The pair checker consumes a checked `TraceArithmeticCalibrationV0` and
retains it whole, including both paths and all five open questions. This
anchors the negative witness in one common declared document coordinate.

The integer implementation uses u32 and admits the count formula exactly for
1 <= n <= floor((2^32 - 1) / 3) + 1 = 1,431,655,766. No allocation of a path
of that maximum length is asserted; it is a boundary of the arithmetic rule.

## 3. Positive result: temporal count factorization

For every path in the stated domain with n frames,

    T(p) = (n, n - 1, 3(n - 1)).

Proof: n frames have exactly n - 1 adjacent handoffs by the path invariant;
each complete handoff carries three labelled ports. The construction code
retains n as its step count. Therefore the time-count projection factors
through construction length. Equivalently, the count-level map on (S,C)
can ignore S and use this length. No timing or scheduling interpretation is
needed for this argument.

The Rust count rule rejects n = 0 and port-count overflow. The path witness
first invokes the existing validator and encoder, then independently applies
the length formula and compares it with the path-derived time code. It keeps
the raw path and its content coordinate. The count rule is reusable on one-,
two-, and three-frame paths derived from the checked source document.

This is a count-level instance of a characteristic-map idea. It supplies no
semantic time transport, clock, execution-cost prediction, or M6 filler.

## 4. Negative result: current (T,S) cannot recover full C

For observations O and target C on any declared carrier D, a necessary
condition for C = f composed with O is:

    O(p) = O(q) implies C(p) = C(q), for every p,q in D.

This follows immediately from single-valuedness of f. On the image O(D),
the condition is also sufficient: assign each observation its unique C
value. This set-theoretic criterion by itself gives no efficient algorithm.

The first recorded M6 pair violates the necessary condition for O = (T,S):

    p = compute verify compute
    q = verify compute verify
    T(p) = T(q) = (3, 2, 6)
    S(p) = S(q) = ((0,1,2), (15,16,17))
    incidence(C(p)) = (2,1,0)
    incidence(C(q)) = (1,2,0).

Thus no ordinary single-valued function of only these T and S coordinates
recovers the complete construction code on any domain containing both paths.
This is an exact finite counterexample, not a search-exhaustion inference.
It already separates mechanism incidence, before considering ordered words.

The checker rederives the source projections, requires equal T and S and
unequal complete C, and binds the two displayed outputs to the retained paths.
Exchanging compute and verify in a freshly Rust-validated document reverses
the displayed construction codes while reusing the same checking method.

## 5. What a repair must declare

An enriched input must distinguish at least this pair. One may instead ask
for a coarser construction characteristic or a relation-valued reconstruction,
but its target, observer, and retained residual must be explicit. Naming a
new function does not restore information already lost by its inputs.

The two useful terms here are **count factorization** and **projection
insufficiency**. They designate an implemented rule and a checked obstruction
criterion. They are not new stable language primitives, learned universal
concepts, or automatic entries in the inquiry vocabulary.

## 6. Artifact and replay

`TraceProjectionWitnessPairV0` has its own research schema and frozen method
identifier. It embeds the complete checked calibration, its canonical
BLAKE3 coordinate, two temporal count witnesses, and the recovery obstruction.
Decoding through `from_json` rechecks the source and every derived field;
plain Serde decoding alone is not authorization. Digests bind content and do
not authenticate external provenance.

Run:

```bash
cargo test -p adva-witness --test trace_projection
cargo run -p adva-witness --example trace_projection_witnesses -- \
  programs/bootstrap-0/first-trace-arithmetic.adva \
  > target/trace-projection-witness-pair.adva
```

The example emits canonical JSON on stdout and timing/size diagnostics on
stderr. Timings separate source loading/checking, derivation/checking, and
rechecking/serialization. They exclude compilation, process startup, and
stdout transfer. Peak memory is explicitly unmeasured. The formula uses a
constant number of bounded integer operations; complete validation, retained
paths, polynomial projections, and serialization have additional costs.

Tests cover reuse on shorter checked paths and the exchanged-mechanism
document, zero and overflow, missing handoffs, repeated frame coordinates,
forged counts, forged negative evidence, changed method/source coordinates,
and checked JSON round-tripping. CI generates the actual pair and retains it
for exact replay alongside the existing unchanged calibration.

## 7. First recorded execution

The first successful Rust execution is retained in
[CI run 33946738577](https://github.com/mountain/adva/actions/runs/33946738577)
at source commit `31d64a5107fb1d88ea2a299e6feb67ca15d2cbb4`. Its seven new
integration tests passed in 0.02 seconds. The actual emitted bytes are saved
as [the paired witness](../../programs/bootstrap-0/trace-projection-witness-pair.adva).
The retrieved bytes were checked against the SHA-256 printed by that runner:

```text
bytes: 17261
SHA-256: ea3299e47ed9af47d6a85f2f339e07dcee5790da36cbcb39af192a854072da07
source BLAKE3: 09be4633b0cbef2e9d8a29f2e6b7b2ea1a1bf7e3f715655d411b42f18af3d407
```

That single debug-build sample reported 689 microseconds for loading/checking,
854 for derivation/checking, and 1456 for rechecking/encoding, totaling 2999
microseconds. These are observed pipeline timings with the exclusions listed
above, not an amortized speedup or a performance guarantee. No search was
needed, and peak memory was not measured.

CI regenerates the witness and requires byte equality with this retained file.
The source calibration, all five open questions, and the frozen verification
method retain their previous contents.

## 8. Remaining obligations

The frozen inquiry roots remain Open and the verification method remains
refinement-only. The positive count result is deliberately narrower than the
original time-characteristic semantic obligation. The negative result rejects
one literal recovery formulation; it does not refute enriched, quotient, or
relational three-domain proposals. Neither result normalizes ordered holonomy,
identifies a shared truth coordinate, authenticates observations, or proves
universality. A future admission into the verification frontier needs an
explicitly versioned typed predicate and a statement of exactly what closes.

The next minimal step is to declare the missing input or revised target for
construction recovery, then test it against both retained histories. This
gives problem formation a concrete interface requirement instead of an
unbounded request to keep searching.
