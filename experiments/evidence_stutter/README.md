# Evidence-stutter calibration

This external bounded audit reads the pinned Git-tree projection retained in
`input-index.json`. It does not execute the archived 0162 children.

```sh
python3 experiments/evidence_stutter/calibration.py \
  --output /tmp/adva-evidence-stutter.json
```

Use a fresh output path. The program refuses overwrite, caps CPU and address
space, checks exact 400-round coverage, and runs variation, missing-coverage,
and duplicate-coordinate controls.

`EvidenceStutter` is a byte-projection judgment. It is not native semantic
identity, authentication, proof of no learning under every observer, or
permission to erase retained history.
