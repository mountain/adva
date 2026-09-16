#!/usr/bin/env python3
"""Original finite external calibration; no native Adva identities or authority.

ChatGPT (OpenAI), through Mingli Yuan's account proxy; Unknown v0.3.
Account use is not endorsement, review, or a correctness guarantee.
"""
import argparse
import itertools
import json
from pathlib import Path
import resource
import signal
import sys
import time
from fractions import Fraction as F

START = time.perf_counter()
COUNTS = {"work_units": 0, "assertions": 0}


def tick():
    if COUNTS["work_units"] >= 10000 or time.perf_counter() - START > 30:
        raise RuntimeError("UnknownBudget")
    COUNTS["work_units"] += 1


def require(ok, name):
    tick()
    COUNTS["assertions"] += 1
    if not ok:
        raise AssertionError(name)


def validate(table, reference, probability):
    n = len(table)
    tick()
    if not 1 <= n <= 6 or any(len(row) != n for row in table):
        raise ValueError("IncompleteGroupTable")
    if len(reference) != n or len(probability) != n:
        raise ValueError("MissingAtom")
    if any(x <= 0 for x in reference):
        raise ValueError("NonpositiveReference")
    if any(x < 0 for x in probability):
        raise ValueError("NegativeMass")
    if sum(reference) != 1 or sum(probability) != 1:
        raise ValueError("NonunitMass")
    require(all(type(x) is int and 0 <= x < n for row in table for x in row), "closure")
    identities = [e for e in range(n) if all(table[e][x] == table[x][e] == x for x in range(n))]
    require(len(identities) == 1, "unique identity")
    e = identities[0]
    inverse = []
    for x in range(n):
        choices = [y for y in range(n) if table[x][y] == table[y][x] == e]
        require(len(choices) == 1, "unique inverse")
        inverse.append(choices[0])
    for x, y, z in itertools.product(range(n), repeat=3):
        require(table[table[x][y]][z] == table[x][table[y][z]], "associativity")
    return e, inverse


def moments(reference, probability):
    density = []
    for mass, weight in zip(probability, reference):
        tick()
        density.append(mass / weight)
    mean = sum(w * d for w, d in zip(reference, density))
    energy = sum(w * d * d for w, d in zip(reference, density))
    variance = sum(w * (d - mean) ** 2 for w, d in zip(reference, density))
    require(mean == 1, "density normalization")
    require(energy == 1 + variance and energy >= 1, "quadratic density identity")
    require((energy == 1) == all(d == 1 for d in density), "positive-reference equality criterion")
    return {"density": density, "mean": mean, "energy": energy, "variance": variance}


def observe(table, reference, probability, labels, full):
    atoms = sorted(set(labels))
    weights = [sum(reference[x] for x, label in enumerate(labels) if label == atom) for atom in atoms]
    masses = [sum(probability[x] for x, label in enumerate(labels) if label == atom) for atom in atoms]
    require(sum(weights) == sum(masses) == 1, "pushforward mass")
    observed = moments(weights, masses)
    residual = sum(reference[x] * (full["density"][x] - observed["density"][atoms.index(labels[x])]) ** 2 for x in range(len(table)))
    require(full["energy"] - observed["energy"] == residual >= 0, "coarsening energy loss identity")
    product, representatives, witness = {}, {}, None
    for x, y in itertools.product(range(len(table)), repeat=2):
        tick()
        key, out = (labels[x], labels[y]), labels[table[x][y]]
        if key in product and product[key] != out and witness is None:
            witness = {"first_pair": representatives[key], "second_pair": [x, y], "outputs": [product[key], out]}
        product.setdefault(key, out)
        representatives.setdefault(key, [x, y])
    return {"map": labels, "atoms": atoms, "reference": weights, "probability": masses,
            **observed, "lost_energy": residual, "multiplicative": witness is None,
            "noncongruence_witness": witness,
            "quotient_table": [[product[(x, y)] for y in atoms] for x in atoms] if witness is None else None}


def joints(table, reference, e, inverse):
    n, outputs = len(table), {}
    for name in ("independent", "inverse_correlated"):
        joint, product = [], [F(0)] * n
        for x in range(n):
            row = []
            for y in range(n):
                tick()
                mass = reference[x] * reference[y] if name == "independent" else reference[x] if y == inverse[x] else F(0)
                row.append(mass)
                product[table[x][y]] += mass
            joint.append(row)
        left = [sum(row) for row in joint]
        right = [sum(joint[x][y] for x in range(n)) for y in range(n)]
        require(left == right == reference, "same uniform marginals")
        require(sum(product) == 1, "product mass")
        expected = reference if name == "independent" else [F(int(x == e)) for x in range(n)]
        require(product == expected, "joint-dependent product")
        independent = all(joint[x][y] == left[x] * right[y] for x, y in itertools.product(range(n), repeat=2))
        require(independent == (name == "independent"), "independence explicit")
        outputs[name] = {"joint": joint, "left": left, "right": right, "product": product, "independent": independent}
    return outputs


