#!/bin/sh
# 双二进制解释关系试验：用法  ./aeg-binary-relation.sh /path/P /path/Q
# 全程有界、只读源文件；错误与孔洞全部保留（stderr/Unknown/Rejected 即下一轮能量）。
set -u
P="$1"; Q="$2"
OUT="$(dirname "$0")"
D="$OUT/evidence-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$D/binaries"
cp "$P" "$D/binaries/P.bin" 2>>"$D/errors.log" || echo "copy P failed" >>"$D/errors.log"
cp "$Q" "$D/binaries/Q.bin" 2>>"$D/errors.log" || echo "copy Q failed" >>"$D/errors.log"

echo "== stage 0: pin =="
{ echo "P=$P"; echo "Q=$Q"; ls -l "$P" "$Q"; } > "$D/pins.txt" 2>>"$D/errors.log"
shasum -a 256 "$P" "$Q" >> "$D/pins.txt" 2>>"$D/errors.log"
file "$P" "$Q" > "$D/file-types.txt" 2>>"$D/errors.log"

echo "== stage 1: structure =="
otool -hv "$P" "$Q" > "$D/otool-headers.txt" 2>>"$D/errors.log"
otool -l "$P" "$Q" > "$D/otool-load.txt" 2>>"$D/errors.log"
nm -m "$P" "$Q" > "$D/symbols.txt" 2>>"$D/errors.log" || echo "nm failed (stripped?) -> hole" >>"$D/errors.log"

echo "== stage 2: vocabulary =="
strings "$P" | sort -u > "$D/strings-P.txt" 2>>"$D/errors.log"
strings "$Q" | sort -u > "$D/strings-Q.txt" 2>>"$D/errors.log"
comm -12 "$D/strings-P.txt" "$D/strings-Q.txt" > "$D/strings-common.txt"
{ echo "P unique: $(wc -l < "$D/strings-P.txt")"; echo "Q unique: $(wc -l < "$D/strings-Q.txt")";
  echo "common: $(wc -l < "$D/strings-common.txt")"; } > "$D/vocabulary-summary.txt"

echo "== stage 3: byte relation =="
python3 "$OUT/chunk-hash.py" "$P" "$Q" > "$D/chunks.json" 2>>"$D/errors.log"

echo "== stage 4: hypotheses =="
python3 "$OUT/hypotheses.py" "$D" > "$D/hypotheses.json" 2>>"$D/errors.log"

echo "== stage 5: receipt =="
python3 "$OUT/write-receipt.py" "$D" > "$D/receipt-08.json" 2>>"$D/errors.log"
echo "done -> $D"
echo "holes/errors:"; cat "$D/errors.log" 2>/dev/null | head -20
