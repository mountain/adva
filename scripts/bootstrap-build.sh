#!/usr/bin/env bash
# Linux bootstrap packaging; existing Rust semantics and Cargo.lock are retained.
set -euo pipefail
if [[ $# != 1 ]]; then
  echo 'usage: bash scripts/bootstrap-build.sh NEW-OUTPUT-DIRECTORY' >&2
  exit 2
fi
adva_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
adva_output=$1
adva_toolchain=1.94.0
for adva_command in cargo rustc sha256sum timeout; do
  command -v "$adva_command" >/dev/null || { echo "missing prerequisite: $adva_command" >&2; exit 2; }
done
cd -- "$adva_root"
sha256sum --check bootstrap/inputs.sha256
# Fresh directory and target: no reuse of a previous build or report.
mkdir -- "$adva_output"
adva_output=$(cd -- "$adva_output" && pwd)
mkdir -- "$adva_output/bin" "$adva_output/library" "$adva_output/reports" "$adva_output/programs"
cp -R adva-library/stability "$adva_output/library/stability"
cp programs/native-run/arithmetic.adva "$adva_output/programs/arithmetic.adva"
cp bootstrap/inputs.sha256 "$adva_output/source-inputs.sha256"
{
  echo 'profile=adva-bootstrap-linux-v0'
  echo 'source_base=1037b433851392a1a9cb0f0e954757a300d6df8b (plus files pinned in source-inputs.sha256)'
  echo 'library_commit=7496a5c893fadf5d72fd29cf7ad5a63f42586b4b'
  echo "toolchain=$adva_toolchain"
  rustc +"$adva_toolchain" --version --verbose
  cargo +"$adva_toolchain" --version
  uname -srm
} > "$adva_output/build-context.txt"
# Cargo downloads the locked dependencies if not already available. Offline
# distribution additionally needs cargo vendor plus an approved source config.
timeout --kill-after=10s 600s cargo +"$adva_toolchain" build --locked --release \
  -p adva-witness --bin adva --target-dir "$adva_output/build-target" \
  > "$adva_output/build.stdout" 2> "$adva_output/build.stderr"
cp "$adva_output/build-target/release/adva" "$adva_output/bin/adva"
# Work outside the source directory: the runtime uses explicit resource paths.
cd -- "$adva_output"
timeout --kill-after=5s 30s bin/adva run programs/arithmetic.adva --output reports/arithmetic.adva
timeout --kill-after=5s 30s bin/adva library check --path library --epoch 1 --output reports/check.json
timeout --kill-after=5s 30s bin/adva library reuse --path library --epoch 1 --word 0 --input 2 --output reports/reuse.json
# Failure is expected; retain its exact exit code and structured report. The
# separate acceptance checker must confirm that the cause is the zero guard.
set +e
timeout --kill-after=5s 30s bin/adva library reuse --path library --epoch 1 --word 0 --input 0 --output reports/zero.json > reports/zero.stdout 2> reports/zero.stderr
adva_zero_exit=$?
set -e
echo "$adva_zero_exit" > reports/zero.exit
if [[ "$adva_zero_exit" != 2 || ! -f reports/zero.json ]]; then
  echo 'zero control did not produce a bounded rejection report' >&2
  exit 2
fi
sha256sum bin/adva library/stability/epoch-0000.json library/stability/epoch-0001.json programs/arithmetic.adva reports/arithmetic.adva reports/check.json reports/reuse.json reports/zero.json > bundle.sha256
echo 'Build and command invocations finished. Validate the report contents with:'
echo "python3 $adva_root/scripts/check_bootstrap.py $adva_output"
