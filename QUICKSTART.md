# Quick Start Guide

This guide will help you get started with the Architecture Governance Toolkit in under 10 minutes.

## Prerequisites

### Required Tools
```bash
# Python 3.8+
python3 --version

# Git
git --version

# Install Python analysis tools
pip install radon pipdeptree pyyaml
```

### Optional Tools (for advanced features)
```bash
# Node.js (for JavaScript projects)
npm --version

# Docker (for containerized execution)
docker --version

# Security scanners
# Trivy: https://github.com/aquasecurity/trivy
# Semgrep: pip install semgrep
```

## Step 1: Set Up Your Environment

```bash
# Clone the repository (if not already done)
git clone https://github.com/ivi374forivi/reverse-engine-recursive-run.git
cd reverse-engine-recursive-run

# Create artifacts directory
mkdir -p artifacts/sbom artifacts/timeseries

# Make scripts executable
chmod +x scripts/*.sh
```

## Step 2: Configure Service Paths (Optional)

Edit `config/service_paths.yaml` to map services to their code paths:

```yaml
services:
  my-service:
    paths:
      - "src/myservice/"
```

## Step 3: Run Basic Analysis

### Option A: Using Make (Recommended)

```bash
# Run full analysis pipeline
make full-analysis

# Or run individual steps:
make hotspots      # Analyze code complexity and churn
make ownership     # Detect knowledge concentration
make drift         # Detect architecture drift
make risk          # Generate consolidated risk report
```

### Option B: Manual Execution

```bash
# 1. Analyze code complexity
radon cc -j -s src/ > artifacts/complexity.json || echo '{}' > artifacts/complexity.json

# 2. Analyze churn (last 90 days)
git log --since=90.days --name-only --pretty=format: | \
  sort | grep -v '^$' | uniq -c > artifacts/churn.txt

# 3. Merge into hotspot analysis
python3 scripts/hotspot_merge.py \
  --churn artifacts/churn.txt \
  --complexity artifacts/complexity.json \
  --out artifacts/hotspots.json

# 4. Analyze ownership concentration
python3 scripts/ownership_diff.py --out artifacts/ownership.json

# 5. Detect architecture drift
echo '{"nodes":[],"edges":[],"meta":{"ref":"'$(git rev-parse HEAD)'"}}' > artifacts/current_graph.json
cp artifacts/current_graph.json artifacts/previous_graph.json  # First run
python3 scripts/scan_drift.py \
  --current artifacts/current_graph.json \
  --previous artifacts/previous_graph.json \
  --out artifacts/drift_report.json

# 6. Generate consolidated risk report
python3 scripts/risk_update.py \
  --hotspots artifacts/hotspots.json \
  --ownership artifacts/ownership.json \
  --drift artifacts/drift_report.json \
  --out artifacts/consolidated_risk.json
```

## Step 4: Review Results

### Hotspots Report
```bash
# View top risky files
python3 -c "import json; d=json.load(open('artifacts/hotspots.json')); \
  print('Top 10 Hotspots:'); \
  [print(f\"{h['file']}: {h['risk_score']:.3f}\") for h in d['hotspots'][:10]]"
```

### Ownership Report
```bash
# View knowledge concentration
python3 -c "import json; d=json.load(open('artifacts/ownership.json')); \
  print('Knowledge Concentration Issues:'); \
  [print(f\"{r['path']}: {r['top_concentration']:.1%} - {r.get('flag','OK')}\") \
   for r in d['directories'][:10] if r.get('flag')]"
```

### Consolidated Risk
```bash
# View all risks
cat artifacts/consolidated_risk.json | jq '.derived_risks[] | {id, type, severity, component}'
```

## Step 5: Generate SBOM (Optional)

```bash
# Generate Software Bill of Materials
./scripts/gen_sbom.sh --out artifacts/sbom --ref "$(git rev-parse HEAD)"

# View results
ls -lh artifacts/sbom/
```

## Step 6: Security Scanning (Optional)

### With Trivy
```bash
# Scan for vulnerabilities
trivy fs --format json . > artifacts/trivy_raw.json

# Normalize findings
python3 scripts/parse_trivy.py \
  --input artifacts/trivy_raw.json \
  --out artifacts/security_findings.json

# Re-run risk aggregation with security
python3 scripts/risk_update.py \
  --hotspots artifacts/hotspots.json \
  --ownership artifacts/ownership.json \
  --drift artifacts/drift_report.json \
  --security artifacts/security_findings.json \
  --out artifacts/consolidated_risk.json
```

