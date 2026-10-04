# Continuation-resolution cross-language cross-check

This project-original bounded experiment gives the exact ten Research 0253
input triples to a zero-dependency Node receiver and compares its three-way
classification and preserved tuple with the archived Python receipts.

Reproduce into a new directory:

```console
python experiments/continuation_resolution_crosscheck/run.py \
  --output /tmp/adva-continuation-resolution-crosscheck
```

The run starts ten Node processes and no Python receiver or target process.
`ImplementationAgreement` is only a local finite comparison outcome. Any
classification, preserved-tuple or provenance divergence is retained as
`UnknownImplementationAgreement`; neither outcome grants continuation or
native authority.

The frozen retained execution keeps its one-second child deadline. A later
full-suite CI replay disclosed that this deadline is not a portable Node
startup envelope after a heavily loaded test job. The separate
[`ci-validation-contract.json`](ci-validation-contract.json) permits five
seconds per child only for a fresh validation replay, while retaining the same
ten processes, twenty-second outer deadline, 40,000 structural-unit limit,
inputs, receiver and semantic projection. Reproduce that profile with:

```console
python - <<'PY'
import importlib.util
from pathlib import Path

path = Path("experiments/continuation_resolution_crosscheck/run.py")
spec = importlib.util.spec_from_file_location("crosscheck", path)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
raise SystemExit(runner.main(
    Path("/tmp/adva-continuation-resolution-crosscheck-ci"),
    validation_timeout_seconds=5,
))
PY
```

A timeout remains an implementation or environment failure. It is not an
`UnknownImplementationAgreement` result or a semantic counterexample.

Authored by ChatGPT (OpenAI), contributed under Unknown v0.3 through Mingli
Yuan's authorized GitHub account proxy. Account use is not his authorship,
review, endorsement or correctness guarantee.
