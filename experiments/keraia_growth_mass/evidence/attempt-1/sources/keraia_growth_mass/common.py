"""Pinned external interpreter imports and reproducible source accounting."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
CYCLES = EXPERIMENTS / "keraia_cycle_mass"
MACHINE = EXPERIMENTS / "keraia_read_machine"
sys.path.insert(0, str(CYCLES))
sys.path.insert(0, str(MACHINE))

import cycles as C
import machine as M
import oracle as O
from syntax import Budget, Limit, I, R
from support import GROW, LOOP, IDENTITY, K, READ_ALIAS, app


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sources():
    paths = sorted(HERE.glob("*.py")) + sorted(HERE.glob("*.json"))
    paths += [CYCLES / name for name in ("cycles.py", "support.py")]
    paths += [MACHINE / name for name in ("machine.py", "syntax.py", "oracle.py")]
    return {str(path.relative_to(EXPERIMENTS)): path for path in paths}


def manifest():
    return {name: hashlib.sha256(path.read_bytes()).hexdigest()
            for name, path in sources().items()}
