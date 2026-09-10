# Pairing transport: a prepared native boundary and an executed exact check

Date: 2026-09-10. Continues `lattice-polar-and-mirror-boundary.md` and the
Proposed `lattice-polar` profile. Base main is
`0e4be5f81f59cd208b14bd21ea8a3250e8f7f289`; PR #175 was still an unmerged
draft when this continuation began. No stable semantic implementation changes.

## Result first

The exact external check covers **384/384** primal/dual pairs. Correct
contragredient transport preserves every pairing. Applying the primal shear
on the dual side gives **232/336** mismatches for TO24 and **24/48** for a new
cube fixture. Nine exact coefficient checks give `A^T B = I`.

An explicit linear Adva Lisp module and a runner through the existing
Rust-backed Python facade are supplied. **Native execution is UnknownRuntime**:
this environment has neither Cargo/rustc nor the installed `adva` extension.
Zero programs were compiled and zero native evaluations were performed.
The native test is prepared, not passed. Python syntax and source parenthesis
balance were checked; these do not establish Adva parsing or linearity.

## Frozen question and arithmetic

The complete pre-execution contract is
`experiments/pairing_transport/contract.json`. There is one route, no search,
384 pairs, a 30-second wall limit, 25 CPU seconds, 512 MiB address-space limit,
2 MiB output limit, 100 native nodes per program, and at most 1,155 native
evaluations including three reload checks. Output creation refuses overwrite.

Let

\[
A=\begin{pmatrix}1&1&0\\0&1&0\\0&0&1\end{pmatrix},\qquad
B=\begin{pmatrix}1&0&0\\-1&1&0\\0&0&1\end{pmatrix}=A^{-T}.
\]

For exact rational vectors, bilinearity proves

\[
\langle Ax,By\rangle=x^T A^T B y=x^T y.
\]

This is an elementary algebraic identity, not a numerical inference. The
nine integer coefficient checks independently instantiate the two supplied
matrices. They do not prove that a not-yet-compiled program implements them.

For the TO24 polar, write `y=q/6`. Its numerator list consists of the six
vectors `+/-3 e_i` and the eight vectors `( +/-2, +/-2, +/-2 )`.
The Rust-targeted input ports carry `x1,x2,x3,q1,q2,q3`; the denominator is
positive external interpretation data, not a seventh semantic wire or a
discarded native input. The unit-cube reuse has denominator one.

Only integer numerator calculations are requested from native Real/f64.
All input magnitudes are at most three. Inspection of these fixed expressions
bounds every arithmetic intermediate in absolute value by 54, well below
the exact-integer range of binary64. There is no division, underflow,
nonfinite input, or rounded one-third in the requested native evaluation.
This bound depends on both the submitted grammar and the finite input range;
it grants no general exact Real arithmetic.

The obstruction survives the coordinate change: `x=(1,2,0)`, `q=(3,0,0)`
have numerator three and denominator six. Correct transport sends them to
`(3,2,0)` and `(3,-3,0)`, again giving `3/6=1/2`. Using the wrong dual map
gives `9/6=3/2`. Neither renaming nor a smaller observational epsilon makes
the correct nonintegral pairing an integer.

## Proposed native binding and its residual

`programs/research/lattice-polar/pairing.lisp` uses the existing Lisp module
syntax. It is **not** the JSON research envelope accepted by `adva run`.
It exports `reference`, `transported`, and `wrong-dual`. Coordinate reuse is
spelled with explicit `copy` and ordered helper holes. No new builtin is added.

The supplied adapter is designed to perform these checks when the extension
is installed:

1. Verify the fixed source-byte pin, then request Rust parsing, linking and
   compilation via `adva.link_modules` and `Workspace.function`.
2. Read the compiler's root graft holes, ordered ports and exact entry wires;
   attach only external coordinate-role metadata to those existing bindings.
   Require the wires to occur in the Rust-checked initial cut.
3. Retain the complete IR, compilation/validation certificates, graft trace
   and whole-program slice. Require two copy operations in the transported
   and negative programs, zero in the reference.
