# 0234 — The rate of a periodic arithmetic program is its generator action, not its Jacobian

**Date**: 2026-09-25 · **Native carrier**: `crates/adva-witness/src/am_power_weight.rs` ·
**Calibration**: `crates/adva-witness/examples/am_variation_reading.rs` ·
**CI**: a `cargo test` step in `.github/workflows/ci.yml`

**Status**: one bounded native calibration in Rust. No stable API change, no
`ValueType`, no `OperationSpec`, no IR version, no Seal, no library admission, no
transport, no terminology home, and no claim about any physical object. Nothing is
imported from any external repository: `mountain/process-geometry` is cited as an
external mathematical reference and no text, code, identifier or data of it is
copied here.

中文摘要：0233 把十二相位周期 A/M 程序的年度一阶读数写成矩阵乘积 `M_[0]=J_11⋯J_0`。
本笔记保留更正：**矩阵/Jacobian 只是 observer 产物，不是 A/M 原生的变率载体**。
原生变率是生成元对幂-权基底 `Φ_{ν,w}=a^ν e^{(w−ν)v}` 的作用表读数：乘积=标号相加，
`AΦ_{ν,w}=νΦ_{ν−1,w−1}`，`MΦ_{ν,w}=wΦ_{ν,w}`，系数精确落在 `ℚ[exp(ℚ)]`，
`A^{-1}` 在 `ν=−1` 强制 `log a`（witness `a>0`），`M^{-1}` 在 `w=0` 强制 v-Jordan，
默认 `OrdinaryOnly` 下两者都是类型化 fail-closed。混合字降到正仿射幺半群
`(b,k)(c,ℓ)=(b+kc,kℓ)`。用这套语言读 0233 的十二相位夹具：年度 holonomy 的膨胀率
`3/8`，年度返回 `3/8h+1/8h²+1/64h³+1/512h⁴`，`A` 作用读数为
`3/8+1/4a+3/64a²+1/128a³`，它在参考点 `a=0` 的取值**等于** holonomy——两条读数互相
校验，而不是一次矩阵乘法。全部为精确有理、无浮点、无 Python。

## 1. What is answered, and what is corrected

Note [0233](0233-periodic-programs-before-floquet-observations.md) posed a finite
carrier of twelve open programs, an exact finite-change identity, a first-degree
"Floquet" reading `M_[0] = J_11⋯J_0`, and a polynomial observer question. Its
evidence table left two items open: a paired-execution correspondence with a
variation certificate, and a first-degree observation composing over native
slices. It also described the first-degree reading as a product of Jacobians.

That reading is corrected here, and the correction is the point of the note. In
this project's arithmetic-process language a linear map is not the native carrier
of change:

- the native finite object is the **difference of two executions**, and it must be
  certified before any derivative is taken;
- the native infinitesimal object is the **action of the arithmetic generators**
  `A` (Addition) and `M` (Multiplication) on a declared process-adapted function
  language;
- a matrix, jet or Jacobian may be produced afterwards as an **observer product**,
  and receives no semantic-carrier credit.

So the question answered here is not "what is the annual Jacobian" but "what does
the arithmetic generator read on the annual composite of the twelve programs, in
a carrier that the arithmetic itself generates".

## 2. The native carrier

The carrier is the rank-one rational power–weight family

\[
\Phi_{\nu,w}=a^{\nu}e^{(w-\nu)v},\qquad \nu\in\mathbb{Z},\ w\in\mathbb{Q},
\]

with exact rational labels and a constant readout extension whose coefficients are
finite rational combinations of formal `exp(q)` atoms, `q ∈ ℚ`, with
`exp(q)·exp(r) = exp(q+r)`. A canonical element is a finite map from the key
`(ν, w, q)` to a rational coefficient; zero coefficients are dropped and every
element has one representation.

