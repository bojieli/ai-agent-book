#!/usr/bin/env bash
# Assemble the MkDocs docs directory (`_web/`) from the book Markdown sources.
# Only Markdown + images are copied; code, PDFs and LaTeX sources are left out
# so the generated site stays small. The original sources are never modified.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/_web"

rm -rf "$DEST"
mkdir -p "$DEST"

# Site homepage (root index.md).
cp "$ROOT/index.md" "$DEST/index.md"

# The four language editions, each with its images/ subfolder.
for lang in book book-en book-ta book-vi; do
  mkdir -p "$DEST/$lang"
  cp -R "$ROOT/$lang" "$DEST/"
done

# Keep only Markdown and images; drop .tex/.py/.lua/.pdf/.sh etc.
find "$DEST" -type f \
  ! -name '*.md' \
  ! -name '*.svg' \
  ! -name '*.png' \
  ! -name '*.jpg' \
  ! -name '*.jpeg' \
  -delete

echo "Assembled docs into $DEST"
