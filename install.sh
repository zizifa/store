#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-.}"

mkdir -p "$TARGET/.clinerules" "$TARGET/docs/cline"
cp "$ROOT/.clineignore" "$TARGET/.clineignore"
cp "$ROOT/.clinerules/"*.md "$TARGET/.clinerules/"
cp "$ROOT/docs/cline/"*.md "$TARGET/docs/cline/"
cp "$ROOT/README.md" "$TARGET/README-cline-config.md"

echo "Cline configuration installed into: $TARGET"
echo "Review git diff, then commit the configuration."
