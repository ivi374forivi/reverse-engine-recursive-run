#!/usr/bin/env bash
# adr_new.sh
# Create a new ADR from template with incremental numbering.
# Usage: ./scripts/adr_new.sh "Decision Title"
set -euo pipefail
TITLE="${1:-}"
if [[ -z "$TITLE" ]]; then
  echo "Usage: $0 \"Decision Title\"" >&2
  exit 1
fi
ADR_DIR="docs/adr"
TEMPLATE="$ADR_DIR/ADR_TEMPLATE.md"
mkdir -p "$ADR_DIR"
# Determine next number
NEXT_NUM=$(printf "%04d" $( (ls "$ADR_DIR" 2>/dev/null | grep -E '^[0-9]{4}-' | sed 's/-.*//' | sort -n | tail -1; echo 0000) | tail -1 | awk '{print $1+1}') )
FILENAME="$ADR_DIR/${NEXT_NUM}-$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9\-').md"
DATE=$(date -u +"%Y-%m-%d")
if [[ ! -f "$TEMPLATE" ]]; then
  echo "Template missing at $TEMPLATE" >&2
  exit 1
fi
sed -e "s/{{NUMBER}}/$NEXT_NUM/g" \
    -e "s/{{DATE}}/$DATE/g" \
    -e "s/{{TITLE}}/$TITLE/g" \
    "$TEMPLATE" > "$FILENAME"
echo "Created ADR: $FILENAME"
# Update index
if command -v python3 >/dev/null && [[ -f scripts/adr_index.py ]]; then
  python3 scripts/adr_index.py --dir "$ADR_DIR" --out "$ADR_DIR/0000-record-architecture-decisions.md" || true
fi
