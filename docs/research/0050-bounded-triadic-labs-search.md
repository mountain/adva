# A Bounded Triadic Search Machine for Exact LABS Witnesses

Status: executable research calibration following
[`0038-triadic-characteristic-inference-calibration.md`](0038-triadic-characteristic-inference-calibration.md),
[`0048-directional-energy-of-a-learned-characteristic.md`](0048-directional-energy-of-a-learned-characteristic.md),
and
[`0049-triadic-universal-computation-form-plan.md`](0049-triadic-universal-computation-form-plan.md).

The executable is the standalone workspace crate
[`experiments/labs-search`](../../experiments/labs-search/README.md).
The independent verifier is
[`experiments/labs-search/verify.py`](../../experiments/labs-search/verify.py).

This note implements one narrow decision:

> Before implementing a universal three-computer form, instantiate three
> independently injectable programs on one finite, exact, difficult-search /
> cheap-verification benchmark.

The selected benchmark is the low-autocorrelation binary sequence problem
(LABS). The implementation supplies a temporal trajectory program, a spatial
residual program, a constructive archive program, an explicit scheduler,
exact integer verification, checkpoint/resume, independent workers, and
ablation by program subset.

It does **not** supply code-as-data in the stable Adva language, Turing
universality, coupled universality, a stable three-computer API, a general
learning theorem, a state-of-the-art LABS solver, or a claim in `claims.toml`.
It does not modify the Rust semantic authority of the current Adva core. The
crate is an isolated research executable whose candidate identities are local
to the benchmark.

---

## 0. Executive result

The bounded machine has the form

\[
\mathbb M^{\mathrm{LABS}}_Q
=
(V;P_t,P_X,P_K;\sigma;A;R),
\]

where:

- \(V\) is an exact witness verifier;
- \(P_t\) is a temporal trajectory program;
- \(P_X\) is a spatial residual-field program;
- \(P_K\) is a constructive splice program;
- \(\sigma\) is an adaptive scheduler;
- \(A\) is a finite symmetry-deduplicated elite archive; and
- \(R\) is a checked report containing the witness, statistics, and trace.

The dependency chain is

\[
\boxed{
\text{checked candidate}
\longrightarrow
\text{one scheduled program proposal}
\longrightarrow
\text{exact verification}
\longrightarrow
\text{accept / reject / archive}
\longrightarrow
\text{checked witness report}.
}
\]

The three programs share a state and verifier, but they do not share one
untyped decoder and are not identified with the three observation sections of
a 3-form. This directly respects the correction recorded in note 0049:
observation supplies an environment; a program determines what computation is
performed in that environment.

---

# Part I. Why LABS is the first witness benchmark

## 1. Exact finite statement

A candidate is

\[
s=(s_0,\ldots,s_{n-1}),
\qquad
s_i\in\{-1,+1\}.
\]

Its aperiodic autocorrelations are

\[
C_k(s)
=
\sum_{i=0}^{n-k-1}s_i s_{i+k},
\qquad
1\leq k<n,
\]

and its exact energy is

\[
E(s)
=
\sum_{k=1}^{n-1}C_k(s)^2.
\]

The derived merit factor is

\[
F(s)=\frac{n^2}{2E(s)}.
\]

The search objective is to minimize the integer \(E(s)\). A proposed witness
is verified by recomputing \((C_1,\ldots,C_{n-1})\) and their squared sum. No
floating tolerance participates in the truth of the result; the floating
merit factor is only a display projection.

## 2. Why the benchmark is structurally suitable

LABS satisfies the intended witness profile:

\[
\boxed{
\text{large combinatorial search space}
+
\text{short finite witness}
+
\text{exact quadratic verifier}.
}
\]

It also exposes a nontrivial residual rather than one scalar score. Two
sequences with equal energy can have very different correlation vectors.
Hence the benchmark can test whether a program that reads residual structure
has value beyond scalar hill climbing.

## 3. Symmetry and accountable quotienting

The energy is invariant under at least:

1. global sign reversal;
2. sequence reversal; and
3. multiplication by the alternating sign pattern \((-1)^i\).

The archive deduplicates the resulting eight-element orbit by a canonical
representative. The running trajectory is not silently replaced by its
canonical representative, because trajectory identity and orbit identity are
different data. The quotient is used only for bounded archive duplication.

