# Compiled Summary: Architecture Reverse Engineering & Governance Stack

## 1. Core Objectives
- Map architecture (code + process) for closed source repos
- Quantify risk via churn, complexity, coverage gaps, criticality, security
- Detect architecture drift (nodes/edges changed)
- Identify knowledge concentration
- Generate SBOM + security ingestion
- Produce consolidated risk register
- Feed metrics to Backstage and CI governance loops
- Enable safe AI summarization
- Provide remediation backlog with weighted formula
- Support compliance & IP awareness

## 2. Key Artifacts

| Category | Artifact Examples |
|----------|-------------------|
| Scripts | gen_sbom.sh, scan_drift.py, hotspot_merge.py, ownership_diff.py, risk_update.py, parse_trivy.py, parse_semgrep.py |
| Config | drift_config.yaml, risk_weights.yaml, service_paths.yaml, adr_enforcement.yaml |
| Templates | Executive summary, remediation backlog, AI-safe prompts |
| Security | Normalized Trivy/Semgrep parsers & schema |
| Risk Model | Linear + extended (non-linear + security dimension) |
| Backstage | Metrics annotations strategy & service entity examples |
| CI | GitHub Actions workflow arch-governance.yml |
| Container | Dockerfile.analysis for reproducible environment |

## 3. Data Flows

1. **Codebase Analysis**
   - Codebase → Complexity (radon) + Churn (git) + Coverage → Hotspots
   - Codebase → SBOM (Syft) → Security (Trivy) → Normalized findings

2. **Drift Detection**
   - Dependency Graph Snapshots → Drift detection (edge churn & boundary flags)

3. **Risk Aggregation**
   - Git history → Ownership concentration analysis
   - All upstream reports → Risk aggregator → Consolidated JSON

4. **Integration**
   - Consolidated JSON + service path mapping → Backstage annotations & dashboards
   - ADR generation scaffolding → Captures rationale for architecture changes/drift responses

## 4. Risk Dimensions & Scoring

### Dimensions
- **Churn**: Code volatility (git activity)
- **Complexity**: Cyclomatic complexity metrics
- **Coverage Gap**: Missing test coverage
- **Criticality**: Business impact weighting
- **Security Hotspot**: Vulnerability presence (optional)
- **Knowledge Concentration**: Bus factor analysis (adjusts severity)
- **Drift**: Global/edge-level architecture changes

### Default Linear Weights
```
churn:           0.4 (40%)
complexity:      0.4 (40%)
coverage_gap:    0.1 (10%)
criticality:     0.1 (10%)
```

### Extended Model
- Optional exponentiation (non-linear scaling)
- Security dimension weighting
- Severity escalation rules

### Severity Escalation Rules
- Security HIGH/CRITICAL → automatic HIGH severity
- Knowledge concentration > 0.8 & criticality ≥ 4 → escalate one level
- Boundary violation → at least MEDIUM severity

## 5. Governance Loop

**Nightly or scheduled execution:**
1. Generate metrics & artifacts
2. Evaluate thresholds (drift, vulnerabilities)
3. Open issues / update backlog / annotate Backstage
4. Recompute risk trends (store time series) for regression detection

## 6. Compliance & IP

- Maintain SBOM + license metadata (CycloneDX/SPDX)
- Record decision rationale using ADR template
- Classify artifacts (Internal / Confidential)
- Redact potential secrets in derivative outputs
- Support SOX, PCI DSS, HIPAA, ISO 27001 audits

## 7. Backstage Integration

### Annotations
- `analysis.hotspotsScore`: Aggregated risk score
- `analysis.knowledgeConcentration`: Top contributor percentage
- `analysis.securityFindings`: High severity count
- `analysis.driftChurnRatio`: Architecture change velocity
- `analysis.lastRiskUpdate`: Timestamp of last analysis

### Frontend Plugin Widgets
- Risk Overview (aggregated metrics)
- Hotspots Table (top N with drill-down)
- Knowledge Concentration Gauge
- Dependency Graph Visualization
- Cycle Detection Display

### Data Sources
- consolidated_risk.json
- Enriched service mapping
- Time-series historical data

## 8. ADR Process

**Structured Decision Recording:**
- Scripted creation of numbered ADR Markdown files
- Consistent metadata: Title, Status, Context, Decision, Consequences
- Index auto-regenerated for navigation
- Tags for drift/security triggers with evidence artifact links

**Enforcement:**
- Boundary violations require ADR references
- CI gates on missing justifications
- Temporal exemptions with expiry dates

## 9. Extensibility Hooks

- Add Semgrep findings ingestion (normalized schema)
- Dynamic weighting per release phase via environment or config
- Service-level SLO correlation (attach p95 latency to hotspots)
- Deploy metrics ingestion API for multi-repo unification
- OpenTelemetry integration for runtime drift detection

## 10. Suggested Next Enhancements

- Store historical snapshots in object storage (MinIO/S3)
- Add ADR linting (ensure boundary violations spawn ADR or waiver)
- Implement GraphQL API for UI component risk slices
- Use OpenTelemetry to detect runtime "untraced" edges vs static edges
- Anomaly detection (Z-score) on time-series metrics
- Cycle severity scoring (weight by node centrality)
- Automatic ADR draft creation for missing justifications

## 11. File Groups

### Core Analysis
- Scripts for SBOM, drift, hotspots, ownership, risk aggregation
- Security tool parsers (Trivy, Semgrep, Gitleaks)
- Diff-aware risk analysis
- Time-series persistence

