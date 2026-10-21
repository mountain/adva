"""Finite complete-name correspondence for two-step open lines.

Research-local Python only; not native Adva identity or transport authority.
Original contribution by Codex (OpenAI), under Unknown v0.3.
"""

from collections import Counter
from dataclasses import asdict, dataclass, replace
import hashlib
import json
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


@dataclass(frozen=True)
class RenamingCorrespondence:
    whole: tuple
    cells: tuple
    ports: tuple
    sources: tuple
    occurrences: tuple
    channels: tuple
    thread_steps: tuple
    holes: tuple
    residuals: tuple
    alternatives: tuple


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      default=lambda item: item.value).encode() + b"\n"


def dependencies():
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "tests/python"))
    from experiments.open_line_residual import run as residual
    from experiments.open_line_thread import run as thread
    from test_bootstrap_zero_whole_cut_grammar import (
        Crossing, HistoryComposition, Hole, ThreadStep, Use,
    )
    return residual, thread, Crossing, HistoryComposition, Hole, ThreadStep, Use


def explicit_correspondence():
    """Independently stated fixture map; no prefix rule is trusted by the receiver."""
    return RenamingCorrespondence(
        whole=(("whole-6", "open-reuse-whole-6"),),
        cells=(("c-KX", "open-reuse-c-KX"), ("c-Xt", "open-reuse-c-Xt"),
               ("c-tK", "open-reuse-c-tK")),
        ports=(("p-KX-L", "open-reuse-p-KX-L"), ("p-KX-R", "open-reuse-p-KX-R"),
               ("p-Xt-L", "open-reuse-p-Xt-L"), ("p-Xt-R", "open-reuse-p-Xt-R"),
               ("p-tK-L", "open-reuse-p-tK-L"), ("p-tK-R", "open-reuse-p-tK-R")),
        sources=(("s-KX-L", "open-reuse-s-KX-L"), ("s-KX-R", "open-reuse-s-KX-R"),
                 ("s-Xt-L", "open-reuse-s-Xt-L"), ("s-Xt-R", "open-reuse-s-Xt-R"),
                 ("s-tK-L", "open-reuse-s-tK-L"), ("s-tK-R", "open-reuse-s-tK-R")),
        occurrences=(("o-KX-L", "open-reuse-o-KX-L"), ("o-KX-R", "open-reuse-o-KX-R"),
                     ("o-Xt-L", "open-reuse-o-Xt-L"), ("o-Xt-R", "open-reuse-o-Xt-R"),
                     ("o-tK-L", "open-reuse-o-tK-L"), ("o-tK-R", "open-reuse-o-tK-R")),
        channels=(("e-1", "open-reuse-e-1"), ("e-2", "open-reuse-e-2")),
        thread_steps=(("thread-a", "reuse-thread-a"), ("thread-b", "reuse-thread-b")),
        holes=(("h-tK-L", "hole-open-reuse-p-tK-L"),
               ("h-KX-R", "hole-open-reuse-p-KX-R")),
        residuals=(("r-tK-L", "residual-open-reuse-p-tK-L"),
                   ("r-KX-R", "residual-open-reuse-p-KX-R")),
        alternatives=(("h-tK-L-option-0", "hole-open-reuse-p-tK-L-0"),
                      ("h-tK-L-option-1", "hole-open-reuse-p-tK-L-1"),
                      ("h-KX-R-option-0", "hole-open-reuse-p-KX-R-0"),
                      ("h-KX-R-option-1", "hole-open-reuse-p-KX-R-1")),
    )


def namespace_ledgers(form):
    return {
        "whole": (form.name,),
        "cells": tuple(item.name for item in form.cells),
        "ports": tuple(item.name for item in form.ports),
        "sources": tuple(item.source for item in form.ports),
        "occurrences": tuple(item.occurrence for item in form.ports),
        "channels": tuple(item.name for item in form.channels),
        # Namespace declaration order is canonical by name and is independent of
        # the raw word occurrence order. rename_source below preserves occurrence order.
        "thread_steps": tuple(sorted(
            step.name for channel in form.channels for step in channel.thread
        )),
        "holes": tuple(item.name for item in form.holes),
        "residuals": form.residuals,
        "alternatives": tuple(alt.name for row in form.alternatives for alt in row.alternatives),
    }


