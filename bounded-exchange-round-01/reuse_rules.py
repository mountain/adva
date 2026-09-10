#!/usr/bin/env python3
"""Frozen rule module for bounded exchange round 04.

The same content-token rule used in replies 02 and 03, now pinned by the
SHA-256 of these exact bytes. No arguments, no side effects.
"""
import re

STOP = set("""a an the and or but if then else for of to in on at by with from as is are was were be been being
am do does did done have has had having will would shall should can could may might must not no nor
this that these those it its i you your he she they them we us our his her their there here what which who whom
when where why how all any each every some such more most much many few other own same so than too very just
also only into upon per via about above after again against between below under over before during while until
because although though since once""".split())

TOKEN = re.compile(r"[A-Za-z][A-Za-z'-]*|[0-9]+")
TARGET = "use"
MAX_CONTEXT_WORDS = 25
MIN_SIDE_TOKENS = 2


def content_tokens(text):
    return [t.lower() for t in TOKEN.findall(text)
            if t.lower() not in STOP and not t.isdigit()]


def build_freq_rank(tokens):
    """Return (freq_of_target, rank_of_target, freq_dict, rank_order)."""
    d = {}
    for t in tokens:
        d[t] = d.get(t, 0) + 1
    order = sorted(d, key=lambda w: -d[w])  # stable: first-occurrence ties
    rank = {w: i + 1 for i, w in enumerate(order)}
    return d.get(TARGET, 0), rank.get(TARGET), d, order


def filtered_lines(text):
    """The reply-03 construction: stripped, non-empty lines; locators are
    1-based indexes into this filtered array (not raw file line numbers)."""
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


def context_from_lines(lines, target=TARGET, max_words=MAX_CONTEXT_WORDS,
                       min_side=MIN_SIDE_TOKENS):
    """Shortest span with >= min_side tokens on each side, <= max_words.
    Input is the filtered line array. Ties keep scan order (first line wins).
    Returns (locator, span_text) with locator = 1-based filtered index."""
    candidates = []
    for lineno, ln in enumerate(lines, 1):
        toks = TOKEN.findall(ln)
        for i, t in enumerate(toks):
            if t.lower() == target and i >= min_side and len(toks) - 1 - i >= min_side:
                lo = max(0, i - (max_words - 1) // 2)
                hi = min(len(toks), lo + max_words)
                span = " ".join(toks[lo:hi])
                candidates.append((len(toks[lo:hi]), lineno, span))
    if not candidates:
        return None, None
    candidates.sort(key=lambda c: c[0])  # stable: earliest line wins ties
    return candidates[0][1], candidates[0][2]
