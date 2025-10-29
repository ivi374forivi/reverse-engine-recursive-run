#!/usr/bin/env python3
"""
parse_trivy.py

Converts raw Trivy JSON output into normalized security findings expected by risk_update.py.

Usage:
  python scripts/parse_trivy.py --input artifacts/trivy_raw.json --out artifacts/security_findings.json

Output Schema (list):
[
  {
    "id": "SEC-TRIVY-CVE-2024-12345",
    "severity": "HIGH",
    "component": "requirements.txt::package@1.0.0",
    "desc": "Summary",
    "cve": "CVE-2024-12345",
    "package": "package",
    "installed_version": "1.0.0",
    "fixed_version": "1.0.1",
    "recommendation": "Upgrade to 1.0.1"
  }
]
"""
import json, argparse, sys

SEV_ORDER = ["CRITICAL","HIGH","MEDIUM","LOW","UNKNOWN"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    try:
        with open(args.input) as f:
            data = json.load(f)
    except Exception as e:
        print(f"[WARN] Could not read input: {e}", file=sys.stderr)
        data = {}

    results = []
    # Trivy output may be either a dict with "Results" or a list per target
    if isinstance(data, dict):
        candidates = [data]
    elif isinstance(data, list):
        candidates = data
    else:
        candidates = []

    for item in candidates:
        for result in item.get("Results", []):
            target = result.get("Target", "UNKNOWN_TARGET")
            for vuln in result.get("Vulnerabilities", []) or []:
                sev = vuln.get("Severity","UNKNOWN").upper()
                pkg = vuln.get("PkgName","unknown")
                inst = vuln.get("InstalledVersion","?")
                fix = vuln.get("FixedVersion")
                cve = vuln.get("VulnerabilityID","")
                summary = vuln.get("Title") or vuln.get("Description","")
                rec = f"Upgrade to {fix}" if fix else "Monitor upstream; no fixed version."
                results.append({
                    "id": f"SEC-TRIVY-{cve}",
                    "severity": "HIGH" if sev == "CRITICAL" else sev,
                    "component": f"{target}::{pkg}@{inst}",
                    "desc": summary[:300],
                    "cve": cve,
                    "package": pkg,
                    "installed_version": inst,
                    "fixed_version": fix,
                    "recommendation": rec
                })

    with open(args.out,"w") as f:
        json.dump(results,f,indent=2)

    print(f"[SECURITY] Normalized {len(results)} findings -> {args.out}")

if __name__ == "__main__":
    main()