def checked_maps(candidate, left, right):
    left_ledgers, right_ledgers = namespace_ledgers(left), namespace_ledgers(right)
    maps = {}
    for name in left_ledgers:
        pairs = getattr(candidate, name)
        if not isinstance(pairs, tuple) or any(
                not isinstance(pair, tuple) or len(pair) != 2 for pair in pairs):
            raise ValueError(name + " mapping must be an ordered tuple of pairs")
        if tuple(a for a, _ in pairs) != left_ledgers[name]:
            raise ValueError(name + " mapping source coverage/order differs")
        if tuple(b for _, b in pairs) != right_ledgers[name]:
            raise ValueError(name + " mapping target coverage/order differs")
        if len({a for a, _ in pairs}) != len(pairs):
            raise ValueError(name + " mapping source is not injective")
        if len({b for _, b in pairs}) != len(pairs):
            raise ValueError(name + " mapping target is not injective")
        maps[name] = dict(pairs)
    return maps


def rename_source(form, maps):
    cells = tuple(replace(item, name=maps["cells"][item.name],
                          left_port=maps["ports"][item.left_port],
                          right_port=maps["ports"][item.right_port]) for item in form.cells)
    ports = tuple(replace(item, name=maps["ports"][item.name],
                          cut=maps["cells"][item.cut], source=maps["sources"][item.source],
                          occurrence=maps["occurrences"][item.occurrence]) for item in form.ports)
    channels = tuple(replace(item, name=maps["channels"][item.name],
        source_port=maps["ports"][item.source_port], target_port=maps["ports"][item.target_port],
        thread=tuple(replace(step, name=maps["thread_steps"][step.name])
                     for step in item.thread)) for item in form.channels)
    open_ports = tuple(replace(item, port=maps["ports"][item.port],
        hole=maps["holes"][item.hole], residual=maps["residuals"][item.residual])
        for item in form.open_ports)
    productions = tuple(replace(item, source=maps["sources"][item.source],
        occurrences=tuple(maps["occurrences"][x] for x in item.occurrences))
        for item in form.productions)
    holes = tuple(replace(item, name=maps["holes"][item.name],
                          port=maps["ports"][item.port]) for item in form.holes)
    alternatives = tuple(replace(row, hole=maps["holes"][row.hole],
        alternatives=tuple(replace(alt, name=maps["alternatives"][alt.name])
                           for alt in row.alternatives)) for row in form.alternatives)
    return replace(form, name=maps["whole"][form.name], cells=cells, ports=ports,
        channels=channels, open_ports=open_ports,
        circle_order=tuple(maps["ports"][x] for x in form.circle_order),
        residuals=tuple(maps["residuals"][x] for x in form.residuals),
        productions=productions, holes=holes, alternatives=alternatives)


def rename_term(term, maps, HistoryComposition, Hole, Use):
    if type(term) is not HistoryComposition or type(term.first) is not Hole or type(term.second) is not Use:
        raise ValueError("outside the fixed predecessor AM candidate grammar")
    return replace(term,
        first=replace(term.first, name=maps["holes"][term.first.name]),
        second=replace(term.second, source=maps["sources"][term.second.source],
                       occurrence=maps["occurrences"][term.second.occurrence]))


def receive(left, right, left_term, right_term, candidate, dependencies_):
    residual, thread, _, HistoryComposition, Hole, _, Use = dependencies_
    residual._validate_whole(left)
    residual._validate_whole(right)
    if tuple(len(x.thread) for x in left.channels) != (2, 0) or \
            tuple(len(x.thread) for x in right.channels) != (2, 0):
        raise ValueError("correspondence profile requires thread lengths (2,0)")
    if type(candidate) is not RenamingCorrespondence:
        raise ValueError("candidate must have the exact local correspondence type")
    maps = checked_maps(candidate, left, right)
    mapped_source = rename_source(left, maps)
    if mapped_source != right:
        raise ValueError("right source differs from complete renamed source")
    mapped_term = rename_term(left_term, maps, HistoryComposition, Hole, Use)
    if mapped_term != right_term:
        raise ValueError("right AM term differs from renamed term")
    left_record = thread.receive_two_step(left_term, left, residual.propose(left), residual)
    right_record = thread.receive_two_step(right_term, right, residual.propose(right), residual)
    return {"status": "RenamingCorrespondenceChecked",
            "correspondence": asdict(candidate), "mapped_source": asdict(mapped_source),
            "mapped_term": asdict(mapped_term), "left_record": left_record,
            "right_record": right_record, "continuation_authorized": False}


