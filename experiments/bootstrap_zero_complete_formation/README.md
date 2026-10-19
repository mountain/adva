# Bootstrap Zero complete finite formation

This package freezes Research 0267's finite syntax-formation boundary. It adds
no stable API and performs no arithmetic evaluation.

From repository root, replay the new cases and then the complete research-local
Bootstrap Zero suite:

```sh
python -m pytest -q tests/python/test_bootstrap_zero_complete_formation.py -p no:cacheprovider
python -m pytest -q 'tests/python/test_bootstrap_zero*.py' -p no:cacheprovider
python -m ruff check tests/python/test_bootstrap_zero_whole_cut_grammar.py tests/python/test_bootstrap_zero_distributivity_record.py tests/python/test_bootstrap_zero_complete_formation.py
python -m ruff format --check tests/python/test_bootstrap_zero_whole_cut_grammar.py tests/python/test_bootstrap_zero_distributivity_record.py tests/python/test_bootstrap_zero_complete_formation.py
```

The exact frozen question and prohibitions are in `contract.json`; the measured
local replay is in `evidence/attempt-1/execution.json`.