4. Reimport each serialized IR through `adva.load_program`, which calls the
   Rust validator. Check unchanged IR, history and source partition. Imported
   IR must not gain a compilation certificate or a graft trace retroactively.
5. Compare all 1,152 native evaluations to the exact integer numerators and
   evaluate one fresh cube instance through each of the three reimports.
   Retain evaluation certificates. Equal values do not identify histories.

These steps are implementation proposals until executed. A hash is a byte
pin, not a SourceId, provenance certificate or runtime attestation. Replay
must use a build from the reviewed branch; a distribution/version attestation
is not implemented by this experiment. No mock Rust object is constructed.

The six-coordinate pairing program must **not** be submitted to the current
exactly-three-source triadic observer policy. The two mathematical triples
are not intrinsically K/X/t wire types. Extending that observer policy is a
separate obligation. This separates geometric dual coordinates from Adva's
reserved future `D*` observer pullback.

## Evidence, costs and replay

Saved files:

- `experiments/pairing_transport/evidence-corrected.json`: all 384 inputs, exact outputs,
  reduced rational pairings, wrong-direction controls, nine coefficients,
  source/contract/adapter hashes and explicit empty native evidence.
- `experiments/pairing_transport/execution-cost-corrected.json`: serialization/write
  timing and final process high-water RSS.
- `tests/python/test_pairing_transport_boundary.py`: a native-required test
  for the existing Python CI environment. It neither mocks nor skips Rust.

The corrected run used 4.969 ms for exact construction/checking and 5.163 ms
through the runtime-availability check. JSON serialization and same-code
roundtrip checking took 1.533 ms; writing took 0.118 ms. Final process
high-water RSS was **13,440 KiB (13.125 MiB)**. Output was 47,206 bytes;
that size is not a memory estimate.

One necessary correction replay was made. Static API review found that a
causal frontier contains `CutWire` wrappers, whereas graft entry wires are
`WireRef` values. The prepared adapter initially compared the different
shapes directly; it now compares each wrapper's `wire` field. The native
branch was not executed before or after this fix. Its runtime correctness
remains unverified. The first evidence/cost files are preserved under their
original names, with matching original code in `replay-before-cutwire-fix.py`.
Both runs' measured pre-serialization, codec and write intervals total
**13.116 ms**; their maximum high-water RSS is 13.125 MiB. This total is not
end-to-end process startup or research time.

Research, source formation, review and network time were not instrumented.
No acceleration, novelty, learned theorem or real-user utility measurement
is claimed. The cube reuse cost is included, not separately timed.

External replay (expected to retain UnknownRuntime when Rust is absent):

```bash
python3 -S experiments/pairing_transport/replay.py --output /tmp/pairing-external-fresh.json
```

After building/installing the reviewed branch with the repository's existing
development procedure, run **without `-S`**, so the installed extension is
visible:

```bash
python3 experiments/pairing_transport/replay.py --require-native --output /tmp/pairing-native-fresh.json
pytest -q tests/python/test_pairing_transport_boundary.py
```

The CLI enforces its limits. Missing native runtime writes the finite external
report and exits with code two under `--require-native`; it is not success.
Unexpected native errors propagate as failures. The native test has not been
run locally. No old experiment was rerun and no old witness was overwritten.

## Terminology and the next boundary

**No new word is needed.** `lattice-polar` remains Proposed, now with the
prepared `pairing-transport.v0` continuation. `refine`, `quotient` and `mirror`
retain their earlier boundaries. An external matrix identity, a compiled
program observation, a lattice judgment, and a mirror correspondence remain
different claims. The previous claims registry remains unchanged.

This helps Mingli and subsequent agents express the precise question to the
native machine: does the declared coordinate interpretation match this
checked program while its copies and history remain available? Benefit to
Jiamin's actual task remains unmeasured.

The next minimal step is a **single native-required replay** in the available
Rust build environment, saving the produced IR/certificates and any failure.
Only after that may the binding obligation be marked finite-native-checked.
Even success will not issue `free`, `Seal`, an M6 filler, a Pascal-derived
geometry admission, a mirror construction or a universality theorem.