def trial(output):
    started = time.perf_counter()
    contract = json.loads((HERE / "contract.json").read_bytes())
    for path, digest in contract["input_sha256"].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest:
            raise ValueError("input fingerprint mismatch: " + path)
    dependencies_ = dependencies()
    residual, _, Crossing, _, _, ThreadStep, _ = dependencies_
    formation_start = time.perf_counter()

    def with_word(form, prefix):
        word = (ThreadStep(prefix + "a", 1, Crossing.OVER),
                ThreadStep(prefix + "b", 2, Crossing.UNDER))
        return replace(form, channels=(replace(form.channels[0], thread=word), form.channels[1]))

    def reverse_word(form):
        return replace(form, channels=(replace(form.channels[0],
            thread=form.channels[0].thread[::-1]), form.channels[1]))

    left = with_word(residual._fixture(open_last=True), "thread-")
    right = with_word(residual.fresh_open(), "reuse-thread-")
    left_reverse, right_reverse = reverse_word(left), reverse_word(right)
    left_term, right_term = residual.term_for(left), residual.term_for(right)
    correspondence = explicit_correspondence()
    formation_seconds = time.perf_counter() - formation_start
    assertions = 0
    calls = 0
    records = []

    def check(condition):
        nonlocal assertions
        assertions += 1
        if not condition:
            raise AssertionError("check failed: " + str(assertions))

    def attempt(label, lsource, rsource, lterm, rterm, candidate, expected=None):
        nonlocal calls
        calls += 1
        check(calls <= contract["budgets"]["max_receiving_calls_per_attempt"])
        before = time.perf_counter()
        try:
            value = receive(lsource, rsource, lterm, rterm, candidate, dependencies_)
            reason = None
        except ValueError as error:
            value, reason = None, str(error)
        seconds = time.perf_counter() - before
        if expected is None:
            check(value is not None and reason is None)
            check(value["continuation_authorized"] is False)
            check(value["mapped_source"] == asdict(rsource))
            check(value["mapped_term"] == asdict(rterm))
            records.append({"case": label, "outcome": "Checked", "seconds": seconds,
                            "left": asdict(lsource), "right": asdict(rsource), "result": value})
            return value, seconds
        check(value is None)
        check(reason == expected)
        records.append({"case": label, "outcome": "Refused", "seconds": seconds,
                        "left": asdict(lsource), "right": asdict(rsource),
                        "candidate": asdict(candidate), "reason": reason})
        return None, seconds

    first, first_seconds = attempt("forward", left, right, left_term, right_term, correspondence)
    reused, reuse_seconds = attempt("reversed-reuse", left_reverse, right_reverse,
                                    left_term, right_term, correspondence)
    check(first["correspondence"] == reused["correspondence"])
    check(left.channels[0].thread[::-1] == left_reverse.channels[0].thread)
    check(right.channels[0].thread[::-1] == right_reverse.channels[0].thread)
    check(tuple(correspondence.thread_steps) == (("thread-a", "reuse-thread-a"),
                                                  ("thread-b", "reuse-thread-b")))
    check({x.source for x in left.ports}.isdisjoint(x.source for x in right.ports))
    check({x.occurrence for x in left.ports}.isdisjoint(x.occurrence for x in right.ports))

    def swap_targets(pairs):
        return (pairs[0][0], pairs[1][1]), (pairs[1][0], pairs[0][1])

    controls = (
        ("reversed-target-source", left, right_reverse, correspondence,
         "right source differs from complete renamed source"),
        ("swapped-step-targets", left, right,
         replace(correspondence, thread_steps=swap_targets(correspondence.thread_steps)),
         "thread_steps mapping target coverage/order differs"),
        ("duplicate-step-target", left, right,
         replace(correspondence, thread_steps=(("thread-a", "reuse-thread-a"),
                                               ("thread-b", "reuse-thread-a"))),
         "thread_steps mapping target coverage/order differs"),
        ("swapped-occurrence-targets", left, right,
         replace(correspondence, occurrences=swap_targets(correspondence.occurrences)),
         "occurrences mapping target coverage/order differs"),
        ("swapped-source-targets", left, right,
         replace(correspondence, sources=swap_targets(correspondence.sources)),
         "sources mapping target coverage/order differs"),
        ("swapped-residual-targets", left, right,
         replace(correspondence, residuals=swap_targets(correspondence.residuals)),
         "residuals mapping target coverage/order differs"),
        ("swapped-hole-targets", left, right,
         replace(correspondence, holes=swap_targets(correspondence.holes)),
         "holes mapping target coverage/order differs"),
        ("reversed-port-map-order", left, right,
         replace(correspondence, ports=correspondence.ports[::-1]),
         "ports mapping source coverage/order differs"),
        ("wrong-whole-target", left, right,
         replace(correspondence, whole=(("whole-6", "foreign-whole"),)),
         "whole mapping target coverage/order differs"),
        ("omitted-alternative-map", left, right,
         replace(correspondence, alternatives=correspondence.alternatives[:-1]),
         "alternatives mapping source coverage/order differs"),
    )
    check(tuple(row[0] for row in controls) == tuple(contract["negative_controls"]))
    negative_start = time.perf_counter()
    for label, lsource, rsource, candidate, reason in controls:
        attempt(label, lsource, rsource, left_term, right_term, candidate, reason)
    negative_seconds = time.perf_counter() - negative_start
    serialization_start = time.perf_counter()
    payload = encode(records)
    decoded = json.loads(payload)
    check(decoded[0]["result"]["correspondence"] == decoded[1]["result"]["correspondence"])
    check(decoded[0]["result"]["mapped_source"] == decoded[0]["right"])
    check(decoded[1]["result"]["mapped_source"] == decoded[1]["right"])
    check(calls == 12)
    check(len(payload) < contract["budgets"]["max_evidence_bytes_per_attempt"])
    serialization_seconds = time.perf_counter() - serialization_start
    (output / "cases.json").write_bytes(payload)
    summary = {"status": "Passed", "assertions": assertions, "receiving_calls": calls,
        "positive_pairs": 2, "refusal_controls": 10, "search_nodes": 0,
        "new_words": 0, "formation_seconds": formation_seconds,
        "first_receiving_seconds": first_seconds, "reuse_receiving_seconds": reuse_seconds,
        "negative_receiving_seconds": negative_seconds,
        "serialization_and_decode_seconds": serialization_seconds,
        "total_seconds_before_summary": time.perf_counter() - started,
        "peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "python": platform.python_version(), "base_commit": contract["base_commit"],
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "contract_sha256": hashlib.sha256((HERE / "contract.json").read_bytes()).hexdigest(),
        "missing_costs": ["primitive validation work units", "hard memory cap",
                          "separate authoring time", "human practical-use measurement"]}
    (output / "execution.json").write_bytes(encode(summary))
    print(json.dumps(summary))


