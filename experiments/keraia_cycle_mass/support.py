import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
DEPENDENCY = PARENT / "keraia_read_machine"
sys.path.insert(0, str(DEPENDENCY))


def sources():
    files = sorted(HERE.glob("*.py")) + sorted(HERE.glob("*.json"))
    files += [DEPENDENCY / name for name in ("syntax.py", "machine.py", "oracle.py")]
    return {str(p.relative_to(PARENT)): p for p in files}


def manifest():
    return {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in sources().items()}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def words(n):
    for size in range(n + 1):
        for value in range(2**size):
            yield format(value, "0" + str(size) + "b") if size else ""


def app(a, b):
    return "1" + a + b


IDENTITY = "11000"
K = "11010100110010100"
LOOP_ABS = "1100100"
LOOP = app(LOOP_ABS, LOOP_ABS)
GROW_ABS = "110011000"
GROW = app(GROW_ABS, GROW_ABS)
READ_ALIAS = app(IDENTITY, "0")
DISCARD_READ = app(app(READ_ALIAS, IDENTITY), IDENTITY)
SELECT_LOOP = app(app(READ_ALIAS, LOOP), IDENTITY)


def sequence(reads, delays):
    result = IDENTITY
    for _ in range(reads):
        result = app(DISCARD_READ, result)
    for _ in range(delays):
        result = app(IDENTITY, result)
    return result
