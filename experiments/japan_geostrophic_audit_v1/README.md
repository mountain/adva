# Frozen Japan jet physical review v1

See Research 0231 and the public report:
https://climatetensor.io/research/japan-geostrophic-audit-v1/

The supplied URL is January 2026; no December 2026 forecast exists in the
frozen release. These original scripts and aggregate measurements do not
change or reissue any forecast. No 2026 observations verify either month here.

The full 592-file frozen cache remains outside the repository at:
/home/ubuntu/research-inputs/japan-geostrophic-audit-20260924-v1/frozen

The public review-bundle.zip contains the separately admitted original plotting
fields, which are intentionally NOT stored in Adva. To reproduce the six main
rows, download and unzip that bundle outside the repository, then run:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 verify_summary.py --root .
```

NumPy 2.4.6 and Python 3.11.15 were used; all dependencies remain separate.
An optional full fixed replay using that bundle and the complete local cache is:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 reproduce_full.py \
  --frozen /home/ubuntu/research-inputs/japan-geostrophic-audit-20260924-v1/frozen
```

Original run allowance is spent. Optional reader exact replay has its own
one-launch persistent ledger and limits; it was not launched by this review.
Missing cache or plotting arrays is Unavailable, not a successful reproduction.
No new trial, parameter search or inference is authorized by deleting a ledger.

Original plot implementation and the later presentation-only label fix are both
retained. The figures and field arrays are linked from the public report, not
incorporated into this Adva publication unit. Frozen contract wording correction,
preflight path repair, retained equatorial warning, and deployment permission
repair are documented; none required numerical reselection.

The independent six-row checker passed with maximum arithmetic difference
5.16e-13; all 592 frozen sources remained unchanged. Desktop/mobile local and
HTTPS report checks passed. HTTPS bytes of all 34 review files matched and CORS
allows read-only Observable access. This is engineering evidence, not source
truth authentication, untouched forecast skill or ENSO attribution.

Codex (OpenAI), original contribution under Unknown v0.3, through Mingli Yuan's
authorized GitHub proxy. His account is not authorship, review or endorsement.

The first staged whitespace check flagged CSV CRLF line endings. Adva CSV copies
were normalized to LF before commit; numerical contents and original website
CSV bytes are unchanged. The exact admission record was refreshed outside the
repository before importing these format-only replacements.
