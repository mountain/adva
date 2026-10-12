"""Public historical navigation and actual refusal controls; no private access.

Codex (OpenAI), through Mingli Yuan's authorized account proxy; Unknown v0.3.
"""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("philosophy_placement", ROOT / "scripts/check_philosophy_placement.py")
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


class PhilosophyPlacementTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="adva-public-placement-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True, capture_output=True)
        entries, witnesses = [], []
        for index in ("0004", "0005", "0006"):
            source = f"docs/philosophy/{index}-original.md"
            data = (f"Original public fixture {index}; finite scope only.\n" * 30).encode()
            self.write(source, data)
            entries.append({"id": index, "source_path": source,
                            "target_path": f"originals/philosophy/{index}-original.md",
                            "sha256": CHECKER.digest(data), "git_blob": CHECKER.blob_id(data),
                            "bytes": len(data), "title": f"Question {index}",
                            "question": f"How can finite observation {index} be revised?",
                            "public_use": "Retain assumptions while planning a finite check.",
                            "open_obligation": "No native or universal result follows."})
            path = f"programs/bootstrap-0/{index}-witness.adva"
            raw = f"Original documentary witness fixture {index}.\n".encode()
            self.write(path, raw)
            witnesses.append({"path": path, "sha256": CHECKER.digest(raw),
                              "git_blob": CHECKER.blob_id(raw), "bytes": len(raw)})
        subprocess.run(["git", "-C", str(self.root), "add", "docs", "programs"],
                       check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.root), "-c", "user.name=Placement Fixture",
                        "-c", "user.email=fixture@example.invalid", "commit", "-qm", "Public original fixture"],
                       check=True, capture_output=True)
        commit = subprocess.run(["git", "-C", str(self.root), "rev-parse", "HEAD"],
                                check=True, capture_output=True, text=True).stdout.strip()
        self.mapping = {"schema": "adva.research-placement.v0.1",
                        "source": {"repository": "mountain/adva", "commit": commit},
                        "target": {"repository": "mountain/mingli-library", "commit": "f" * 40,
                                   "visibility": "private"},
                        "authority": {"receiver_outcome": "CustodyBytesVerified",
                                      "semantic_verification": "NotRun", "native_admission": "NotGranted",
                                      "public_replay": CHECKER.PUBLIC_REPLAY},
                        "entries": entries, "witnesses": witnesses,
                        "custody_evidence": {"repository": "mountain/mingli-library", "commit": "f" * 40,
                                             "path": "migrations/philosophy-origins-v1/receipt.json",
                                             "sha256": "c" * 64, "status": "CustodyBytesVerified",
                                             "scope": "External private custody observation; not publicly replayed"}}
        for index, entry in enumerate(entries):
            entry["history_url"] = f"https://github.com/mountain/adva/blob/{commit}/{entry['source_path']}"
            self.write(entry["source_path"], (
                f"<!-- research-placement:v1:{entry['id']} -->\n# Compatibility stub\n"
                f"{entry['history_url']}\nmountain/mingli-library\n{'f' * 40}\n"
                f"{entry['target_path']}\n{entry['sha256']}\nPrivate maintenance home only.\n"
                f"[Retained witness](../../{witnesses[index]['path']})\n").encode())
        self.consumer = {"schema": "adva.philosophy-placement-consumer.v0.1",
                         "source": copy.deepcopy(self.mapping["source"]),
                         "target": {k: self.mapping["target"][k] for k in ("repository", "commit")},
                         "entries": [{k: e[k] for k in CHECKER.IDENTITY} for e in entries],
                         "witnesses": copy.deepcopy(witnesses)}
        self.write(CHECKER.GUIDE_PATH, CHECKER.render_guide(self.mapping).encode())
        self.save()

    def write(self, path, data):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    def save(self, mapping=None, consumer=None):
        mapping = self.mapping if mapping is None else mapping
        consumer = copy.deepcopy(self.consumer if consumer is None else consumer)
        raw = (json.dumps(mapping, indent=2) + "\n").encode()
        consumer["map_sha256"] = CHECKER.digest(raw)
        self.write(CHECKER.MAP_PATH, raw)
        self.write(CHECKER.CONSUMER_PATH, (json.dumps(consumer, indent=2) + "\n").encode())

    def test_real_repository_public_successor(self):
        report = CHECKER.check()
        self.assertEqual(report["status"], "HistoricalNavigationChecked", report)
        self.assertEqual(len(report["checks"]), 3)
        self.assertEqual(report["retained_witnesses"], 3)
        self.assertEqual(report["native_admission"], "NotGranted")
        self.assertIn("NotReplayed", report["private_custody"])

    def test_private_unavailable_still_checks_only_public_history(self):
        # The fixture has no private repository, key, credential or private bytes.
        # Observe all child commands to verify the successful route uses local Git only.
        real_run = subprocess.run
        commands = []

        def observe(argv, **kwargs):
            commands.append(argv)
            self.assertEqual(kwargs["env"]["GIT_NO_LAZY_FETCH"], "1")
            self.assertEqual(kwargs["env"]["GIT_TERMINAL_PROMPT"], "0")
            return real_run(argv, **kwargs)

        with patch.object(CHECKER.subprocess, "run", side_effect=observe):
            report = CHECKER.check(self.root)
        self.assertEqual(report["status"], "HistoricalNavigationChecked", report)
        self.assertTrue(commands)
        self.assertTrue(all(c[0] == "git" and c[7] in ("show", "cat-file") for c in commands))
        self.assertTrue(all("--no-lazy-fetch" in c and "protocol.allow=never" in c for c in commands))
        self.assertTrue(all("fetch" not in c and "clone" not in c for c in commands))
        self.assertEqual(report["private_custody"], "RecordedObservationOnly;NotReplayed;NoPrivateRequest")

    def test_independent_pins_reject_wrong_source_target_and_digest(self):
        for mutation in ("source_commit", "target_commit", "source_digest", "source_blob",
                         "source_bytes", "target_path", "witness_digest"):
            with self.subTest(mutation=mutation):
                mapping = copy.deepcopy(self.mapping)
                if mutation == "source_commit":
                    mapping["source"]["commit"] = "a" * 40
                elif mutation == "target_commit":
                    mapping["target"]["commit"] = "b" * 40
                elif mutation == "source_digest":
                    mapping["entries"][0]["sha256"] = "0" * 64
                elif mutation == "source_blob":
                    mapping["entries"][0]["git_blob"] = "0" * 40
                elif mutation == "source_bytes":
                    mapping["entries"][0]["bytes"] += 1
                elif mutation == "target_path":
                    mapping["entries"][0]["target_path"] = "originals/other.md"
                else:
                    mapping["witnesses"][0]["sha256"] = "0" * 64
                self.save(mapping)
                report = CHECKER.check(self.root)
                self.assertEqual(report["status"], "Rejected", report)

    def test_map_cannot_choose_its_own_digest_and_entries_cannot_disappear(self):
        raw = (self.root / CHECKER.MAP_PATH).read_bytes()
        self.write(CHECKER.MAP_PATH, raw + b" ")
        self.assertEqual(CHECKER.check(self.root)["status"], "Rejected")
        for mutation in ("missing", "duplicate", "native", "semantic", "private_replay", "receiver",
                         "custody_coordinate", "custody_status"):
            with self.subTest(mutation=mutation):
                mapping = copy.deepcopy(self.mapping)
                if mutation == "missing":
                    mapping["entries"].pop()
                elif mutation == "duplicate":
                    mapping["entries"][1] = copy.deepcopy(mapping["entries"][0])
                elif mutation == "native":
                    mapping["authority"]["native_admission"] = "Granted"
                elif mutation == "semantic":
                    mapping["authority"]["semantic_verification"] = "Verified"
                elif mutation == "private_replay":
                    mapping["authority"]["public_replay"] = "PrivateCustodyReplayed"
                elif mutation == "receiver":
                    mapping["authority"]["receiver_outcome"] = "DocumentaryAccepted"
                elif mutation == "custody_coordinate":
                    mapping["custody_evidence"]["commit"] = "0" * 40
                else:
                    mapping["custody_evidence"]["status"] = "NativeAccepted"
                self.save(mapping)
                report = CHECKER.check(self.root)
                self.assertEqual(report["status"], "Rejected", report)

    def test_actual_changed_witness_stub_and_generated_guide_rejected(self):
        for path in (self.mapping["witnesses"][0]["path"],
                     self.mapping["entries"][0]["source_path"], CHECKER.GUIDE_PATH):
            with self.subTest(path=path):
                original = (self.root / path).read_bytes()
                self.write(path, b"Broken replacement\n")
                self.assertEqual(CHECKER.check(self.root)["status"], "Rejected")
                self.write(path, original)

    def test_guide_uses_new_question_and_rejects_stale_output(self):
        mapping = copy.deepcopy(self.mapping)
        mapping["entries"][0]["question"] = "What evidence would refute this observer?"
        self.assertNotEqual(CHECKER.render_guide(mapping), CHECKER.render_guide(self.mapping))
        self.save(mapping)
        self.assertEqual(CHECKER.check(self.root)["status"], "Rejected")
        self.write(CHECKER.GUIDE_PATH, CHECKER.render_guide(mapping).encode())
        self.assertEqual(CHECKER.check(self.root)["status"], "HistoricalNavigationChecked")

    def test_missing_public_object_and_budget_exhaustion_are_unknown(self):
        consumer = copy.deepcopy(self.consumer)
        mapping = copy.deepcopy(self.mapping)
        mapping["source"]["commit"] = consumer["source"]["commit"] = "a" * 40
        self.save(mapping, consumer)
        self.assertEqual(CHECKER.check(self.root)["status"], "Unknown")
        self.save()
        with patch.object(CHECKER.subprocess, "run", side_effect=subprocess.TimeoutExpired("git", 1)):
            report = CHECKER.check(self.root)
        self.assertEqual(report["status"], "Unknown", report)
        self.assertEqual(report["native_admission"], "NotGranted")

    def test_corrupted_bytes_are_rejected_even_if_both_metadata_pins_are_changed(self):
        mapping, consumer = copy.deepcopy(self.mapping), copy.deepcopy(self.consumer)
        mapping["entries"][0]["sha256"] = consumer["entries"][0]["sha256"] = "0" * 64
        self.save(mapping, consumer)
        report = CHECKER.check(self.root)
        self.assertEqual(report["status"], "Rejected", report)
        self.assertIn("SHA-256 differs", report["reason"])

    def test_path_traversal_and_duplicate_json_keys_are_rejected(self):
        mapping, consumer = copy.deepcopy(self.mapping), copy.deepcopy(self.consumer)
        mapping["entries"][0]["source_path"] = consumer["entries"][0]["source_path"] = "../private.txt"
        self.save(mapping, consumer)
        self.assertEqual(CHECKER.check(self.root)["status"], "Rejected")
        with self.assertRaises(CHECKER.ValidationError):
            CHECKER.load_json(b'{"commit":"a","commit":"b"}')


if __name__ == "__main__":
    unittest.main()
