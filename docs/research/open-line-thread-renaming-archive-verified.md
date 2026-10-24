# Open-line thread renaming: independent archive verification completed

Status: bounded finite experiment. The previously successful receiver evidence
now also has the separately required archive-only verification. This supports
one exact registry claim and does not promote a word or a native operation.

## Frozen question and current dependencies

The verifier-only contract was frozen on 2026-10-24 at draft PR 226 head
`09931719bff896a7e0e143a9bc9848e424ff09c6`, with merged `main` unchanged at
`2154b3c6716e7b5a19b98b81aca7940c0c93fe7d`. Draft PR 227 concerns a separate
finite positivity and epistemic-identity model and does not alter this chain.

The exact question was whether one archive-only verifier could check the
immutable attempt-4 evidence after the one already diagnosed source repair,
without importing or executing the receiver. The contract allowed one route,
one verifier process, zero receiver runs, zero search nodes and zero correction
replays. Its source change was restricted to loading `negative_controls` from
the inherited `contract.json` instead of the later validation contract.

Research 0090's general coverage obligation remains open. Research 0092
promotion therefore remains blocked, and Research 0123's
`arithmetic-universality` and `hypothesized-arithmetic-truth` remain Proposed.
There is no arithmetic domain in this experiment: additive zero and
multiplicative unity stay distinct and unevaluated.

## Result

The sole verifier process returned `ArchiveVerified` with 62 checks. It checked:

- every pinned predecessor input and retained historical evidence coordinate;
- byte equality of the archived execution and stdout records;
- the two positive and ten refused case names, outcomes and exact reasons;
- complete forward and reversed source mappings under one correspondence;
- preservation of raw `(a,b)` versus `(b,a)` thread order after fresh renaming;
- all six source and occurrence pairs in the two swap controls, including the
  four untouched tail pairs;
- the five immutable attempt-4 file digests and the recorded 1 MiB bound.

The verifier imports no experiment receiver and starts no receiver process. The
five evidence digests equal the coordinates frozen in the new contract and in
the generated archive report. The earlier
`FiniteRunPassedArchiveUnknown` record remains unchanged as the historical
pause; this note records its separately budgeted successor.

## Cost and replay

The verifier reports 0.0017684089980321005 seconds and 10,624 KiB peak RSS on
this Linux process. Its canonical report is 564 bytes. Search nodes, receiver
runs, correction replays and new words are all zero. Source formation consisted
of the declared six-added/one-removed-line lookup repair; its authoring time was
not measured. JSON serialization time is included in the verifier total and was
not measured separately. The prior receiver construction, receiving and
serialization costs remain those recorded by the predecessor note; they were
not spent again.

Replay the archive-only check against a new absent output path:

```console
timeout 30s python3 experiments/open_line_thread_renaming/verify_attempt4.py /tmp/archive-verification.json
```

The checker refuses to overwrite an existing report.

## Exact boundary

The result supports only the declared two fresh-name pairs and ten controls over
trusted research dataclasses and retained canonical JSON. It does not establish
unrestricted alpha-equivalence, a native Adva identity or transport operation,
braid or topological equivalence, history semantics, all-fillings coverage,
M6 closure, native `free`, arithmetic truth or arithmetic universality. Hashes
are integrity coordinates, not authentication. No continuation is authorized.

The result helps a later human or agent distinguish a receiver's finite semantic
check from a separately replayed archive-integrity check while preserving the
failure chain that led to both. Practical benefit to Jiamin Zhao remains
unmeasured.

The smallest next research step is not a broader renaming theorem. It is a
single native-boundary question: choose one exact source/occurrence identity
leaf in this profile and ask whether the existing Rust input-binding
certificate can receive that leaf correspondence without reconstructing it in
Python. This requires a new contract and must preserve the present finite claim
unchanged if the native bridge is unavailable.

This record is project-original work by ChatGPT (OpenAI), submitted through
Mingli Yuan's authorized GitHub account proxy. It is not his authorship, review,
endorsement or correctness guarantee. It is contributed under Unknown v0.3 and
imports no external expression or payload.
