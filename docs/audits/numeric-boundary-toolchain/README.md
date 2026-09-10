# Numeric boundary & resource integrity report (2026-09-10)

Internal evidence-grade bug report consolidating the numeric boundary audit
thread: the four FINDINGS.md defects, the two follow-up defects found during
fix review, the k28 JSON transport closure, and the AEG-side calibration
findings. Machine record with commit pins, severity model and verification
ledger: `report.json` (schema `adva.numeric-boundary-integrity-report.research`).

## 1. Scope and method

- Repositories: `mountain/adva` (engine + supervisor) and local `AEG`
  (research trials). Audited scope: 58 production files scanned for float
  types, conversions, rounding, finite checks, casts and debug-only
  assertions; boundary-computing call paths read in full.
- Method chain: Xe-incident boundary classes (rounding direction on a safety
  boundary, self-consistent assertions, build-dependent checks, alignment-
  dependent triggers) → static scan → C binary64 scalar model → native Rust
  bit-pattern replay → frozen-baseline evidence discipline → versioned fixes
  → native acceptance gates.

## 2. Threat model and security relevance

The harness promises (a) retained research evidence (receipts, lineage,
reports) that is replayed, cited and cross-language compared, and (b) strict
resource admission for bounded child programs in the Quine relay supervisor.
Malformed or adversarial inputs/programs are in scope as accidental inputs;
this is not a hostile multi-tenant boundary. Findings are integrity and
containment defects, not memory-safety issues. **No Critical severity and no
remote exploitability was found; no CVE-style advisory is implied.**

## 3. Findings table

| ID | Location | Class | Sev | Status |
|----|----------|-------|-----|--------|
| F-1 | `operation.rs` log@1 | avoidable intermediate overflow | Medium | Fixed `61a7ae4` |
| F-2 | `term.rs` `Rational::as_f64` | double-rounded operands cross unit boundary | High | Fixed `ade4f88` |
| F-3 | eval/PyO3/serialization | nonfinite values accepted or serialized as null | Medium | Fixed `ade4f88` |
| F-4 | `quine_relay.py` | `max(1, floor(remaining))` expands sub-second budget | Low | Fixed `61a7ae4` |
| F-5 | `quine_relay.py` child recheck | allowance recomputed after fork from zero RUSAGE_CHILDREN | Low | Fixed `ade4f88` |
| F-6 | serde_json reports | decimal-to-binary parsing/round-trip discrepancy (k28) | Medium | Fixed `ade4f88`, closure `4a881d7` |
| A-1 | AEG `calibration.py` | float `ceil(log)` on an integral boundary | Low | Fixed AEG `62bced8` |
| A-2 | AEG `.merge-two-sides.py` `norm()` | float-based predicate needs input-type review | Info | Noted, demo-only |

Severity definitions: **High** — silently wrong numerical values can be
retained in evidence without a backstop. **Medium** — integrity or scope gaps
with partial backstops, or evidence-pipeline false negatives. **Low** —
contained boundary overshoot with a fail-closed backstop, or latent traps.
**Info** — demonstration-only latent traps.

## 4. Per-finding detail

See `report.json` for impact, bit-pattern evidence and verification per
finding. Highlights: F-2 changed `2^53/(2^53+1)` from `1.0` to the nearest
binary64 below 1; F-6 old report echoed `0.9999999962747096`
(`0x3feffffffdffffff`) where the submitted value was `0.9999999962747097`
(`0x3feffffffe000000` = `1 - 2^-28`), and the replay now preserves the exact
bits with values `[1.0]`.

## 5. Not found

No floating-point-to-allocation-size path analogous to the Xe VRAM bug; no
silent acceptance of an overspent budget run (post-hoc checks held); no
certificate found to over-claim exact numerical truth; no memory unsafety.

## 6. Residual open items

- Intermediate values and unused differentials are not certified finite
  (documented certificate scope).
- No rounding-error bound for arbitrary programs; `log@2` removes the
  avoidable overflow, not every last-bit difference.
- `toolchain-watch.json` historical fields are pre-merge snapshots; the
  post-merge state is recorded in `merge_refresh_20260910` (commit `60b37d8`,
  now on origin/main).
- k28 closure record lives on `research/k28-json-transport-closure` (`4a881d7`),
  not yet merged.
- AEG `.merge-two-sides.py` `norm()` (A-2) needs a full input-type review; the quoted expression preserves Python integer inputs.

## 7. Verification ledger

Local (macOS, rustc 1.96.1, Python 3.14.6): fmt clean; adva-ir 2/2;
adva-lisp 19/19 incl. `operation::tests` 3/3; `numeric_boundary` 3/3 debug and
3/3 release; k28 regression passed; example diagnostic v2 emitted;
`test_quine_cpu_budget.py` 6/6; k28 replay bit-exact; AEG budget suite 6/6 and
calibration output JSON-equal to the archived report. Upstream
(`native-verification.json`, rustc 1.97.1, Python 3.11.15): clippy -D warnings;
workspace 229 passed; release 64 passed; examples 37 passed; pytest
1637/2382 passed; catalog check consistent. Full command list in `report.json`.

## 8. Reusable methodology checklist

1. Boundary-direction questions: what lies below/above the line; does
   rounding contract (inward) or expand (outward) the safe region; is the
   assertion derived from the same logic it checks?
2. Independent oracles: exact Fractions, bit patterns, power-of-two
   expectations.
3. Model first, native second: C scalar model reproduces, then native replay
   gates.
4. Bit-pattern replay at every transport boundary (parse and serialize both
   sides; compare `to_bits`).
5. Frozen baselines: retained evidence is never relabeled; audit scripts
   refuse to run against drifted source.
6. Versioned fixes: register the corrected rule as a new version; legacy
   replay stays executable.
7. Native acceptance gate order: fmt → clippy → debug/release tests →
   examples → extension build → full pytest.
8. Toolchain defect watch: MSRV/CI inventory with triage records.

## 9. Reuse

Future audits can cite `report.json` (pinned commits, severity model,
ledger). The checklist in section 8 is intended to be the standing method for
boundary-class reviews.

## Merge review corrections (2026-09-10)

F-6: serde_json's `float_roundtrip` feature selects its decimal-to-binary
parser (`src/de.rs`), not output formatting. The stored echo alone did not
isolate the two boundaries; retain the bit-exact replay without attributing
the loss to the formatter or promising arbitrary lexeme preservation.

A-2: the quoted expression returns `int(value)` from the original value when
its float predicate is integral. The Python integer 9007199254740993 remains
9007199254740993 under this expression. The earlier claim that this code
necessarily collapses integers above 2^53 is withdrawn. Other input types
and the full AEG caller remain unreviewed; this is not a claim of safety for
that program. Historical merge-status phrases above describe the authoring
snapshot. See report.json for the correction and retained source coordinates.
