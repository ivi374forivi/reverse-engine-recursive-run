#!/usr/bin/env python3
"""
risk_update.py

Aggregates multiple reports into a consolidated risk register delta.

Inputs (any subset):
  --hotspots hotspots.json (from hotspot_merge.py)
  --drift drift_report.json (from scan_drift.py)
  --ownership ownership.json (from ownership_diff.py)
  --security findings_security.json (custom format)
  --out consolidated_risk.json

Security findings expected format:
[
  {"id":"SEC-001","severity":"HIGH","component":"auth_middleware.py","desc":"Missing rate limit"}
]

Produces:
{
  "timestamp": "...",
  "sources": {...},
  "derived_risks": [
     { "id":"RISK-HOTSPOT-file.py", "type":"HOTSPOT", "severity":"MEDIUM", ... }
  ]
}

Severity Heuristic (example):
  - HOTSPOT risk_score >=0.75 -> HIGH
  - HOTSPOT risk_score >=0.5 -> MEDIUM else LOW
  - Ownership SINGLE_CONTRIBUTOR & criticality>=3 -> HIGH else MEDIUM
  - Drift breach -> MEDIUM unless churn_ratio >= 0.3 then HIGH
  - Security: passthrough severity
"""
import json, argparse, time

def load(path):
    if not path: return None
    with open(path) as f: return json.load(f)

def hotspot_sev(score):
    if score >= 0.75: return "HIGH"
    if score >= 0.5: return "MEDIUM"
    return "LOW"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--hotspots")
    ap.add_argument("--drift")
    ap.add_argument("--ownership")
    ap.add_argument("--security")
    ap.add_argument("--out", required=True)
    args=ap.parse_args()

    hotspots = load(args.hotspots)
    drift = load(args.drift)
    ownership = load(args.ownership)
    security = load(args.security)

    derived=[]

    if hotspots:
        for h in hotspots.get("hotspots",[]):
            sev = hotspot_sev(h["risk_score"])
            derived.append({
                "id": f"RISK-HOTSPOT-{h['file']}",
                "type":"HOTSPOT",
                "component": h["file"],
                "severity": sev,
                "details": h,
                "recommendation":"Refactor / add tests / reduce complexity; prioritize if part of production path."
            })

    if drift:
        s=drift["summary"]
        if s["breach"]:
            sev = "HIGH" if s["churn_ratio"]>=0.3 else "MEDIUM"
            derived.append({
                "id": f"RISK-DRIFT-{s.get('current_ref')}",
                "type":"ARCH_DRIFT",
                "severity": sev,
                "details": s,
                "recommendation":"Initiate architecture review; validate new edges for boundary violations."
            })
        for flag in drift.get("core_boundary_flags",[]):
            derived.append({
                "id": f"RISK-BOUNDARY-{flag['from']}->{flag['to']}",
                "type":"BOUNDARY_VIOLATION",
                "severity":"MEDIUM",
                "details": flag,
                "recommendation":"Assess if new dependency is intentional; consider facade or inversion."
            })

    if ownership:
        for d in ownership.get("directories",[]):
            if not d.get("flag"): continue
            sev="MEDIUM"
            if d["flag"]=="SINGLE_CONTRIBUTOR" and d.get("criticality",1)>=3:
                sev="HIGH"
            elif d["flag"]=="HIGH_CONCENTRATION" and d.get("criticality",1)>=4:
                sev="HIGH"
            derived.append({
                "id": f"RISK-OWN-{d['path']}",
                "type":"KNOWLEDGE_CONCENTRATION",
                "severity": sev,
                "details": d,
                "recommendation":"Spread knowledge via pairing, docs, secondary owner assignment."
            })

    if security:
        for finding in security:
            derived.append({
                "id": finding.get("id","SEC-UNSET"),
                "type":"SECURITY",
                "severity": finding.get("severity","MEDIUM"),
                "details": finding,
                "recommendation": finding.get("remediation","Review & patch.")
            })

    out = {
      "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
      "sources": {
        "hotspots": bool(hotspots),
        "drift": bool(drift),
        "ownership": bool(ownership),
        "security": bool(security)
      },
      "derived_risks": derived
    }

    with open(args.out,"w") as f:
        json.dump(out,f,indent=2)

    print(f"[RISK] Consolidated {len(derived)} risks -> {args.out}")

if __name__=="__main__":
    main()
