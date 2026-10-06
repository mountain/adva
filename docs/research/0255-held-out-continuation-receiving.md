# Research 0255: Held-out continuation receiving without an answer label

Status: **bounded finite held-out implementation comparison**. This note adds
no native operation, framework `accept`, executable continuation permission,
new fuel or vocabulary word.

## Question and frozen boundary

[Research 0254](0254-cross-language-continuation-receiving-agreement.md)
compares a Python and a Node continuation receiver, but both read the ten
fixtures that had already been used to develop the Python gate. That agreement
could therefore be confined to known examples. The next minimum question is:
when a third process constructs new canonical problem--history--budget and
terminal-resolution bytes without importing either receiver or supplying the
expected gate answer, do both receivers still agree and preserve the tuple?

The [contract](../../experiments/continuation_resolution_heldout/contract.json)
freezes one route, one Perl constructor, two optimized Python receiver
processes, two Node receiver processes, zero target processes, five seconds
per child, twenty outer seconds, 40,000 constructor units, 50,000 receiver
units, 100 comparison units and zero search candidates. The three source
files have distinct SHA-256 coordinates. The constructor uses only Perl core
modules and directly emits canonical bytes; it does not read either receiver,
their old evidence or any expected gate classification.

The two neutral instances provide a reuse check for the same construction
method. They retain distinct attempts, pair coordinates, histories and exact
natural-number budgets:

| Instance | Terminal state | Budget `(initial, spent, remaining)` |
| --- | --- | --- |
| `rho` | completed | `(31, 19, 12)` |
| `tau` | cancelled | `(37, 21, 16)` |

The supervisor does not contain an expected outcome for either instance. It
checks only that each observed result belongs to the established three-way
range, the two receivers agree, the preserved tuple equals the constructed
tuple, all selected bytes stay unchanged, and fuel and authority remain zero.

## Result

The sole execution passed 71 explicit supervisor checks. Both Python and Node
observed `ContinuationReady` for `rho` and `tau`; those labels are recorded
outputs rather than constructor or comparator inputs. Each comparison returned
`ImplementationAgreement`, and each receiver preserved the newly constructed
continuation exactly. All fourteen selected case files remained byte-identical
before and after receiving.

Four comparison-only controls retained the existing refusal boundary:

- changed classification -> `UnknownImplementationAgreement`;
- changed preserved tuple -> `UnknownImplementationAgreement`;
- same source provenance -> `UnknownImplementationAgreement`;
- missing second result -> `UnknownImplementationAgreement`.

This removes one narrow alternative explanation for Research 0254: the two
receivers are not agreeing only because the supervisor reuses archived answers.
It does not establish that their shared written specification is correct.

## Measured cost

The retained
[execution](../../experiments/continuation_resolution_heldout/evidence/attempt-1/execution.json)
records:

- one Perl constructor, two Python receivers, two Node receivers and zero
  target processes;
- 15,674 constructor units, 10,528 receiver units and 17 comparison units;
- 0.09808677699993495 seconds constructor wall, 0.45257825499993487 seconds
  summed Python wall and 0.25751138700024967 seconds summed Node wall;
- 0.8128668070003187 seconds whole-run wall and
  0.0018367999978181615 seconds evidence serialization;
- 35,448 KiB maximum child RSS and 12,288 KiB supervisor RSS, as category
  maxima rather than concurrent aggregate memory;
- 26 retained evidence files using 17,503 filesystem bytes; this size is not
  a memory measurement;
- zero search candidates and zero correction replays.

Construction design, authoring and publication time are unmeasured.

The first validation wrapper could not start because `/usr/bin/time` is absent;
it launched no test or receiver. A subsequent `python -m pytest` preflight also
stopped before collection because pytest is not installed, after about
0.020475821999752952 seconds with 8,704 KiB maximum child RSS. Standard Python
then loaded the same two test functions directly. The retained-evidence check
and one fresh five-process replay passed in 0.6657857489999515 seconds. That
fresh replay repeated 15,674 constructor, 10,528 receiver and 17 comparison
units, took 0.648730274999707 seconds internally and measured 35,188 KiB
maximum child RSS. It is validation cost, not a second research attempt.

## Meaning and residual

No new word is justified. `ImplementationAgreement` and
`UnknownImplementationAgreement` remain local result labels. The result is a
held-out transport and reuse check: two existing receivers accepted two new
canonical instances produced without their fixtures or answer labels. It
helps Mingli and later agents distinguish a receiver comparison from a
fixture replay while retaining the exact problem, ordered history and budget.
Its practical value for Jiamin's actual task remains unmeasured.

This bounded result is intentionally not added to `docs/claims.toml` in this
round. The public transfer route did not reproduce that large UTF-8 blob
exactly, so the branch update stops short of changing the claim registry rather
than publishing a truncated replacement.

The constructor creates internally consistent terminal-resolution receipts;
it does not independently prove that a real terminal event occurred. All
three programs still share this repository, host, schema description, SHA-256
semantics and one Python supervisor. Perl/JSON::PP is an additional dependency,
not a native Adva implementation or independent human review. Common-mode
specification defects, malicious processes, authentication, power-loss
durability, distributed consistency and exactly-once execution remain open.

The experiment does not perform a continuation, grant effect or retry
permission, implement native `communicate`, `accept`, `free` or `Close`,
establish Research 0090 coverage or Research 0092 promotion, close M6, prove
hypothesized arithmetic truth or establish arithmetic universality.

The next minimum step is adversarial rather than broader: let a fourth
constructor independently encode the same two abstract instance descriptions
without reading the Perl bytes, and compare the canonical outputs. Any byte
or semantic divergence must remain explicit rather than being normalized away.

Authored by ChatGPT (OpenAI), contributed under Unknown v0.3 through Mingli
Yuan's authorized GitHub account proxy. Account use is not his authorship,
review, endorsement or correctness guarantee.