### Visualization
- Backstage Plugin (React components, types, plugin registration)
- Graph visualization with force-directed layout
- Risk overview widgets
- Knowledge concentration gauges

### Infrastructure
- Docker Compose stack for local execution & observability
- Dockerfile.analysis for reproducible environments
- GitHub Actions workflows
- Backend API service (Node/Express or FastAPI)

### Documentation
- ADR automation scripts, templates, index generator
- Executive summary template
- Security ingestion guides
- Risk weighting customization docs

## 12. Security Posture

- Assure pipeline isolation
- Avoid exfiltrating raw code in SBOM
- Restrict artifact distribution to internal consumers
- AI prompts sanitized (no secrets, no large literal blocks)
- Provide minimal structural metadata for summarization
- Classification labels on all outputs

## 13. Metrics & KPIs

| Metric | Current | Target | Purpose |
|--------|---------|--------|---------|
| Lead Time | TBD | < 2 days | Development velocity |
| Change Failure Rate | TBD | < 15% | Deployment quality |
| Test Coverage (Critical) | TBD | > 80% | Risk mitigation |
| Mean Time to Restore | TBD | < 1 hour | Incident response |
| Drift Churn Ratio | TBD | < 0.12 | Architecture stability |
| Knowledge Concentration | TBD | < 0.60 | Bus factor risk |

## 14. Tool Chain

### Analysis Tools
- **Complexity**: radon (Python), plato (JavaScript), gocyclo (Go)
- **SBOM**: Syft, CycloneDX CLI
- **Security**: Trivy, Semgrep, Gitleaks
- **Dependencies**: pipdeptree, npm list, go mod graph

### Infrastructure
- **Container**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Storage**: MinIO (optional S3-compatible)
- **Observability**: Jaeger, Grafana (optional)

### Frontend
- **Framework**: Backstage
- **Visualization**: react-force-graph, Material-UI
- **Language**: TypeScript/React

### Backend
- **Runtime**: Node.js + Express OR Python + FastAPI
- **Data**: JSON/JSONL files, optional database

## 15. Quick Start Commands

```bash
# Initialize environment
mkdir -p artifacts/sbom artifacts/timeseries

# Generate SBOM
./scripts/gen_sbom.sh --out artifacts/sbom --ref $(git rev-parse HEAD)

# Analyze complexity and churn
radon cc -j -s src/ > artifacts/complexity.json
git log --since=90.days --name-only --pretty=format: | \
  sort | grep -v '^$' | uniq -c > artifacts/churn.txt

# Create hotspot analysis
python scripts/hotspot_merge.py \
  --churn artifacts/churn.txt \
  --complexity artifacts/complexity.json \
  --out artifacts/hotspots.json

# Detect drift
python scripts/scan_drift.py \
  --current artifacts/current_graph.json \
  --previous artifacts/previous_graph.json \
  --out artifacts/drift_report.json

# Analyze ownership
python scripts/ownership_diff.py --out artifacts/ownership.json

# Consolidate risks
python scripts/risk_update.py \
  --hotspots artifacts/hotspots.json \
  --drift artifacts/drift_report.json \
  --ownership artifacts/ownership.json \
  --security artifacts/security_findings.json \
  --out artifacts/consolidated_risk.json

# Start backend server
cd server && npm install && npm run dev

# Record time-series snapshot
python scripts/record_timeseries.py \
  --services config/service_paths.yaml \
  --out-dir artifacts/timeseries
```

## 16. Red Flags to Watch For

- God modules (5000+ lines, high churn)
- Silent side effects (functions performing network I/O unexpectedly)
- Inconsistent error models (mixed exceptions vs return codes)
- Ad hoc retry loops without backoff
- Hard-coded credentials / tokens
- Feature flags with TODO: remove (years old)
- Incomplete migrations (migration file present; table absent)
- Multiple JSON schema versions coexisting without migration logic

## 17. Success Criteria

- ✅ Baseline risk metrics established for all services
- ✅ Automated governance pipeline running nightly
- ✅ Backstage integration displaying real-time metrics
- ✅ ADR process adopted for architectural decisions
- ✅ Security findings integrated into risk scoring
- ✅ Knowledge concentration below threshold
- ✅ No undocumented boundary violations
- ✅ Time-series data enabling trend analysis

## 18. Anti-Patterns to Avoid

- Over-sharing internal wiki with sensitive code blocks
- Unreviewed AI generation introducing license-incompatible snippets
- Shadow services deployed but not in registry
- Static secrets committed historically but never rotated
- Misleading aspirational architecture diagrams accepted by auditors
- Overfitting weights to a single incident
- Ignoring normalization when new files shift max values
- Failing to document rationale for threshold changes

## 19. Conclusion

This comprehensive toolkit provides:
- **Visibility**: Clear view of architecture and risk landscape
- **Governance**: Automated detection of drift and violations
- **Compliance**: Audit trails and decision records
- **Quality**: Continuous improvement through metrics
- **Safety**: Security vulnerability integration
- **Sustainability**: Knowledge transfer and bus factor mitigation

The system is designed to be:
- **Modular**: Use components independently
- **Extensible**: Easy to add new analyzers and metrics
- **Secure**: Privacy-preserving for closed-source code
- **Actionable**: Clear remediation guidance
- **Scalable**: Works from single repo to large organizations

---
*Generated: 2025-10-29*  
*Classification: Internal*  
*Source: AI-Assisted Design Process*
