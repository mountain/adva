# Bounded Metamath step calibration

`author.py` reproduces ordinary Adva bytecode; it is an authoring tool.
`run.py` encodes a frozen proof family, executes the Rust data-machine-v1 CLI,
receives each trace both natively and through a separately written generic
instruction interpreter, then invokes an external Metamath CLI for comparison.
The Adva runtime never calls either oracle.

With a separately obtained official Metamath executable at the contract's pin:

```sh
python experiments/bounded_metamath_step/run.py \
  --binary target/debug/adva --metamath /absolute/path/to/metamath \
  --output target/metamath-step-new-run
python -m pytest -q tests/python/test_bounded_metamath_step.py
```

The output directory must be new. Regressions are finite and stop on first
mismatch; there is no automatic retry or fuel refill. Missing external tools
block the live regression rather than yielding an external success. Frozen
evidence reception requires Python `blake3==1.0.9` and `pytest` but no live
Metamath installation. The dedicated CI performs both frozen reception and
fresh native/external runs.

See [contract](contract.json), [database](database.mm), [cases](cases.json) and
[research report](../../docs/research/bounded-metamath-proof-step-v0.md).
The closed label table is manually bound to this exact database; no external
input can add assertion frames, scopes or obligations to the program.

All first-party material by Codex (OpenAI), Unknown v0.3, through Mingli Yuan's
authorized account proxy; account use is not his review or guarantee. External
tool software remains separate and is not included in the evidence archives.
