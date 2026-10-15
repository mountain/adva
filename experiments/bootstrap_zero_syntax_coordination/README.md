# Finite AM syntax coordination projection

Research 0268 defines a structured, research-local projection for an accepted
`AMTerm`. It preserves constructor order and bound leaf payloads without
assigning arithmetic or temporal semantics.

The corrected targeted replay is:

```sh
python -m pytest -q tests/python/test_bootstrap_zero_syntax_coordination.py -p no:cacheprovider
```

The broader local integration replay is deliberately `Unknown/NotRun`. Its
first launch passed a shell wildcard literally through `subprocess`, so pytest
found no file. The single correction replay permitted by the frozen contract
had already been spent on the deduplicated candidate count; the command was not
retried. A later continuation may run the literal expanded file list under a
new contract.

The exact question and limits are in `contract.json`; retained outcomes are in
`evidence/`.
