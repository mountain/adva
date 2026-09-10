"""Explicit successor-contract entry for the scalar checker merged in #179."""
import hashlib
import json
from pathlib import Path

import replay

HERE = Path(__file__).resolve().parent


def main():
    successor = HERE/'main-contract-v1.json'
    contract = json.loads(successor.read_text())
    predecessor = HERE/'contract.json'
    if contract.get('version') != 1 or contract['supersedes']['path'] != str(predecessor.relative_to(replay.ROOT)):
        raise SystemExit('invalid successor contract')
    if hashlib.sha256(predecessor.read_bytes()).hexdigest() != contract['supersedes']['sha256']:
        raise SystemExit('historical contract changed')
    # Reuse the original checker under an explicitly selected successor contract.
    # The old entry and its original contract/evidence remain byte-identical.
    replay.CONTRACT = successor
    return replay.main()


if __name__ == '__main__':
    raise SystemExit(main())
