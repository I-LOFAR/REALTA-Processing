#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <path>"
    exit 1
fi

BASE_PATH="$1"

if [[ ! -d "$BASE_PATH" ]]; then
    echo "Error: '$BASE_PATH' is not a directory"
    exit 1
fi

find "$BASE_PATH" -type f -name "*.fil" -print0 | while IFS= read -r -d '' fil; do
    out="${fil}.zst"
    echo "Compressing $fil → $out"

    zstd -T0 "$fil" -o "$out" && rm "$fil"
done

echo "Done: all .fil files under $BASE_PATH compressed and originals removed."
