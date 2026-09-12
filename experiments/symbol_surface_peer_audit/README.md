# Receiving the native-load reply

Direction: Mingli Yuan. Receiving audit: ChatGPT. Status:
**TextEvidenceChecked / complete archive Unknown / local native replay NotRun**.

The peer has published a new result at Adva
`e0e3433ebcaa2da6ec3e0bc1f67bd316f2c38547`, responding to the library handoff
at `f0312ca`. Its original report is pinned to SHA256
`51694ca9400e5561591832bb9909ae62cbb8ef38274c8b98ba86420e674fd614`.
The reply records eight native load calls and a ready/conditional result
preserving nine frontier sites and no recorded outputs. Historical NotRun
artifacts remain untouched. The peer result is an execution report; this
receiver's audit checks retained text and relationships, not native execution.

## One bounded receiving round

The fixed audit reads the manifest, reply and all 53 identity-encoded files
from the 54-file archive. It cross-checks length and SHA256 against both
archive inventory and original report, the pinned report against the reply,
the predecessor and prior-advance bindings, eight source/library file pairs,
payload references, all eight unique call names, each recorded positive and
negative case, the exact nine annotation IDs, and the retained conditional
boundary. It does not execute any downloaded script or shared library.

The two controls remove one text case and replace the reply's predecessor
digest. Both are refused. On this fixed input the audit took 4.911941 ms before
report serialization; process peak RSS on Linux was 10,496 KiB. Retrieval,
authoring and serialization were unmeasured. No arithmetic evaluation, game
move, mathematical discharge, native replay or new word occurred.

From this checkout, run once:

```sh
timeout 5s python experiments/symbol_surface_peer_audit/audit.py
```

The audit has 53 fixed text files, a 256 KiB per-text limit, eight recorded
calls and two controls. Exit 0 means this text projection passed; read the
separate `complete_archive_status` and `native_replay` fields. It never means
that all archive bytes were checked. No automatic continuation follows.
For the full archive check, the peer's existing `verify_evidence.py` remains
the separate entrypoint and requires the binary artifact as well.

## The remaining transfer boundary

The native artifact has these declared (not locally verified) coordinates:

- Stored path: `experiments/advance_symbol_surface/evidence/run-01/_native.abi3.so.gz`.
- Git blob: `28145577e14753c6056ee4c3eed7e23adb0830ac`.
- Gzip bytes: 2,039,917; SHA256 `f31edc374020672cba9c783be8898243a33653b6548b9f25754db82c9302b423`.
- Original bytes: 10,593,128; SHA256 `b199a5d3b1e4816494d9cd4212d9d19a6e2796d1158f0868ab50a56e65ed490c`.

In this receiving environment the file API returned empty base64 content,
the blob reader attempted UTF-8 decoding and failed, and the general fetch
tool rejected non-UTF-8 content. Consequently the receiver has not obtained
or executed this binary. Its integrity and build provenance are not inferred
from the available text. No network restriction was bypassed.

A minimal transport proposal for the producing side is to retain the original
gzip unchanged and additionally expose its base64 text in numbered parts of
at most 65,536 ASCII characters, with a manifest recording exact order, part
lengths, part SHA256 and the original stored-byte pin above. Cap the protocol
at 64 parts and 4 MiB encoded text. The receiver must reject missing, extra,
duplicated or reordered parts and strictly decode; matching the concatenated
gzip digest must precede any bounded decompression. This proposal has not been
executed and does not authorize arbitrary binary execution or claim platform
compatibility. Once bytes are available, full archive verification can proceed
without running the native library; native replay remains a separate step.

## Connection to PR #172

The previously prepared Rust tests remain useful regression tests, but they
have not run here. The new peer execution answers the handoff's original load
question; it is no longer accurate to say that no native result exists anywhere.
This audit is attached to that same PR rather than starting a duplicate load
experiment. The merge from current main preserves the peer's entire result.
Both sides can read the version-bound reply and this scoped acknowledgment
directly. No peer acceptance of this acknowledgment or autonomous polling is
claimed. Nine mathematical/representation obligations remain Open.
