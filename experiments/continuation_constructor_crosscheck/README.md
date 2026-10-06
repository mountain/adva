# Continuation constructor cross-check

This bounded experiment compares two independently executed construction paths
for the two abstract Research 0255 continuation instances. The new Java 17
source-file constructor reads only `abstract-instances.tsv`. It runs before the
frozen Perl output directory exists. The frozen Perl constructor then builds
the same logical instances from its own project-original source.

The comparison requires all fourteen per-case JSON payloads to be canonical and
byte-identical. It does not compare the implementation-specific manifests. A
changed byte, incomplete coverage, noncanonical representation, or copied
source coordinate returns `UnknownImplementationAgreement`.

Reproduce into a new directory:

```sh
python experiments/continuation_constructor_crosscheck/run.py \
  --output /tmp/continuation-constructor-crosscheck
```

The Java, Perl and Python runtimes are external dependencies. This local finite
comparison is not native Adva authority, independent human review, receipt
truth, or a continuation permission.
