# Proposed target-adapter obligation contract, 2026-11-09

**Finite result: `PassedFiniteStructuralContractReview`.** This is a problem-
formation and tooling result. It does not implement or execute a target adapter.

Main remains at `17e1842addcd9f9262eef87bd19c5eabcdc843e1` and draft
PR #232 remains the only open pull request. The prior native run established
three controls for the pinned raw helper's own synthetic fixture, but that
helper still does not carry the target's two supplied diagrams or their
qualified cross-diagram endpoint relation. Re-running those controls would not
address the residual. This continuation instead asks whether the missing
adapter obligation can be stated precisely enough to reject common premature
closures before any implementation begins.

## Frozen question, objects and budget

The frozen contract is [`contract.json`](contract.json), SHA-256
`72b28be5fc2f13f246ef034318b5c0abffe7c528c3a5a2192ff8bf655d1163da`.
It fixes one route, one canonical interface document, one positive case and
twelve structural mutations. The process caps are 30 seconds wall time,
20 seconds CPU, 256 MiB address space and 1 MiB output. Candidate search has
zero candidates and zero nodes. At most one correction replay is allowed for a
specific implementation error.

The types are deliberately not collapsed:

| Obligation | Required retained structure |
| --- | --- |
| A. Request binding | request schema, canonical-byte SHA-256 and receiver-context SHA-256 |
| B-left. Native admission | ordered left slot, serialized-diagram SHA-256, Rust authority and an explicit not-yet-implemented status |
| B-right. Native admission | the same independently for the ordered right slot |
| C. Endpoint relation | diagram role and digest plus source ID, occurrence ID and path on both ordered sides |
| D. Receiver outcome | `Accepted`, `Refused` or `Unknown`, each with interpretation and residual |

The proposed document is
[`adapter-obligation-v0.json`](adapter-obligation-v0.json), SHA-256
`2cb19dff7fc86ce0940ce6877e5b3be2c570cd7e8667e4bac0bcfed2c795f8f3`.
Its schema identifier is an interface label, not a new research word, native
type or capability claim. The document contains no opaque request or diagram
bytes.

The arithmetic boundary is documentary but checked. Additive zero remains
`A-B=0` on its typed additive carrier. Multiplicative unit remains `A/B=1` on a
separate typed multiplicative carrier and requires a nonzero denominator;
`A=B=0` is explicitly undefined for the quotient. Interchange, commutation and
history erasure are not authorized.

## Finite controls and result

The direct checker accepts only the proposed status and complete A+B+B+C+D
shape. The twelve mutations remove or conflate one obligation at a time:

1. missing second diagram;
2. duplicate diagram role;
3. missing source identity;
4. a right endpoint substituted as the left relation endpoint;
5. missing wrong-path control;
6. same-value/different-origin substitution changed from `Refused` to
   `Accepted`;
7. an unimplemented native boundary falsely marked implemented;
8. additive and multiplicative carrier conflation;
9. removed multiplicative nonzero guard;
10. local-image equality promoted to M6;
11. `Accepted` without the recorded-outcome check; and
12. erased adapter-implementation residual.

The corrected run accepted the canonical document and rejected all twelve
mutations. Thirteen tests ran. It read zero opaque-request bytes, read zero
diagram bytes and performed zero native executions. The consolidated result is
[`outcome.json`](outcome.json); the exact corrected stdout is
[`corrected-run-stdout.json`](corrected-run-stdout.json), whose SHA-256 is
`b99b1ad2b7f0c163815c7255c2585525ca22d89631a632028769f9f92a6bb84c`.

| Measured corrected stage | Cost |
| --- | ---: |
| JSON load | 82,474 ns |
| direct structural verification | 114,623 ns |
| thirteen-case finite suite | 1,194,737 ns |
| process elapsed before serialization | 1,394,419 ns |
| result serialization measurement | 172,120 ns |
| outer wall clock | 0.05 s |
| outer user / system CPU | 0.03 s / 0.01 s |
| process maximum RSS | 12,288 KiB |
| final stdout | 1,465 bytes |

Maximum RSS is Linux `RUSAGE_SELF` for the one Python process, not a process-
tree or system peak. Contract/tool/report construction time was not
instrumented. Repository file size is not used as a memory measurement.

## Retained implementation error and correction

The first invocation passed the same thirteen semantic controls, but the runner
computed `serialized_bytes` before adding that member to the final JSON. It
reported 1,437 bytes while the outer process observed 1,465 bytes. This is
retained as [`first-attempt.json`](first-attempt.json), with stdout SHA-256
`10c637d2f127b8188a161ddb5e44771270278d92b17eb5592615cf5d526e85c2`.

The sole correction changed only the final length calculation to a fixed point.
The interface, mutations and budgets were unchanged. The corrected runner's
own `correction_replays: 0` describes no internal retry within that process; the
consolidated outcome records the one externally authorized correction replay.

## Replay

From this directory:

```sh
timeout 30s python -B run_check.py
```

The runner applies the CPU, address-space and file-output limits itself. The
external timeout supplies the wall bound. `verify.py`, `test_verify.py` and
`run_check.py` are original first-party review tooling under Unknown v0.3 and
have SHA-256 values
`6f8032de83a6c00eaeed2c3d1662894712a55d6cac9cbbf843213f38d3d1766f`,
`3f6f67d9ccc427f2a7bab6ceec5f9eb51ae89501fcef0537b0225d0b97d47a8a`
and `762559ac1eabf2547891af06f1520ed7adfb63a917683260750e4cefa3664c48`
respectively.

## Interpretation, vocabulary and residual

The result makes the missing problem more explicit: any future adapter must
bind one request, admit both ordered diagrams independently, compare endpoints
qualified by diagram/source/occurrence/path, and retain a typed outcome. It
also gives implementers a minimum refusal suite. It does not show that such an
adapter exists at the pinned machine boundary or that the real target request
will pass.

No word is formed or revised. The schema label remains a proposed interface
name. `arithmetic-universality` and `hypothesized-arithmetic-truth` remain
Proposed external words. Research 0090 coverage is open, so Research 0092
all-fillings closure and vocabulary promotion remain blocked. Local image
equality does not supply an M6 filler. Native `free`/`Close`, authentication,
social trust, independent review and practical value remain unproved.

This helps Mingli Yuan and later implementers turn an underspecified residual
into a versioned input/output boundary and finite refusal checklist. It gives
Jiamin Zhao no demonstrated end-user capability yet. The smallest continuation
is to review this proposed boundary independently and, only if it survives,
implement one Rust-authoritative adapter that consumes the real pair and runs
the canonical valid case, wrong diagram/path case and same-value/different-
origin case without changing their types.

Original contract, tooling and report by Codex (OpenAI), contributed under
Unknown v0.3 and submitted through Mingli Yuan's GitHub account as authorized
proxy. Account ownership is not authorship, review, endorsement or a
correctness guarantee.
