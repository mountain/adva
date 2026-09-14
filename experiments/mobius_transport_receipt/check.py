"""Bounded external receipt calibration; no native Adva authority."""
import argparse
import copy
import itertools
import json
from pathlib import Path
import resource
import time

START = time.perf_counter()
UNITS = 0
CAP = 100000
LETTERS = "abAB"
INF = "inf"


class Refusal(Exception):
    pass


def tick():
    global UNITS
    UNITS += 1
    if UNITS > CAP or time.perf_counter() - START > 15:
        raise Refusal("UnknownResource")


def require(ok, tag="InvalidSchema"):
    tick()
    if not ok:
        raise Refusal(tag)


def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), allow_nan=False)


def pairs(items):
    out = {}
    for k, v in items:
        if k in out:
            raise Refusal("InvalidSchema")
        out[k] = v
    return out


def parse(raw):
    require(type(raw) is str and len(raw.encode()) <= 65536)
    try:
        value = json.loads(raw, object_pairs_hook=pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(Refusal("InvalidSchema")))
    except (ValueError, RecursionError):
        raise Refusal("InvalidSchema") from None
    def visit(v, depth=0):
        require(depth <= 12)
        require(type(v) in (dict, list, str, int))
        if type(v) is int:
            require(abs(v) <= 1000)
        if type(v) is dict:
            for key, item in v.items():
                require(len(key) <= 100)
                visit(item, depth + 1)
        elif type(v) is list:
            for item in v:
                visit(item, depth + 1)
        elif type(v) is str:
            require(len(v) <= 200)
    visit(value)
    return value


def keys(d, names):
    require(type(d) is dict and set(d) == set(names.split()))


def matrix(m, p):
    require(type(m) is list and len(m) == 4)
    require(all(type(v) is int and 0 <= v < p for v in m))
    require((m[0]*m[3]-m[1]*m[2]) % p != 0, "InvalidInverse")


def mul(a, b, p):
    tick()
    return [(a[0]*b[0]+a[1]*b[2]) % p,
            (a[0]*b[1]+a[1]*b[3]) % p,
            (a[2]*b[0]+a[3]*b[2]) % p,
            (a[2]*b[1]+a[3]*b[3]) % p]


def inv(m, p):
    # Projective inverse: adjugate, no unjustified scalar division.
    matrix(m, p)
    return [m[3], -m[1] % p, -m[2] % p, m[0]]


def act(m, x, p):
    tick()
    n, d = (m[0], m[2]) if x == INF else ((m[0]*x+m[1]) % p, (m[2]*x+m[3]) % p)
    return n * pow(d, -1, p) % p if d else INF


def context(p):
    return {"schema": "adva.external.mobius-context.v0", "p": p,
            "source_scope": "source-F"+str(p), "target_scope": "target-F"+str(p),
            "composition": "left-after-right", "H": [1, 2, 1, 1],
            "generators": [[1, 1, 0, 1], [1, 0, 1, 1]],
            "probes": [0, 1, INF], "predicate": [0, 1]}


def source(c):
    a, b = c["generators"]
    return [a, b, inv(a, c["p"]), inv(b, c["p"])]


def produce(c):
    p, h = c["p"], c["H"]
    gs = source(c)
    ts = [mul(mul(h, g, p), inv(h, p), p) for g in gs]
    return {"schema": "adva.external.mobius-transport-receipt.v0", "context": copy.deepcopy(c),
            "target_matrices": ts,
            "target_probes": [act(h, x, p) for x in c["probes"]],
            "target_predicate": [act(h, x, p) for x in c["predicate"]],
            "observations": [[label, x, act(t, act(h, x, p), p)]
                             for label, t in zip(LETTERS, ts)
                             for x in list(range(p))+[INF]]}


