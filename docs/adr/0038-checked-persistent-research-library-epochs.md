# ADR 0038: Publish checked, immutable research library epochs

Status: research V0 implementation; execution evidence belongs to Research 0150.

Research 0149 has experiment receipts but no library loader. The requested
continuation adds a bounded Rust API in `adva-witness::library_checkpoint`
(re-exported at the crate root) and a `library_epoch` Cargo example. This
supersedes only the lack of persistence in that calibration; the 0149 source,
contract and receipts remain untouched.

Snapshots retain the complete bounded catalogue, supplied observations,
revisits, exact feature/exclusion readings and existing native witness nodes.
An origin names its input artifact and assumption authority. An epoch greater
than zero binds its predecessor digest and must retain every previous
candidate and history step as an exact prefix. A newly added candidate belongs
to the next epoch's frozen catalogue, not a changed kernel inside a run.

Loading validates a maximum four-epoch ancestry using only generated local
filenames, rederives diagnostic readings and ArithmeticTransition/Seal nodes
with `WitnessStoreV0`, and compares the complete snapshot. Only this procedure
creates `CheckedLibraryV0`. Stored flags, summaries or JSON decoding alone do
not authorize use. Checker-source/dependency revision changes fail closed.
The example imports old proposal data, not old certificate authority.

Publication rechecks the snapshot and parent before a no-clobber hard-link
commit of a flushed same-directory temporary file. Readers use explicit epoch
paths. There is no mutable latest pointer; an incomplete staging file is not
a committed epoch. This local, single-workflow boundary does not claim a
distributed transaction, authentication, global anti-fork accounting or
automatic recovery after physical interruption.

Only nonempty feature-closed terminal snapshots with valid required native
witnesses may publish. New observations may exclude a new candidate without
deleting it. Reuse of a loaded word separately checks every concrete nonzero
obligation: diagnostic point evaluation at zero is not guarded execution.

The stable operation registry, `adva.ir`, `AdvaDocumentV0`, semantic identities,
Q4/M6 formation and prior documentary library index are unchanged. No stable
learner, syntax discovery, generic program inverse, native M6 filler or
open-world convergence theorem is implied. Research 0150's additional point
observation is explicitly supplied, not inferred from old model closure.
