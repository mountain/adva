# Receiving the golden-ratio calibration

Date: 2026-09-10. Direction: Mingli Yuan. Receiving review: ChatGPT.
Status: **PartialReceivingAudit**, with an exact arithmetic reuse.
This review is an addendum; it does not relabel the producer's historical
contract, execution, or admission status.

## Reviewed revisions and merge order

- Adva producer head: `9ae99c9b637e14ee307e4fcc6019334665c93530`.
- Library producer head: `c9fce90d13fe927614a3b9e9e81826b23692e0fe`.
- Reviewed main bases: Adva `60b37d8a4c155994acc7207f2feecc1da7cc6441`;
  library `bc92ddce3053d6afc7df39dabeecf00a5ae0db07`.

Both producer branches were two commits ahead of their main, with no commits
behind. Adva's gitlink already selects the library producer head. Land the
library branch first, then the consuming Adva branch. Preserve that exact
gitlink: a library merge commit need not replace its already-reviewed parent.

## Receiving evidence and limits

The receiver fetched the changed text and binary resources at those revisions.
Fourteen of fifteen staged artifacts matched their declared byte counts and
SHA256 values. The GitHub contents interface returned empty content for
`golden-ratio/source/reference/Golden_ratio.pdf`; its blob interface rejected
binary UTF-8 decoding. The PDF was not reconstructed, replaced or excluded
from the original calibration's acceptance requirements.

A separate bounded receiving audit called the existing field/sequence, word,
rectangle, icosahedron, golden-rectangle, hyperbolic, substitution, search,
refusal, receipt and external-replay routines. It did **not** call the original
whole-resource calibration or issue its `Passed` status.

- Arithmetic/replay checks: **738**, nodes **2635**.
- Eleven result payloads matched the producer's retained evidence exactly.
- The delivered child checker replayed with agreement; this is reproduction
  of the delivered implementation, not a new independent oracle.
- Receiving audit wall time: **0.166736165 seconds**, including retrieval from
  the local snapshot, digest checks, the child replay and the small reuse below.
  Network retrieval and review/authoring time are excluded.
- Receiving process peak RSS: **14848 KiB**. Child peak memory was not measured
  separately in this audit.
- The audit was launched under an external 30-second timeout, a 25-second CPU
  limit and a 256 MiB address-space limit; no candidate search was performed.
- Documentary catalog and key-word check: **CatalogConsistent**, 23 entries
  and 23 names, 95 files, 101 references, 2268416 bytes, 0.005825845 seconds
  before serialization. The growth obligation remains **Open**.
- The pytest suite was **NotRun**: pytest is absent from both available Python
  installations. This is not a test failure or a test pass.
- Whole-resource calibration, PDF byte verification, and native Adva/Rust
  verification remain **NotRun** on the receiving side.

The producer's separately retained 815-check full calibration is not replaced
by these receiving numbers.

## Documentation clarifications

These qualifications govern reuse of the producer's prose and contract:

1. In the implemented field encoding `(p + q*sqrt(5))/2`, `p,q` are rational
   coefficients (`Fraction`), not necessarily integers. The integer-ring
   predicate additionally requires integer coefficients of matching parity.
   Integer-pair wording cannot describe all of Q(sqrt(5)).
2. The bound `0 < phi^(-n) < 1/2` is checked for **2 <= n <= 24**.
   It fails for n=1. The implementation already guards this with `n >= 2`.
3. The PDF routine checks pinned bytes, header, revision marker and trailer.
   Its title and creation date are copied from declared metadata; they are not
   parsed from the PDF by that routine. Header/trailer probes are not a full
   PDF well-formedness validator.
4. The bare calibration CLI uses hard-coded cooperative budgets and a child
   timeout. It does not install the contract's CPU/address-space limits.
   The receiving audit's explicit outer limits must not be attributed to it.
5. `word_residual_polynomial` returns only the translation component. Equal
   counts of `a` and `A` restore multiplier one, but do not in general
   eliminate negative powers from the translation Laurent polynomial.
   The particular nine-letter word checked here has no negative powers.
6. In the receipt's seed-versus-tail control, the ordered seeded bracket is
   [21/13, 13/8]: **21/13** is the lower endpoint. The executable counterexample
   29/18 < 21/13 is correct; one control description calls 13/8 the lower
   endpoint incorrectly.

These are scope corrections, not reasons to rewrite or re-pin the historical
witness. A future versioned contract should incorporate them explicitly.

## Small reuse: spectrum of a nonclosed word versus a closed affine word

From the preceding H2 calculation, let
G = [[1,1],[0,1]], U = [[1,0],[-1,1]].
Their commutator is H = G U G^-1 U^-1 = [[1,1],[1,2]], not the identity.
It has characteristic polynomial t^2 - 3t + 1, with roots phi^2 and phi^-2.

The delivered tool computes the translation residual of the affine word
`abbbaBAAB` as -(t^2 - 3t + 1). Using its actual K implementation:

- phi^2 has coefficient pair [3,1], phi^-2 has pair [3,-1];
- both annihilate the characteristic polynomial and the word residual;
- the affine word is the identity at both parameters;
- at the fresh non-root control phi^4, it is not the identity.

Thus the two constructions share a parameter equation. H itself remains a
nonidentity Mobius transformation of H2; the affine word's closure does not
close H, identify the two actions, erase history or establish universality.

A minimal reproduction from the reviewed paired checkout is:

```sh
timeout 5s python -S - <<'PY'
import importlib.util
from pathlib import Path
path = Path("experiments/golden_ratio/calibration.py")
spec = importlib.util.spec_from_file_location("golden", path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
word = "abbbaBAAB"
p = m.word_residual_polynomial(word)
assert p == {2: -1, 1: 3, 0: -1}
for exponent in (2, -2):
    t = m.PHI ** exponent
    assert t*t - m.rational(3)*t + m.ONE == m.ZERO
    assert m.evaluate_polynomial(p, t) == m.ZERO
    assert m.affine_word(t, word) == m.IDENTITY
assert m.affine_word(m.PHI ** 4, word) != m.IDENTITY
print("SharedParameterChecked; distinct actions retained")
PY
```

## Next minimal step

On a complete checkout, replay the original calibration and the three affected
pytest modules. For mathematical continuation, bind a closure judgment to its
action, parameter, observation frame and retained word, so a shared polynomial
cannot transfer closure between the two constructions.
