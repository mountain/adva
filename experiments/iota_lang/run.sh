#!/bin/bash
# Bounded iota-lang reconnection run (adva research 0167).
#
# Compiles the reconnected machine and replays the seventeen recorded cases of
# iota-lang src/tests/java/iota/SKITest.java.
#
#   ./run.sh <iota-lang-checkout> <output.jsonl>
#
# Refuses to overwrite an existing output path. All classes go to a temporary
# directory; nothing is written into the iota-lang checkout.
set -u

if [ "$#" -ne 2 ]; then
  echo "usage: run.sh <iota-lang-checkout> <output.jsonl>" >&2
  exit 2
fi

SRC="$1"
OUT="$2"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -d "$SRC" ]; then
  echo "no such checkout: $SRC" >&2
  exit 2
fi
if [ -e "$OUT" ]; then
  echo "refusing to overwrite: $OUT" >&2
  exit 2
fi

WORK="$(mktemp -d)"
echo "# work dir: $WORK"

{
  echo "# iota-lang reconnection run"
  echo "# date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "# checkout: $SRC"
  echo "# head: $(git -C "$SRC" rev-parse HEAD 2>/dev/null || echo unknown)"
  echo "# head_subject: $(git -C "$SRC" log -1 --pretty=%s 2>/dev/null || echo unknown)"
  echo "# dirty: $(git -C "$SRC" status --porcelain 2>/dev/null | wc -l | tr -d ' ') modified paths"
  echo "# ski_test_sha256: $(shasum -a 256 "$SRC/src/tests/java/iota/SKITest.java" 2>/dev/null | cut -d' ' -f1)"
  echo "# at_test_count: $(grep -c '@Test' "$SRC/src/tests/java/iota/SKITest.java" 2>/dev/null)"
  echo "# java: $(java -version 2>&1 | head -1)"
  echo "# javac: $(javac -version 2>&1 | head -1)"
} > "$OUT"

mkdir -p "$WORK/classes"

echo "# compile:" >> "$OUT"
javac --release 17 -proc:none -Xlint:none -d "$WORK/classes" \
  $(find "$HERE/java" -name '*.java') >> "$OUT" 2>&1
JAVAC_STATUS=$?
echo "# javac_exit: $JAVAC_STATUS" >> "$OUT"

if [ "$JAVAC_STATUS" -ne 0 ]; then
  echo "# run aborted: compile failed" >> "$OUT"
  exit 1
fi

java -cp "$WORK/classes" iota.ReplayDriver >> "$OUT" 2>&1
echo "# driver_exit: $?" >> "$OUT"
