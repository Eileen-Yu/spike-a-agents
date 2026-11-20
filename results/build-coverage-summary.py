#!/usr/bin/env python3
"""Scorecard for the v3-standard quickstart coverage run (results/coverage/quickstarts-v3)."""
import re, datetime
from pathlib import Path
HERE = Path(__file__).resolve().parent
OUT = HERE / "coverage" / "quickstarts-v3"
LEDGER = OUT / "ledger.tsv"

def rows():
    if not LEDGER.exists(): return []
    lines = LEDGER.read_text().splitlines()
    head = lines[0].lstrip("# ").split("\t")
    return [dict(zip(head, l.split("\t"))) for l in lines[1:] if l.strip() and not l.startswith("#")]

def tok(v):
    try: n = int(str(v).replace(",", ""))
    except Exception: return "-"
    return f"{n/1e6:.1f}M" if n >= 1e6 else f"{n/1e3:.0f}k"

def wall(v):
    try: s = int(v); return f"{s//60}m{s%60:02d}s"
    except Exception: return "-"

def main():
    rs = rows()
    if not rs: return
    ok = sum(1 for r in rs if r["status"].startswith("ok"))
    now = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    out = ["# Quickstart coverage — v3 standard", "",
           f"_Updated {now}._ Prompt: `text-quickstart` block in [`../../spike-prompt.md`](../../spike-prompt.md). Claude, MCP signed in, graded by the harness (proof through Catalyst), one cell at a time with per-cell cleanup.", "",
           f"**{ok}/{len(rs)} ok** (pre-v3 README-follow run, self-graded: 15/15)", "",
           "| Quickstart | Result | kind | via Catalyst | MCP calls | tokens in | time | id |", "|---|---|---|---|---:|---:|---:|---|"]
    for r in rs:
        out.append(f"| {r['slug'].removeprefix('qs-')} | {'ok' if r['status'].startswith('ok') else '**'+r['status']+'**'} | {r.get('kind','-')} | {r.get('via','-')} | {r.get('mcp_calls','-')} | {tok(r.get('tokens_in'))} | {wall(r.get('wall_s'))} | `{r.get('agent_id','-')}` |")
    (OUT / "SCORECARD.md").write_text("\n".join(out) + "\n")
    print(f"quickstarts v3: {ok}/{len(rs)} ok")

if __name__ == "__main__":
    main()
