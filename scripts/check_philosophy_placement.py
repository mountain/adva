#!/usr/bin/env python3
"""Offline public navigation check for three relocated philosophy originals.

Codex (OpenAI), through Mingli Yuan's authorized account proxy; Unknown v0.3.
This checks historical public bytes, retained witnesses and documentary links.
It never requests the private home or replays its custody receiver.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = "docs/migrations/philosophy-origins-v1.json"
CONSUMER_PATH = "dependencies/philosophy-origins.consumer.json"
GUIDE_PATH = "docs/RESEARCH_GUIDE.md"
MAX_BYTES = 1_048_576
IDENTITY = ("id", "source_path", "target_path", "sha256", "git_blob", "bytes")
WITNESS_IDENTITY = ("path", "sha256", "git_blob", "bytes")
PUBLIC_REPLAY = "HistoricalSourceBytesChecked;PrivateCustodyNotReplayed"


class ValidationError(ValueError):
    """A supplied coordinate, digest, authority or document conflicts."""


class Unavailable(RuntimeError):
    """Required public historical bytes or checking budget is unavailable."""


def require(value, message):
    if not value:
        raise ValidationError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def blob_id(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def safe_path(value):
    require(isinstance(value, str) and value and "\\" not in value,
            "path must be a nonempty POSIX relative path")
    path = PurePosixPath(value)
    require(not path.is_absolute() and all(p not in (".", "..") for p in value.split("/"))
            and "//" not in value and "\x00" not in value,
            "unsafe relative path")
    return value


def read_bytes(root, path):
    path = safe_path(path)
    location = root / path
    require(location.resolve().is_relative_to(root.resolve()), "path escapes checkout")
    require(location.is_file() and not location.is_symlink(), "required public file missing")
    require(location.stat().st_size <= MAX_BYTES, "public file exceeds bounded byte budget")
    return location.read_bytes()


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON object key")
        result[key] = value
    return result


def load_json(data):
    try:
        return json.loads(data, object_pairs_hook=_unique_object)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValidationError("invalid JSON") from error


def _coordinate(data):
    require(isinstance(data, dict), "repository coordinate must be an object")
    require(isinstance(data.get("repository"), str) and
            re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", data["repository"]),
            "invalid repository identity")
    require(isinstance(data.get("commit"), str) and
            re.fullmatch(r"[0-9a-f]{40}", data["commit"]) and data["commit"] != "0" * 40,
            "full non-placeholder commit required")
    return {key: data[key] for key in ("repository", "commit")}


def _identity(data, fields):
    require(isinstance(data, dict) and all(key in data for key in fields),
            "incomplete byte identity")
    for key in fields:
        if key.endswith("path"):
            safe_path(data[key])
    require(isinstance(data["sha256"], str) and re.fullmatch(r"[0-9a-f]{64}", data["sha256"]),
            "invalid SHA-256")
    require(isinstance(data["git_blob"], str) and re.fullmatch(r"[0-9a-f]{40}", data["git_blob"]),
            "invalid Git blob")
    require(type(data["bytes"]) is int and 0 < data["bytes"] <= MAX_BYTES,
            "invalid bounded byte count")
    return {key: data[key] for key in fields}


def _matches(data, identity, label):
    require(len(data) == identity["bytes"], f"{label}: byte count differs")
    require(digest(data) == identity["sha256"], f"{label}: SHA-256 differs")
    require(blob_id(data) == identity["git_blob"], f"{label}: Git blob differs")


class HistoricalReader:
    """Read only explicitly pinned local Git objects, within a shared deadline."""

    def __init__(self, root, budget_seconds):
        require(isinstance(budget_seconds, (int, float)) and
                not isinstance(budget_seconds, bool) and 0 < budget_seconds <= 60,
                "checking deadline must be between 0 and 60 seconds")
        self.root = root
        self.deadline = time.monotonic() + budget_seconds

    def run(self, *args):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise Unavailable("historical Git deadline exhausted")
        try:
            result = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch",
                                     "-c", "protocol.allow=never", "-C", str(self.root),
                                     *args], capture_output=True, check=False,
                                    timeout=min(5, remaining),
                                    env={**os.environ, "GIT_NO_LAZY_FETCH": "1",
                                         "GIT_TERMINAL_PROMPT": "0"})
        except (subprocess.TimeoutExpired, OSError) as error:
            raise Unavailable("historical Git lookup unavailable") from error
        if result.returncode:
            raise Unavailable("required fixed public Git object is unavailable; fetch it explicitly")
        require(len(result.stdout) <= MAX_BYTES, "historical bytes exceed bounded budget")
        return result.stdout

    def commit(self, commit):
        require(self.run("cat-file", "-t", commit).strip() == b"commit",
                "source revision is not a commit")

    def read(self, commit, path):
        object_name = f"{commit}:{safe_path(path)}"
        size = self.run("cat-file", "-s", object_name).strip()
        require(size.isdigit() and int(size) <= MAX_BYTES,
                "historical object exceeds bounded byte budget")
        return self.run("show", object_name)


def render_guide(mapping):
    """Render independently authored public questions from documentary metadata."""
    lines = ["# Research Guide: Finite Observers, Witnesses and Revision", "",
             "This public guide organizes three research questions. The original personal",
             "notes now have a private maintenance home; their already-public fixed Git",
             "versions remain accessible without private credentials. These questions and",
             "reading directions are documentary context, not executable claims.", "",
             "The public checker verifies historical source bytes, preserved witness files",
             "and this generated navigation. It does not replay the private custody receiver.", ""]
    for entry in mapping["entries"]:
        lines.extend([f"## {entry['id']}: {entry['title']}", "",
                      f"**Question.** {entry['question']}", "",
                      f"**Public research use.** {entry['public_use']}", "",
                      f"**Open obligation.** {entry['open_obligation']}", "",
                      f"[Historical public original]({entry['history_url']}) · "
                      f"[Compatibility entry](philosophy/{Path(entry['source_path']).name})", ""])
    lines.extend(["## Verification and authority", "",
                  "Run `python scripts/check_philosophy_placement.py` from a checkout containing",
                  f"the fixed public source commit `{mapping['source']['commit']}`. A missing",
                  "historical object or exhausted checking deadline produces `Unknown`; a",
                  "coordinate, digest, witness, stub or navigation mismatch produces `Rejected`.", "",
                  "The private custody observation is recorded separately; private originals",
                  "are not requested or assumed available. Semantic verification remains",
                  "`NotRun`, and native admission remains `NotGranted`.", "",
                  f"Private maintenance home: `{mapping['target']['repository']}` at",
                  f"`{mapping['target']['commit']}`. Its externally recorded custody outcome",
                  "is `CustodyBytesVerified`; this public navigation check does not verify that",
                  "private receiver or turn the recorded outcome into native authority.", "",
                  "Source paths and full identities are retained in",
                  "[the placement map](migrations/philosophy-origins-v1.json); the public consumer",
                  "[independently pins them](../dependencies/philosophy-origins.consumer.json).",
                  "No executable machine dependency or frozen research evidence is replaced.", "",
                  "Original guide/checker contribution: Codex (OpenAI), Unknown v0.3, through",
                  "Mingli Yuan's authorized account proxy; account use is not his review.", ""])
    return "\n".join(lines)


def validate(mapping, consumer, root=ROOT, *, budget_seconds=15, historical=None):
    require(isinstance(mapping, dict) and isinstance(consumer, dict), "JSON object required")
    require(mapping.get("schema") == "adva.research-placement.v0.1", "unknown placement schema")
    require(consumer.get("schema") == "adva.philosophy-placement-consumer.v0.1",
            "unknown public consumer schema")
    source, target = _coordinate(mapping["source"]), _coordinate(mapping["target"])
    require(source == _coordinate(consumer["source"]), "source differs from independent consumer pin")
    require(target == _coordinate(consumer["target"]), "target differs from independent consumer pin")
    require(source["repository"] == "mountain/adva", "unsupported public source repository")
    require(target["repository"] == "mountain/mingli-library" and
            mapping["target"].get("visibility") == "private", "private maintenance home differs")
    authority = mapping["authority"]
    require(authority == {"receiver_outcome": "CustodyBytesVerified", "semantic_verification": "NotRun",
                          "native_admission": "NotGranted", "public_replay": PUBLIC_REPLAY},
            "unsupported authority or private-replay claim")
    custody = mapping["custody_evidence"]
    require(isinstance(custody, dict) and set(custody) ==
            {"repository", "commit", "path", "sha256", "status", "scope"},
            "incomplete external custody observation")
    require(_coordinate(custody) == target, "external custody coordinate differs from target")
    safe_path(custody["path"])
    require(isinstance(custody["sha256"], str) and
            re.fullmatch(r"[0-9a-f]{64}", custody["sha256"]), "invalid custody receipt digest")
    require(custody["status"] == "CustodyBytesVerified" and
            custody["scope"] == "External private custody observation; not publicly replayed",
            "unsupported external custody authority")
    entries = mapping["entries"]
    require(isinstance(entries, list) and len(entries) == 3 and
            {entry.get("id") for entry in entries} == {"0004", "0005", "0006"},
            "exactly the three selected entries required")
    actual = [_identity(entry, IDENTITY) for entry in entries]
    pinned = [_identity(entry, IDENTITY) for entry in consumer["entries"]]
    require(actual == pinned, "entry identities differ from independent consumer pins")
    require(len({entry["source_path"] for entry in actual}) == 3 and
            len({entry["target_path"] for entry in actual}) == 3, "duplicate source or target path")
    witnesses = [_identity(item, WITNESS_IDENTITY) for item in mapping["witnesses"]]
    require(len(witnesses) == 3 and len({w["path"] for w in witnesses}) == 3,
            "exactly three distinct retained witnesses required")
    require(witnesses == [_identity(item, WITNESS_IDENTITY) for item in consumer["witnesses"]],
            "witness identities differ from independent consumer pins")
    historical = historical or HistoricalReader(root, budget_seconds)
    historical.commit(source["commit"])
    checks = []
    for index, entry in enumerate(entries):
        for key in ("title", "question", "public_use", "open_obligation"):
            require(isinstance(entry.get(key), str) and entry[key].strip(),
                    "public reading metadata missing")
        history_url = (f"https://github.com/{source['repository']}/blob/{source['commit']}/"
                       f"{entry['source_path']}")
        require(entry["history_url"] == history_url, "historical public URL differs")
        _matches(historical.read(source["commit"], entry["source_path"]), entry,
                 f"historical original {entry['id']}")
        stub = read_bytes(root, entry["source_path"])
        require(len(stub) < entry["bytes"] and digest(stub) != entry["sha256"],
                "original has not been replaced by a bounded compatibility stub")
        text = stub.decode("utf-8")
        for token in (f"<!-- research-placement:v1:{entry['id']} -->", history_url,
                      target["repository"], target["commit"], entry["target_path"], entry["sha256"],
                      f"../../{witnesses[index]['path']}"):
            require(token in text, f"compatibility stub {entry['id']} lacks {token}")
        checks.append({"id": entry["id"], "historical_source": "ExactBytesChecked",
                       "compatibility_stub": "NavigationChecked"})
    for witness in witnesses:
        _matches(historical.read(source["commit"], witness["path"]), witness,
                 f"historical witness {witness['path']}")
        _matches(read_bytes(root, witness["path"]), witness,
                 f"retained witness {witness['path']}")
    require(read_bytes(root, GUIDE_PATH).decode("utf-8") == render_guide(mapping),
            "public guide differs from declared questions and navigation")
    return {"schema": "adva.philosophy-placement-check.v0.1", "status": "HistoricalNavigationChecked",
            "source": source, "target": target, "checks": checks, "retained_witnesses": len(witnesses),
            "private_custody": "RecordedObservationOnly;NotReplayed;NoPrivateRequest",
            "semantic_verification": "NotRun", "native_admission": "NotGranted"}


def check(root=ROOT, mapping_path=MAP_PATH, consumer_path=CONSUMER_PATH, *, budget_seconds=15):
    try:
        raw = read_bytes(root, mapping_path)
        mapping = load_json(raw)
        consumer = load_json(read_bytes(root, consumer_path))
        require(isinstance(consumer, dict), "consumer JSON object required")
        require(digest(raw) == consumer.get("map_sha256"), "placement map differs from independent digest")
        return validate(mapping, consumer, root, budget_seconds=budget_seconds)
    except Unavailable as error:
        return {"schema": "adva.philosophy-placement-check.v0.1", "status": "Unknown", "reason": str(error),
                "private_custody": "NotReplayed;NoPrivateRequest", "native_admission": "NotGranted"}
    except (ValidationError, KeyError, TypeError, UnicodeError) as error:
        return {"schema": "adva.philosophy-placement-check.v0.1", "status": "Rejected", "reason": str(error),
                "private_custody": "NotReplayed;NoPrivateRequest", "native_admission": "NotGranted"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--budget-seconds", type=float, default=15)
    args = parser.parse_args()
    result = check(args.root, budget_seconds=args.budget_seconds)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "HistoricalNavigationChecked" else 1


if __name__ == "__main__":
    raise SystemExit(main())
