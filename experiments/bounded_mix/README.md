# Bounded input-binding mix and self-application

Authored by ChatGPT (OpenAI), submitted through Mingli Yuan's GitHub account
as an authorized proxy; not his authorship, review or correctness guarantee.

This is a conservative, program-independent input-binding specializer written
in the existing structured Adva subset. It is an engineering baseline for
self-application. It does not evaluate static arithmetic, eliminate interpreter
dispatch, or establish a general optimizing partial evaluator.

`q` receives a pair node with tag 42 and fields `[s, d]`. The ordinary Adva
program `mix` receives `[wire(q), s]` in that same pair encoding and emits a
program for `d`. It constructs `s` with generic instructions, constructs the
bound pair, rewrites every `input` to copy that pair, and shifts all jump and
branch targets by the literal-prefix length. Every other body instruction is
retained. The static value is never read from a later host file or callback.

Write `emit(P, x)` for decoding a returned wire value into a target program.
The resulting equations can be checked on actual emitted programs:

```
residual = emit(mix, [wire(I), p])
compiler = emit(mix, [wire(mix), wire(I)])
cogen    = emit(mix, [wire(mix), wire(mix)])
```

Running `compiler` on `p` must emit exactly `residual`; running `cogen` on
`wire(I)` must emit exactly `compiler`. Matching only their final arithmetic
values would not check these code-producing equations. The two object languages
use distinct interpreter code: affine arithmetic and tagged add/multiply/reject.
These equations are the conservative binding instances of the projection
relationships in [Williams and Perugini](https://arxiv.org/html/1611.09906v3).
No speedup or removal of the original interpreter follows from input binding.

## Boundaries and receiving

Only source programs already admitted by Rust, with at most 48 registers and
no names starting `mix_`, are in the input boundary. Sixteen scratch registers
are appended (`mix_A` through `mix_P`). Static node construction uses twelve
depth-indexed stacks. Node depth 11 (root at zero) is refused; an integer may
occupy that depth. All other v1 limits still apply independently. The additional
scratch data may change capacity/fuel outcomes, so resource exhaustion is
Unknown, not a preserved arithmetic rejection or a divergence theorem.

The generated source and target are the same instruction language. No native
operation knows about `mix`, object interpreters, or compilation. Python authors
source once, applies the existing wire codec, and independently checks the
literal prefix and complete body correspondence. The receiver is recursive;
the Adva producer uses explicit work stacks. Its receipt is an external research
artifact, not a native transformation certificate or a stable semantic identity.
Host loading and source admission remain explicit imports.

`contract.json` fixes the input family, protected observations, controls and
budgets before execution. It permits one six-call preflight and one 72-call v1
campaign, with no retries or automatic profile widening. The campaign is also
required to retain a third-projection capacity failure if it occurs. The
independent construction predicted 3,959 target instructions against
v1's 2,048 instruction limit, with a code vector also wider than v1's 2,048-node
arity bound. The executed v1 campaign confirmed an arity refusal at instruction
58,551. Its 67 calls, five first/second code equalities and 18 terminal pairs are
retained; it did not execute an admitted compiler generator.

`contract-v1.json` separately authorizes one 48-call continuation on the v2
capacity profile, with the same time/memory/artifact/fuel budgets. V2 changes only
version markers and instruction/node-arity limits to 4,096; the v0/v1 sources are
unchanged. This continuation passed: the 3,959-instruction compiler generator was
emitted, admitted and executed for both interpreters. Its compilers exactly equal
direct second-projection output. Five first/second code equalities and ten exact
terminal/rejection pairs passed, with 90,036 prior native steps replayed. Total
v2 campaign cost was 439.802 wall seconds and 438.924 aggregate CPU seconds.
The [report](../../docs/research/bounded-mix-and-three-projections.md) records
the controls and remaining optimizing-specializer obligations.

## Reproduction

Use a Python environment with `blake3` and build the release `adva` binary.
The preflight compiles `mix.source.adva` using the existing Adva self compiler,
receives that compilation, and checks a literal binding through native execution
and complete replay. Use new output directories:

```sh
python3 -B experiments/bounded_mix/preflight.py \
  --binary target/release/adva --output target/mix-preflight-01
python3 -B experiments/bounded_mix/campaign.py \
  --binary target/release/adva --preflight target/mix-preflight-01 \
  --output target/mix-campaign-01
python3 -B experiments/bounded_mix/campaign_v2.py \
  --binary target/release/adva --preflight target/mix-preflight-01 \
  --v1-evidence target/mix-campaign-01 --output target/mix-v2-campaign-01
```

These are separately finite runs, not an automatic retry loop. Review the
declared contracts before a new invocation. The checked-in completed runs use
`evidence/preflight-01`, `evidence/v1-attempt-01` and `evidence/v2-attempt-01`.
Each `complete.tar.gz` retains the entire original directory; `retention.json`
binds every member by size and digest. To inspect raw traces, unpack an archive
into a new directory. Run v2 before archiving its v1 input directory, since its
foreign-checkpoint control reads the retained v1 prefix.

The actual v2 compiler generator is available as
[`third-generation.target.adva`](evidence/v2-attempt-01/third-generation.target.adva).
The regression tests validate archive integrity and the recorded equations
without launching another research campaign:

```sh
python3 -B -m pytest -q tests/python/test_bounded_mix.py tests/python/test_bounded_mix_evidence.py
```

`author.py` reproduces the checked-in source and external seed, but never runs
during native specialization. `receive.py` checks correspondence. The native
reports retain complete programs, inputs, traces, states and costs. Failed
reports remain present and receive no success label.

An engineering import collision initially selected the older experiment's
`fixtures` module during a host capacity calculation. Package-qualified imports
fixed that error before any native preflight or campaign; it is not an executed
specialization failure. Ten initial structural/mutation tests then passed.
