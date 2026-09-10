# Interpretation obligation: one finite native-facing calibration

See [Research 0166](../../docs/research/0166-interpretation-obligation.md).
The contract predates the sole invocation. `run-01/` retains its exact bytes,
executed source, four fresh Rust reports, stdout/stderr, eleven diagnostic cases
and costs. It does not contain the machine-specific executable; its actual
SHA256 and the source/build reference are retained.

From a current authorized Adva checkout with the pinned library available:

```sh
cargo +1.94.0 build --locked --release -p adva-witness --bin adva
timeout --kill-after=2s 22s python3 experiments/interpretation_obligation/calibration.py \
  --adva target/release/adva --library adva-library --output /tmp/interpretation-replay-01
```

Use a new output directory. Building/installing the toolchain is outside this
20-second calibration contract. The recorded run used the previously built
bootstrap executable, verified against its recorded reference hash. Another
trusted local build may have different executable bytes: the script records
that difference and still requires the same library bytes, embedded checker
revision, selected snapshot digest and scoped native responses. This is not an
executable authentication service or a reproducible-machine-code theorem.

The script imposes Linux CPU/address-space/file limits and four child timeouts.
The external `timeout` guards blocked work/checkpointing. A hard kill may leave
only partial files. No retry, widened scope or new child campaign starts
automatically. The archived comparison replay uses the same Python checker;
it is not an independent proof kernel. The small AST meaning is stipulated,
not learned from arbitrary prose. API `judge` is a diagnostic over this finite
family of freshly generated records and declared corruptions, not a general
untrusted-report importer.

Check stored bytes without running Rust:

```sh
python3 - <<'PY'
import hashlib, json
from pathlib import Path
p = Path('experiments/interpretation_obligation/run-01')
r = json.loads((p / 'report.json').read_text())
for name, pin in r['files'].items():
    raw = (p / name).read_bytes()
    assert len(raw) == pin['bytes']
    assert hashlib.sha256(raw).hexdigest() == pin['sha256']
assert (p / 'contract.json').read_bytes() == (p.parent / 'contract.json').read_bytes()
assert (p / 'calibration.py').read_bytes() == (p.parent / 'calibration.py').read_bytes()
print('stored input/report integrity checked; no native replay')
PY
```
