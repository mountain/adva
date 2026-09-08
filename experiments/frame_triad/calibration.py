#!/usr/bin/env python3
"""One bounded external frame/triad calibration; no native Adva identities."""
import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
import resource
import signal
import time

UNITS = 0
DEADLINE = 0.0
LIMIT = 0


def charge(n=1):
    global UNITS
    UNITS += n
    if UNITS > LIMIT or time.monotonic() > DEADLINE:
        raise TimeoutError("logical or wall limit")


def same(a, b):
    charge()
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def partition(n, worlds):
    if not worlds:
        return {"status": "InconsistentFrame", "positive": [], "negative": [], "open": []}
    both_and, either_or = (1 << n) - 1, 0
    for w in worlds:
        both_and &= w
        either_or |= w
    return {"status": "ConsistentFrame",
            "positive": [q for q in range(n) if (both_and >> q) & 1],
            "negative": [q for q in range(n) if not ((either_or >> q) & 1)],
            "open": [q for q in range(n) if ((either_or ^ both_and) >> q) & 1]}


def tuple_oracle(n, worlds):
    """Complete tuple table; does not call partition or use its bit reductions."""
    charge(1 + n * len(worlds))
    rows = [tuple((w // (2 ** q)) % 2 for q in range(n)) for w in worlds]
    out = {"status": "ConsistentFrame" if rows else "InconsistentFrame",
           "positive": [], "negative": [], "open": []}
    if rows:
        for q in range(n):
            ones = sum(row[q] for row in rows)
            out["negative" if ones == 0 else "positive" if ones == len(rows) else "open"].append(q)
        assert sorted(out["positive"] + out["negative"] + out["open"]) == list(range(n))
    return out


def check_partition(n, worlds, claim):
    same(claim, tuple_oracle(n, worlds))


def check_family_row(row):
    n, mask = row["n"], row["family_mask"]
    expected = [w for w in range(2 ** n) if (mask // (2 ** w)) % 2 == 1]
    same(row["worlds"], expected)
    check_partition(n, expected, row["partition"])


def permute_world(w, permutation):
    return sum(((w >> q) & 1) << permutation[q] for q in range(len(permutation)))


def continuation(rounds, grant):
    n, worlds, history, archive = 0, [0], [], []
    active = None
    cursor = None
    for index in range(rounds):
        for action in ("extend", "select", "check", "drop"):
            if len(history) >= grant:
                cursor = {"round": index, "action": action}
                break
            before = worlds[:]
            event = {"round": index, "action": action}
            if action == "extend":
                worlds = sorted(worlds + [w | (1 << n) for w in worlds])
                n += 1
                event.update(before=before, after=worlds[:])
            elif action == "select":
                active = {"q": index, "checked": False, "answer": None}
                event["q"] = index
            elif action == "check":
                answer = index & 1  # explicitly supplied alternating fixture
                active.update(checked=True, answer=answer)
                event.update(q=index, answer=answer, certificate="alternating-fixture-v0")
            else:
                assert active["checked"]
                answer = active["answer"]
                worlds = [w for w in worlds if ((w >> index) & 1) == answer]
                rejected = [w for w in before if w not in worlds]
                archive.append({"q": index, "answer": answer, "rejected": rejected})
                event.update(before=before, after=worlds[:], rejected=rejected)
                active = None
            history.append(event)
            charge()
        if cursor is not None:
            break
    return {"input": {"rounds": rounds, "grant": grant, "scope": "external:frame-triad:v0"},
            "status": "Unknown:Fuel" if cursor is not None else "CompletedFinitePrefix",
            "n": n, "worlds": worlds, "partition": partition(n, worlds),
            "history": history, "archive": archive, "active": active, "cursor": cursor,
            "spent": len(history), "remaining": grant - len(history)}


def check_continuation(receipt, rounds, grant):
    """Replay from frozen inputs using tuples and arithmetic, not the producer."""
    same(receipt["input"], {"rounds": rounds, "grant": grant, "scope": "external:frame-triad:v0"})
    tuples, history, archive, active = [()], [], [], None
    steps = min(4 * rounds, grant)
    actions = ("extend", "select", "check", "drop")
    for k in range(steps):
        charge()
        i, stage = divmod(k, 4)
        old = sorted(sum(v * 2 ** j for j, v in enumerate(t)) for t in tuples)
        event = {"round": i, "action": actions[stage]}
        if stage == 0:
            tuples = [t + (b,) for t in tuples for b in (0, 1)]
            new = sorted(sum(v * 2 ** j for j, v in enumerate(t)) for t in tuples)
            event.update(before=old, after=new)
        elif stage == 1:
            active = {"q": i, "checked": False, "answer": None}
            event["q"] = i
        elif stage == 2:
            answer = i - 2 * (i // 2)
            active.update(checked=True, answer=answer)
            event.update(q=i, answer=answer, certificate="alternating-fixture-v0")
        else:
            assert active and active["checked"]
            answer = active["answer"]
            kept = [t for t in tuples if t[i] == answer]
            removed = sorted(sum(v * 2 ** j for j, v in enumerate(t)) for t in tuples if t[i] != answer)
            tuples = kept
            new = sorted(sum(v * 2 ** j for j, v in enumerate(t)) for t in tuples)
            archive.append({"q": i, "answer": answer, "rejected": removed})
            event.update(before=old, after=new, rejected=removed)
            active = None
        history.append(event)
    n = len(tuples[0])
    worlds = sorted(sum(v * 2 ** j for j, v in enumerate(t)) for t in tuples)
    expected = {"input": receipt["input"],
                "status": "CompletedFinitePrefix" if steps == 4 * rounds else "Unknown:Fuel",
                "n": n, "worlds": worlds, "partition": tuple_oracle(n, worlds),
                "history": history, "archive": archive, "active": active,
                "cursor": None if steps == 4 * rounds else {"round": steps // 4, "action": actions[steps % 4]},
                "spent": steps, "remaining": grant - steps}
    same(receipt, expected)


def check_extension(n, old, new):
    charge(len(new) + len(old))
    assert old and new
    assert len(set(new)) == len(new)
    assert all(type(w) is int and 0 <= w < 2 ** (n + 1) for w in new)
    assert sorted(set(w % (2 ** n) for w in new)) == old
    for w in old:
        assert sorted(v // (2 ** n) for v in new if v % (2 ** n) == w) == [0, 1]


def reject(name, fn, output):
    try:
        fn()
    except AssertionError:
        output.append({"name": name, "status": "Rejected"})
    else:
        raise AssertionError("negative control accepted: " + name)


def calibrate(contract, report):
    rows, edges, extensions = [], [], []
    report.update(partitions=rows, updates=edges, extensions=extensions)
    covariance = selectors = 0
    for n in contract["families"]["question_sizes"]:
        for mask in range(1 << (1 << n)):
            charge()
            worlds = [w for w in range(1 << n) if (mask >> w) & 1]
            part = partition(n, worlds)
            check_partition(n, worlds, part)
            rows.append({"n": n, "family_mask": mask, "worlds": worlds, "partition": part})
            check_family_row(rows[-1])
            for pi in itertools.permutations(range(n)):
                transformed = sorted(permute_world(w, pi) for w in worlds)
                # Independent incidence equation for each transported coordinate.
                for w in worlds:
                    for q in range(n):
                        charge()
                        assert (permute_world(w, pi) // (2 ** pi[q])) % 2 == (w // (2 ** q)) % 2
                expected = {"status": part["status"], **{k: sorted(pi[q] for q in part[k]) for k in ("positive", "negative", "open")}}
                same(tuple_oracle(n, transformed), expected)
                covariance += 1
                if part["open"]:
                    # A frame order is supplied and transported, never regenerated from labels.
                    order = list(range(n))
                    chosen = next(q for q in order if q in part["open"])
                    other = next(q for q in [pi[x] for x in order] if q in expected["open"])
                    assert other == pi[chosen]
                    selectors += 1
            if not worlds:
                continue
            new = sorted(worlds + [w | (1 << n) for w in worlds])
            check_extension(n, worlds, new)
            new_part = tuple_oracle(n + 1, new)
            same(new_part["positive"], part["positive"])
            same(new_part["negative"], part["negative"])
            same(new_part["open"], part["open"] + [n])
            extensions.append({"n": n, "family_mask": mask, "extended_worlds": new})
            for q in range(n):
                for answer in (0, 1):
                    charge()
                    kept = [w for w in worlds if ((w >> q) & 1) == answer]
                    dropped = [w for w in worlds if w not in kept]
                    checked_kept = [w for w in worlds if (w // 2 ** q) % 2 == answer]
                    same(kept, checked_kept)
                    assert sorted(kept + dropped) == worlds and not set(kept) & set(dropped)
                    if kept:
                        after = tuple_oracle(n, kept)
                        assert set(part["positive"]) <= set(after["positive"])
                        assert set(part["negative"]) <= set(after["negative"])
                        assert set(after["open"]) <= set(part["open"])
                        if q in part["open"]:
                            assert len(after["open"]) < len(part["open"])
                            assert len(kept) < len(worlds)
                    edges.append({"n": n, "family_mask": mask, "q": q, "answer": answer,
                                  "kept": kept, "rejected_models": dropped,
                                  "status": "Admissible" if kept else "Rejected:InconsistentAnswer"})
    # Independent full coverage count and literal case-key audit.
    expected_rows = {(n, m) for n in (0, 1, 2, 3) for m in range(2 ** (2 ** n))}
    assert len(rows) == len(expected_rows) and {(r["n"], r["family_mask"]) for r in rows} == expected_rows
    expected_edges = {(n, m, q, b) for n in (0, 1, 2, 3) for m in range(1, 2 ** (2 ** n)) for q in range(n) for b in (0, 1)}
    assert len(edges) == len(expected_edges) and {(e["n"], e["family_mask"], e["q"], e["answer"]) for e in edges} == expected_edges
    report.update(partitions=rows, updates=edges, extensions=extensions)
    traces = []
    for rounds, grant in contract["families"]["traces"]:
        receipt = continuation(rounds, grant)
        check_continuation(json.loads(json.dumps(receipt)), rounds, grant)
        traces.append(receipt)
    report["traces"] = traces
    controls = []
    bad = partition(3, list(range(8))); bad["open"].pop()
    reject("omitted_open_question", lambda: check_partition(3, list(range(8)), bad), controls)
    false = {"status": "ConsistentFrame", "positive": [0], "negative": [], "open": [1, 2]}
    reject("false_positive", lambda: check_partition(3, list(range(8)), false), controls)
    reject("empty_family_as_universe", lambda: check_partition(3, [], partition(3, list(range(8)))), controls)
    missing = {"n": 3, "family_mask": 255, "worlds": [0], "partition": partition(3, [0])}
    reject("missing_model_coverage", lambda: check_family_row(missing), controls)
    wrong_transport = partition(3, [1])
    reject("wrong_coordinate_transport", lambda: check_partition(3, [2], wrong_transport), controls)
    mutations = {
        "forged_frame_scope": lambda r: r["input"].update(scope="another-frame"),
        "fuel_reset": lambda r: r.update(remaining=16),
        "erased_history": lambda r: r["history"].pop(0),
        "unchecked_drop": lambda r: r["history"].pop(2),
        "forged_answer": lambda r: r["history"][2].update(answer=1),
    }
    for name, mutate in mutations.items():
        r = copy.deepcopy(traces[1]); mutate(r)
        reject(name, lambda r=r: check_continuation(r, 4, 16), controls)
    r = copy.deepcopy(traces[2]); r["status"] = "CompletedFinitePrefix"
    reject("premature_return", lambda: check_continuation(r, 4, 3), controls)
    reject("nonconservative_extension", lambda: check_extension(1, [0, 1], [0, 2]), controls)
    same([c["name"] for c in controls], contract["negative_controls"])
    # Fully symmetric C3 input is fixed, but rotation has no fixed selectable point.
    selector_failures = [{"chosen": q, "rotated": (q + 1) % 3} for q in range(3)]
    assert all(x["chosen"] != x["rotated"] for x in selector_failures)
    report.update(negative_controls=controls, fixed_selector_failures=selector_failures,
                  counts={"model_families": len(rows), "consistent_families": len(extensions),
                          "update_cases": len(edges), "admissible_updates": sum(e["status"] == "Admissible" for e in edges),
                          "coordinate_covariance_cases": covariance, "framed_selection_cases": selectors,
                          "conservative_extensions": len(extensions), "continuation_traces": len(traces),
                          "negative_controls": len(controls)})


def main():
    global DEADLINE, LIMIT
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="evidence.json")
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    raw_contract = (here / "contract.json").read_bytes()
    contract = json.loads(raw_contract)
    limits = contract["limits"]
    output = Path(args.output)
    if output.exists():
        raise FileExistsError("choose a fresh output path")
    start = time.monotonic()
    DEADLINE, LIMIT = start + limits["wall_seconds"], limits["logical_units"]
    resource.setrlimit(resource.RLIMIT_CPU, (limits["cpu_seconds"], limits["cpu_seconds"]))
    resource.setrlimit(resource.RLIMIT_AS, (limits["address_space_mib"] * 2 ** 20,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (limits["file_bytes"],) * 2)
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("wall alarm")))
    signal.alarm(limits["wall_seconds"])
    report = {"schema": "external.frame-triad.evidence.v0", "status": "Running",
              "contract_sha256": hashlib.sha256(raw_contract).hexdigest(),
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "native_three_machine_identification": "Open"}
    exit_code = 0
    try:
        calibrate(contract, report)
        report["status"] = "PassedFiniteCalibration"
        encoded = json.dumps(report, sort_keys=True, separators=(",", ":"))
        charge(1 + len(encoded) // 1024)
        parsed = json.loads(encoded)
        same(parsed, report)
        report["serialized_replay"] = "Passed"
    except TimeoutError as exc:
        report.update(status="Unknown:Resource", failure=str(exc)); exit_code = 2
    except Exception as exc:
        report.update(status="ImplementationFailure", failure=type(exc).__name__ + ": " + str(exc)); exit_code = 1
    report["costs"] = {"logical_units": UNITS, "elapsed_before_checkpoint_seconds": time.monotonic() - start,
                       "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                       "checkpoint": "One no-clobber write, at most 2 MiB, OS limits still active"}
    data = (json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if len(data) > limits["file_bytes"]:
        raise RuntimeError("checkpoint exceeds declared size")
    with output.open("xb") as stream:
        stream.write(data)
    print(json.dumps({"status": report["status"], "counts": report.get("counts"),
                      "costs": report["costs"], "bytes": len(data), "failure": report.get("failure")}))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
