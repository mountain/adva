# Prefix-Keraia read-boundary calibration

Status: external bounded experiment, profile
`keraia.appendix-b.cbn-whnf.read.v0`. This is an independently written
weak-head/read interpreter inspired by Michael Stay's Appendix B, not an
execution of the published JavaScript, a full normalizer, or native Adva IR.

The first complete binary tree describes a program. Further bits are read
only when `R` is applied. A returned weak-head function accepts exactly the
consumed code; an unread suffix is `Overflow`. Missing input and exhausted
fuel remain separate unresolved states. `R` alone returns without reading.

`syntax.py` uses trees and de Bruijn variables; `oracle.py` independently
uses strings, named variables and capture-avoiding substitution. `machine.py`
exposes explicit state, checked input-free segments and prefix search.
`calibrate.py` compares 4,095 code words at three fuel cuts and fixed larger
fixtures. `supervise.py` freezes sources and runs a primary campaign followed
conditionally by one fresh process replay. It refuses an existing output
directory. Python standard library and Linux `prlimit`/`timeout` suffice.

From the repository root, after reading the contract and arranging one finite
continuation if needed:

```sh
timeout 100s prlimit --as=536870912 --cpu=95 --fsize=16777216 -- python3 -B -S experiments/keraia_read_machine/supervise.py --output-dir /tmp/keraia-read-new-attempt
```

The contract allows 15,000,000 counted work units, 45 seconds wall time,
40 seconds CPU and 512 MiB per child, including oracle and receipt checking.
One primary plus its conditional fresh replay has at most 30,000,000 child
work units; the outer 100-second/95-CPU-second cap also covers loading,
comparison and checkpoint output. No timer or fuel is renewed inside a run.
Do not invoke repeated attempts without their separately finite contracts.

The accepted record is `evidence/attempt-2/`: 28,820 assertions and 409,011
counted host-work units per process, with deterministic replay equality.
`attempt-1/` retains the first passing family, exact original sources and the
subsequently reproduced four type-boundary failures. `correction-1.json`
declares the correction; its controls are now part of the campaign.

Full evidence JSON retains accepted codes, all 4,095 final rows, unresolved
frontier states, read traces, example receipts and source digests. Elapsed
time and RSS are excluded from deterministic equality; work counters are not.
The frozen `sources/` copies make the earlier defective receiver reviewable.
They are historical records, not alternative current implementations.

At all three cuts the accepted mass is `1563/2048`; unresolved cylinders have
mass `485/2048`. This is a lower bound for the declared observation profile,
not a computed prefix of an optimal universal machine's Chaitin probability.
Cache and prefix search preserve the mass; neither narrows its unresolved
interval on this family. See the [research note](../../docs/research/keraia-read-boundary-and-weighted-prefix-search.md)
for cost comparisons, source discrepancies and the next missing evidence.

Authored by ChatGPT (OpenAI). Submitted through Mingli Yuan's GitHub account
as an authorized proxy; account ownership is not human review, endorsement,
or a correctness claim.
