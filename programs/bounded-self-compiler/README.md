# Structured Adva compiler source

`compiler.source.adva` is the complete structured source of the compiler.
`compiler.seed.adva` is its externally seeded target; native self compilation
produces identical canonical target bytes. `compiler.input.json` represents the
source as ordinary v1 machine data. `example.source.adva` is the retained
five-iteration loop fixture, whose compiled target returns the exact integer 5.

See the [reusable compilation command and boundaries](../../experiments/bounded_self_compiler/README.md)
and [executed report](../../docs/research/bounded-self-compiler-and-futamura.md).
