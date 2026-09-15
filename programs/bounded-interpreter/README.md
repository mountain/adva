# An arithmetic interpreter written in the Adva research data language

The unchanged `interpreter.adva` contains 51 typed instructions. Rust executes
generic data, stack, integer and control operations. The program itself selects
the meaning of object tags and the order of evaluation. It has no host evaluator
callback. This is a separate research profile, not ordinary PSC0 source.

Object syntax is finite tagged data:

- tag 0 with one integer field: a literal;
- tag 1 with two object fields: addition;
- tag 2 with two object fields: multiplication.

The supplied `input.json` encodes `2 + (3 * 4)`. Integers are signed 64-bit,
checked exactly; overflow rejects. A node is an ordered tree value, not a native
semantic identity. The register names and `instruction-labels.json` make the
bytecode's dispatch, expansion, reduction and return locations inspectable.

Build and run from the repository root into fresh paths:

```sh
cargo build --locked -p adva-witness --bin adva
target/debug/adva data-run programs/bounded-interpreter/interpreter.adva \
  --input programs/bounded-interpreter/input.json --fuel 2048 --quantum 17 \
  --output /tmp/adva-interpreter-prefix.adva
target/debug/adva data-run programs/bounded-interpreter/interpreter.adva \
  --input programs/bounded-interpreter/input.json --fuel 2048 --quantum 2048 \
  --resume /tmp/adva-interpreter-prefix.adva --output /tmp/adva-interpreter-result.adva
```

The first call suspends. The second rechecks the 17-step prefix and returns 14
after 134 total instruction steps. The original lifetime fuel remains 2048;
the replayed 17 steps are separately recorded checking work. Passing a different
original fuel, program or input with that checkpoint rejects.

For receiving only, replace `--resume` with `--check`, set `--quantum 0`, and
choose another fresh output path. Admission failures exit 2 without a run;
runtime rejection retains a run and exits 2. Suspension and fuel exhaustion
retain their exact status and exit 0, without certifying nontermination.

The interpreter's own instruction list is not in its arithmetic object grammar.
This is interpretation of multiple programs as data, not self interpretation.
See [the report](../../docs/research/bounded-native-data-interpreter.md).
