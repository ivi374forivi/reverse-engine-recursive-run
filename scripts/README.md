# Scripts Toolkit

This directory contains automation utilities supporting reverse engineering and ongoing architecture governance for a closed-source monorepo or multi-service environment.

## Overview

| Script | Purpose | Key Output |
|--------|---------|------------|
| gen_sbom.sh | Generate CycloneDX/SPDX SBOMs across ecosystems | sbom_combined.cyclonedx.json |
| scan_drift.py | Compare dependency / service graphs for drift | drift_report.json |
| hotspot_merge.py | Merge churn + complexity + coverage + criticality into ranked hotspots | hotspots.json |
| ownership_diff.py | Detect knowledge concentration per directory | ownership.json |
| risk_update.py | Aggregate multiple analyses into consolidated risk register | consolidated_risk.json |
| parse_trivy.py | Normalize Trivy security findings | security_findings.json |
| parse_semgrep.py | Normalize Semgrep security findings | security_findings.json |
| adr_new.sh | Create new Architecture Decision Record | docs/adr/NNNN-title.md |

## Suggested CI Pipeline Steps

```
flowchart LR
  A[Checkout] --> B[gen_sbom.sh]
  B --> C[Complexity & Churn Jobs]
  C --> D[hotspot_merge.py]
  D --> E[scan_drift.py]
  E --> F[ownership_diff.py]
  F --> G[risk_update.py]
  G --> H[Publish Artifacts + Dashboard]
```

## Example Usage

### Generate SBOM
```bash
./scripts/gen_sbom.sh --out artifacts/sbom --ref $(git rev-parse HEAD)
```

### Analyze Hotspots
```bash
radon cc -j -s src/ > artifacts/complexity.json
git log --since=90.days --name-only --pretty=format: | sort | grep -v '^$' | uniq -c > artifacts/churn.txt
python3 scripts/hotspot_merge.py \
  --churn artifacts/churn.txt \
  --complexity artifacts/complexity.json \
  --out artifacts/hotspots.json
```

### Detect Drift
```bash
python3 scripts/scan_drift.py \
  --current artifacts/current_graph.json \
  --previous artifacts/previous_graph.json \
  --out artifacts/drift_report.json
```

### Analyze Ownership
```bash
python3 scripts/ownership_diff.py --out artifacts/ownership.json
```

### Aggregate Risks
```bash
python3 scripts/risk_update.py \
  --hotspots artifacts/hotspots.json \
  --drift artifacts/drift_report.json \
  --ownership artifacts/ownership.json \
  --out artifacts/consolidated_risk.json
```

## Security & Privacy Notes

- Never commit raw proprietary code into SBOM outputs—SBOMs should only list dependency coordinates
- Redact or classify artifacts with a footer: `Generated from commit <sha> at <timestamp> Classification: Internal`
- If using LLM summarization, feed only structural metadata (file paths, complexity metrics), not full file contents, unless approved

## Script Details

### gen_sbom.sh
Detects ecosystems automatically and generates CycloneDX/SPDX SBOMs:
- Node.js (package.json)
- Python (requirements.txt, pyproject.toml)
- Go (go.mod)
- Java (pom.xml, *.gradle)
- Rust (Cargo.toml)

**Requirements**: syft, npm, pip, go, jq

### scan_drift.py
Compares two dependency graph snapshots and detects:
- Added/removed nodes
- Added/removed edges
- Churn ratio
- Boundary violations (new edges into previously isolated nodes)

**Exit codes**:
- 0: Below threshold
- 2: Drift threshold exceeded

### hotspot_merge.py
Combines multiple risk dimensions:
- Churn (git activity)
- Complexity (cyclomatic complexity)
- Coverage gap (1 - test coverage)
- Criticality (business impact weight)

**Configuration**: Environment variables `RISK_W_*` or config/risk_weights.yaml

### ownership_diff.py
Analyzes git commit authorship per directory:
- Top contributor percentage
- Flags HIGH_CONCENTRATION (>60%) or SINGLE_CONTRIBUTOR
- Optional criticality weighting

### risk_update.py
Aggregates risk sources into consolidated register:
- Hotspots (code-level risks)
- Drift (architecture changes)
- Ownership (knowledge concentration)
- Security (vulnerabilities)

**Severity heuristics**:
- Hotspot score ≥0.75 → HIGH
- Security CRITICAL/HIGH → HIGH
- Single contributor + criticality ≥3 → HIGH

### parse_trivy.py
Normalizes Trivy scanner output:
- Extracts CVE, severity, package, versions
- Generates actionable recommendations
- Outputs JSON array compatible with risk_update.py

### parse_semgrep.py
Normalizes Semgrep scanner output:
- Maps ERROR→HIGH, WARNING→MEDIUM, INFO→LOW
- Includes line numbers and rule IDs
- Outputs JSON array compatible with risk_update.py

### adr_new.sh
Creates new ADR from template:
- Auto-increments number (0001, 0002, ...)
- Populates date and title
- Updates ADR index automatically

## Extending

- Add coverage ingestion: produce `coverage.json` with `{ "files": { "path": fraction } }`
- Add custom risk weighting via environment variables for `hotspot_merge.py`
- Create custom parsers for other security tools following the pattern

## Local Repro

```bash
# Install dependencies
pip install radon pipdeptree pyyaml

# Run analysis
./scripts/gen_sbom.sh --out artifacts/sbom --ref $(git rev-parse HEAD)
python3 scripts/hotspot_merge.py --churn artifacts/churn.txt --complexity artifacts/complexity.json --out artifacts/hotspots.json
```

## Next Steps

- Integrate dashboards (e.g., Backstage plugin) to surface top hotspots and drift deltas
- Schedule nightly drift detection with alerting (Slack webhook on exit code 2)
- Set up time-series tracking for trend analysis