| Law | Statement | Where it is checked |
| --- | --- | --- |
| Product | `Φ_{ν,w}·Φ_{μ,z} = Φ_{ν+μ, w+z}`, exp labels add | `product_law_adds_powers_weights_and_exp_labels` |
| Addition generator | `A Φ_{ν,w} = ν Φ_{ν−1, w−1}` | `generators_act_by_power_and_weight` |
| Multiplication generator | `M Φ_{ν,w} = w Φ_{ν,w}` | `generators_act_by_power_and_weight` |
| PBW order | `M^n A^m = A^m (M−m)^n` | `pbw_identity_has_zero_residual_and_a_nonzero_wrong_control` |
| Addition resonance | `A^{-1}` at `ν = −1` is a typed `log a` extension requiring the witness `a > 0` | `resonances_are_typed_under_both_policies` |
| Multiplication resonance | `M^{-1}` at `w = 0` is a typed v-Jordan extension | `resonances_are_typed_under_both_policies` |
| Finite mixed words | `(b,k)(c,ℓ) = (b+kc, kℓ)`, `T_bD_k` normal form | `affine_composition_is_chronological_and_order_sensitive` |

Two guards keep the reading honest. The polynomial submodule is defined exactly as
the terms with `q = 0` and `w = ν`; composition and evaluation are refused with a
typed error outside it, so an element carrying `v` can never be silently read as a
polynomial. And the resonance policy defaults to `OrdinaryOnly`, where a resonant
inverse is a typed refusal rather than an element of the base algebra: an
extension is something a caller declares, not something the algebra assumes.

In this carrier `A` acts on the polynomial submodule exactly as `∂_a` and `M` as
`a∂_a`, so the annual first-degree number of 0233 is recovered as an
**action-table reading**, and no linearization is introduced to obtain it.

## 3. The 0233 twelve-phase fixture in this language

The fixture is the twelve phase maps `F_m(x) = s_{m+1} + a_m(x − s_m) + q_m(x − s_m)²`
on the reference path `(0,1,2,1,0,−1,−2,−1,0,1,0,−1,0)`, with two nonlinear phases
and ten translations. Read natively:

| Reading | Native meaning | Exact value |
| --- | --- | --- |
| Annual holonomy | chronological composition of the twelve affine parts in `T_bD_k` | dilation `3/8`, translation `0` |
| Annual return | the twelve phase maps composed inside the carrier, minus the reference endpoint | `3/8 h + 1/8 h² + 1/64 h³ + 1/512 h⁴` |
| Addition rate | `A` applied to the annual element | `3/8 + 1/4 a + 3/64 a² + 1/128 a³` |
| Rate at the reference | `A(annual)` evaluated at `a = 0` | `3/8`, equal to the holonomy dilation |
| Multiplication weight | `M` applied to the annual element | `3/8 a + 1/4 a² + 3/64 a³ + 1/128 a⁴` |
| Finite differences | the annual element evaluated at declared `h`, with `E(h) − (3/8)h` retained | `h=1/2: 1809/8192`, `h=1/4: 13345/131072`, `h=−1/4: −11295/131072`, `h=−1/2: −1295/8192` |

The two rate readings agree by construction and the agreement is asserted: the
multiplicative holonomy of the ordered composition and the Addition-generator
reading at the reference are the same rational number, reached by two different
native routes. That cross-check is what a bare multiplier cannot supply, and it is
the reason the correction matters.

## 4. Controls, including the ones that force the exponential class

| Control | Result |
| --- | --- |
| Swapped nonlinear phases | holonomy still `3/8`; coefficients `0, 3/8, 17/128, 3/128, 1/512` — same first-degree reading, different process |
| Shifted periodic reference `c_m = s_m + 1/8` | defects `−31/512`, `−15/512` and ten zeros: a periodic reference is not a periodic solution |
| Declared multiplicative-flow phases with rational labels `1/2` and `−1/3` | the composite label is exactly `e^{1/6}`, and the rational polynomial submodule refuses the reading with a typed error — this is the case that forces the exponential class rather than a wider polynomial module |
| Resonant inverses | `A^{-1}` at `ν = −1` returns the typed logarithmic extension with its `a > 0` witness; `M^{-1}` at `w = 0` returns the typed Jordan extension; under `OrdinaryOnly` both fail closed |
| Wrong-order affine composition | differs from the chronological composite, so the order of the twelve phases is not decoration |

