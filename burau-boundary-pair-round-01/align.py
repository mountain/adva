#!/usr/bin/env python3
"""Burau boundary pair alignment, round 01.

Objects:
  2607.05283v1.pdf  BBB (Bharathram-Birman-Brendle), "The Burau representation
                    of the braid group is faithful for n = 4", 26 pp, 2026.
  9904100v2.pdf     Bigelow, "The Burau representation is not faithful for
                    n = 5", Geom. Topol. 3 (1999) 397-404, 8 pp.

Alignment probe: pin both PDFs, compare text layers word-by-word, measure
the title edit distance, key-phrase frequencies, and the parameter adjacency.
"""
import hashlib
import json
import os
import re
import sys

ROOT = os.path.join(os.path.expanduser("~"), "Adva", "AEG",
                    "trials", "burau-boundary-pair-round-01")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def words_of(path):
    raw = open(path).read()
    return re.findall(r"[A-Za-z][A-Za-z'-]*|[0-9]+", raw)


def freq(tokens):
    d = {}
    for t in tokens:
        d[t] = d.get(t, 0) + 1
    return d


def main():
    bbb_tok = [w.lower() for w in words_of(os.path.join(ROOT, "bbb-full.txt"))]
    big_tok = [w.lower() for w in words_of(os.path.join(ROOT, "bigelow-full.txt"))]
    bbb_f, big_f = freq(bbb_tok), freq(big_tok)
    shared = set(bbb_f) & set(big_f)
    bbb_only = set(bbb_f) - set(big_f)
    big_only = set(big_f) - set(bbb_f)

    def phrase_count(text, phrase):
        return len(re.findall(re.escape(phrase), text, re.IGNORECASE))

    bbb_raw = open(os.path.join(ROOT, "bbb-full.txt")).read()
    big_raw = open(os.path.join(ROOT, "bigelow-full.txt")).read()

    report = {
        "schema": "aeg.burau-pair.alignment",
        "inputs": {
            "positive": "2607.05283v1.pdf",
            "negative": "9904100v2.pdf",
            "positive_sha256": sha256_file(os.path.join(ROOT, "2607.05283v1.pdf")),
            "negative_sha256": sha256_file(os.path.join(ROOT, "9904100v2.pdf")),
            "positive_pages": 26,
            "negative_pages": 8,
            "positive_words": len(bbb_tok),
            "negative_words": len(big_tok),
        },
        "vocabulary": {
            "shared": len(shared),
            "positive_only": len(bbb_only),
            "negative_only": len(big_only),
            "overlap_coefficient": round(len(shared) / min(len(bbb_f), len(big_f)), 4),
            "positive_distinctive": sorted(bbb_only, key=lambda w: -bbb_f[w])[:15],
            "negative_distinctive": sorted(big_only, key=lambda w: -big_f[w])[:15],
        },
        "titles": {
            "positive_title": ("The Burau representation of the braid group is "
                               "faithful for n = 4"),
            "negative_title": "The Burau representation is not faithful for n = 5",
            "relation": ("negation of 'faithful' + parameter 4 -> 5 + "
                         "drop 'of the braid group': the negative title is the "
                         "positive title under 3 edit operations"),
        },
        "key_phrases": {
            "faithful": [phrase_count(bbb_raw, "faithful"),
                         phrase_count(big_raw, "faithful")],
            "not faithful": [phrase_count(bbb_raw, "not faithful"),
                             phrase_count(big_raw, "not faithful")],
            "n = 4": [phrase_count(bbb_raw, "n = 4"),
                      phrase_count(big_raw, "n = 4")],
            "n = 5": [phrase_count(bbb_raw, "n = 5"),
                      phrase_count(big_raw, "n = 5")],
            "kernel": [phrase_count(bbb_raw, "kernel"),
                       phrase_count(big_raw, "kernel")],
            "curve": [phrase_count(bbb_raw, "curve"),
                      phrase_count(big_raw, "curve")],
            "disk": [phrase_count(bbb_raw, "disk"),
                     phrase_count(big_raw, "disk")],
            "point-pushing": [phrase_count(bbb_raw, "point-pushing"),
                              phrase_count(big_raw, "point-pushing")],
            "Brunnian": [phrase_count(bbb_raw, "Brunnian"),
                         phrase_count(big_raw, "Brunnian")],
            "Jones": [phrase_count(bbb_raw, "Jones"),
                      phrase_count(big_raw, "Jones")],
            "Bigelow": [phrase_count(bbb_raw, "Bigelow"),
                        phrase_count(big_raw, "Bigelow")],
            "Birman": [phrase_count(bbb_raw, "Birman"),
                       phrase_count(big_raw, "Birman")],
        },
        "provenance": {
            "positive_authors": ["Vasudha Bharathram", "Joan S. Birman",
                                 "Tara E. Brendle"],
            "negative_authors": ["Stephen Bigelow"],
            "negative_proposed_by": "Joan Birman",
            "negative_seconded_by": ["Shigeyuki Morita", "Dieter Kotschick"],
            "negative_journal": "Geometry & Topology 3 (1999) 397-404",
            "positive_year": 2026,
            "negative_year": 1999,
            "year_gap": 27,
            "bridge_person": "Joan Birman appears in both: proposer of the "
                             "1999 negative paper, co-author of the 2026 "
                             "positive paper",
        },
    }
    out = os.path.join(ROOT, "alignment.json")
    with open(out, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("wrote", out)
    print("overlap:", report["vocabulary"]["overlap_coefficient"])
    print("key phrases (positive, negative):")
    for k, v in report["key_phrases"].items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    sys.exit(main())
