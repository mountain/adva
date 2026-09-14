# Keraia parametric-growth failed preflight

This directory retains a frozen contract, the draft checker and two failed
launch records. Neither launch reached a mathematical verdict. Attempt 1
failed on the isolated staging import path; attempt 2, after the only allowed
correction, failed because the draft called a nonexistent `oracle.named`
function.

The files are failure evidence, not an accepted certificate. See
`docs/research/keraia-parametric-growth-preflight-pause.md`.

The exact local launches were:

```console
timeout 65s python -B -S experiments/keraia_growth_certificate/supervise.py \
  --output-dir experiments/keraia_growth_certificate/evidence/attempt-1

PYTHONPATH=upstream/keraia_cycle_mass:upstream/keraia_read_machine \
timeout 65s python -B -S experiments/keraia_growth_certificate/supervise.py \
  --output-dir experiments/keraia_growth_certificate/evidence/attempt-2
```

The `PYTHONPATH` correction reflects only the temporary local staging layout;
in the repository the dependencies are sibling experiment directories.
