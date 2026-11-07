# Static receiver review after durable reference capture, 2026-11-06

The 2026-11-06 continuation reached **NoExactRouteWithinSelectedSurface**. This is a statement about executable route declarations under a fixed selector and term grammar. All three receiver cases remain `NotRun`. PR [#232](https://github.com/mountain/adva/pull/232) retains its separate outcome of `Unknown / EvidenceCaptureFailure`.

## Evidence

The contract, driver, synthetic controls, historical driver and dependency lock were pinned before the sole production attempt. The recorded contract SHA-256 is `3130a81a4933af62cc35b2c980fe2fdd3cbc2f197f055c58524891c495eafe47`. The machine checkout was clean at `mountain/adva-machine@a0b710a2517f06f2fe03cc463e855548adf418ac`. The Adva review base was `7f40b3cd3b6d05ad39c74f49cf20d9394ec549b4`.

| Object | Count | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| Selected machine files, historical compact manifest convention | 71 | 673,385 input bytes | `accee123f7a2849ef38610f172713cce4caa3ee88cd7a10124e62794e7a59983` |
| Saved manifest including its trailing LF | 71 | 9,495 | `27e35cefeb58dc6c517bbff8d30896f321b1b61907d6b8ef1aec6a809b8b1030` |
| Saved canonical JSONL, one reference per matching line | 430 | 32,276 | `f31bd194761e9bb3bd536f9a2e8ebf9ce7a8bc9e5fc4d107fcc9569e0a04ef2d` |

The [attempt directory](machine-reference-ledger-20261106/) holds the manifest, ledger, last worker phase, worker receipt and supervisor record. Each reference contains only a repository-relative path, a one-based line and its ordered matched terms. The manifest supplies each file's SHA-256. Capture stdout and stderr were both empty. The worker exited 0, the supervisor recorded 3.931 s wall time and wait4 reported 20,228 KiB ru_maxrss on Linux. This is a worker resource measurement. One production attempt, zero manual reruns or production corrections, zero reads of the opaque request and zero semantic executions.

The receipt was verified before classification. Its SHA-256 is `3a0b97db6ae274f03503fe583b901608a88d0bb4c8b95aa9086dbb328e86f421`. Later review re-opened the 430 named locations in 45 pinned machine files and verified their reported terms at those locations. There was no second search. The [static review](machine-reference-ledger-review-20261106.json) assigns each coordinate exactly once to a reason with four grades. It includes the route composition checks and explicit limits. No-hit files remain in the manifest.

## What the four checks found

| Obligation on one receiving route | Finding |
| --- | --- |
| A. Versioned opaque request or lossless typed equivalent | The data-machine command requires a fixed program/input envelope. The selected raw-evidence command takes a payload and separately bound receiver context. Neither interface declares a lossless mapping for this frozen request. |
| B. Two checked native diagram admissions | A semantic JSON import certificate is documented. In the executable VM path, one native call admits a program and a later native call receives its execution trace. These calls do not declare admission of two supplied diagrams. |
| C. Qualified source/occurrence/path endpoint relation | Templates and frame/slice documentation describe identities on existing carriers. The selected interfaces supply no check tying the target qualified endpoints to both admitted diagrams of the same request. |
| D. Receiver outcome | VM reports, documentary receipts and local raw-intake dispositions exist on their respective profiles. None of those profiles declares the complete A–C chain for that outcome. |

The most important delegation boundary is [the raw-evidence intake CLI](https://github.com/mountain/adva-machine/blob/a0b710a2517f06f2fe03cc463e855548adf418ac/experiments/native_evidence_intake/src/main.rs#L15-L25). Its interface exposes a checker and a local disposition. The checker body lies outside the frozen selection. Its internal capability remains undetermined. The distinctions in the table can also be inspected at the [VM admission and replay](https://github.com/mountain/adva-machine/blob/a0b710a2517f06f2fe03cc463e855548adf418ac/toolchain/execute.py#L47-L75), [documentary receipt](https://github.com/mountain/adva-machine/blob/a0b710a2517f06f2fe03cc463e855548adf418ac/spec/framework/documentary-exchange-v1.md#L100-L114) and [diagram import boundary](https://github.com/mountain/adva-machine/blob/a0b710a2517f06f2fe03cc463e855548adf418ac/docs/SEMANTIC_SCOPE.md#L278-L284).

The finite decision concerns declaration coverage at the specified revision, grammar and four-obligation standard. Runtime, unselected modules, later revisions and the possibility of engineering a new adapter remain open.

## Offline verification

For final acceptance use the post-capture verifier. It binds the exact reviewed receipt, supervisor record and classification. It checks the worker's explicit completion status and times against the frozen budgets. A copy of the original supervisor with `worker_status=Unknown` and `elapsed_ns=91000000000` passed the original receipt-only verification. The new entry rejects either discrepancy independently. The stored capture satisfies both checks.

```sh
python3 -B scripts/verify_pinned_machine_reference_review.py
# Optionally resolve exactly the 430 saved coordinates in a local Git repository.
python3 -B scripts/verify_pinned_machine_reference_review.py --machine /path/to/adva-machine
python3 -B -m unittest discover -s tests/python -p 'test_pinned_machine_reference_*.py' -v
```

The optional source check hashes each referenced file and checks terms only at retained line numbers. It never searches for new hits. The static grades remain the reviewer's judgments. The following lower-level commands and counts document the original verification at capture time.

```sh
python3 -B scripts/inventory_pinned_machine_reference_ledger.py \
  --contract-sha256 3130a81a4933af62cc35b2c980fe2fdd3cbc2f197f055c58524891c495eafe47 verify
python3 -B -m unittest discover -s tests/python -p 'test_pinned_machine_reference_*.py' -v
```

Fifteen synthetic tests exercise closed stdout, interrupted and silently truncated writes, post-commit tampering, file/decode failures, a blocked search, receipt fsync failure, missing supervisor evidence and the attempt guard. Four offline tests cover the frozen receipt, all distinct review coordinates, missing or substituted coordinates, and four-judgment completeness. Mechanical checks establish byte/coordinate integrity; the interpretation of the receiving obligations is the attributed static review.

Original continuation, implementation and technical review by Codex (OpenAI), offered under Unknown v0.3. Any authorized GitHub submission would use Mingli Yuan's account as proxy. Account ownership supplies no technical signoff.
