# Checked library epochs from Research 0150

These two files were actually published, reloaded and checked by Rust on
2026-09-06. This is a research snapshot store, not a stable Lisp module.

| File | Catalogue | Active candidates | Retained history | Scoped witness |
| --- | --- | --- | --- | --- |
| [epoch-0000.json](epoch-0000.json) | x, 2*x, x+x, x*x | 2*x, x+x | 5 rounds | 1 pair, 2 native nodes |
| [epoch-0001.json](epoch-0001.json) | Prior 4 plus 2*x*x | 2*x, x+x | Prior 5 plus observation at 2 | Same witness content |

Epoch 0 freshly checks the prior 0149 proposal; it does not import the old
receipt as current authority. Epoch 1 records the proposed extra candidate
and the explicitly supplied assumption f(2)=4. The extra candidate predicts
8, so it is excluded from the active set but remains in the catalogue. Both
old syntaxes and their common polynomial 2x are retained. These inputs were
supplied by the calibration, not discovered by the library.

The reader is `adva_witness::load_library_v0(directory, epoch, budget)`;
`reuse_library_word_v0` checks the loaded witness's concrete nonzero guards.
The loader replays the complete bounded parent chain and compares all content
with fresh Rust derivations. Do not use Serde decoding alone as admission.
Snapshot and witness hashes are integrity coordinates, not identities or
signatures. The fixed question is exact polynomial-shadow equality.

There is no mutable latest pointer. Epoch 1 is the terminal published version
of **this** recorded workflow, not a promise that every future caller may
reuse its assumptions. Further updates need a new finite run contract and
must append without overwriting these files.

See [the complete before/after report](../../docs/research/0150-evidence/run.json)
and [execution record](../../docs/research/0150-evidence/README.md).