def instance(name):
    carrier = list(itertools.permutations(range(3))) if name == "S3" else list(range(4))
    n, table = len(carrier), []
    for x in carrier:
        row = []
        for y in carrier:
            tick()
            row.append(carrier.index(tuple(x[y[k]] for k in range(3))) if name == "S3" else (x + y) % n)
        table.append(row)
    reference, probability = [F(1, n)] * n, [F(0)] * n
    if name == "S3":
        a, b, c = [carrier.index(x) for x in ((1, 0, 2), (0, 2, 1), (1, 2, 0))]
        probability[0], probability[a], probability[c] = F(1, 6), F(1, 2), F(1, 3)
        parity = [sum(x[i] > x[j] for i in range(3) for j in range(i + 1, 3)) % 2 for x in carrier]
    else:
        probability[0] = probability[1] = F(1, 2)
        parity = [x % 2 for x in carrier]
    e, inverse = validate(table, reference, probability)
    full, uniform = moments(reference, probability), moments(reference, reference)
    require(full["energy"] == (F(7, 3) if name == "S3" else F(2)), "fixture energy")
    observations = {"parity": observe(table, reference, probability, parity, full)}
    require(observations["parity"]["multiplicative"], "parity congruence")
    require(observations["parity"]["energy"] == 1, "parity hides fine variation")
    if name == "S3":
        classes = ["E" if x == e else "T" if table[x][x] == e else "C" for x in range(n)]
        observations["conjugacy_class"] = observe(table, reference, probability, classes, full)
        require(not observations["conjugacy_class"]["multiplicative"], "class noncongruence")
        require(classes[a] == classes[b] and table[a][a] == e and table[a][b] == c, "explicit aa versus ab")
        require(table[a][b] != table[b][a], "noncommutativity")
        require(observations["conjugacy_class"]["energy"] == 1, "class observation hides fine variation")
        observations["conjugacy_class"]["specified_witness"] = {"a": a, "b": b, "aa": e, "ab": c, "ba": table[b][a]}
    translations = {"left": [], "right": []}
    for direction in translations:
        for g in range(n):
            translated = [F(0)] * n
            for x in range(n):
                tick()
                translated[table[g][x] if direction == "left" else table[x][g]] += probability[x]
            energy = moments(reference, translated)["energy"]
            require(energy == full["energy"], "uniform-reference translation invariance")
            translations[direction].append(energy)
    controls = []
    fixtures = [("missing reference atom", table, reference[:-1], probability, "MissingAtom"),
                ("zero reference atom", table, [F(0)] + reference[1:], probability, "NonpositiveReference"),
                ("negative mass", table, reference, [F(-1)] + probability[1:], "NegativeMass"),
                ("non-unit probability total", table, reference, [F(0)] * n, "NonunitMass"),
                ("incomplete group table", [table[0][:-1]] + table[1:], reference, probability, "IncompleteGroupTable")]
    for label, invalid_table, invalid_ref, invalid_p, expected in fixtures:
        try:
            validate(invalid_table, invalid_ref, invalid_p)
        except ValueError as error:
            require(str(error) == expected, "exact refusal")
            controls.append({"name": label, "outcome": str(error), "table": invalid_table, "reference": invalid_ref, "probability": invalid_p})
        else:
            raise AssertionError("invalid input accepted: " + label)
    return {"name": name, "carrier": carrier, "table": table, "identity": e, "inverse": inverse,
            "reference": reference, "probability": probability, "uniform": uniform, "full": full,
            "observations": observations, "joints": joints(table, reference, e, inverse),
            "translation_energies": translations, "controls": controls}


def encode(value):
    if isinstance(value, F):
        return str(value)
    raise TypeError(type(value).__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    output = parser.parse_args().output
    output.mkdir(parents=True, exist_ok=False)
    contract_bytes = Path(__file__).with_name("contract.json").read_bytes()
    (output / "contract.json").write_bytes(contract_bytes)
    result = {"profile": "adva.research.finite-group-probability.v0", "execution": "ExternalCalibration",
              "authority": "No native Adva identity, probability operation, Close or free", "instances": [], "search_candidates": 0}
    try:
        resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024,) * 2)
        signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(RuntimeError("UnknownBudget")))
        signal.alarm(30)
        for name in ("S3", "C4"):
            result["instances"].append(instance(name))
        result["outcome"] = "PassedFiniteCalibration"
    except Exception as error:
        result.update(outcome="Failure", failure={"type": type(error).__name__, "message": str(error)})
    finally:
        signal.alarm(0)
    result["cost"] = {**COUNTS, "verification_wall_seconds": time.perf_counter() - START,
                      "peak_process_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                      "rss_platform": sys.platform, "work_unit_definition": "One attempted assertion, validation gate, or explicit tick for an enumerated product/moment/joint/translation cell; not scalar or CPU operations",
                      "missing_measurements": "Final result encoding/write cost and research/authoring cost are not included"}
    (output / "result.json").write_text(json.dumps(result, default=encode, indent=2) + "\n")
    print(json.dumps({"outcome": result["outcome"], "cost": result["cost"]}))
    return 0 if result["outcome"] == "PassedFiniteCalibration" else 1


if __name__ == "__main__":
    raise SystemExit(main())
