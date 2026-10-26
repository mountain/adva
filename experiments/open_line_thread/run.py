"""Two-step open-line syntax experiment, not native Adva authority.

Codex (OpenAI), original under Unknown v0.3, via Mingli Yuan account proxy.
"""

import hashlib
import json
import platform
from pathlib import Path
import resource
import subprocess
import sys
import time
from collections import Counter
from dataclasses import asdict, replace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      default=lambda item: item.value).encode() + b"\n"


def dependencies():
    sys.path.insert(0, str(ROOT))
    from experiments.open_line_residual import run as previous
    from test_bootstrap_zero_whole_cut_grammar import Crossing, Motion, ThreadStep
    return previous, Crossing, Motion, ThreadStep


def receive_two_step(term, expected, candidate, previous):
    """Separate local profile: exact source-bound record, no arbitrary-byte parser."""
    if (len(expected.cells), len(expected.ports), len(expected.channels),
            len(expected.open_ports), len(expected.residuals)) != (3, 6, 2, 2, 2):
        raise ValueError("outside two-step open-line domain")
    previous._validate_whole(expected)
    if tuple(len(channel.thread) for channel in expected.channels) != (2, 0):
        raise ValueError("two-step profile requires thread lengths (2,0)")
    if type(candidate) is not previous.OpenLineProposal or candidate != previous.propose(expected):
        raise ValueError("proposal differs from independently bound source")
    am = previous._coordinate_am(term, expected)
    if am.residuals != candidate.residuals:
        raise ValueError("AM and open-line residual ledgers differ")
    return {"status": "PairedResearchRecord", "profile": "open-line-two-step-v0",
            "am": asdict(am), "open_line": asdict(candidate),
            "open_bindings": tuple((x.port, x.hole, x.residual) for x in candidate.open_ports)}


