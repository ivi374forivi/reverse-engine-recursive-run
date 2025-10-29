# Executive Architecture & Risk Summary
Generated: {{DATE}}  
Source Refs: {{REPO_LIST_WITH_SHAS}}  
Classification: {{CLASSIFICATION_LEVEL}}  
Prepared By: {{AUTHOR}}  

## 1. Objectives
- Primary Goal(s): {{GOALS}}  
- Scope: {{IN_SCOPE_COMPONENTS}}  
- Exclusions: {{OUT_OF_SCOPE}}  

## 2. High-Level Architecture Snapshot
Describe the current logical layers, key services, and primary data stores.

| Layer | Components | Purpose | Notes |
|-------|------------|---------|-------|
| Ingress | {{API_GATEWAYS}} | Entry points | |
| Core Domain | {{CORE_SERVICES}} | Business logic | |
| Data | {{DATA_STORES}} | Persistence | |
| Integration | {{EXT_APIS}} | External dependencies | |
| Observability | {{OBS_STACK}} | Monitoring & tracing | |

## 3. Key Findings (Top 5)
1. {{FINDING_1}} (Impact: {{IMPACT_1}}, Severity: {{SEVERITY_1}})
2. {{FINDING_2}}
3. {{FINDING_3}}
4. {{FINDING_4}}
5. {{FINDING_5}}

## 4. Risk Heat Map
| Category | High | Medium | Low | Notes |
|----------|------|--------|-----|-------|
| Security | {{SEC_HIGH}} | {{SEC_MED}} | {{SEC_LOW}} | {{SEC_NOTES}} |
| Architecture Drift | {{DRIFT_HIGH}} | {{DRIFT_MED}} | {{DRIFT_LOW}} | |
| Knowledge Concentration | {{KNOW_HIGH}} | {{KNOW_MED}} | {{KNOW_LOW}} | |
| Performance | {{PERF_HIGH}} | {{PERF_MED}} | {{PERF_LOW}} | |
| Compliance | {{COMP_HIGH}} | {{COMP_MED}} | {{COMP_LOW}} | |

## 5. Hotspots (Code-Level)
| File/Module | Risk Score | Components (Churn/Complexity/Coverage/Crit) | Rationale | Action |
|-------------|-----------:|---------------------------------------------|-----------|--------|
| {{FILE_1}} | {{RISK_1}} | {{COMP_BREAKDOWN_1}} | {{WHY_1}} | {{ACTION_1}} |
| {{FILE_2}} | {{RISK_2}} | {{COMP_BREAKDOWN_2}} | {{WHY_2}} | {{ACTION_2}} |

## 6. Architecture Drift Summary
- New Nodes: {{DRIFT_ADDED_NODES}}
- Removed Nodes: {{DRIFT_REMOVED_NODES}}
- Edge Churn Ratio: {{DRIFT_CHURN_RATIO}}
- Boundary Violations: {{BOUNDARY_FLAGS_COUNT}}
- Assessment: {{DRIFT_ASSESSMENT}}

## 7. Security Snapshot
| Area | Status | Notable Gaps | Priority Action |
|------|--------|--------------|-----------------|
| AuthN/AuthZ | {{AUTH_STATUS}} | {{AUTH_GAPS}} | {{AUTH_ACTION}} |
| Secrets Mgmt | {{SECRETS_STATUS}} | {{SECRETS_GAPS}} | {{SECRETS_ACTION}} |
| Dependency Vulns | {{VULN_STATUS}} | {{VULN_GAPS}} | {{VULN_ACTION}} |
| Input Validation | {{VALID_STATUS}} | {{VALID_GAPS}} | {{VALID_ACTION}} |
| Logging & Audit | {{AUDIT_STATUS}} | {{AUDIT_GAPS}} | {{AUDIT_ACTION}} |

## 8. Knowledge Concentration
| Path | Top Contributor % | Flag | Criticality | Mitigation |
|------|-------------------|------|-------------|------------|
| {{PATH_1}} | {{PCT_1}} | {{FLAG_1}} | {{CRIT_1}} | {{MITIGATION_1}} |

## 9. Compliance Coverage Matrix
| Control Domain | Evidence Source | Gap | Action | Owner | Target Date |
|----------------|-----------------|-----|--------|-------|-------------|
| {{DOMAIN_1}} | {{EVIDENCE_1}} | {{GAP_1}} | {{ACTION_1}} | {{OWNER_1}} | {{DATE_1}} |

## 10. Prioritized Remediation (Next 90 Days)
| Rank | Title | Category | Effort | Impact | Owner | Dependency | ETA |
|------|-------|----------|--------|--------|-------|-----------|-----|
| 1 | {{ITEM_1}} | {{CAT_1}} | {{EFFORT_1}} | {{IMPACT_1}} | {{OWNER_1}} | {{DEP_1}} | {{ETA_1}} |

## 11. KPIs & Baselines
| Metric | Current | Target | Trend | Notes |
|--------|---------|--------|-------|-------|
| Lead Time | {{LEAD_TIME}} | {{LEAD_TARGET}} | {{TREND}} | |
| Change Failure Rate | {{CHANGE_FAIL}} | {{CHANGE_TARGET}} | | |
| Test Coverage (Critical Paths) | {{COVERAGE}} | {{COVERAGE_TARGET}} | | |
| Mean Time to Restore | {{MTTR}} | {{MTTR_TARGET}} | | |
| Drift Churn Ratio | {{DRIFT_RATIO}} | < {{DRIFT_THRESHOLD}} | | |

## 12. Next Review Cycle
- Proposed Date: {{NEXT_REVIEW_DATE}}
- Trigger Conditions: (e.g., drift > threshold, security CVE > critical)

## 13. Appendices
- Methodology
- Tooling & Commands
- Data Integrity Notes
- Glossary

Footer: Generated from commits {{REPO_LIST_WITH_SHAS}} on {{DATE}} — Classification: {{CLASSIFICATION_LEVEL}}
