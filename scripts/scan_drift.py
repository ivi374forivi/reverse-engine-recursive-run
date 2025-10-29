#!/usr/bin/env python3
"""
scan_drift.py

Compares the current dependency graph / service inventory against a prior snapshot
to detect architecture drift.

Inputs:
  --current current_graph.json
  --previous previous_graph.json
  --threshold 0.1 (fractional % new edges triggering alert)
  --out drift_report.json
  --mode (deps|services) default: deps

Expected schema (deps mode):
{
  "nodes":[{"id":"moduleA","group":"serviceX"}, ...],
  "edges":[{"from":"moduleA","to":"moduleB","type":"import"}, ...],
  "meta":{"ref":"<git-sha>","generated_at":"..."}
}

A lightweight JSON is fine; generate current_graph.json via another internal tool.

For services mode, nodes=services, edges=call relationships or event flows.

Drift Heuristics:
  - Added nodes
  - Removed nodes
  - Added edges
  - Removed edges
  - Edge churn ratio: (#added + #removed) / previous_edge_count
  - Core boundary violation: new edge where target previously had in_degree=0 (potential boundary breach)

Outputs JSON:
{
  "summary": {...},
  "added_nodes": [...],
  "removed_nodes": [...],
  "added_edges": [...],
  "removed_edges": [...],
  "core_boundary_flags": [...]
}

Exit code:
  0 if below threshold
  2 if drift >= threshold (trigger pipeline action)

"""
import json, argparse, sys, hashlib
from collections import defaultdict

def load(path):
    with open(path) as f:
        return json.load(f)

def edge_key(e):
    return (e["from"], e["to"], e.get("type",""))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--current", required=True)
    ap.add_argument("--previous", required=True)
    ap.add_argument("--threshold", type=float, default=0.1)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mode", choices=["deps","services"], default="deps")
    args = ap.parse_args()

    cur = load(args.current)
    prev = load(args.previous)

    prev_nodes = {n["id"]: n for n in prev.get("nodes", [])}
    cur_nodes = {n["id"]: n for n in cur.get("nodes", [])}

    added_nodes = sorted(set(cur_nodes) - set(prev_nodes))
    removed_nodes = sorted(set(prev_nodes) - set(cur_nodes))

    prev_edges_set = set(edge_key(e) for e in prev.get("edges", []))
    cur_edges_set = set(edge_key(e) for e in cur.get("edges", []))

    added_edges_raw = cur_edges_set - prev_edges_set
    removed_edges_raw = prev_edges_set - cur_edges_set

    added_edges = [ {"from":f,"to":t,"type":typ} for (f,t,typ) in added_edges_raw ]
    removed_edges = [ {"from":f,"to":t,"type":typ} for (f,t,typ) in removed_edges_raw ]

    prev_edge_count = len(prev_edges_set) or 1
    churn_ratio = (len(added_edges_raw)+len(removed_edges_raw))/prev_edge_count

    # Degree calculations on previous graph
    in_deg_prev = defaultdict(int)
    for f,t,typ in prev_edges_set:
        in_deg_prev[t]+=1

    core_boundary_flags = []
    for e in added_edges:
        target = e["to"]
        if in_deg_prev.get(target,0)==0 and target in prev_nodes:
            core_boundary_flags.append(e)

    summary = {
        "previous_ref": prev.get("meta",{}).get("ref"),
        "current_ref": cur.get("meta",{}).get("ref"),
        "added_nodes_count": len(added_nodes),
        "removed_nodes_count": len(removed_nodes),
        "added_edges_count": len(added_edges),
        "removed_edges_count": len(removed_edges),
        "churn_ratio": round(churn_ratio,4),
        "threshold": args.threshold,
        "breach": churn_ratio >= args.threshold
    }

    report = {
        "summary": summary,
        "added_nodes": added_nodes,
        "removed_nodes": removed_nodes,
        "added_edges": added_edges,
        "removed_edges": removed_edges,
        "core_boundary_flags": core_boundary_flags,
        "hash": hashlib.sha256(json.dumps(summary, sort_keys=True).encode()).hexdigest()
    }

    with open(args.out,"w") as f:
        json.dump(report,f,indent=2)

    print(json.dumps(summary, indent=2))
    if summary["breach"]:
        print("[DRIFT] Threshold exceeded.", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
