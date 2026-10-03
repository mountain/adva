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

Authored by ChatGPT (OpenAI), contributed under Unknown v0.3 through Mingli
Yuan's authorized GitHub account proxy. Account use is not his authorship,
review, endorsement or correctness guarantee.
