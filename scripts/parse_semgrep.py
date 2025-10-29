#!/usr/bin/env python3
"""
parse_semgrep.py

Convert Semgrep JSON output into normalized security findings list.
Semgrep command example:
  semgrep --json --config p/security-audit --output artifacts/semgrep_raw.json

Expected Semgrep JSON top-level keys:
{
  "results": [
    {
      "check_id": "rule.id",
      "path": "src/app/file.py",
      "extra": {
         "message": "...",
         "severity": "ERROR" | "WARNING" | "INFO",
         "metadata": { ... }
      },
      "start": {"line": 10}
    }
  ]
}

Severity Mapping:
- ERROR -> HIGH
- WARNING -> MEDIUM
- INFO -> LOW

Output schema aligns with parse_trivy.py:
[
  {
    "id": "SEC-SEMGREP-rule.id",
    "severity": "HIGH",
    "component": "src/app/file.py",
    "desc": "message (line 10)",
    "recommendation": "See rule metadata or internal secure coding guidelines."
  }
]
"""
import json, argparse, sys

MAP = {
    "ERROR": "HIGH",
    "WARNING": "MEDIUM",
    "INFO": "LOW"
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    try:
        data = json.load(open(args.input))
    except Exception as e:
        print(f"[SEMGREP] Failed to load input: {e}", file=sys.stderr)
        json.dump([], open(args.out,"w"))
        return

    results = data.get("results", [])
    out = []
    for r in results:
        check_id = r.get("check_id","UNKNOWN")
        path = r.get("path","UNKNOWN")
        extra = r.get("extra", {})
        msg = extra.get("message","")
        sev_raw = extra.get("severity","INFO").upper()
        sev = MAP.get(sev_raw, "LOW")
        line = r.get("start",{}).get("line")
        desc = f"{msg} (line {line})" if line else msg
        out.append({
            "id": f"SEC-SEMGREP-{check_id}",
            "severity": sev,
            "component": path,
            "desc": desc[:300],
            "recommendation": "Review Semgrep rule guidance; apply fix or suppress with justification."
        })

    with open(args.out,"w") as f:
        json.dump(out,f,indent=2)
    print(f"[SEMGREP] Normalized {len(out)} findings -> {args.out}")

if __name__ == "__main__":
    main()
