#!/usr/bin/env python3
"""
ownership_diff.py

Analyzes commit authorship concentration per directory and flags potential
knowledge concentration risks.

Inputs:
  Runs 'git log' internally unless provided a pre-collected JSON.

Flags:
  - Directories where top contributor > threshold (default 0.6)
  - Directories with single contributor over last N days
  - Directories criticality weighting (optional YAML mapping directory->tier)

JSON Output:
{
  "summary": {...},
  "directories": [
    {
      "path":"src/core",
      "total_commits":123,
      "authors":[{"email":"a@x","count":70,"pct":0.569}, ...],
      "top_concentration":0.569,
      "flag":"HIGH_CONCENTRATION"
    }
  ]
}
"""
import subprocess, argparse, json, os
from collections import defaultdict, Counter
from pathlib import Path

try:
    import yaml
except:
    yaml = None

def git_files_since(days):
    cmd = ["bash","-lc", f'git log --since={days}.days --name-only --pretty=format:"%ae"']
    out = subprocess.check_output(cmd).decode().splitlines()
    return out

def bucket_by_directory(entries, depth):
    dir_author = defaultdict(Counter)
    current_author=None
    for line in entries:
        if "@" in line and "/" not in line:
            current_author=line.strip()
        elif "/" in line and current_author:
            p=Path(line.strip())
            # skip deletions/empties
            if not str(p).strip():
                continue
            parts=p.parts[:depth]
            d="/".join(parts)
            dir_author[d][current_author]+=1
    return dir_author

def load_criticality(path):
    if not path or not yaml: return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--depth", type=int, default=2)
    ap.add_argument("--threshold", type=float, default=0.6)
    ap.add_argument("--criticality")
    ap.add_argument("--out", required=True)
    args=ap.parse_args()

    raw=git_files_since(args.days)
    dir_author=bucket_by_directory(raw, args.depth)
    crit_map=load_criticality(args.criticality)

    results=[]
    for d, counter in dir_author.items():
        total=sum(counter.values())
        authors=[]
        for email, count in counter.most_common():
            pct=count/total if total else 0
            authors.append({"email":email,"count":count,"pct":round(pct,3)})
        top_pct=authors[0]["pct"] if authors else 0
        flag=None
        if top_pct >= args.threshold and len(authors)>1:
            flag="HIGH_CONCENTRATION"
        elif len(authors)==1:
            flag="SINGLE_CONTRIBUTOR"
        crit=crit_map.get(d,1)
        results.append({
            "path":d,
            "total_commits":total,
            "authors":authors,
            "top_concentration":top_pct,
            "criticality":crit,
            "flag":flag
        })

    results.sort(key=lambda r: (r["flag"] is not None, r["top_concentration"]*r["criticality"]), reverse=True)

    summary={
        "directories_analyzed": len(results),
        "time_window_days": args.days,
        "high_concentration_count": sum(1 for r in results if r["flag"]=="HIGH_CONCENTRATION"),
        "single_contributor_count": sum(1 for r in results if r["flag"]=="SINGLE_CONTRIBUTOR")
    }

    with open(args.out,"w") as f:
        json.dump({"summary":summary,"directories":results}, f, indent=2)

    print(json.dumps(summary, indent=2))

if __name__=="__main__":
    main()