### With Semgrep
```bash
# Run Semgrep security scan
semgrep --config p/security-audit --json --output artifacts/semgrep_raw.json

# Normalize findings
python3 scripts/parse_semgrep.py \
  --input artifacts/semgrep_raw.json \
  --out artifacts/security_semgrep.json
```

## Step 7: Create an ADR (Optional)

```bash
# Create a new Architecture Decision Record
./scripts/adr_new.sh "Adopt Microservices Architecture"

# This creates: docs/adr/0001-adopt-microservices-architecture.md
# Edit the file to document your decision
```

## Step 8: Docker Execution (Optional)

```bash
# Build analysis container
make build-analysis-image

# Run analysis in container
docker run --rm -v $(pwd):/workspace -w /workspace analysis:local \
  bash -lc "make full-analysis"
```

## Understanding the Output

### Risk Scores
- **0.70+**: HIGH risk - immediate attention needed
- **0.50-0.69**: MEDIUM risk - plan remediation
- **< 0.50**: LOW risk - monitor

### Risk Components
- **Churn**: High change frequency indicates instability
- **Complexity**: High cyclomatic complexity indicates maintenance burden
- **Coverage**: Low test coverage indicates quality risk
- **Criticality**: Business impact weighting

### Drift Metrics
- **Churn Ratio**: (Added + Removed edges) / Previous edges
- **Threshold**: Default 0.1 (10%)
- **Boundary Violations**: New dependencies into previously isolated modules

### Knowledge Concentration
- **Threshold**: Default 0.6 (60%)
- **Flag**: HIGH_CONCENTRATION or SINGLE_CONTRIBUTOR
- **Risk**: Bus factor and knowledge transfer challenges

## Next Steps

1. **Automate**: Set up CI/CD pipeline (see `.github/workflows/` examples in transcript)
2. **Integrate**: Connect to Backstage for visualization
3. **Customize**: Adjust risk weights in `config/risk_weights.yaml`
4. **Iterate**: Run analysis regularly (nightly recommended)
5. **Act**: Use remediation backlog template to track improvements

## Troubleshooting

### No churn data
```bash
# Check git history
git log --since=90.days --oneline | wc -l
# If zero, adjust --days parameter in ownership_diff.py
```

### Empty complexity report
```bash
# Install radon
pip install radon

# For JavaScript projects, use plato:
npm install -g plato
plato -r -d artifacts/ src/
```

### Permission denied on scripts
```bash
chmod +x scripts/*.sh
```

### Missing Python dependencies
```bash
pip install radon pipdeptree pyyaml
```

## Common Workflows

### Weekly Risk Review
```bash
make full-analysis
cat artifacts/consolidated_risk.json | jq '.derived_risks[] | select(.severity=="HIGH")'
```

### Pre-Release Security Check
```bash
trivy fs --severity HIGH,CRITICAL --format json . > artifacts/trivy_raw.json
python3 scripts/parse_trivy.py --input artifacts/trivy_raw.json --out artifacts/security_findings.json
```

### Quarterly Architecture Review
```bash
# Generate executive summary data
make full-analysis
# Use templates/executive_summary_template.md to create report
```

## Configuration Options

### Risk Weighting
Edit `config/risk_weights.yaml` or use environment variables:
```bash
export RISK_W_CHURN=0.3
export RISK_W_COMPLEXITY=0.35
export RISK_W_COVERAGE=0.15
export RISK_W_CRITICALITY=0.10
```

### Drift Threshold
```bash
python3 scripts/scan_drift.py --threshold 0.15 ...
```

### Ownership Window
```bash
python3 scripts/ownership_diff.py --days 60 ...
```

## Getting Help

- Review `README.md` for comprehensive documentation
- Check `docs/summary_compiled.md` for detailed explanations
- Examine script headers for usage information
- Review templates in `templates/` directory

## Success Metrics

After initial setup, you should have:
- ✅ Hotspots report identifying risky code
- ✅ Ownership report highlighting bus factor risks
- ✅ Drift report tracking architecture changes
- ✅ Consolidated risk register for governance
- ✅ Optional: SBOM and security findings

You're now ready to implement continuous architecture governance!
