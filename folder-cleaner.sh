#!/bin/bash

ROOT_DIR="${1:-.}"

echo "Removing empty directories under: $ROOT_DIR"
echo "-------------------------------------------"

find "$ROOT_DIR" -type d -empty -print -delete