def trial(output):
    started = time.perf_counter()
    contract = json.loads((HERE / "contract.json").read_bytes())
    for name, digest in contract["input_sha256"].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise ValueError("input fingerprint mismatch: " + name)
    previous, Crossing, Motion, ThreadStep = dependencies()
    construction_start = time.perf_counter()

    def with_word(form, prefix):
        word = (ThreadStep(prefix + "a", 1, Crossing.OVER),
                ThreadStep(prefix + "b", 2, Crossing.UNDER))
        return replace(form, channels=(replace(form.channels[0], thread=word), form.channels[1]))

    def reverse_word(form):
        return replace(form, channels=(replace(form.channels[0], thread=form.channels[0].thread[::-1]),
                                       form.channels[1]))

    first = with_word(previous._fixture(open_last=True), "thread-")
    fresh = with_word(previous.fresh_open(), "reuse-thread-")
    sources = {"canonical": first, "canonical-reversed": reverse_word(first),
               "fresh": fresh, "fresh-reversed": reverse_word(fresh)}
    proposals = {name: previous.propose(form) for name, form in sources.items()}
    terms = {name: previous.term_for(form) for name, form in sources.items()}
    construction_seconds = time.perf_counter() - construction_start
    assertions = 0
    calls = 0
    records = []
    outputs = {}
    durations = {}

    def check(condition):
        nonlocal assertions
        assertions += 1
        if not condition:
            raise AssertionError("check failed: " + str(assertions))

    def receive(term, form, candidate):
        nonlocal calls
        calls += 1
        check(calls <= contract["budgets"]["max_receiving_calls_per_attempt"])
        return receive_two_step(term, form, candidate, previous)

    for name, form in sources.items():
        before = time.perf_counter()
        result = receive(terms[name], form, proposals[name])
        durations[name] = time.perf_counter() - before
        check(result["open_line"]["channels"] == tuple(asdict(c) for c in form.channels))
        check(result["open_bindings"] == tuple((x.port, x.hole, x.residual) for x in form.open_ports))
        check(result["am"]["residuals"] == form.residuals)
        check(result["am"]["uses"] == ((form.ports[0].source, form.ports[0].occurrence, "A"),))
        outputs[name] = result
        records.append({"case": name, "expected_source": asdict(form), "term": asdict(terms[name]),
                        "candidate": asdict(proposals[name]), "output": result})

    collisions = []
    for name in ("canonical", "fresh"):
        other = name + "-reversed"
        a, b = sources[name], sources[other]
        check(a != b)
        check(proposals[name] != proposals[other])
        check(outputs[name]["am"] == outputs[other]["am"])
        check(Counter(a.channels[0].thread) == Counter(b.channels[0].thread))
        check(a.channels[0].source_port == b.channels[0].source_port)
        check(a.channels[0].target_port == b.channels[0].target_port)
        check(a.channels[0].motion == b.channels[0].motion)
        collisions.append({"a": name, "b": other, "equal_am": True,
                           "equal_step_multiset": True, "unequal_ordered_proposals": True})
    check(first.name != fresh.name)
    check({x.occurrence for x in first.ports}.isdisjoint(x.occurrence for x in fresh.ports))
    check({x.name for x in first.channels[0].thread}.isdisjoint(x.name for x in fresh.channels[0].thread))
    check(first.residuals != fresh.residuals)

    c = proposals["canonical"]
    channel = c.channels[0]
    step_a, step_b = channel.thread

    def change_channel(**changes):
        return replace(c, channels=(replace(channel, **changes), c.channels[1]))

    mutations = {
        "reverse-word": proposals["canonical-reversed"],
        "drop-step": change_channel(thread=(step_a,)),
        "rename-step": change_channel(thread=(replace(step_a, name="foreign-step"), step_b)),
        "change-gap": change_channel(thread=(replace(step_a, gap=3), step_b)),
        "change-crossing": change_channel(thread=(replace(step_a, crossing=Crossing.UNDER), step_b)),
        "reverse-motion": change_channel(motion=Motion.REVERSE if channel.motion == Motion.FORWARD else Motion.FORWARD),
        "rename-residual": replace(c, residuals=("foreign-residual", c.residuals[1])),
        "foreign-source": proposals["fresh"],
    }
    check(list(mutations) == contract["candidate_refusals"])

    def refusal(label, form, candidate, reason, term):
        try:
            receive(term, form, candidate)
        except ValueError as error:
            actual = str(error)
        else:
            actual = "unexpected acceptance"
        check(actual == reason)
        records.append({"case": label, "expected_source": asdict(form), "term": asdict(term),
                        "candidate": asdict(candidate), "outcome": "Refused", "reason": actual})

    negative_start = time.perf_counter()
    for name, candidate in mutations.items():
        refusal(name, first, candidate, "proposal differs from independently bound source", terms["canonical"])
    bad_gap = replace(first, channels=(replace(channel, thread=(replace(step_a, gap=True), step_b)), first.channels[1]))
    duplicate = replace(first, channels=(replace(channel, thread=(step_a, replace(step_b, name=step_a.name))), first.channels[1]))
    empty = replace(first, channels=(replace(channel, thread=()), first.channels[1]))
    for name, form, reason in (
        ("boolean-gap", bad_gap, "thread gap must select adjacent ports of the six-port carrier"),
        ("duplicate-step-name", duplicate, "thread step names must be distinct within the raw word"),
        ("empty-word", empty, "two-step profile requires thread lengths (2,0)"),
    ):
        refusal(name, form, previous.propose(form), reason, terms["canonical"])
    negative_seconds = time.perf_counter() - negative_start
    old_refusals = []
    for name in ("canonical", "fresh"):
        try:
            previous.receive(terms[name], sources[name], proposals[name])
        except ValueError as error:
            reason = str(error)
        else:
            reason = "unexpected acceptance"
        check(reason == "this trial admits only empty thread words")
        old_refusals.append({"case": name, "reason": reason})

    serialization_start = time.perf_counter()
    payload = encode({"records": records, "collisions": collisions, "old_profile_refusals": old_refusals})
    decoded = json.loads(payload)
    for row in decoded["records"][:4]:
        check(row["output"]["open_line"]["channels"][0]["thread"] ==
              row["expected_source"]["channels"][0]["thread"])
    serialization_seconds = time.perf_counter() - serialization_start
    check(calls == 15)
    check(len(payload) < contract["budgets"]["max_evidence_bytes_per_attempt"])
    (output / "cases.json").write_bytes(payload)
    summary = {"status": "Passed", "assertions": assertions, "receiving_calls": calls,
        "positive_cases": 4, "candidate_refusals": 8, "source_refusals": 3,
        "old_profile_refusals": 2, "collision_pairs": 2, "search_nodes": 0,
        "new_words": 0, "construction_seconds": construction_seconds,
        "receiving_seconds": durations, "negative_receiving_seconds": negative_seconds,
        "serialization_and_decode_seconds": serialization_seconds,
        "total_seconds_before_summary": time.perf_counter() - started,
        "peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "python": platform.python_version(), "base_commit": contract["base_commit"],
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "contract_sha256": hashlib.sha256((HERE / "contract.json").read_bytes()).hexdigest(),
        "missing_costs": ["primitive checker operations", "separate implementation-authoring time",
                          "hard memory cap", "human task utility"]}
    (output / "execution.json").write_bytes(encode(summary))
    print(json.dumps(summary))


def supervise(output):
    if output.exists():
        raise ValueError("refuse to overwrite prior attempt")
    output.mkdir(parents=True)
    started = time.perf_counter()
    command = [sys.executable, str(Path(__file__).resolve()), "--trial", str(output)]
    try:
        result = subprocess.run(command, capture_output=True, timeout=30)
        status = "Completed" if result.returncode == 0 else "Failed"
        stdout, stderr, code = result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired as error:
        status, stdout, stderr, code = "UnknownTimeout", error.stdout or b"", error.stderr or b"", None
    (output / "stdout.txt").write_bytes(stdout)
    (output / "stderr.txt").write_bytes(stderr)
    summary = {"status": status, "returncode": code, "timeout_seconds": 30,
               "wall_seconds": time.perf_counter() - started, "child_processes": 1,
               "child_peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
               "supervisor_peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    total_bytes = sum(p.stat().st_size for p in output.iterdir() if p.is_file())
    summary["evidence_bytes_before_supervision"] = total_bytes
    summary["within_1mib"] = total_bytes + len(encode(summary)) < 1048576
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