---

# Part II. The three injected programs

## 4. Temporal program \(P_t\)

The temporal program regards the candidate as a point on an ordered search
trajectory. It samples spin positions, computes the exact incremental energy
change of each single-spin flip, avoids a short list of recently flipped
positions when alternatives exist, and selects among the best sampled moves.

For a flip at position \(j\), the correlation change is

\[
\Delta_j C_k
=
-2s_j
\left(
\mathbf 1_{j\geq k}s_{j-k}
+
\mathbf 1_{j+k<n}s_{j+k}
\right).
\]

Therefore

\[
\Delta_j E
=
\sum_{k=1}^{n-1}
\left(
2C_k\Delta_j C_k
+
(\Delta_j C_k)^2
\right).
\]

This gives an exact \(O(n)\) update for one sampled flip. The temporal program
is not “time itself”; it is one injected program whose state includes ordered
recency and trajectory information.

## 5. Spatial program \(P_X\)

The spatial program reads the current correlation vector as a defect field.
It orders lags by contribution \(C_k^2\), retains a bounded family of dominant
lags, and scores sampled flips by the energy change restricted to those lags.
The full energy of the selected proposal is still computed exactly before the
proposal is returned.

Thus its local observation is

\[
R_X(s)
=
\operatorname{TopLags}
\{(k,C_k(s)^2):1\leq k<n\}.
\]

Its proposal need not be the best move under total scalar energy. This is
intentional: it tests whether organizing the residual field can escape scalar
search plateaus or expose stable defect patterns.

## 6. Constructive program \(P_K\)

The constructive program reads a finite elite archive. It selects an archived
partner, replaces a contiguous block of the current candidate by the
partner's block, applies a bounded set of spin mutations, normalizes only the
global sign, and returns the best exactly evaluated child among a bounded
number of trials.

Schematically,

\[
P_K(s,a;[l,r),M)
=
\operatorname{Mutate}_M
\bigl(s_{<l}\,a_{[l,r)}\,s_{\geq r}\bigr).
\]

This is a deliberately weak first construction grammar. It provides a
nonlocal program family and a concrete place to add learned motifs, skew
constructions, block libraries, or length-changing lifts later.

## 7. The scheduler \(\sigma\)

The scheduler uses an upper-confidence-bound score over the enabled program
set. Reward is based primarily on exact current-energy improvement and new
incumbent improvement, with a very small acceptance credit. The constructive
program is normally eligible only at a declared interval so its quadratic
child evaluations do not dominate runtime.

This scheduler is explicit and serialized. It is not intrinsic to the theory.
The following are configuration choices subject to ablation:

- reward coefficients;
- exploration strength;
- construction interval;
- uphill acceptance rule;
- restart interval;
- archive size; and
- trace stride.

---

# Part III. Exactness, reports, and finite failure

## 8. Exact internal state

Every current or archived candidate stores:

\[
(s,C(s),E(s)).
\]

Single-spin updates transport all three values incrementally. Unit tests
recompute the entire state after every possible flip of a fixture. Loaded
checkpoints are also fully recomputed before execution resumes.

## 9. Independent verifier

The Rust report stores the best sequence, complete correlation vector, integer
energy, and derived merit factor. A separate Python standard-library program
recomputes the witness without importing or calling the Rust search crate. It
also emits a SHA-256 digest of the sign string.

This gives two different verification paths:

\[
V_{\mathrm{Rust}}(w)=1,
\qquad
V_{\mathrm{Python}}(w)=1.
\]

Agreement does not prove the absence of all implementation errors, but it
removes the most direct same-code verifier failure.

## 10. Search exhaustion returns only a bounded result

A run report says:

- which programs were enabled;
- how many scheduler steps each worker executed;
- which deterministic seeds were used;
- the best exact witness found;
- program use, acceptance, and improvement statistics;
- restart counts; and
- a bounded trace.

Failure to improve a baseline means only

\[
\operatorname{Unknown}(\text{declared search budget and configuration}).
\]

It never establishes nonexistence or optimality. Exact optimality is available
only through the separately bounded exhaustive command for small lengths.

---

