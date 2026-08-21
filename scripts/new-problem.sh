#!/usr/bin/env bash
# Scaffold problems/<slug>/ from refs/problem-template/.
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "usage: scripts/new-problem.sh <slug>" >&2
  echo "  <slug> is kebab-case, e.g. two-squares-gap" >&2
  exit 1
fi

slug="$1"
case "$slug" in
  "" | -* | *- | *--* | *[!a-z0-9-]*)
    echo "error: slug must be kebab-case (lowercase letters, digits, single hyphens)" >&2
    exit 1
    ;;
esac

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
template="$repo_root/refs/problem-template"
dest="$repo_root/problems/$slug"

if [ ! -d "$template" ]; then
  echo "error: template not found at $template" >&2
  exit 1
fi
if [ -e "$dest" ]; then
  echo "error: problems/$slug already exists" >&2
  exit 1
fi

cp -R "$template" "$dest"

# Fill {{slug}} and {{date}} placeholders (portable: no sed -i).
today="$(date +%F)"
find "$dest" -type f -name '*.md' | while IFS= read -r f; do
  sed "s/{{slug}}/$slug/g; s/{{date}}/$today/g" "$f" > "$f.tmp"
  mv "$f.tmp" "$f"
done

echo "Created problems/$slug/"
echo
echo "Next (from AGENTS.md):"
echo "  1. Fill problems/$slug/PROBLEM.md — statement, published record, what would count as a dent."
echo "  2. Add a row to the README Problems table."
echo "  3. When you run a model on it, add a row to the README \"Which model ran what\" table."
