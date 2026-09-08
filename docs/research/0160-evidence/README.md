# Research 0160 evidence: bounded advance loop

The three-cycle bounded advance loop ran locally on 2026-09-07 with the
synthetic six-slot pipeline driver. Files are byte copies of the local
`/Users/mingli/Adva/AEG/.campaign` records; this registration does not re-run
the loop.

| File | Content |
| --- | --- |
| [advance-loop-summary.json](advance-loop-summary.json) | Loop summary: 3 cycles x (100 rounds x 12 launches), learn/run Completed, free AdapterUnavailable, status Unknown, stopped by the cycle bound, no breakthrough |
| [driver.py](driver.py) | The bounded advance-loop driver (byte copy of the local `.advance-loop.py`) |
| archive-cycle1/ | Pre-loop 100-round campaign output archived at cycle-1 start (baseline) |
| archive-cycle2/ | Loop cycle 1 output |
| archive-cycle3/ | Loop cycle 2 output |
| final-rounds/ | Loop cycle 3 output, retained in place with its summary.json |

Each round directory retains the six learn slots (transition, frontier, stdout,
stderr), the run slots, and the phase reports. Free remains
NotRun/AdapterUnavailable throughout. A new run requires a human-written
authorization marker; this registration does not restart the loop. No knowledge
epoch, native word, or catalog entry is produced; the math growth obligation is
unchanged.
