#!/usr/bin/env python3
"""
hotspot_merge.py

Merges churn, complexity, (optional) coverage, and criticality metadata into a ranked hotspot report.

Inputs:
  --churn churn.txt (format: "<count> <filepath>")
  --complexity complexity.json (Radon JSON, Plato summary, or custom: see adapter)
  --coverage coverage.json (optional: { "files": { "path": coverage_pct_float } })
  --criticality criticality.yaml (optional: YAML mapping file->criticality score 1-5)
  --out hotspots.json
  --top 50

Risk score formula (default):
  risk = (normalized_churn * 0.4 + normalized_complexity * 0.4 + coverage_penalty * 0.1 + criticality_factor * 0.1)
Where:
  normalized_churn = churn / max_churn
  normalized_complexity = file_avg_cc / max_cc
  coverage_penalty = (1 - coverage) (coverage in 0..1; if missing assume 0.5)
  criticality_factor = criticality / max_criticality (default criticality=1)

Override with env vars:
  RISK_W_CHURN, RISK_W_COMPLEXITY, RISK_W_COVERAGE, RISK_W_CRITICALITY
"""
import argparse, json, sys, os, math
from collections import defaultdict

try:
    import yaml
except:
    yaml = None

def load_churn(path):
    churn = {}
    with open(path) as f:
        for line in f:
            line=line.strip()
            if not line: continue
            parts=line.split()
            if len(parts) < 2: continue
            count=int(parts[0])
            file=parts[1]
            churn[file]=count
    return churn

def load_complexity(path):
    """
    Expect radon cc -j output OR a dict { "path": [{"complexity":int}, ...] }.
    Returns mapping file->avg complexity.
    """
    with open(path) as f:
        data=json.load(f)
    result={}
    for file, blocks in data.items():
        if not isinstance(blocks,list):
            continue
        if not blocks:
            avg=0
        else:
            avg=sum(b.get("complexity",0) for b in blocks)/len(blocks)
        result[file]=avg
    return result

def load_coverage(path):
    with open(path) as f:
        data=json.load(f)
    if "files" in data:
        return data["files"]
    return data

def load_criticality(path):
    if not yaml:
        raise RuntimeError("pyyaml required for criticality YAML")
    with open(path) as f:
        return yaml.safe_load(f) or {}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--churn", required=True)
    ap.add_argument("--complexity", required=True)
    ap.add_argument("--coverage")
    ap.add_argument("--criticality")
    ap.add_argument("--out", required=True)
    ap.add_argument("--top", type=int, default=50)
    args=ap.parse_args()

    churn=load_churn(args.churn)
    complexity=load_complexity(args.complexity)
    coverage=load_coverage(args.coverage) if args.coverage else {}
    criticality=load_criticality(args.criticality) if args.criticality else {}

    max_churn=max(churn.values()) if churn else 1
    max_cc=max(complexity.values()) if complexity else 1
    max_crit=max(criticality.values()) if criticality else 1

    w_churn=float(os.getenv("RISK_W_CHURN","0.4"))
    w_complexity=float(os.getenv("RISK_W_COMPLEXITY","0.4"))
    w_coverage=float(os.getenv("RISK_W_COVERAGE","0.1"))
    w_crit=float(os.getenv("RISK_W_CRITICALITY","0.1"))
    total = w_churn + w_complexity + w_coverage + w_crit
    if not math.isclose(total,1.0):
        w_churn/=total; w_complexity/=total; w_coverage/=total; w_crit/=total

    files=set(churn)|set(complexity)|set(coverage)|set(criticality)
    records=[]
    for f in files:
        c=churn.get(f,0)
        cc=complexity.get(f,0)
        cov=coverage.get(f,0.5)
        cov_pen=(1 - cov)
        crit=criticality.get(f,1)

        norm_churn = c/max_churn if max_churn else 0
        norm_cc = cc/max_cc if max_cc else 0
        norm_crit = crit/max_crit if max_crit else 0

        risk = (norm_churn*w_churn +
                norm_cc*w_complexity +
                cov_pen*w_coverage +
                norm_crit*w_crit)

        records.append({
            "file": f,
            "churn": c,
            "avg_complexity": round(cc,2),
            "coverage": round(cov,3),
            "criticality": crit,
            "risk_score": round(risk,4),
            "components": {
               "churn": round(norm_churn*w_churn,4),
               "complexity": round(norm_cc*w_complexity,4),
               "coverage_penalty": round(cov_pen*w_coverage,4),
               "criticality_factor": round(norm_crit*w_crit,4)
            }
        })

    records.sort(key=lambda r: r["risk_score"], reverse=True)
    top=records[:args.top]

    with open(args.out,"w") as f:
        json.dump({
            "meta":{
                "weights":{
                    "churn":w_churn,
                    "complexity":w_complexity,
                    "coverage":w_coverage,
                    "criticality":w_crit
                }
            },
            "hotspots": top
        }, f, indent=2)

    print(f"[HOTSPOTS] Wrote {len(top)} entries to {args.out}")

if __name__=="__main__":
    main()