The exp control is the honest form of the "polynomial class containing exp"
question: the fixture's own reading lives in the rational polynomial submodule, and
the exponential carrier is not decoration either. It becomes necessary exactly when
a phase's multiplicative label is a declared rational flow parameter rather than a
rational coefficient, and then the composition law `exp(q)exp(r) = exp(q+r)` gives
the exact composite label.

## 5. Evidence

The native carrier is `crates/adva-witness/src/am_power_weight.rs`; its unit tests
are seconds-scale and cover the laws, the guards, both resonances under both
policies, and negative controls. The calibration is
`crates/adva-witness/examples/am_variation_reading.rs`, which asserts every value
in sections 3 and 4 and writes one deterministic JSON report to a fresh path.

Recorded run:

```sh
cargo test -p adva-witness --lib am_power_weight            # 10 passed
cargo test -p adva-witness --example am_variation_reading   # 2 passed, the CI gate
cargo run  -p adva-witness --example am_variation_reading -- \
  --output target/am-variation-reading.json                 # 31 checks passed, 0 failed
```

The example carries its own test gate, so the CI step asserts the declared
readings instead of merely compiling the file, and the manual run writes the
report and refuses a path that already exists. Both the gate and the report are
deterministic: the report contains no timing, host path or other run-dependent
field, and two runs into two fresh paths are byte identical.

The report records the fixture, the readings, the controls, the check list and its
own scope, and contains no timing, host path or other run-dependent field. The
example uses exact rational arithmetic only: no floating-point value appears
anywhere in the carrier, the fixture or the report.

## 6. What this does not claim

- **No native Floquet calculus.** The word Floquet belongs to 0232/0233's external
  reading. What is established here is an exact action-table reading of one
  declared periodic program in the arithmetic carrier, not a general nonlinear
  spectral theory and not a stability theorem for any orbit.
- **No matrix ontology.** No Jacobian, matrix, jet, eigenvalue or tangent vector is
  computed or needed. The agreement of the two readings in section 3 is asserted
  as an identity of exact rationals, not as a property of a linearization.
- **No physical or meteorological claim.** Nothing here is a weather model, a
  forecast, a stability estimate or an observation. The frozen forecast work of
  0231/0232 is unchanged, and its required inputs are still unavailable in this
  checkout.
- **No stable surface.** No Lisp builtin, `OperationSpec`, `ValueType`, IR version,
  Seal, library admission, transport or receipt is created, and no vocabulary word
  is promoted or given a terminology home.
- **No importation.** `mountain/process-geometry` is cited as an external reference
  for the laws; its text, code and identifiers are not copied into this repository.

## 7. Residual and next boundary

What is established is a finite exact calibration: one carrier, twelve declared
phases, one declared reference, and the controls above, with every value produced
by the native Rust implementation and asserted there. What remains open:

- the completion is declared, not constructed: an observer-directed completion
  along a declared positive weight cone (a target weight or bounded band, with the
  residual above the observer horizon retained) is not implemented here;
- the carrier is rank-one and rational; multivariable arithmetic, higher rank, and
  non-rational labels are outside it and are refused rather than approximated;
- nothing here transports to the frozen weather program: that needs the exact
  forecast program, its frontiers, the reference path, the observation policy and a
  retained nonlinear/forcing residual, none of which exist in this checkout;
- whether some other declared generator analogue reads differently remains open,
  exactly as 0233 recorded for its own boundary.

**No computation outside a contract counts as a result of this repository.**

Authored and checked by deepseek-v4-flash-vision-exp (DeepSeek Harness),
submitted through Mingli Yuan's authorized account proxy. Account use is not his
authorship, review, endorsement or correctness guarantee. One agent wrote the
carrier, the calibration and this note; there is no independent reviewer.
