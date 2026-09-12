#!/bin/bash
# Bounded DualMachine v0 run (adva research 0167, substrate-side only).
#
#   ./run-dual.sh <output.jsonl>
#
# Compiles the DualMachine sources into a temporary directory and runs the
# suite: the recorded iota-lang cases, the space frame, mixed nesting, and the
# refusal of the angle form. Refuses to overwrite an existing output path.
set -u

if [ "$#" -ne 1 ]; then
  echo "usage: run-dual.sh <output.jsonl>" >&2
  exit 2
fi

OUT="$1"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -e "$OUT" ]; then
  echo "refusing to overwrite: $OUT" >&2
  exit 2
fi

WORK="$(mktemp -d)"

{
  echo "# DualMachine v0 run"
  echo "# date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "# spec: DUALMACHINE.md"
  echo "# spec_sha256: $(shasum -a 256 "$HERE/DUALMACHINE.md" | cut -d' ' -f1)"
  echo "# java: $(java -version 2>&1 | head -1)"
  echo "# javac: $(javac -version 2>&1 | head -1)"
} > "$OUT"

mkdir -p "$WORK/classes"
javac --release 17 -proc:none -Xlint:none -d "$WORK/classes" \
  $(find "$HERE/java2" -name '*.java') >> "$OUT" 2>&1
JAVAC_STATUS=$?
echo "# javac_exit: $JAVAC_STATUS" >> "$OUT"
if [ "$JAVAC_STATUS" -ne 0 ]; then
  echo "# run aborted: compile failed" >> "$OUT"
  exit 1
fi

java -cp "$WORK/classes" iota.dual.TestDriver >> "$OUT" 2>&1
echo "# driver_exit: $?" >> "$OUT"
