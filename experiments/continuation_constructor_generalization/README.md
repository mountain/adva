# Generic continuation-constructor generalization

This bounded experiment follows Research 0256 without reusing its two known
instances. Two distinct generic constructor sources were first frozen at commit
`3c448a2358f8ab3a325b9fe7ea28f1b4d9ae6b6c`. Only the next commit introduces
`third-instance.tsv`. Its case, attempt and problem identifiers occur in
neither frozen source.

The Java and Perl constructors each read the strict TSV and independently
derive seven canonical continuation payloads. The comparison requires exact
coverage, canonical representation, distinct source coordinates and
byte-for-byte agreement. A changed byte, missing payload, noncanonical payload
or same-source claim returns `UnknownImplementationAgreement`.

Reproduce into a new directory:

```sh
python3 experiments/continuation_constructor_generalization/run.py \
  --output /tmp/continuation-constructor-generalization
```

The Java, Perl and Python runtimes are external dependencies. This finite
comparison grants no receiver, continuation, effect or native authority and is
not receipt truth, mathematical truth or independent human review.

