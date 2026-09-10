# ADR 0044: Versioned log differential and contained CPU-limit admission

- Status: implemented; native acceptance recorded in the numeric audit follow-up
- Date: 2026-09-10
- Continues: ADR 0003 and PR #173

## Problem

For `log((1/1024)*x)` at `x=2^-1020`, the existing forward rule forms
`1 / 2^-1030` before multiplying by `2^-10`. The reciprocal overflows,
although the correct smooth-expression derivative `2^1020` is finite and
exactly representable. The five-case C binary64 model and independent
power-of-two oracle are preserved in the original numeric audit. The native
tests now exercise this correction; see `NATIVE-FIXES.md` in that audit directory.

Independently, the Quine supervisor expands a remaining 0.25-second aggregate
CPU allowance into a one-second child limit through its minimum-one clamp.
Post-execution rejection does not prevent that pre-execution expansion.

## Decision proposed by this implementation

1. Preserve `adva.builtin:log@1` and its reciprocal-then-multiply realization.
   Register `log@2` with the same unary Real boundary, no exact parameters,
   and `MergeInputs` lineage rule. Its derivative components are computed
   directly as `incoming_derivative / argument`.
2. The single registry selects the version for newly parsed Lisp source.
   `log@2` is its only active `log` surface form. All other surface versions
   remain unchanged. The parser no longer hardcodes version 1 for every form.
3. Stored module terms and diagrams retain their explicit operation version.
   `OperationRef::builtin("log")` remains the legacy version-one constructor;
   it is not a request for the latest surface version. The IR envelope stays
   at version 1: its fields already carry individual operation versions.
   Old runtimes reject `log@2` as unsupported. There is no automatic graph or
   history migration, and no claim that reparsing old source reproduces its
   previous artifact. Replay must retain the old IR or compiler pin.
4. Preserve the existing scalar `ln` and domain check. This change does not
   introduce a finite-only Real API, clamp genuine overflow, repair rational
   conversion or strengthen a certificate into a rounding-error guarantee.
   Ordinary last-bit derivative differences are possible, which is why the
   arithmetic realization has a distinct rule version.
5. Before recording a child invocation, opening its output files or launching
   it, the sequential supervisor requires a positive integer-second CPU limit
   no greater than either the per-child cap or the aggregate remainder.
   If none fits, raise `Exhausted`. Compute the allowance in the parent and
   pass it into the child unchanged: after fork, `RUSAGE_CHILDREN` describes
   a different process and cannot recheck the parent's accumulated usage.
   Existing wall deadlines, process caps, process-group cleanup
   and post-execution CPU checks remain in force.

## Acceptance and residuals

The six Python regressions include a real admitted subprocess, sub-second
refusal before side effects, fractional per-child refusal, contained installed
limits, retained post-execution rejection, and a fork control that makes any
child-side accounting read fail. This last control replaces the invalid
child-side recheck in the initial proposal.
The original measurements are in `experiments/numeric_boundary_audit/FOLLOWUP.md`;
current acceptance and reproduction commands are in that directory's
`NATIVE-FIXES.md`.

Rust tests cover the five log compositions, independent scale reuse, zero and
negative incoming derivatives, genuine overflow, domain refusal, ordinary
inputs, registry selection, unknown-version refusal and both stored versions'
checked JSON replay. Native validation commands and results are retained in
the follow-up; debug, release, formatting and workspace gates apply. The
existing registry claim in `docs/claims.toml` concerns version-one operations;
new implementations have a separate scoped numeric-boundary claim. ADR 0045
adds constant@2, an explicit finite application policy and JSON protections;
it does not reinterpret log@1 or log@2.

Frozen research contracts whose protected source paths include the kernel
must reject this changed source base. Do not alter their pins, overwrite their
evidence or renew their fuel to make this patch pass an old contract. Updating
such contracts is a separate explicit migration.

CPU containment here is about the configured limit and admission decision.
OS accounting/termination granularity and non-isolated or concurrent child
work prevent interpreting it as an exact physical CPU-time guarantee. The
supervisor assumes sequential calls and does not add concurrency accounting.
Neither change proves arithmetic universality, grants `free`, or supplies a
new proof of exact Real evaluation.
