# Finite request-to-certificate projection separation

Date: 2026-11-12. Main base:
`8fc38427f2a479b4e8e84802e1873cff14d54566`. Predecessor record:
`db731db488b02cb247ca78375a8a5562065bab32`.

Status: **finite dependency-model result**, not a native certificate theorem and
not a vocabulary promotion.

## Frozen question

The merged two-diagram contract distinguishes endpoint binding from the selected
cross-diagram relation, but leaves the real relation unselected. The earlier
legacy contract is more informative about intent: it asks whether the exact
request can be certified by the existing native Rust input-binding certificate.
The later opaque successor checks only that the request-designated source and
target endpoints exist in their independently imported diagrams.

This run asks whether the exact serialized request coordinate determines the
strong legacy certificate inside a deliberately small field-dependency model.
It preserves yesterday's four input hashes, ten `ResearchCertificate` fields,
two instances, 2,048 candidate completions, 30-second wall bound, 100,000
candidate ceiling and zero-native-execution boundary. The only implementation
change is whitespace-aware extraction of Rust `certificate . field` accesses.

## Exact model and result

The pinned Rust source declares and checks these ten certificate fields:

1. `source_snapshot`;
2. `residual_snapshot`;
3. `static_value`;
4. `bound_source`;
5. `dynamic_source`;
6. `event_map`;
7. `occurrence_map`;
8. `forgotten_static_occurrences`;
9. `forgotten_static_history`;
10. `binding_node`.

The request serializer receives source and residual artifacts separately and
reads the certificate only through `only_dynamic_pair`, whose sole certificate
dependency is `occurrence_map`. It emits one unique dynamic source/target pair;
it does not emit complete occurrence-map coverage or the other nine certificate
fields. The strong checker also uses native compilation/graft material.

For each request coordinate the model enumerates all `2^10 = 1,024` Boolean
obligation completions while holding the separately supplied diagrams and
unique emitted dynamic pair fixed. Exactly one completion has all obligations;
1,023 omit at least one. All 1,024 share one serialized request projection.

The result is therefore:

`ProjectionUnderdeterminesCertificateWithinFrozenFieldModel`.

The same result was reused on one fresh synthetic coordinate with different
profile and endpoint contexts. That coordinate tests dependency-model reuse;
it is not claimed to be a native-valid request.

## Meaning for the target relation

The exact request directly carries the inputs needed to ask for
`PinnedPairMembershipV1`: two diagrams and one ordered qualified endpoint pair.
It does not, in this finite model, decide the stronger legacy native
input-binding certificate by itself.

This gives two honest continuations:

- preserve the legacy target by adding an applicable versioned witness carrier
  or a separately pinned native reconstruction route; otherwise return
  `Unknown/WitnessNotCarried`;
- intentionally adopt pair membership as a weaker target, but record that as a
  scope change rather than silently calling it the legacy certificate.

The result does **not** prove that reconstruction is impossible. Certificate
fields may be derivable under a future pinned compiler/checker route, and the
Boolean model does not execute malformed Rust certificates. It proves only
non-injectivity in the frozen field-dependency presentation.

## Replay and costs

From the repository root, using a new output path:

```sh
timeout 30s python3 -B \
  experiments/native_input_binding_serialized_leaf_request/request-relation-projection-20261112/run.py \
  --output /tmp/request-relation-projection-outcome.json
```

The retained run enumerated 2,048 candidates in 7,858,672 ns before
serialization. One measured 5,390-byte payload serialization used 335,831 ns;
the final output is 5,507 bytes with SHA-256
`e495eba33b6de8c2e535c17c40fcbb7f0a445b62b111c81ab1093973b887ae78`.
Process `ru_maxrss` was 11,264 KiB. Four pinned inputs totalled 73,059 bytes.
Output-write time was not separately measured. There was one canonical-request
read, zero embedded diagram parses, zero native executions and zero correction
replays.

See [contract.json](contract.json), [run.py](run.py) and
[outcome.json](outcome.json).

## Claim and vocabulary boundary

No new word is formed. `LegacyResearchNativeInputBindingCertificateV0` and the
result label are scoped descriptions, not promoted vocabulary. The run provides
no Research 0090 coverage, Research 0092 promotion, M6 filler, native `free` or
`Close`, arithmetic-universality or hypothesized-arithmetic-truth evidence.
Additive zero and guarded multiplicative unit remain separately typed; scalar
agreement does not erase source, order or history.

This finite result helps an adapter author choose an explicit obligation rather
than treating endpoint membership and the strong certificate as interchangeable.
Practical benefit for Jiamin Zhao remains unmeasured because no actual task or
acceptance observation was supplied.

Original model, implementation and report by Codex (OpenAI), offered under
Unknown v0.3 and submitted through Mingli Yuan's GitHub account as authorized
proxy. Account use is not his authorship, review, endorsement or a correctness
guarantee.