def supervise(output):
    if output.exists():
        raise ValueError("refuse to overwrite previous attempt")
    output.mkdir(parents=True)
    started = time.perf_counter()
    command = [sys.executable, str(Path(__file__).resolve()), "--trial", str(output)]
    try:
        process = subprocess.run(command, capture_output=True, timeout=30)
        status = "Completed" if process.returncode == 0 else "Failed"
        stdout, stderr, code = process.stdout, process.stderr, process.returncode
    except subprocess.TimeoutExpired as error:
        status, stdout, stderr, code = "UnknownTimeout", error.stdout or b"", error.stderr or b"", None
    (output / "stdout.txt").write_bytes(stdout)
    (output / "stderr.txt").write_bytes(stderr)
    summary = {"status": status, "returncode": code, "timeout_seconds": 30,
        "wall_seconds": time.perf_counter() - started, "child_processes": 1,
        "child_peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        "supervisor_peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    size = sum(path.stat().st_size for path in output.iterdir() if path.is_file())
    summary["evidence_bytes_before_supervision"] = size
    summary["within_1mib"] = size + len(encode(summary)) < 1048576
    (output / "supervision.json").write_bytes(encode(summary))
    print(json.dumps(summary))
    if code != 0 or not summary["within_1mib"]:
        raise SystemExit(1)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--trial":
        trial(Path(sys.argv[2]))
    elif len(sys.argv) == 2:
        supervise(Path(sys.argv[1]))
    else:
        raise SystemExit("usage: python run.py NEW_OUTPUT_DIRECTORY")
