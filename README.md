# Reverse Engineering & Architecture Governance Toolkit

A comprehensive framework for reverse engineering closed-source codebases and implementing continuous architecture governance. This toolkit enables teams to:

- **Map architecture** (code + processes) for proprietary repositories
- **Quantify risk** via churn, complexity, coverage gaps, criticality, and security analysis
- **Detect architecture drift** through dependency graph analysis
- **Identify knowledge concentration** risks across teams
- **Generate SBOMs** and integrate security findings
- **Produce consolidated risk registers** for governance
- **Feed metrics to Backstage** and CI/CD governance loops
- **Enable safe AI summarization** of codebases
- **Provide remediation backlogs** with weighted risk formulas
- **Support compliance & IP awareness**

## Quick Start

### Prerequisites

```bash
# Install required tools
pip install radon pipdeptree cyclonedx-bom pyyaml
npm install -g @cyclonedx/cyclonedx-npm
```

### Basic Usage

```bash
# 1. Generate SBOM
./scripts/gen_sbom.sh --out artifacts/sbom --ref "$(git rev-parse HEAD)"

# 2. Analyze code complexity and churn
radon cc -j -s src/ > artifacts/complexity.json
git log --since=90.days --name-only --pretty=format: | sort | grep -v '^$' | uniq -c > artifacts/churn.txt

# 3. Merge into hotspot analysis
python scripts/hotspot_merge.py \
  --churn artifacts/churn.txt \
  --complexity artifacts/complexity.json \
  --out artifacts/hotspots.json
```

## Core Components

### Scripts (`scripts/`)

| Script | Purpose |
|--------|---------|
| `gen_sbom.sh` | Generate CycloneDX/SPDX SBOMs across ecosystems |
| `scan_drift.py` | Compare dependency graphs to detect architecture drift |
| `hotspot_merge.py` | Merge churn + complexity + coverage into risk scores |
| `ownership_diff.py` | Detect knowledge concentration per directory |
| `risk_update.py` | Aggregate analyses into consolidated risk register |
| `parse_trivy.py` | Normalize Trivy security findings |
| `parse_semgrep.py` | Normalize Semgrep security findings |

### Templates (`templates/`)

- Executive summary template
- Remediation backlog scaffold (YAML)
- AI-safe summarization prompt templates

### Backstage Plugin (`backstage/plugins/architecture-risk/`)

React components for visualizing:
- Risk overview widgets
- Hotspot tables
- Knowledge concentration gauges
- Dependency graph visualization

### Backend Service (`server/`)

Node/Express API serving:
- Service metrics
- Hotspot data
- Dependency graphs
- Cycle detection
- Time-series data

## Architecture

### Risk Scoring Model

Risk is calculated using multiple dimensions:

- **Churn** (40%): Code volatility over 90 days
- **Complexity** (40%): Cyclomatic complexity metrics  
- **Coverage Gap** (10%): Missing test coverage
- **Criticality** (10%): Business impact weighting

Formula:
```
risk = (normalized_churn * 0.4) + (normalized_complexity * 0.4) + 
       (coverage_penalty * 0.1) + (criticality_factor * 0.1)
```

### Drift Detection

Tracks changes in dependency graphs:
- Added/removed nodes (modules, services)
- Added/removed edges (dependencies)
- Edge churn ratio
- Core boundary violations

### Knowledge Concentration

Identifies single points of failure:
- Top contributor percentage per module
- Single contributor warnings
- Criticality-weighted risk

## Advanced Features

### Diff-Aware Risk

Focus on changed files in PRs:
```bash
scripts/diff_changed_files.sh origin/main HEAD > artifacts/changed_files.txt
python scripts/diff_risk.py --hotspots artifacts/hotspots.json \
  --changed artifacts/changed_files.txt --out artifacts/diff_hotspots.json
```

### Time-Series Persistence

Track metrics over time:
```bash
python scripts/record_timeseries.py \
  --services config/service_paths.yaml \
  --out-dir artifacts/timeseries
```

### ADR Enforcement

Ensure architectural decisions are documented:
```bash
python scripts/adr_enforce_boundary.py \
  --drift artifacts/drift_report.json \
  --adr-index docs/adr/0000-record-architecture-decisions.md \
  --config config/adr_enforcement.yaml
```

### Cycle Detection

Find circular dependencies:
```bash
curl http://localhost:8085/api/graph-cycles | jq '.'
```

## CI/CD Integration

See `.github/workflows/arch-governance.yml` for complete pipeline example.

Key steps:
1. Build & test (generate coverage)
2. Static analysis (complexity, churn)
3. SBOM generation
4. Security scanning
5. Hotspot analysis
6. Drift detection
7. Risk aggregation
8. Artifact publishing

## Documentation

- `docs/summary_compiled.md` - Complete system overview
- `docs/diff-aware-risk.md` - Focusing on PR changes
- `docs/time-series-metrics.md` - Historical tracking
- `docs/adr-enforcement.md` - Decision record enforcement
- `docs/graph-cycles.md` - Circular dependency detection
- `docs/security-ingestion.md` - Security tool integration

## Configuration

### Service Path Mapping (`config/service_paths.yaml`)

```yaml
services:
  payments-service:
    paths:
      - "src/payments/"
      - "src/core/payment"
```

### Risk Weights (`config/risk_weights.yaml`)

```yaml
weights:
  churn: 0.30
  complexity: 0.35
  coverage_gap: 0.15
  criticality: 0.10
  security_hotspot: 0.10
```

## Security & Privacy

- No raw source code in SBOM outputs
- Classify artifacts as Internal/Confidential
- Sanitize AI prompts (no secrets, structural metadata only)
- Redact sensitive data before distribution

## License

Internal use - see organization policies.

## Contributing

This toolkit was created through an AI-assisted design process to provide comprehensive architecture governance capabilities. Contributions should follow established patterns and maintain security/privacy standards.