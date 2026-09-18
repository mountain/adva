"""Bounded external proposal, exact reconstruction and independent verification.

Original contribution by ChatGPT (OpenAI), through Mingli Yuan's account proxy,
under Unknown v0.3. A numerical proposer is not a native Adva learner. External
seed bytes and generated numerical inputs remain in the explicitly chosen output.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import platform
import resource
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from experiments.pascal_circle_learning import model

NUMERICAL_EVALUATIONS = 48012
MAX_FUEL = 50000
MAX_INPUT = 1048576
MAX_OUTPUT = 8388608
MEMORY = 2147483648
TOTAL_SECONDS = 240
CONTRACT_SCHEMA = "adva.external.pascal-circle-learning.contract.v1"


class Stopped(Exception):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate-json-key")
        result[key] = value
    return result


def decode(data):
    def invalid(_):
        raise ValueError("nonfinite-json-number")
    return json.loads(data, object_pairs_hook=unique_keys, parse_constant=invalid)


def read_bounded(path, limit=MAX_INPUT):
    with Path(path).open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError("input-byte-limit")
    return data


def load_seed(path):
    raw = read_bounded(path)
    obj = decode(raw)
    if type(obj) is not dict or obj.get("schema") != "adva.external.pascal-circle-seed.v0":
        raise ValueError("unsupported-seed-schema")
    points = obj.get("points")
    if (type(points) is not list or len(points) != 14
            or any(type(p) is not list or len(p) != 2 for p in points)
            or any(type(v) not in (int, float) or not math.isfinite(v) or abs(v) > 1000000
                   for p in points for v in p)):
        raise ValueError("seed-requires-fourteen-bounded-finite-points")
    if len({tuple(p) for p in points}) != 14:
        raise ValueError("seed-points-not-distinct")
    return raw, [[float(v) for v in p] for p in points]


def circle_center(points, labels):
    p, q, r = [points[i] for i in labels[:3]]
    a, b = 2 * (q[0] - p[0]), 2 * (q[1] - p[1])
    d, e = 2 * (r[0] - p[0]), 2 * (r[1] - p[1])
    c = sum(v * v for v in q) - sum(v * v for v in p)
    f = sum(v * v for v in r) - sum(v * v for v in p)
    denominator = a * e - d * b
    if abs(denominator) < 1e-12:
        raise ValueError("seed-circle-chart-degenerate")
    return ((c * e - f * b) / denominator, (a * f - d * c) / denominator)


def relative_angles(parameters):
    result = []
    for name in ("red_t", "blue_t"):
        angles = [2 * math.atan(float(F(v))) for v in parameters[name]]
        result.extend(a - angles[0] for a in angles[1:])
    red = list(map(F, parameters["red_similarity"]))
    blue = list(map(F, parameters["blue_similarity"]))
    delta = complex(float(blue[2] - red[2]), float(blue[3] - red[3]))
    if abs(delta) == 0:
        raise ValueError("warm-start-center-direction-undefined")
    red_angle = 2 * math.atan(float(F(parameters["red_t"][0])))
    result.append(math.atan2(delta.imag, delta.real) - math.atan2(float(red[1]), float(red[0])) - red_angle)
    return result


def initial_diagnostics(points):
    """Floating diagnostics of assigned roles, never an exact acceptance test."""
    report, source_angles = {}, []
    for name, labels, sequence, targets in (
        ("red", [1, 3, 5, 7, 9], [1, 1, 3, 5, 7, 9], [11, None, 13]),
        ("blue", [2, 4, 8, 12], [2, 2, 4, 8, 8, 12], [0, 6, 10]),
    ):
        center = circle_center(points, labels)
        angles = [math.atan2(points[i][1] - center[1], points[i][0] - center[0])
                  for i in labels[:4]]
        source_angles.extend(a - angles[0] for a in angles[1:])
        radius_squared = sum((points[labels[0]][k] - center[k]) ** 2 for k in (0, 1))
        lines = []
        for i, first in enumerate(sequence):
            second = sequence[(i + 1) % 6]
            p, q = points[first], points[second]
            if first == second:
                a, b = p[0] - center[0], p[1] - center[1]
                lines.append((a, b, -a * p[0] - b * p[1]))
            else:
                lines.append(model.line(p, q))
        entries = []
        for i, target in enumerate(targets):
            p = model.cross(lines[i], lines[i + 3])
            scale = max(abs(v) for v in p)
            if scale == 0:
                entries.append({"target": target, "state": "undefined-intersection"})
            elif target is None:
                entries.append({"target": None, "normalized_infinity_residual": abs(p[2]) / scale})
            elif abs(p[2]) < 1e-12 * scale:
                entries.append({"target": target, "state": "infinite-instead-of-finite"})
            else:
                entries.append({"target": target, "displacement": math.hypot(
                    p[0] / p[2] - points[target][0], p[1] / p[2] - points[target][1])})
        report[name] = {
            "center": center, "radius_squared": radius_squared,
            "maximum_circle_residual": max(abs(sum((points[i][k] - center[k]) ** 2 for k in (0, 1))
                                                  - radius_squared) for i in labels),
            "bindings": entries,
        }
    delta = [report["blue"]["center"][i] - report["red"]["center"][i] for i in (0, 1)]
    if math.hypot(*delta) == 0:
        raise ValueError("seed-center-direction-undefined")
    red_a = [points[1][i] - report["red"]["center"][i] for i in (0, 1)]
    source_angles.append(math.atan2(delta[1], delta[0]) - math.atan2(red_a[1], red_a[0]))
    report["center_incidence_residual"] = sum(v * v for v in delta) - report["red"]["radius_squared"]
    report["interpretation"] = (
        "Floating diagnostics of this selected intersection-to-label mapping. "
        "Any mismatch concerns the prescribed roles, not a failure of Pascal's theorem.")
    return report, source_angles


def fit_joint(red, blue, direction, target):
    """Complex normal equations for C,q,s, with the two centers coupled."""
    k = complex(*map(float, direction))
    rows = [None] * 14
    for indices, group, is_red in ((model.RED_GROUP, red, True), (model.BLUE_GROUP, blue, False)):
        for index, point in zip(indices, group, strict=True):
            value = complex(*map(float, point))
            rows[index] = (1 + 0j, value, 0j) if is_red else (1 + 0j, k, value)
    matrix = [[0j] * 4 for _ in range(3)]
    for row, point in zip(rows, target, strict=True):
        wanted = complex(*point)
        for j in range(3):
            for col in range(3):
                matrix[j][col] += row[j].conjugate() * row[col]
            matrix[j][3] += row[j].conjugate() * wanted
    for col in range(3):
        pivot = max(range(col, 3), key=lambda index: abs(matrix[index][col]))
        if abs(matrix[pivot][col]) < 1e-12:
            raise ValueError("singular-joint-fit")
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        denominator = matrix[col][col]
        matrix[col] = [value / denominator for value in matrix[col]]
        for row in range(3):
            if row != col:
                factor = matrix[row][col]
                matrix[row] = [value - factor * basis for value, basis in zip(matrix[row], matrix[col], strict=True)]
    result = [row[3] for row in matrix]
    if not all(math.isfinite(v.real) and math.isfinite(v.imag) for v in result):
        raise ValueError("nonfinite-joint-fit")
    return result


def rationalize(angles, cap, target):
    values = [F(math.tan(angle / 2)).limit_denominator(cap) for angle in angles]
    parameters = {"red_t": [F(0), *values[:3]], "blue_t": [F(0), *values[3:6]], "center_t": [values[6]]}
    red, blue = model.unit_groups(parameters["red_t"], parameters["blue_t"])
    center, q, s = fit_joint(red, blue, model.circle_point(values[6]), target)
    parameters["red_similarity"] = [F(v).limit_denominator(cap) for v in (q.real, q.imag, center.real, center.imag)]
    parameters["blue_linear"] = [F(v).limit_denominator(cap) for v in (s.real, s.imag)]
    params = {key: [str(v) for v in value] for key, value in parameters.items()}
    candidate = model.candidate(params)
    points = [[F(v) for v in p] for p in candidate["points"]]
    minimum_squared = min(sum((points[i][k] - points[j][k]) ** 2 for k in (0, 1))
                          for i in range(14) for j in range(i + 1, 14))
    rms = math.sqrt(sum((float(points[i][k]) - target[i][k]) ** 2
                        for i in range(14) for k in (0, 1)) / 14)
    return params, candidate, minimum_squared, rms


class Run:
    def __init__(self, output, fuel):
        self.output, self.fuel = Path(output).resolve(), fuel
        if self.output == ROOT or ROOT in self.output.parents:
            raise ValueError("external-output-directory-required")
        self.output.mkdir(parents=True, exist_ok=False)
        self.started = time.monotonic()
        self.cpu_started = time.process_time()
        self.children_started = resource.getrusage(resource.RUSAGE_CHILDREN)
        self.report = {
            "schema": "adva.external.pascal-circle-run.v1", "status": "Unknown",
            "reason": "not-run", "fuel_initial": fuel, "numeric_evaluations": 0,
            "exact_candidate_checks": 0, "rationalization_attempts": [], "children": [],
            "native_admission": "not-granted", "native_learning": False,
            "run_role": "bounded-successor-after-user-added-center-incidence",
            "cost_scope": "This invocation only. Earlier separately bounded prototype and refinement pilots are not included; the warm start is explicitly supplied reuse.",
            "platform": {"system": platform.platform(), "python": platform.python_version()},
        }

    def remaining(self):
        left = TOTAL_SECONDS - (time.monotonic() - self.started)
        if left <= 0:
            raise Stopped("total-wall-limit")
        return left

    def write(self, name, value):
        self.remaining()
        path = self.output / name
        payload = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
        used = sum(p.stat().st_size for p in self.output.iterdir() if p.is_file())
        previous = path.stat().st_size if path.exists() else 0
        if used - previous + len(payload) > MAX_OUTPUT:
            raise Stopped("output-byte-limit")
        path.write_bytes(payload)

    def child(self, name, argv, seconds, cpu_seconds):
        timeout = min(seconds, self.remaining())
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        started = time.monotonic()

        def limits():
            resource.setrlimit(resource.RLIMIT_AS, (MEMORY, MEMORY))
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
            resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_OUTPUT, MAX_OUTPUT))
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

        result = None
        with (self.output / (name + ".stdout.txt")).open("wb") as stdout:
            with (self.output / (name + ".stderr.txt")).open("wb") as stderr:
                try:
                    result = subprocess.run(argv, cwd=ROOT, stdout=stdout, stderr=stderr,
                                            timeout=timeout, preexec_fn=limits, check=False)
                except subprocess.TimeoutExpired:
                    raise Stopped(name + "-wall-limit") from None
                finally:
                    after = resource.getrusage(resource.RUSAGE_CHILDREN)
                    self.report["children"].append({
                        "name": name, "exit_code": result.returncode if result else None,
                        "wall_seconds": time.monotonic() - started,
                        "cpu_seconds": after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime,
                        "child_highwater_rss_kib": after.ru_maxrss,
                    })
        self.remaining()
        if sum(p.stat().st_size for p in self.output.iterdir() if p.is_file()) > MAX_OUTPUT:
            raise Stopped("output-byte-limit")
        return result.returncode

    def pin_sources(self):
        contract_bytes = read_bounded(HERE / "contract_v1.json")
        contract = decode(contract_bytes)
        if contract.get("schema") != CONTRACT_SCHEMA:
            raise ValueError("contract-schema-changed")
        pins = {"contract_v1.json": digest(contract_bytes)}
        for name in ("pascal_task", "pascal_witness"):
            pin = contract["sources"][name]
            actual = digest(read_bounded(ROOT / pin["path"]))
            if actual != pin["sha256"]:
                raise ValueError("pinned-pascal-source-changed")
            pins[pin["path"]] = actual
        expected = contract["sources"]["library_commit"]
        if self.child("library-revision", ["git", "-C", str(ROOT / "adva-library"), "rev-parse", "HEAD"], 5, 5):
            raise ValueError("library-revision-unavailable")
        if (self.output / "library-revision.stdout.txt").read_text().strip() != expected:
            raise ValueError("library-revision-changed")
        if self.child("base-commit", ["git", "merge-base", "--is-ancestor", contract["base_commit"], "HEAD"], 5, 5):
            raise ValueError("pinned-base-not-an-ancestor")
        if self.child("gitlink", ["git", "ls-tree", "HEAD", "adva-library"], 5, 5):
            raise ValueError("library-gitlink-unavailable")
        if expected not in (self.output / "gitlink.stdout.txt").read_text().split():
            raise ValueError("library-gitlink-changed")
        if self.child("producer-baseline", ["git", "show", contract["base_commit"] +
                       ":experiments/knowledge_geometry/acceleration_direction.py"], 5, 5):
            raise ValueError("pinned-producer-arithmetic-unavailable")
        helper = ROOT / "experiments/knowledge_geometry/acceleration_direction.py"
        if helper.read_bytes() != (self.output / "producer-baseline.stdout.txt").read_bytes():
            raise ValueError("reused-arithmetic-changed-from-base")
        # The Git show output is first-party code, not an external seed.
        for path in (HERE / "run.py", HERE / "refine.cpp", HERE / "warm-start.json",
                     HERE / "model.py", HERE / "check.py", helper):
            pins[str(path.relative_to(ROOT))] = digest(path.read_bytes())
        self.report["source_sha256"] = pins
        self.report["base_commit"] = contract["base_commit"]
        self.report["library_commit"] = expected

    def execute(self, seed_path):
        if not 0 <= self.fuel <= MAX_FUEL:
            raise ValueError("fuel-outside-contract")
        raw, target = load_seed(seed_path)
        self.report["seed_sha256"] = digest(raw)
        self.report["seed_bytes"] = len(raw)
        if self.fuel < NUMERICAL_EVALUATIONS + 1:
            self.report["reason"] = "insufficient-fuel-for-fixed-proposal-and-one-check"
            return
        self.pin_sources()
        initial, source_angles = initial_diagnostics(target)
        self.write("initial-diagnostics.json", initial)
        warm = decode(read_bounded(HERE / "warm-start.json"))
        generic = relative_angles(warm["parameters"])
        numbers = [v for p in target for v in p] + generic + source_angles
        (self.output / "numeric-input.txt").write_text("\n".join(format(v, ".17g") for v in numbers) + "\n")
        compiler = shutil.which("g++")
        if compiler is None:
            raise Stopped("cxx-compiler-unavailable")
        if self.child("compiler-version", [compiler, "--version"], 5, 5):
            raise Stopped("compiler-version-unavailable")
        executable = self.output / "refine"
        if self.child("compile", [compiler, "-O2", "-std=c++17", str(HERE / "refine.cpp"),
                                  "-o", str(executable)], 45, 45):
            raise Stopped("numerical-proposer-build-failed")
        self.report["numeric_fuel_reserved"] = NUMERICAL_EVALUATIONS
        numeric_code = self.child("numeric", [str(executable), str(self.output / "numeric-input.txt"),
                                              str(self.output / "numeric.json")], 180, 180)
        if not (self.output / "numeric.json").exists():
            raise Stopped("numerical-proposer-no-result")
        numeric = decode(read_bounded(self.output / "numeric.json"))
        self.report["numeric_evaluations"] = numeric.get("evaluations", 0)
        self.report["numeric_evaluations_exact"] = True
        if numeric_code != 0:
            raise Stopped("numerical-proposer-no-feasible-candidate")
        if numeric.get("evaluations") != NUMERICAL_EVALUATIONS:
            raise Stopped("numerical-evaluation-account-mismatch")
        records = numeric.get("records")
        if (type(records) is not list or not 1 <= len(records) <= 20
                or any(type(r) is not dict or type(r.get("angles")) is not list
                       or len(r["angles"]) != 7 or any(type(v) not in (float, int) or not math.isfinite(v)
                                                       for v in r["angles"]) for r in records)):
            raise Stopped("malformed-numerical-records")
        self.report["numeric_best_rms"] = numeric["best_rms"]
        self.report["proposal_state"] = "Proposed"
        for record_index, record in enumerate(reversed(records)):
            for cap in (10000, 1000, 100):
                self.remaining()
                attempted = len(self.report["rationalization_attempts"])
                if NUMERICAL_EVALUATIONS + attempted >= self.fuel:
                    raise Stopped("fuel-exhausted-before-next-rationalization")
                attempt = {"ordinal": attempted, "record_from_best": record_index,
                           "denominator_limit": cap, "verdict": "Refuted"}
                self.report["rationalization_attempts"].append(attempt)
                try:
                    parameters, candidate, minimum_squared, rms = rationalize(record["angles"], cap, target)
                except (ValueError, ZeroDivisionError, OverflowError) as exc:
                    attempt["reason"] = "rational-construction-refused"
                    attempt["diagnostic"] = str(exc)
                    continue
                name = "candidate-" + str(attempted)
                self.write(name + ".json", candidate)
                self.report["exact_candidate_checks"] += 1
                code = self.child(name + "-check", [sys.executable, str(HERE / "check.py"),
                                                    str(self.output / (name + ".json"))], 30, 30)
                checked = decode(read_bounded(self.output / (name + "-check.stdout.txt")))
                if (code, checked.get("status")) not in ((0, "Verified"), (2, "Refuted")):
                    raise Stopped("independent-checker-protocol-failure")
                attempt.update(verdict=checked["status"], failures=checked.get("failures", []),
                               minimum_pair_distance=math.sqrt(float(minimum_squared)), rms_displacement=rms,
                               minimum_pair_distance_squared=str(minimum_squared),
                               minimum_distance_guard=minimum_squared > F(1, 40000))
                if checked["status"] == "Verified" and minimum_squared > F(1, 40000):
                    self.write("candidate.json", candidate)
                    self.write("parameters.json", parameters)
                    self.write("checker.json", checked)
                    self.report.update(status="Verified", reason="independently-checked-rational-witness",
                                       proposal_state="Verified", rms_displacement=rms,
                                       minimum_pair_distance=math.sqrt(float(minimum_squared)),
                                       minimum_pair_distance_squared=str(minimum_squared))
                    return
        self.report["reason"] = "fixed-rationalization-family-exhausted"

    def finish(self):
        children = resource.getrusage(resource.RUSAGE_CHILDREN)
        self.report["wall_seconds_before_final_serialization"] = time.monotonic() - self.started
        self.report["parent_cpu_seconds"] = time.process_time() - self.cpu_started
        self.report["children_cpu_seconds"] = (
            children.ru_utime + children.ru_stime - self.children_started.ru_utime - self.children_started.ru_stime)
        self.report["parent_peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        self.report["child_highwater_rss_kib"] = children.ru_maxrss
        numeric_charge = (self.report["numeric_evaluations"] if self.report.get("numeric_evaluations_exact")
                          else self.report.get("numeric_fuel_reserved", 0))
        self.report["fuel_spent"] = numeric_charge + len(self.report["rationalization_attempts"])
        self.report["fuel_spent_is_upper_bound"] = bool(numeric_charge and not self.report.get("numeric_evaluations_exact"))
        self.report["fuel_remaining"] = self.fuel - self.report["fuel_spent"]
        self.report["output_sha256"] = {p.name: digest(p.read_bytes()) for p in self.output.iterdir() if p.is_file()}
        # Reserve final checkpoint outside the cooperative deadline after an explicit stop.
        data = (json.dumps(self.report, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
        if sum(p.stat().st_size for p in self.output.iterdir() if p.is_file()) + len(data) > MAX_OUTPUT:
            raise Stopped("checkpoint-output-byte-limit")
        (self.output / "report.json").write_bytes(data)
        return self.report


def run(seed, output, fuel=MAX_FUEL):
    attempt = Run(output, fuel)
    try:
        attempt.execute(seed)
    except FileNotFoundError as exc:
        attempt.report.update(status="Unknown", reason="required-input-unavailable", diagnostic=str(exc))
    except (ValueError, OSError, Stopped) as exc:
        attempt.report.update(status="Unknown", reason=str(exc))
    return attempt.finish()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fuel", type=int, default=MAX_FUEL)
    args = parser.parse_args()
    if not 0 <= args.fuel <= MAX_FUEL:
        parser.error("fuel must be between 0 and 50000")
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY, MEMORY))
    resource.setrlimit(resource.RLIMIT_CPU, (180, 180))
    report = run(args.seed, args.output.resolve(), args.fuel)
    print(json.dumps({key: report[key] for key in ("status", "reason", "fuel_spent", "fuel_remaining")}, sort_keys=True))
    return 0 if report["status"] == "Verified" else 3


if __name__ == "__main__":
    raise SystemExit(main())
