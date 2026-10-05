# Held-out continuation receiving

This project-original bounded experiment uses a separate Perl process to
construct two new canonical problem--history--budget tuples and matching
terminal-resolution receipts. The constructor imports neither gate receiver
and supplies no expected gate classification. The existing Python and Node
receivers then classify exactly the constructed bytes.

Reproduce into a new directory:

```console
python experiments/continuation_resolution_heldout/run.py \
  --output /tmp/adva-continuation-resolution-heldout
```

The comparison layer checks only receiver agreement and byte-identical tuple
preservation. Divergence remains `UnknownImplementationAgreement`; agreement
does not authorize continuation, add fuel or establish mathematical truth.

Authored by ChatGPT (OpenAI), contributed under Unknown v0.3 through Mingli
Yuan's authorized GitHub account proxy. Account use is not his authorship,
review, endorsement or correctness guarantee.