# Part IV. Small-scale calibration contract

## 11. Exhaustive reference values

The Rust tests enumerate all sequences with first spin fixed to \(+1\) and
check the following exact optimum energies:

| length \(n\) | exact optimum energy |
|---:|---:|
| 5 | 2 |
| 7 | 3 |
| 8 | 8 |
| 10 | 13 |
| 11 | 5 |
| 13 | 6 |

Fixing the first spin removes only global sign duplication and does not change
the optimum.

## 12. Search calibration target

The deterministic CI calibration uses:

```text
length             = 11
seed               = 19
initial population = 16
scheduler steps    = 8,000
restart interval   = 128
construction every = 8 steps
```

Its acceptance criterion is reaching the exact optimum energy \(5\) and then
passing full independent Rust recomputation. This is a regression target for
the executable, not evidence of competitive LABS performance.

## 13. Required ablations for local large runs

For every serious length and evaluation budget, run at least:

\[
P_t,
\quad
P_X,
\quad
P_K,
\quad
P_t+P_X,
\quad
P_t+P_K,
\quad
P_X+P_K,
\quad
P_t+P_X+P_K.
\]

Use multiple deterministic seeds and report both best energy and distribution
across workers. The full triadic machine has earned causal credit only if its
performance exceeds appropriate single- and double-program controls under the
same accounting.

---

# Part V. Large-run protocol

## 14. Reproducible execution

A representative local run is:

```bash
cargo run --release -p adva-labs-search -- search \
  --length 128 \
  --iterations 10000000 \
  --workers 16 \
  --seed 1 \
  --output labs-128.json

python experiments/labs-search/verify.py labs-128.json
```

Independent workers receive deterministic seeds derived from the base seed.
Single-worker runs can periodically serialize the PRNG, scheduler, archive,
trajectory, incumbent, and trace, then resume exactly.

## 15. Evidence hierarchy

Any external announcement should use the following language discipline:

1. **verified witness**: both verifiers accept the object;
2. **baseline improvement candidate**: it improves a frozen baseline table;
3. **record candidate**: a systematic literature and database check has found
   no better published witness as of a stated date;
4. **record**: an independent domain expert has checked the baseline and
   witness; and
5. **Adva-discovered record**: ablation and trace evidence show that Adva's
   three-program organization made a material contribution.

The executable by itself licenses only the first item.

---

# Part VI. Conservative conclusion and red-team assessment

## 16. Conservative conclusion

The implementation establishes that one bounded search task can be organized
as:

\[
\boxed{
\text{three distinct injected programs}
+
\text{one explicit scheduler}
+
\text{one exact verifier}
+
\text{auditable finite reports}.
}
\]

It also demonstrates that temporal order, spatial residual structure, and
constructive recombination can be represented as operationally different
program contracts rather than three labels attached after computation.

## 17. Red-team assessment

The strongest objections remain substantial:

1. LABS already has mature specialized heuristics; this first solver is not
   expected to be competitive without further work.
2. The three programs may merely repackage ordinary local search, residual
   targeting, and genetic recombination. Only ablations and cross-task reuse
   can show additional content.
3. The spatial program currently reads a hand-selected top-lag statistic; it
   does not learn a characteristic language.
4. The constructive program has a weak grammar and may contribute little.
5. UCB rewards and uphill acceptance are ad hoc and can overfit small lengths.
6. The checkpoint and trace prove reproducibility, not conceptual novelty.
7. Reaching a known small optimum is a correctness calibration, not a research
   result.
8. A future record found mainly by brute-force independent workers must not be
   attributed to the triadic theory without causal evidence.

These objections are reasons to run the experiment, not reasons to suppress
it. The benchmark will either show a measurable advantage, or localize the
missing structure more precisely than another conceptual note can.

## 18. Next decision point

After local runs, inspect:

- full-system versus ablation performance;
- scheduler allocation over time;
- whether dominant residual-lag patterns predict successful moves;
- whether archive motifs transfer across lengths; and
- whether the same machine protocol can be re-instantiated for sorting
  networks without changing its outer report and scheduler contracts.

Successful cross-length and cross-task transfer would support the original
intuition. Failure concentrated in one program would identify the next theory
and engineering bottleneck.
