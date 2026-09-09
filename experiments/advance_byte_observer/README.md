# One bounded step through adva.py

This research-only `advance` profile continues Research 0161's byte projection
and Research 0160's observer refinement. It has one fixed question and no
general task selection, native learning, `free`, or automatic continuation.

The first actual run and its finite interpretation are recorded in
[RESULTS.md](RESULTS.md), with links to the complete retained evidence under
[`evidence/run-01/`](evidence/run-01/). All 61 files are byte-for-byte copies,
including the original report and its 60-file SHA256 inventory. Absolute local
paths inside the historical reports are retained as recorded context.

For every byte b=0..255, let u=(b mod 8)+1 and v=b-2u. Compile four independent
PSC0 programs, each with 256 output positions:

| Profile | Per-byte source |
| --- | --- |
| copy-add | `(add (add (copy u)) v)` |
| scale-add | `(add (scale 2 u) v)` |
| repeated-literal | `(add u (add u v))` |
| reordered-copy | `(add v (add (copy u)))` |

Here u and v are replaced with literal constants. Repeated constants are
separate constant nodes; they do not identify input sources. All four programs
are closed and source-free. The full Rust artifacts retain graph structure,
occurrences, graft information, and history, including operations not visible
in the final values.

The observer ladder cumulatively reads byte value, dependency-node count,
operation-name histogram, and operation names in original compilation order.
Every output's exact node IDs and every partition are retained. The first
separating level is relative to this list and this finite family. Compilation
order is not a canonical causal schedule; the observation is an external
readout of fresh checked artifacts, not a native observer certificate.

The existing Rust `quine_relay` example is rebuilt from pinned, unchanged
kernel inputs. It reloads the same epoch twice as a replay control, checks
doubling and zero refusals, then performs four positive emissions plus three
controls. Separately, pinned 0161 Python sources evaluate the complete byte
family and four iota round trips in a limited child. These remain an external
model; cross-language value agreement grants no language equivalence.

The complete [contract](contract.json) fixes input pins, question, controls,
limits, and outcomes before execution. A receipt binds the exact previous
receipt bytes, but does not authenticate them or repair their earlier ancestry.
No math material, epoch, or historical evidence is rewritten.

From the adva checkout, use a new output path. The `target` directory must exist:

```sh
timeout 190s python3 python/adva/adva.py advance \
  --output target/advance-byte-observer-20260909-01
```

The 180-second cooperative budget includes the offline build, all subprocesses,
fresh controls, analysis and inventory. Child processes have CPU/address/file
caps and process-group cleanup. The outer 190-second timeout is the final host
guard; a forced kill can prevent checkpoint completion. Resource exhaustion
is Unknown and failed controls are Rejected. Partial artifacts remain. There
are zero correction replays in this contract; no repeated campaign starts.

`report.json` retains the source revision, runtime implementation copies,
predecessor SHA256, observations, controls, finite delta and artifact inventory.
`comparisons.json` records all 256 per-byte partitions. The complete native
JSON files support later native rechecks; parsing those files alone never
constitutes semantic admission. Output `.bin` files contain every byte 0..255
and should be inspected as binary data.

Engineering checks (outside the experiment account):

```sh
.venv/bin/python -m pytest -q tests/python/test_advance_boundary.py \
  tests/python/test_math_catalog.py tests/python/test_quine_relay_boundary.py
```
