# ADR 0037: Calibrate library stability at a frozen question boundary

Status: bounded research example; no stable API promotion.

The user requested progress on a library that may evolve but should not drift
inside every run, and on whether repeated zigzags or the existing braids can
provide convergence. Research 0149 freezes the finite question and run limits.

Use an example-local Rust protocol above `adva-witness::ExactExprV0`, not a new
library export or builtin. An epoch retains its ordered candidate syntax,
question, evidence and checker-source/dependency revision. Elimination is
monotone only inside that epoch; the first retained candidate is a deterministic
representative. A new catalogue or question cannot inherit an old receipt by
editing its name. Entire receipts are re-executed, not trusted by digest alone.

Nonempty singleton question-feature coverage permits `FeatureClosed` while
multiple syntax candidates and their histories remain. `Open`, `ModelGap`,
and resource-limited `Unknown` remain distinct. A stuttering or duplicate
round spends resources and retains history but does not constitute progress.
All checks and the prepaid checkpoint share one bounded study account.

Reuse the existing polynomial shadow and braid regression oracles. Point
observations are not guarded arithmetic execution. Braid projection collisions
are not an M6 filler or a program inverse. There is no new general braid
normalizer, active triadic transformation or stable hole calculus.

This calibrates supplied finite candidates and observations; it neither
discovers syntax nor proves an open-world convergence time. A future live
library integration needs separate candidate admission, trusted observation
provenance, append-only storage transactions and cross-version certificate
migration. The research agenda dependency order remains unchanged.
