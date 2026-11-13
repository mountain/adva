# Field-complete witness-carrier separation

Date: 2026-11-13. Main base:
`8fc38427f2a479b4e8e84802e1873cff14d54566`. Predecessor PR:
`#234` at `c649ce2f8754c8b61a0e58ffbe4d38c897a7bc33`.

Status: **finite structural dependency-model result**. The carrier is proposed
only; this run does not serialize or validate a native Rust certificate.

## Frozen question

The predecessor exhausted all `2^10` Boolean completions of the ten checked
`ResearchCertificate` obligations and showed that the request projection alone
places the one complete assignment and 1,023 incomplete assignments in the same
class. This continuation asks the smallest next question:

> Does a request-bound carrier that exposes all ten obligation coordinates
> separate the complete assignment, and is every field necessary for that
> separation inside the same model?

The two applicability coordinates are the exact request hash and the pinned
checker-source hash. The ten ordered certificate dimensions are
`source_snapshot`, `residual_snapshot`, `static_value`, `bound_source`,
`dynamic_source`, `event_map`, `occurrence_map`,
`forgotten_static_occurrences`, `forgotten_static_history`, and
`binding_node`.

## Result

For both the frozen canonical request coordinate and one fresh synthetic
coordinate, the run exhausted all 1,024 Boolean assignments. The comparison
was executed in one process and under the same finite resources.

| observation | classes | largest class | mixed valid/invalid classes |
|---|---:|---:|---:|
| request only | 1 | 1,024 | 1 |
| request plus all ten fields | 1,024 | 1 | 0 |

For each of the ten possible one-field omissions, the class in which every
other field is satisfied has exactly two members: the complete assignment and
the assignment failing only the omitted obligation. Thus every field is
necessary for complete separation in this frozen independence model.

The retained result label is:

`UniqueFieldCompleteSeparationWithinFrozenDependencyModel`.

Five predeclared controls also matched:

- missing `event_map`: `CertificateObstruction/MissingField`;
- missing `forgotten_static_history`:
  `CertificateObstruction/MissingField`;
- altered `binding_node`: `Refused/FieldMismatch`;
- mismatched request pin: `Refused/ApplicabilityMismatch`;
- mismatched checker pin: `Refused/ApplicabilityMismatch`.

The complete experiment was reused on the fresh coordinate. That coordinate is
synthetic dependency-model input, not a claim that a second native request is
valid.

## Replay and measured cost

From the repository root after placing this directory at
`experiments/native_input_binding_serialized_leaf_request/field-complete-witness-carrier-20261113`:

```sh
timeout 30s python3 -B \
  experiments/native_input_binding_serialized_leaf_request/field-complete-witness-carrier-20261113/run.py \
  --output /tmp/field-complete-witness-carrier-outcome.json
```

The retained execution used one route, 2,048 candidates and zero correction
replays. Enumeration and validation used 32,503,582 ns. Carrier formation used
2,671 ns. Baseline serialization used 39,625 ns for 148 bytes; carrier
serialization used 70,812 ns for 1,000 bytes. Outcome serialization used
258,961 ns before the final cost fields were inserted. Process `ru_maxrss` was
11,648 KiB. The contract was read once (3,256 bytes); there were zero native
executions. The outer command returned in 0.032 s. Output-write time and report
construction time were not separately measured.

The retained output is 8,565 bytes with SHA-256
`ddfb6140e0b61f7a01d6a871d163154b98519ef97be16ce0cc67fc7ab3b77cf2`.

## Interpretation and residual

The carrier changes the finite observation partition from one ambiguous class
of size 1,024 to singleton classes. This is an exact comparison inside the
declared model, but its coordinates are Boolean obligation states, not actual
Rust field encodings. It therefore shows what a field-complete carrier must
distinguish; it does not yet show that such a carrier can be serialized,
reconstructed, or accepted by the native checker.

No new word is formed. The schema and result names are scoped labels. Research
0090 coverage remains open, so Research 0092 promotion remains blocked. The
run supplies no M6 filler, native `free` or `Close`, arithmetic universality,
hypothesized arithmetic truth, authentication, social trust, or measured
practical benefit. Additive zero and guarded multiplicative unit remain
separately typed; `0/0` remains undefined, and field completeness does not erase
order, source, occurrence, or history.

The minimum continuation is one native encoding audit: determine whether the
existing Rust certificate type can be losslessly serialized with all ten
fields and applicability pins, or retain `Unknown/NativeEncodingAbsent` with
the exact non-serializable fields. Do not build an adapter before that audit.

Original model, implementation and report by Codex (OpenAI), offered under
Unknown v0.3 and submitted through Mingli Yuan's GitHub account as authorized
proxy. Account use is not his authorship, review, endorsement or a correctness
guarantee.

## Integration status

The branch also registers this script and the two predecessor scripts in the
repository's exact RLIMIT portability inventory. That repair preserves the
inventory check; it is engineering reproducibility evidence, not support for
the mathematical result.
