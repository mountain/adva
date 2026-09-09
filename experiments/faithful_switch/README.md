# Faithful switches and finite reverse observer search

See [Research 0160](../../docs/research/0160-faithful-switch-and-reverse-observer-search.md)
for the mathematical comparison, attribution, exact scope, results, and Open
native obligations.

This is a standalone Python standard-library calibration of direct Laurent
Burau matrices against Artin free-word actions followed by abelianized Fox
derivatives. It retains every source word and result. A second stage searches
a fixed formal-jet ladder for separators of supplied coarse collisions.

The archived `evidence.json` is from one bounded successful invocation.
Its source/contract hashes and `manifest.json` identify the exact bytes.
They are not authentication or native semantic certificates.

To reproduce on Linux with Python 3.11 or later, from this directory:

```sh
timeout 30s python3 calibration.py --output evidence-new.json
```

Use a fresh path. The script refuses to overwrite evidence. A reproduction is
a separate invocation; do not delete or replace the original output. The
contract is trusted local input, not an arbitrary-input service boundary.

The run does not reprove the published four-strand faithfulness result,
validate geometric disk constructions, infer native Adva cells from matrices,
or establish a universal second-order observer. The successful second-order
separation is specific to the complete declared short-word family.
