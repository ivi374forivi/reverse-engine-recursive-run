#!/usr/bin/env bash
#
# gen_sbom.sh
#
# Generates SBOMs (CycloneDX + SPDX) for multiple ecosystems and consolidates them.
# Safe for closed-source environments: outputs only dependency metadata, not source code.
#
# Requirements (install in CI environment):
#   - syft (anchore) OR cyclonedx-cli
#   - pipdeptree (for Python)
#   - npm (for Node)
#   - go (for Go modules)
#   - jq
#
# Usage:
#   ./scripts/gen_sbom.sh --out artifacts/sbom --ref "$(git rev-parse HEAD)"
#   (Run from repo root)
#
set -euo pipefail

OUT_DIR="artifacts/sbom"
REF=""
FORMAT_ALL="true"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out) OUT_DIR="$2"; shift 2;;
    --ref) REF="$2"; shift 2;;
    --no-all) FORMAT_ALL="false"; shift;;
    *) echo "Unknown arg: $1" >&2; exit 1;;
  esac
done

mkdir -p "$OUT_DIR/tmp"

if [[ -z "$REF" ]]; then
  REF="$(git rev-parse HEAD)"
fi

echo "[SBOM] Generating at ref $REF"

timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

# Detect ecosystems
has_node=false
has_python=false
has_go=false
has_java=false
has_rust=false

[[ -f package.json ]] && has_node=true
[[ -f requirements.txt || -f pyproject.toml ]] && has_python=true
[[ -f go.mod ]] && has_go=true
ls *.gradle 2>/dev/null 1>&2 || ls pom.xml 2>/dev/null 1>&2 && has_java=true
[[ -f Cargo.toml ]] && has_rust=true

manifest_summary="$OUT_DIR/manifest_summary.json"
echo '{"ecosystems":[]}' > "$manifest_summary"

append_manifest () {
  jq --arg e "$1" '.ecosystems += [$e]' "$manifest_summary" > "$manifest_summary.tmp" && mv "$manifest_summary.tmp" "$manifest_summary"
}

# Node (CycloneDX)
if $has_node; then
  echo "[SBOM][Node] Installing prod deps (no scripts)..."
  npm ci --ignore-scripts --no-audit --fund=false
  if command -v npx >/dev/null; then
    echo "[SBOM][Node] Generating CycloneDX JSON..."
    npx --yes @cyclonedx/cyclonedx-npm --output-format json --output-file "$OUT_DIR/tmp/node.cdx.json" || echo "[WARN] CycloneDX NPM generation failed"
  fi
  append_manifest "node"
fi

# Python
if $has_python; then
  echo "[SBOM][Python] Building dependency list..."
  PYENV_DIR=".venv-sbom"
  python3 -m venv "$PYENV_DIR"
  source "$PYENV_DIR/bin/activate"
  if [[ -f requirements.txt ]]; then
    pip install -q -r requirements.txt
  elif [[ -f pyproject.toml ]]; then
    pip install -q build pip-tools >/dev/null 2>&1 || true
    pip install -q . >/dev/null 2>&1 || true
  fi
  pip install -q pipdeptree cyclonedx-bom >/dev/null 2>&1 || true
  pipdeptree --json-tree > "$OUT_DIR/tmp/python.dep.json" || true
  cyclonedx-py -o "$OUT_DIR/tmp/python.cdx.json" || true
  deactivate
  append_manifest "python"
fi

# Go
if $has_go; then
  echo "[SBOM][Go] Generating go list..."
  go list -deps -json ./... > "$OUT_DIR/tmp/go.deps.json" 2>/dev/null || true
  if command -v syft >/dev/null; then
     syft dir:. -o cyclonedx-json > "$OUT_DIR/tmp/go.cdx.json" || true
  fi
  append_manifest "go"
fi

# Java (best-effort)
if $has_java; then
  echo "[SBOM][Java] Attempting mvn dependency:tree (if Maven)..."
  if [[ -f pom.xml ]]; then
    mvn -q dependency:tree -DoutputFile="$OUT_DIR/tmp/maven.tree.txt" || true
  fi
  append_manifest "java"
fi

# Rust
if $has_rust; then
  echo "[SBOM][Rust] cargo metadata..."
  cargo metadata --format-version 1 > "$OUT_DIR/tmp/rust.metadata.json" 2>/dev/null || true
  if command -v syft >/dev/null; then
     syft dir:. -o cyclonedx-json > "$OUT_DIR/tmp/rust.cdx.json" || true
  fi
  append_manifest "rust"
fi

# Consolidation (naive merge of CycloneDX components if present)
combined="$OUT_DIR/sbom_combined.cyclonedx.json"
if ls "$OUT_DIR"/tmp/*.cdx.json >/dev/null 2>&1; then
  echo "[SBOM] Combining CycloneDX component lists..."
  # Simple merge: accumulate components arrays uniquely by name+version
  jq -s '
    reduce .[] as $doc (
      {bomFormat:"CycloneDX", specVersion:"1.5", serialNumber:"urn:uuid:'"$(uuidgen 2>/dev/null || echo temp-uuid)"'", version:1, components:[]};
      .components += ($doc.components // [])
    )
    | (.components |= (unique_by(.name + ":" + (.version // ""))))
    | .metadata |= {timestamp:"'"$timestamp"'", tools:[{name:"gen_sbom.sh"}], properties:[{name:"git.ref","value":"'"$REF"'"}]}
  ' "$OUT_DIR"/tmp/*.cdx.json > "$combined" 2>/dev/null || echo '{}' > "$combined"
else
  echo "[WARN] No CycloneDX fragments found; combined file minimal."
  echo '{}' > "$combined"
fi

# SPDX (if syft available)
if command -v syft >/dev/null; then
  echo "[SBOM] Generating SPDX JSON (syft)..."
  syft dir:. -o spdx-json > "$OUT_DIR/sbom.spdx.json" || echo '{}' > "$OUT_DIR/sbom.spdx.json"
fi

cp "$manifest_summary" "$OUT_DIR/manifest_summary.$REF.json"

echo "[SBOM] Done. Outputs in $OUT_DIR
- Combined CycloneDX: $combined
- SPDX (if generated): $OUT_DIR/sbom.spdx.json
- Manifest summary: $OUT_DIR/manifest_summary.$REF.json"
