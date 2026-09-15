"""The research index must stay complete and its counts must stay true.

A merge can bring in notes that the merging branch never indexed, and git does not
treat that as a conflict: the file names differ, so the merge is clean while the
record silently loses a note's reachability and the header count drifts. That is
exactly what happened when the iota-lang line was merged, so this check is kept.
The same applies to named notes and to supporting directories, whose counts the
header states once; both were checked by hand until 2026-09-16 and one of each had
already drifted out of the listing.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "docs/research"
README = RESEARCH / "README.md"


def header_counts():
    text = README.read_text(encoding="utf-8")
    counts = re.search(
        r"\*\*(\d+) numbered\s+notes, (\d+) named notes and (\d+) supporting directories\*\*", text
    )
    assert counts, "the header counts are not where they were"
    return tuple(int(group) for group in counts.groups())


def numbered_note_files():
    return sorted(p.name for p in RESEARCH.glob("[0-9][0-9][0-9][0-9]-*.md"))


def named_note_files():
    return sorted(
        p.name
        for p in RESEARCH.glob("*.md")
        if not re.fullmatch(r"[0-9]{4}-.*", p.name) and p.name != README.name
    )


def supporting_directories():
    return sorted(p.name for p in RESEARCH.iterdir() if p.is_dir() and not p.name.startswith("__"))


def linked_files():
    return set(re.findall(r"\]\(([0-9]{4}-[A-Za-z0-9._\-]+\.md)\)",
                          README.read_text(encoding="utf-8")))


def linked_named_notes():
    linked = set(re.findall(r"\]\(([A-Za-z0-9._\-]+\.md)\)", README.read_text(encoding="utf-8")))
    return linked - set(numbered_note_files())


def linked_directories():
    return set(re.findall(r"\]\(([A-Za-z0-9._\-]+/)\)", README.read_text(encoding="utf-8")))


def test_every_numbered_note_is_indexed():
    missing = [n for n in numbered_note_files() if n not in linked_files()]
    assert not missing, "notes reachable only through the directory listing: %s" % missing


def test_every_indexed_note_exists():
    absent = [n for n in sorted(linked_files()) if not (RESEARCH / n).exists()]
    assert not absent, "index entries pointing at nothing: %s" % absent


def test_every_named_note_is_indexed():
    missing = [n for n in named_note_files() if n not in linked_named_notes()]
    assert not missing, "named notes reachable only through the directory listing: %s" % missing


def test_every_supporting_directory_is_indexed():
    missing = [d for d in supporting_directories() if d + "/" not in linked_directories()]
    assert not missing, "directories reachable only through the directory listing: %s" % missing


def test_the_header_count_matches_the_directory():
    claimed, _, _ = header_counts()
    actual = len(numbered_note_files())
    assert claimed == actual, "header claims %d numbered notes, directory holds %d" % (
        claimed, actual)


def test_the_named_count_matches_the_directory():
    _, claimed, _ = header_counts()
    actual = len(named_note_files())
    assert claimed == actual, "header claims %d named notes, directory holds %d" % (
        claimed, actual)


def test_the_directory_count_matches_the_directory():
    _, _, claimed = header_counts()
    actual = len(supporting_directories())
    assert claimed == actual, "header claims %d supporting directories, directory holds %d" % (
        claimed, actual)


def test_shared_numbers_are_tolerated_but_each_note_still_has_a_number():
    numbers = {}
    for name in numbered_note_files():
        numbers.setdefault(name[:4], []).append(name)
    assert numbers, "no numbered notes at all"
    for number, files in numbers.items():
        assert int(number) > 0
        for name in files:
            assert name.startswith(number + "-")
