# Bounded native interpreter calibration

Direction: Mingli Yuan. Implementation and checking: ChatGPT (OpenAI), through
his account as authorized proxy; no personal endorsement or independent human
review is implied.

`contract.json` freezes the scope. `preflight.py` checks one native run with the
independent instruction receiver. `supervise.py` freezes sources, launches one
primary and one fresh campaign, and archives every original file before cleanup.
Each archive has 836 files, including programs, inputs, complete native traces,
mutated checkpoints, stderr refusals and costs. No failed full campaign occurred.

The two campaigns each ran 129 regular object programs and the declared controls
through 170 native CLI calls. Each passed 333 campaign assertions and independently
checked 16,911 machine-state edges. The direct object-language oracle is separate
from both the Rust VM and the Python instruction receiver.

For a new, explicitly bounded reproduction, after building the native binary
and installing the test dependencies:

```sh
timeout 260s python3 -B experiments/bounded_native_interpreter/supervise.py \
  --binary target/debug/adva --output /tmp/adva-interpreter-new-attempt
```

Choose a new directory. The supervisor includes source copying, checking and
archiving in its finite outer run; each child additionally has a 120-second wall
limit, a 110-second CPU limit and a 768 MiB address-space limit. This instruction
does not automatically repeat a failed campaign. Regression tests only receive
the retained evidence; they do not launch another search or native campaign.

The full source snapshot and raw archive bytes are retained in
`evidence/attempt-1`. `results.json` contains the common deterministic result;
`execution.json` keeps the distinct host costs and archive hashes.