def verify(raw, expected_raw, fuel=None):
    global CAP
    old_cap = CAP
    if fuel is not None:
        CAP = min(CAP, UNITS + fuel)
    try:
        r, c = parse(raw), parse(expected_raw)
        keys(c, "schema p source_scope target_scope composition H generators probes predicate")
        require(c["schema"] == "adva.external.mobius-context.v0")
        require(c["p"] in (5, 7))
        p = c["p"]
        xs = list(range(p)) + [INF]
        require(c["composition"] == "left-after-right", "InvalidConvention")
        require(type(c["source_scope"]) is str and type(c["target_scope"]) is str)
        require(c["source_scope"] != c["target_scope"])
        matrix(c["H"], p)
        require(type(c["generators"]) is list and len(c["generators"]) == 2)
        for m in c["generators"]:
            matrix(m, p)
        for name in ("probes", "predicate"):
            require(type(c[name]) is list and all(x in xs for x in c[name]))
            require(len(c[name]) == len(set(c[name])))
        keys(r, "schema context target_matrices target_probes target_predicate observations")
        require(r["schema"] == "adva.external.mobius-transport-receipt.v0")
        require(canon(r["context"]) == canon(c), "InvalidContextBinding")
        require(type(r["target_matrices"]) is list and len(r["target_matrices"]) == 4)
        gs, h = source(c), c["H"]
        for t in r["target_matrices"]:
            matrix(t, p)
        # Verifier checks the pointwise square, not producer's conjugacy product.
        for g, t in zip(gs, r["target_matrices"]):
            for x in xs:
                require(act(t, act(h, x, p), p) == act(h, act(g, x, p), p), "InvalidTransport")
        require(r["target_probes"] == [act(h, x, p) for x in c["probes"]], "InvalidObserver")
        require(type(r["target_predicate"]) is list and all(x in xs for x in r["target_predicate"]))
        require(len(r["target_predicate"]) == len(set(r["target_predicate"])))
        for x in xs:
            require((act(h, x, p) in r["target_predicate"]) == (x in c["predicate"]), "InvalidPredicate")
        require(type(r["observations"]) is list)
        seen = set()
        for row in r["observations"]:
            require(type(row) is list and len(row) == 3)
            label, x, y = row
            require(type(label) is str and label in list(LETTERS) and x in xs and y in xs)
            require((label, x) not in seen, "InvalidDuplicateObservation")
            seen.add((label, x))
            require(y == act(h, act(gs[LETTERS.index(label)], x, p), p), "InvalidEvidence")
        missing = [[l, x] for l in LETTERS for x in xs if (l, x) not in seen]
        return {"status": "UnknownCoverage" if missing else "AcceptedTransportForDeclaredAction",
                "missing": missing, "native_admission": False}
    except Refusal as error:
        return {"status": str(error), "native_admission": False}
    finally:
        CAP = old_cap


def word_action(ms, w, x, p):
    for letter in reversed(w):
        x = act(ms[LETTERS.index(letter)], x, p)
    return x


