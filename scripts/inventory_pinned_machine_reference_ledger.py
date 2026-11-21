#!/usr/bin/env python3
"""One production attempt; verify saved evidence offline. No receiver invocation."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import stat
import subprocess
import sys
import tempfile
import time

import inventory_pinned_machine_root_surface as prior

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments/native_input_binding_serialized_leaf_request"
CONTRACT = EXP / "machine-reference-ledger-contract-20261106.json"
RUN = EXP / "machine-reference-ledger-20261106"
SCHEMA = "adva.research.machine-reference-ledger.v1"
LEDGER_CAP = 8 * 1024 * 1024


def encode(value):
    return json.dumps(value, ensure_ascii=True, separators=(",", ":")).encode("ascii")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def sync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


@contextmanager
def staged(target):
    # Private tempfile on the same filesystem. A killed process may leave an
    # untrusted .tmp file. Readers only consider the named receipt and files.
    with tempfile.NamedTemporaryFile(dir=target.parent, suffix=".tmp", delete=False) as f:
        tmp = Path(f.name)
        try:
            yield f
            f.flush()
            os.fsync(f.fileno())
            f.close()
            os.replace(tmp, target)
            sync_dir(target.parent)
        finally:
            tmp.unlink(missing_ok=True)


def save(path, value):
    with staged(path) as f:
        data = encode(value) + b"\n"
        require(f.write(data) == len(data), "short JSON write")


def regular_bytes(path, limit):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as f:
        info = os.fstat(fd)
        require(stat.S_ISREG(info.st_mode) and info.st_size <= limit,
                "expected a bounded regular file")
        data = f.read(limit + 1)
        require(len(data) == info.st_size, "unstable file size")
        return data


def load_json(path, limit=1_000_000):
    return json.loads(regular_bytes(path, limit))


def frozen_contract(digest):
    raw = CONTRACT.read_bytes()
    require(sha(raw) == digest, "contract SHA-256 mismatch")
    contract = json.loads(raw)
    for path, expected in contract["input_sha256"].items():
        require(sha((ROOT / path).read_bytes()) == expected, "frozen input SHA-256 mismatch")
    lock = load_json(ROOT / "dependencies/adva-machine.lock.json")["machine"]
    require(lock["revision"] == contract["machine"]["revision"] == prior.EXPECTED_REVISION
            and lock["repository"] == contract["machine"]["repository"], "lock mismatch")
    return contract["selection_anchor"]


def check_manifest(manifest, anchor):
    require(len(manifest) == anchor["files"]
            and sum(row["bytes"] for row in manifest) == anchor["bytes"]
            and sha(encode(manifest)) == anchor["sha256"], "selection anchor mismatch")


@contextmanager
def search_timer():
    def timeout(_sig, _frame):
        raise SearchDeadline("content search deadline")
    previous = signal.signal(signal.SIGALRM, timeout)
    signal.setitimer(signal.ITIMER_REAL, prior.MAX_SEARCH_NS / 1e9)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


class SearchDeadline(RuntimeError):
    pass


class SearchFailure(RuntimeError):
    pass


def references(machine, manifest):
    started = time.monotonic_ns()
    folded = [(term, term.casefold()) for term in prior.TERMS]
    count = 0
    for entry in manifest:
        path = entry["path"]
        try:
            raw = regular_bytes(machine / path, entry["bytes"])
            require(len(raw) == entry["bytes"] and sha(raw) == entry["sha256"],
                    "machine file changed after preflight")
            lines = raw.decode("utf-8").splitlines()
            for number, line in enumerate(lines, 1):
                if time.monotonic_ns() - started >= prior.MAX_SEARCH_NS:
                    raise SearchDeadline()
                lower = line.casefold()
                terms = [term for term, needle in folded if needle in lower]
                if terms:
                    count += 1
                    require(count <= prior.MAX_HITS, "candidate bound exceeded")
                    yield {"path": path, "line": number, "terms": terms}
        except Exception as error:
            # All errors produced while advancing this file belong to search.
            # Never copy an exception message which could quote dependency data.
            raise SearchFailure(path, type(error).__name__) from error


def write_references(f, rows):
    digest = hashlib.sha256()
    count = size = 0
    for row in rows:
        data = encode(row) + b"\n"
        size += len(data)
        require(size <= LEDGER_CAP, "reference byte bound exceeded")
        require(f.write(data) == len(data), "short ledger write")
        digest.update(data)
        count += 1
    return {"entries": count, "bytes": size, "sha256": digest.hexdigest()}


def check_evidence(run, anchor, ledger):
    manifest_raw = regular_bytes(run / "manifest.json", 1_000_000)
    manifest = json.loads(manifest_raw)
    check_manifest(manifest, anchor)
    require(manifest_raw == encode(manifest) + b"\n", "noncanonical manifest")
    data = regular_bytes(run / "references.jsonl", LEDGER_CAP)
    require(len(data) == ledger["bytes"] and sha(data) == ledger["sha256"],
            "ledger bytes or digest differ")
    sizes = {entry["path"]: entry["bytes"] for entry in manifest}
    last = ("", 0)
    count = 0
    for line in data.splitlines(keepends=True):
        row = json.loads(line)
        require(list(row) == ["path", "line", "terms"] and encode(row) + b"\n" == line,
                "noncanonical reference")
        key = (row["path"], row["line"])
        terms = row["terms"]
        require(key[0] in sizes and type(key[1]) is int and 0 < key[1] <= sizes[key[0]]
                and key > last, "unknown, duplicate or unordered location")
        require(isinstance(terms, list) and terms and
                terms == [term for term in prior.TERMS if term in terms],
                "unknown, duplicate or unordered terms")
        last = key
        count += 1
    require(count == ledger["entries"] == anchor["candidate_lines"], "candidate count differs")


def collect(machine, run, anchor, digest):
    phase = "attempt_record"
    start = time.monotonic_ns()
    try:
        save(run / "phase.json", {"contract_sha256": digest, "phase": phase})
        phase = "preflight"
        save(run / "phase.json", {"contract_sha256": digest, "phase": phase})
        manifest, aggregate = prior.preflight(machine)
        require(aggregate == anchor["sha256"], "historical manifest differs")
        check_manifest(manifest, anchor)
        preflight_end = time.monotonic_ns()
        phase = "manifest_capture"
        save(run / "phase.json", {"contract_sha256": digest, "phase": phase})
        save(run / "manifest.json", manifest)
        check_manifest(load_json(run / "manifest.json"), anchor)
        phase = "content_search_and_write"
        save(run / "phase.json", {"contract_sha256": digest, "phase": phase})
        search_start = time.monotonic_ns()
        with staged(run / "references.jsonl") as f:
            with search_timer():
                ledger = write_references(f, references(machine, manifest))
                require(ledger["entries"] == anchor["candidate_lines"], "candidate count differs")
            search_end = time.monotonic_ns()
            if search_end - search_start > prior.MAX_SEARCH_NS:
                raise SearchDeadline()
        phase = "readback"
        save(run / "phase.json", {"contract_sha256": digest, "phase": phase})
        check_evidence(run, anchor, ledger)
        phase = "receipt_commit"
        save(run / "phase.json", {"contract_sha256": digest, "phase": phase})
        receipt = {
            "schema": SCHEMA, "inventory": "ReferencesRetained", "route_review": "Pending",
            "machine_revision": prior.EXPECTED_REVISION, "contract_sha256": digest,
            "selection": anchor, "manifest_file_bytes": (run / "manifest.json").stat().st_size,
            "manifest_file_sha256": sha((run / "manifest.json").read_bytes()),
            "ledger": ledger, "preflight_ns": preflight_end - start,
            "search_and_write_ns": search_end - search_start,
            "through_readback_ns": time.monotonic_ns() - start,
            "driver_ru_maxrss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        }
        save(run / "receipt.json", receipt)
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        if phase == "preflight":
            reason = "RefusedBeforeSearch"
        elif isinstance(error, (SearchFailure, SearchDeadline)):
            reason = "RefusedDuringSearch"
        else:
            reason = "EvidenceCaptureFailure"
        failure = {"status": "Unknown", "reason": reason, "phase": phase,
                   "contract_sha256": digest, "exception": type(error).__name__}
        if isinstance(error, SearchFailure):
            failure["path"], failure["exception"] = error.args
        # A directory fsync can fail AFTER renaming a receipt. Withdraw it. A
        # failed/missing supervisor exit is also disqualifying, even on I/O loss.
        (run / "receipt.json").unlink(missing_ok=True)
        save(run / "failure.json", failure)
        return 3


def capture(machine, run, anchor, digest):
    # Claim the designated attempt before forking; a crash never releases it.
    run.mkdir(mode=0o700)
    sync_dir(run.parent)
    start = time.monotonic_ns()
    pid = os.fork()
    if pid == 0:
        try:
            os.setsid()
            code = collect(machine, run, anchor, digest)
        except BaseException:
            os._exit(4)
        os._exit(code)
    timed_out = False
    while True:
        finished, status, usage = os.wait4(pid, os.WNOHANG)
        if finished:
            break
        if time.monotonic_ns() - start >= 90_000_000_000:
            timed_out = True
            try:
                os.killpg(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            _, status, usage = os.wait4(pid, 0)
            break
        time.sleep(0.02)
    exitcode = os.waitstatus_to_exitcode(status)
    # Only a clean supervisor record referring to this receipt permits verify.
    clean_exit = exitcode == 0 and not timed_out
    receipt_hash = sha(regular_bytes(run / "receipt.json", 1_000_000)) if clean_exit else None
    supervisor = {"worker_status": "ExitedCleanly" if clean_exit else "Unknown",
                  "contract_sha256": digest, "worker_exit": exitcode,
                  "timed_out": timed_out, "receipt_sha256": receipt_hash,
                  "elapsed_ns": time.monotonic_ns() - start, "wait4_ru_maxrss_kib_linux": usage.ru_maxrss}
    try:
        save(run / "supervisor.json", supervisor)
    except BaseException:
        (run / "supervisor.json").unlink(missing_ok=True)
        raise
    return 0 if clean_exit else 3


def verify(run, anchor, digest):
    supervisor = load_json(run / "supervisor.json")
    receipt_hash = sha(regular_bytes(run / "receipt.json", 1_000_000))
    require(supervisor["contract_sha256"] == digest and supervisor["worker_exit"] == 0
            and supervisor["timed_out"] is False and supervisor["receipt_sha256"] == receipt_hash,
            "missing successful supervisor evidence")
    require(not (run / "failure.json").exists(), "failed attempt")
    receipt = load_json(run / "receipt.json")
    require(receipt["schema"] == SCHEMA and receipt["inventory"] == "ReferencesRetained"
            and receipt["contract_sha256"] == digest and receipt["selection"] == anchor
            and receipt["machine_revision"] == prior.EXPECTED_REVISION, "wrong receipt")
    check_evidence(run, anchor, receipt["ledger"])
    raw = regular_bytes(run / "manifest.json", 1_000_000)
    require(len(raw) == receipt["manifest_file_bytes"] and sha(raw) == receipt["manifest_file_sha256"],
            "manifest file mismatch")
    return receipt_hash


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    cap = sub.add_parser("capture")
    cap.add_argument("--machine", required=True, type=Path)
    sub.add_parser("verify")
    parser.add_argument("--contract-sha256", required=True)
    args = parser.parse_args()
    try:
        require(sys.platform.startswith("linux"), "Linux execution profile required")
        anchor = frozen_contract(args.contract_sha256)
        if args.action == "capture":
            return capture(args.machine.resolve(), RUN, anchor, args.contract_sha256)
        receipt_sha = verify(RUN, anchor, args.contract_sha256)
        print(json.dumps({"verified_receipt_sha256": receipt_sha}))
        return 0
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as error:
        # Never print a full candidate, exception payload or a success fallback.
        print(json.dumps({"action": args.action, "status": "Unknown",
                          "exception": type(error).__name__}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
