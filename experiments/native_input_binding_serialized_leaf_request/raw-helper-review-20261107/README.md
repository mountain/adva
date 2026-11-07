# Delegated raw-evidence helper review, 2026-11-07

**Decision: `NoExactRouteViaPinnedRawHelper` — static source review only.**

The pinned helper implements a strictly fixed, locally checked arithmetic
roundtrip intake. It has real request-byte/context checks and real local
source/occurrence/path binding checks. Its accepted input and data flow do not
admit the target request's two supplied diagrams or check their supplied
qualified endpoint relation. The existence of these local checks must not be
reported as absence of all source checking, or as fulfillment of the target
request. Native execution was unavailable in this review.

This is an independent source re-examination by Codex (OpenAI), not an
independent human review or a formal verification of the Rust implementation.
No GitHub write, frozen opaque-request read/execution, declaration-surface
search, machine-source edit or dependency-lock upgrade occurred.

## Fixed inputs and relation to the predecessor

- Machine: `mountain/adva-machine@a0b710a2517f06f2fe03cc463e855548adf418ac`.
- Adva review base: `mountain/adva@9a070f610cebf782bcb1a64edd94c312a1073b85`,
  [Draft PR #232](https://github.com/mountain/adva/pull/232).
- The existing 430-row / 32,276-byte reference ledger was read and its digest
  checked: `f31bd194761e9bb3bd536f9a2e8ebf9ce7a8bc9e5fc4d107fcc9569e0a04ef2d`.
  No candidate search was repeated and no previous static grade was rewritten.
- [predecessor.json](predecessor.json) binds the retained artifacts and six
  CLI coordinates. The predecessor's `NoExactRouteWithinSelectedSurface` and
  historical `Unknown / EvidenceCaptureFailure` keep their original scopes.
- This extension names 11 files / 187,052 bytes and 27 line intervals, with
  file SHA-256, Git blob IDs and interval SHA-256. It stops at the listed native
  boundary calls; it is not a repository-wide or transitive implementation audit.

The manual call-path scoping preceded the new reproduction freeze. The
contract does not pretend those observations were made under a prior
pre-registration. Its separately frozen digest is:

`91f97bdaaa351962f9706da3dfd740dbf7b4f55fb8360780ff07f8e65cbb2752`

## Actual call path

`main::check` calls `intake::check_paths`, which reads two bounded files and
calls `check_bytes`. That function checks the independent binding, strictly
decodes `RawEvidence`, calls `validate_raw`, checks the raw byte digest, and
then calls `native::run_received` (R01, R02, R05–R09).

`native.rs` lexically includes
`experiments/checked_roundtrip_reuse/src/checked_roundtrip.rs`. It reconstructs
two native arithmetic expressions from the received fixed literal tokens,
forms the fixed eight-node witness, and uses a private local checked handle
twice. Each use compiles a newly generated pass-through module and instantiates
the witness through that compilation's graft root (R08–R14).

See [references.json](references.json) for every immutable source URL and
line interval; see [dependency-boundary.json](dependency-boundary.json) for
called APIs, adjacent APIs and unreviewed dependencies.

## Findings for the four obligations

| Obligation | Present checks in this helper | Limit for the target request |
| --- | --- | --- |
| A — request identity | Binding-file BLAKE3 against a caller-supplied independent pin; receiver/context equality; complete equality against locally reconstructed profile, origin, premise, interpretation and build binding; strict raw shape; whole-fixture equality; raw-byte BLAKE3 (R02–R06). | These checks identify `adva.fixed-roundtrip-raw-evidence.v0`, not the frozen opaque request. No lossless request mapping is supplied on this route. Hashes do not authenticate a producer or establish semantic identity. |
| B — two supplied diagrams admitted | The two local cache uses each generate a new Lisp program. `compile_function` validates its generated diagram and graft trace before returning a compilation artifact (R13, R19, R20). | No input field supplies two diagrams; two transitions and two local uses are different objects from the requested diagram pair. `import_diagram_json` exists in an adjacent API but is not called on received payload data here. |
| C — qualified source/occurrence/path relation | `instantiate_from_graft` checks compilation/graft certificates, root linkage, ordered three-hole interfaces and singleton lineage; it derives source, occurrence and path from that local compilation. The caller rejects reuse of `(program, source, occurrence)` across the two uses (R14, R16–R18). | The relation is internal to each receiver-generated context. The payload does not supply the target endpoint tuple or a cross-diagram relation. Fixed literal `p/q` incidence and an origin repository/hash record are not that relation. |
| D — outcome on the same route | Code assigns `LocalCheckedAndUsed`, `Rejected` or `Unknown`; the CLI maps these to 0, 2 or 3 (R01, R06, R09). | A local outcome concerns the fixed roundtrip only. No target-request receiver outcome was executed or established. |

The decisive restriction is stronger than a failed keyword search:
`validate_raw` compares the entire decoded record with `fixture()` (R05).
Before native dispatch, the fixed JSON schema, exact fixture semantics and
raw-byte pin must all match (R02, R03, R06). The record contains origin/profile
data, two fixed transitions, fixed seeds/composition and guards. It has no
diagram pair or qualified endpoint-relation input. Under these checks, this
unmodified route supplies no faithful receiver for the described target request.
This is a source-level judgment under the stated Rust/Serde/hash assumptions,
not a runtime theorem or a proof against a future adapter.

Two distinctions matter when reusing the lower-level code:

1. The sibling `FormedCellV0::instantiate` explicitly compares a supplied
   binding's occurrence/source/path against one checked diagram (R15). The
   reviewed CLI calls `instantiate_from_graft` instead. The sibling method's
   existence supplies neither a payload decoder nor a two-diagram relation.
2. General witness `Compose` combines formed summaries and guards (R21).
   The literal roundtrip incidence checks are in this wrapper and its retained
   `first_check` (R05, R12). Summary composition alone must not be credited with
   checking the requested endpoint relation.

## Dependency and trust boundary

The standalone Cargo package uses path dependencies on `adva-ir`, `adva-lisp`
and `adva-witness`, plus pinned registry packages (R26). The two source-binding
functions name 40 fingerprint declarations covering 38 unique paths. They
are recorded as declarations; only the 11 selected file bytes were read by
the frozen verifier. The other paths were not expanded into a new inventory.

This is not a complete compiler dependency closure or a verified binary build
identity. Arithmetic/seed implementations, parser/linker internals, other IR
and compiler internals, third-party libraries and the platform remain trusted
or unreviewed at this cut. `rust-toolchain.toml` selects `stable`, not an exact
compiler binary (R27). Native continuation must record its actual toolchain.
The importer itself declares finite PSC0 scope and does not replay callee
provenance (R20); no broader guarantee is inferred here.

## Executed checks and unexecuted controls

| Evidence class | Actual observation |
| --- | --- |
| Interface and documentation | Inspected at the fixed machine revision. |
| Static implementation | Call/data-flow review of the named helper and boundary functions; 27 referenced intervals. |
| Executed integrity verification | One attempt; all 11 source files and 27 intervals matched; 0.3705 s wall time. |
| Executed synthetic integrity controls | 14/14 passed: one positive plus 13 mutations, including truncation, same-length source change, missing/duplicate reference, shifted coordinate, out-of-scope reference, wrong revision, symlink mode, budget, URL and contract/artifact pin changes. 0.2187 s process wall time. |
| Native fixed-fixture controls | `NotRun`: neither `cargo` nor `rustc` was available. No dependency download or compiler substitution was attempted. |
| Original three semantic receiver cases | All `NotRun`; opaque request reads and executions both zero. |

The Python controls test only the evidence verifier. They do not generate
native identities or prove the static interpretation. The native implementation's
existing tests were read as test source (R23–R24), not counted as executed.
[native-plan.json](native-plan.json) lists 14 named native tests and finite
offline build/run limits. [receipt.json](receipt.json) binds commands, logs,
costs, contract digest and unavailable-toolchain evidence. Resource `maxrss`
fields are cumulative child-process maxima, not per-stage memory deltas.

One preparation error is retained in the contract: an initially requested
end line 1175 exceeded a 1173-line file. It was corrected before the frozen
attempt. The completed verification had no retries or corrections.

Recheck from this directory with Python 3 and a local machine checkout at the
exact pin; source reads use committed Git blobs, not mutable working files:

```sh
python3 -B verify.py --machine /path/to/adva-machine \
  --contract-sha256 91f97bdaaa351962f9706da3dfd740dbf7b4f55fb8360780ff07f8e65cbb2752
python3 -B -m unittest -v test_verify
```

Those commands reproduce integrity checks, not the original attempt's measured
resource envelope. To reproduce the envelope use the contract's parent wall
timeout and Linux CPU/address-space/file-size limits; preserve new receipts
separately. An independent digest must come from the review record, not from
silently recomputing a modified contract and trusting it.

## Next minimum validation target

The smallest executable follow-up is to build this unchanged package once,
offline and at the same machine pin, and run three already-present test
selectors: `received_fixed_proof_checks_and_reuses_independently`,
`every_semantic_and_origin_dimension_is_exactly_bound`, and
`altered_receiver_binding_cannot_authorize_itself_even_when_repinned`.
Their full names and assertions are in the native plan. Require exactly one
test to run per full selector and retain build identity and failure output.
This establishes the fixed helper's positive/rejection behavior on synthetic
data; it still does not run or accept the opaque request.

For the original goal, the next missing *interface* is a separately versioned
receiver/adapter carrying both supplied diagrams and their qualified endpoint
relation. Its minimal future acceptance contract must bind request identity,
admit each diagram through the existing Rust boundary, and reject a foreign
or wrong-path endpoint and a same-value/different-origin substitution. That
design is a new task, not an existing capability discovered in this helper.

No claim is made about other machine routes, later revisions, whole-repository
absence, native `free`/`Close`, consumer adoption or arithmetic universality.
No static result here advances those statuses.

Original review, evidence tooling and technical checks: Codex (OpenAI),
contributed under Unknown v0.3. No dependency source or opaque request bytes
are included. Any future approved GitHub submission would use Mingli Yuan's
account as proxy; account ownership is not authorship, review, endorsement or
a correctness guarantee. This delivery was not submitted to GitHub.