def run():
    construction = checking = reuse = serialization = 0.0
    fixtures, tests, word_results = [], [], []
    for p in (5, 7):
        t0 = time.perf_counter()
        c = context(p)
        r = produce(c)
        construction += time.perf_counter() - t0
        fixtures.append({"expected_context": c, "receipt": r})
        cases = [("positive", copy.deepcopy(r), "AcceptedTransportForDeclaredAction")]
        def case(name, mutate, expected):
            v = copy.deepcopy(r)
            mutate(v)
            cases.append((name, v, expected))
        case("one-sided", lambda v: v.update(target_matrices=[mul(c["H"], g, p) for g in source(c)]), "InvalidTransport")
        case("unchanged-probes", lambda v: v.update(target_probes=c["probes"]), "InvalidObserver")
        case("unchanged-predicate", lambda v: v.update(target_predicate=c["predicate"]), "InvalidPredicate")
        case("wrong-scope", lambda v: v["context"].update(source_scope="other"), "InvalidContextBinding")
        case("wrong-order", lambda v: v["context"].update(composition="right-after-left"), "InvalidContextBinding")
        case("missing-infinity", lambda v: v.update(observations=[row for row in v["observations"] if row[1] != INF]), "UnknownCoverage")
        case("missing-pole", lambda v: v.update(observations=[row for row in v["observations"] if row[1] != p-1]), "UnknownCoverage")
        case("duplicate-observation", lambda v: v["observations"].append(v["observations"][0]), "InvalidDuplicateObservation")
        case("wrong-value", lambda v: v["observations"][0].__setitem__(2, INF), "InvalidEvidence")
        case("singular-target", lambda v: v["target_matrices"].__setitem__(0, [0, 0, 0, 0]), "InvalidInverse")
        case("boolean-coordinate", lambda v: v["observations"][0].__setitem__(1, True), "InvalidSchema")
        case("float-coordinate", lambda v: v["observations"][0].__setitem__(1, 0.0), "InvalidSchema")
        case("claimed-status", lambda v: v.update(status="Verified"), "InvalidSchema")
        t0 = time.perf_counter()
        for name, candidate, want in cases:
            result = verify(canon(candidate), canon(c))
            assert result["status"] == want, (p, name, result, want)
            tests.append({"p": p, "name": name, "result": result, "input": candidate})
        for name, raw, fuel, want in [
                ("duplicate-json-key", '{"schema":"x","schema":"y"}', None, "InvalidSchema"),
                ("oversize", " "*65537, None, "InvalidSchema"),
                ("zero-fuel", canon(r), 0, "UnknownResource")]:
            result = verify(raw, canon(c), fuel)
            assert result["status"] == want, (p, name, result)
            tests.append({"p": p, "name": name, "result": result})
        checking += time.perf_counter() - t0
        t0 = time.perf_counter()
        gs, ts, h = source(c), r["target_matrices"], c["H"]
        count = 0
        for length in range(5):
            for word in itertools.product(LETTERS, repeat=length):
                for x in list(range(p))+[INF]:
                    assert word_action(ts, word, act(h, x, p), p) == act(h, word_action(gs, word, x, p), p)
                    count += 1
        # Literal histories are not normalized away merely because values agree.
        histories = [{"word": w, "outputs": [word_action(ts, w, x, p) for x in list(range(p))+[INF]]} for w in ("", "aA", "Aa")]
        assert histories[0]["outputs"] == histories[1]["outputs"] == histories[2]["outputs"]
        assert len({item["word"] for item in histories}) == 3
        word_results.append({"p": p, "words": 341, "pointwise_checks": count, "histories": histories})
        reuse += time.perf_counter() - t0
    t0 = time.perf_counter()
    result = {"status": "Passed", "fixtures": fixtures, "controls": tests, "word_reuse": word_results,
              "residual": ["External fixed-prime profile only", "No native identities or authorization", "Receiver context suitability and author authentication are not established", "No speedup, learning, universality, or RH claim"]}
    assert json.loads(canon(result)) == result
    serialization += time.perf_counter() - t0
    result["cost"] = {"work_units": UNITS, "construction_ms": 1000*construction,
                      "receipt_checking_ms": 1000*checking, "word_reuse_ms": 1000*reuse,
                      "serialization_replay_ms": 1000*serialization,
                      "elapsed_before_final_write_ms": 1000*(time.perf_counter()-START),
                      "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                      "search_candidates": 0, "correction_replays": 0}
    return result


if __name__ == "__main__":
    resource.setrlimit(resource.RLIMIT_CPU, (15, 15))
    resource.setrlimit(resource.RLIMIT_AS, (256*1024**2, 256*1024**2))
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--receipt")
    parser.add_argument("--expected-context")
    args = parser.parse_args()
    if bool(args.receipt) != bool(args.expected_context):
        parser.error("receipt mode requires an independent expected-context file")
    if args.receipt:
        def limited(path):
            with open(path, "rb") as f:
                return f.read(65537).decode("utf-8")
        result = verify(limited(args.receipt), limited(args.expected_context))
    else:
        result = run()
    output = canon(result) + "\n"
    if len(output.encode()) > 1048576:
        raise SystemExit("UnknownResource: output limit")
    Path(args.output).write_text(output)
    print(canon({k: v for k, v in result.items() if k in ("status", "cost")}))
