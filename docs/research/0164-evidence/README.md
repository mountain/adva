# Retained Quine relay evidence

This bundle preserves 152 original text artifacts from the local experiment
and publication validation. The four large native JSON reports are stored as
lossless gzip; `manifest.json` records both stored and original byte lengths
and SHA-256 digests. One compiler log is also compressed to preserve its
original whitespace. Original reports, paths, contracts and source snapshots
are unchanged. The two platform-specific `q-bin` executables remain local;
their sizes and hashes are recorded as omissions, and `q.rs` is retained.

| Directory | Recorded outcome |
| --- | --- |
| `run-01` | Linker file-size exhaustion before any relay candidate was constructed. The original report says Rejected and incorrectly counts one candidate. Its retained addendum classifies the failure as Unknown; no original record is rewritten. |
| `run-02` | One explicitly debited correction; complete byte closure and seven passing controls. |
| `publication-03` | One separately budgeted publication validation; the same byte closure and controls, with the revised kernel-content gate. |
| `postcommit-check` | The executed implementation bytes equal commit `16b96e2ac256bba4ac3058a1d9272049da544a75`; the revised source gate also passes after that commit. |

The initial commit command lacked a configured Git identity, so the full
publication relay ran before the successful commit. Its source snapshots were
then compared byte-for-byte with the actual commit, and the Git boundary was
checked after committing. This is not recorded as a second full relay.

The three relay supervisor invocations used 50 supervised calls and 34.270079
child CPU seconds in total. The post-commit gate check used two additional
Git calls and is recorded separately. Build failure costs remain included.
Compilation subprocesses are descendants of those supervised calls; these
counts do not claim to enumerate every process forked by Cargo or rustc.

From the repository root:

```sh
python3 experiments/quine_relay/verify_evidence.py
```

This command checks every stored file against the manifest, lossless
decompression, retained Python byte equality, repeated Rust output, the seven
recorded controls and the two distinct retained diagrams. It does not execute
the generated programs, revalidate native certificates, authenticate the
records or begin a new research trial. CI performs this same bounded check.

For an independent native replay, use the instructions in
[`experiments/quine_relay/README.md`](../../../experiments/quine_relay/README.md).
An old local-only contract describes its original trial. Publishing this
selected copy was subsequently authorized by the user; that later authorization
does not alter the historical contract, admit a library entry or promote a
native semantic operation.
