# murphy with the Iota combinator spelled `ι`

Date: 2026-09-20. Direction: Mingli Yuan. Authored by DeepSeek Harness
(deepseek-v4-flash-vision-exp) through his authorized account proxy; account use
is not his authorship, review, endorsement or correctness guarantee.

This directory is a **derived publication unit**. It carries the murphy programs
with one change: the Iota combinator is written `ι` instead of `i`. The admitted
murphy unit under `experiments/murphy/` is **not** modified — its bytes, its
digests, its evidence and its admission record of 2026-09-19 stand exactly as
they were, and the transport packages built from it keep their pins.

## Why

One letter carries four meanings across this project and its neighbours:

| Where | `i` means |
| --- | --- |
| Mathematics | the imaginary unit |
| `spec/framework/iota-frame-v1.md` (adva-machine) | the complex structure `J` |
| the iota-lang case corpus | the **identity** combinator, with the Iota combinator written `ι` |
| the murphy documentary source | the **Iota** combinator |

Spelling the Iota combinator `ι` removes the collision on the murphy side, and
matches the spelling the iota-lang corpus already uses for the same combinator.

## The declared renaming

```json
{"from": "i", "to": "ι", "scope": "the Iota combinator token only; '*' is unchanged"}
```

Only that one token changes. A source in this unit contains `ι` and no `i`;
`*AB` still means application. Character counts are identical to the original
(823, 1647, 743, 671, 725); byte counts differ because `ι` is two bytes in
UTF-8.

| Program | Original file | Bytes | This unit | Bytes | SHA-256 (this unit) |
| --- | --- | ---: | --- | ---: | --- |
| `P` | `experiments/murphy/murphy.iota` | 824 | `murphy-iota-v0/murphy.iota` | 1236 | `48c0ad98…` |
| `PP` | `experiments/murphy/evidence/PP.iota` | 1648 | `murphy-iota-v0/PP.iota` | 2472 | `3309314b…` |
| `C` | `experiments/murphy/evidence/C.iota` | 744 | `murphy-iota-v0/C.iota` | 1116 | `89395853…` |
| `J` | `experiments/murphy/evidence/J.iota` | 672 | `murphy-iota-v0/J.iota` | 1008 | `fc900f7f…` |
| `N` | `experiments/murphy/evidence/N.iota` | 726 | `murphy-iota-v0/N.iota` | 1089 | `06c2d960…` |

`renaming.json` records the exact correspondence, including both SHA-256
digests per program and the frozen relations the rename must preserve.

## What must be preserved, and where it is checked

A rename may change spelling and nothing else. The relations the original unit
froze are listed in `renaming.json` and re-checked on the machine interface by
the research-local Iota substrate
(`experiments/iota-substrate/contract-murphy-renamed.json` in
`mountain/adva-machine`):

- the counted witness for the self-application `PP` — 1,808 contractions,
  `j` 822 / `S` 549 / `K` 437, node peak 7,627, normal-form digest
  `8d0434eb…`;
- the counted witnesses for the coordinate programs `C` (919), `J` (831) and
  `N` (897), with their rule histograms, node peaks and digests;
- the coordinate laws `C² = I`, `J² = N`, `J⁴ = I`, `C J C = N J`, `N² = I`,
  recomputed natively on the declared four-slot product;
- the two negative witnesses the unit retained: `J² ≠ I` and `C ≠ J` on opaque
  slots.

The check runs each of them in **both** spellings and requires identical
outcomes, so "preserved" means the two spellings are indistinguishable in every
relation the unit recorded — not merely that the new files parse.

## What this unit is not

- **Not a replacement.** It is a derived unit; the documentary spelling remains
  the one the 2026-09-19 admission record, its transports and their receipts
  pin. Nothing here reissues, retires or supersedes those digests.
- **Not a semantic change.** No rule, order, counting, encoding or bound is
  altered, and no claim about the murphy results is strengthened.
- **Not an admission.** It grants no native Adva operation, type, `Seal` or
  epoch; it registers no checker and makes no proof claim. Its verification
  statement points at an executed machine-side check, and the authority is that
  check and its retained residual.
