# Gold twin-machine closure control

This external finite experiment checks one pending Research 0090 negative
control. Two machines can have equal positive traces at an early stage while a
later positive event separates their eventual domains. Without a complete
finite coverage certificate, the receiver returns `CertificateObstruction`;
elapsed time never creates a negative certificate.

Run from the repository root into a new output directory:

```console
timeout 65s python -B -S experiments/gold_twin_close/supervise.py \
  --output-dir /tmp/adva-gold-twin-new
```

The committed attempt contains one primary run and one fresh-process replay.
It is not a stable Rust judgment, unrestricted Gold-theorem proof, Keraia mass
result, native close operation or universality claim.
