# ADR 0036: Bounded prime verification before Python orchestration

Status: research V0 implementation; execution evidence is in Research 0148.

The finite prime witnesses in Research 0147 have an external Python checker.
The next agreed step is a Rust-owned finite verification boundary and a thin
`python/adva/adva.py` entry. Preparation for this step is now finalized; it
does not require solving the full quantified theorem or implementing native
`free`.

Add a separate research request/result schema and `adva-prime-verify` binary
inside `adva-witness`. The request contains one bounded natural-number list,
N, a proposed prime q, cofactor k and verification fuel. Rust rechecks the
input primes, exact product-plus-one, N=q*k, outside-list membership and q's
prime-divisor coverage. All integers are at most 65535, lists contain at most
six entries from 2 through 13, and checking fuel is at most 1024. Zero fuel
returns Unknown. This bounded profile uses exact Rust integers; no stable
Nat domain or Lisp operation is added. Existing BigInt expression APIs are
unchanged. A zero remainder is a valid divisibility result and is not routed
through `ExactExprV0::evaluate_guarded`.

The result retains the request, checked divisor prefix, consumed/remaining
fuel and status. A finite success allows only retention of this certificate.
`native_universe=NotImplemented` and `native_free=NotGranted` remain explicit.
No SourceId, OccurrenceId, EquationCell or program identity is allocated.

Python snapshots the request, invokes the selected native executable once
under finite time/output bounds, checks its protocol and echoed input, and
saves the native result and process history. It implements no prime checker
or arithmetic fallback. Missing tools produce BackendUnavailable/NotRun;
timeout and exhausted verification remain distinguishable. The executable
is a caller-selected trust input; a filename or checksum does not authenticate
an arbitrary executable. No network or publication operation is added.

The supported standalone invocation is
`python3 python/adva/adva.py prime-check REQUEST --native NATIVE --output NEW`.
The existing package initializer eagerly imports the PyO3 extension, so
`python -m adva.adva` is not promised to work without an installed extension.
This step does not rewrite `__init__.py`, shadow the package with a root
`adva.py`, or migrate directories.

The older six-stage learn roundtrip and its six subsequent requested free
slots are a separate task. Its p-to-2p-to-p witnesses are not prime witnesses;
its absent free adapter stays absent. One task's certificate never discharges
the other's guards or history obligations. General Adva result dispatch and
the full Universe(Prime) proof remain later explicit versioning decisions.
