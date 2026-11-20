#!/usr/bin/env python3
"""Regenerate the Spike A v3 records from the batch ledger.

Writes results/plugin-quality-v3/SCORECARD.md and replaces the block between
<!-- v3:begin --> and <!-- v3:end --> in results/SUMMARY.md. Safe to run any
time (run-matrix-loop.sh calls it after every cell through publish.sh).

Logs stay local (gitignored: they can hold credentials). Only redacted RESULT
excerpts are copied into the scorecard.
"""
import csv, datetime, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent            # results/
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "plugin-quality-v3"
LEDGER = OUT / "ledger.tsv"
SUMMARY = HERE / "SUMMARY.md"
FINDINGS = OUT / "FINDINGS.md"

NAMES = {
    "langgraph": "LangGraph", "langchain": "LangChain", "crewai": "CrewAI", "adk": "Google ADK",
    "strands": "Strands", "pydantic-ai": "Pydantic AI", "openai-agents": "OpenAI Agents",
    "claude-agents": "Claude Agent SDK", "smolagents": "smolagents", "deepagents": "Deep Agents",
    "holmesgpt": "HolmesGPT", "dapr-agents": "Dapr Agents", "byoa": "BYOA",
    "microsoft-agent-framework": ".NET MAF", "spring-ai": "Spring AI", "langchaingo": "LangChainGo",
    "eino": "Eino", "mastra": "Mastra", "goose": "Goose",
}
ORDER = list(NAMES)
FAIL_TICKET = {"dapr-agents": "CAP-2932"}
TOP_FINDINGS = [
    "1. **Skills have no first-class \"connect an existing agent\" path**: App vs Agent contradicts (landed on App: Claude 8/21, Codex 2/2, Copilot 1/2), skills never say Catalyst doesn't host your code, no documented way to prove a run, name checks mislead — [CAP-2876](https://linear.app/diagrid/issue/CAP-2876) (Urgent)",
    "2. **Tunnel return path times out at ~10s → HTTP 502** on slow agent turns; Agent kind has no timeout setting — [CAP-2931](https://linear.app/diagrid/issue/CAP-2931)",
    "3. **Credentials in transcripts**: agent printed `~/.diagrid/creds`; `get_connection` returns tokens into chat — [CAP-2926](https://linear.app/diagrid/issue/CAP-2926)",
    "4. **Invisible quotas**: pub/sub 10-topic cap (Dapr Agents crashed on leftover topics, ok on a clean project) and identity cap — [CAP-2932](https://linear.app/diagrid/issue/CAP-2932)",
    "5. **MCP vs CLI on different env/org**, no CLI fallback, `DIAGRID_MCP_URL` undocumented — [CAP-2921](https://linear.app/diagrid/issue/CAP-2921)",
    "6. **MCP/CLI behaviour misleads**: readiness, silent side effects, list filters, dry run, console URL — [CAP-2929](https://linear.app/diagrid/issue/CAP-2929)",
    "7. **Cost**: ~1.9M tokens / ~3 min per connect (≈ week-1 baseline); Copilot 4–8 min — [CAP-2541](https://linear.app/diagrid/issue/CAP-2541)",
]
CLIENTS = ["claude", "codex", "copilot"]
# Spec matrix (CAP-2783): every framework × Claude; LangGraph+BYOA × Codex/Copilot; LangGraph × Claude ×3
def planned():
    cells = {(s, "claude"): 1 for s in ORDER}
    cells[("langgraph", "claude")] = 3
    for s in ("langgraph", "byoa"):
        for c in ("codex", "copilot"):
            cells[(s, c)] = 1
    return cells

REDACT = [
    (re.compile(r"eyJ[\w-]{8,}\.[\w-]{8,}\.[\w-]{8,}"), "[REDACTED-JWT]"),
    (re.compile(r"(?i)(dapr-api-token|authorization|api[_-]?key|token)([\"':= ]+(bearer )?)(?!<)([A-Za-z0-9._~+/=-]{20,})"), r"\1\2[REDACTED]"),
    (re.compile(r"sk-[A-Za-z0-9_-]{16,}"), "[REDACTED-KEY]"),
    (re.compile(r"\b[A-Za-z0-9+/]{60,}={0,2}"), "[REDACTED-B64]"),
]
def redact(s):
    for rx, rep in REDACT:
        s = rx.sub(rep, s)
    return s

def read_ledger():
    if not LEDGER.exists():
        return []
    rows = []
    with LEDGER.open() as f:
        header = None
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            if line.startswith("#"):
                header = line.lstrip("# ").split("\t")
                continue
            vals = line.split("\t")
            rows.append(dict(zip(header, vals + [""] * (len(header) - len(vals)))))
    return rows

def metrics_row(slug, client, attempt):
    p = OUT / f"{slug}-{client}-{attempt}-metrics.md"
    if not p.exists():
        return {}
    lines = [l for l in p.read_text().splitlines() if l.startswith("|")]
    if len(lines) < 3:
        return {}
    head = [c.strip() for c in lines[0].strip("|").split("|")]
    vals = [c.strip() for c in lines[2].strip("|").split("|")]
    return dict(zip(head, vals))

def result_excerpt(log):
    if not log.exists():
        return ""
    t = log.read_text(errors="replace")
    i = t.find("RESULT")
    if i < 0:
        return redact("\n".join(t.strip().splitlines()[-25:]))
    start = t.rfind("\n", 0, i) + 1
    body = t[start:].strip()
    body = body.replace("```", "").strip()
    lines = body.splitlines()[:80]
    return redact("\n".join(lines))

def headline(log):
    if not log.exists():
        return ""
    for line in log.read_text(errors="replace").splitlines():
        line = line.strip()
        if line and not line.startswith(("⚠", "RESULT", "```")):
            return redact(line[:220])
    return ""

def _int(v):
    try: return int(str(v).replace(",", ""))
    except Exception: return None

def fmt_s(s):
    return f"{s//60}m {s%60:02d}s" if s is not None else "-"

def batch_windows():
    """(start, end) wall-clock windows from loop.log, one per runner invocation."""
    log = OUT / "loop.log"
    if not log.exists(): return []
    import datetime as dt
    wins, start = [], None
    for line in log.read_text(errors="replace").splitlines():
        m = re.search(r"matrix v3 start (\S+)", line)
        if m: start = m.group(1)
        m2 = re.search(r"(parallel batch done|queue empty|SPIKE_MAX_CELLS=\d+ reached) ?(\S+)?", line)
        if m2 and start:
            end = m2.group(2)
            wins.append((start, end)); start = None
    return wins

def cost_section(rows):
    out = ["## Time and token cost", "",
           "Per cell: `wall` = harness clock from cell start to grading (all clients); Claude also has session wall from `session_metrics.py`.",
           "Claude `tokens in` = fresh input + cache reads + cache writes (what the model read). Codex reports one total (in+out). Copilot reports ↑/↓ and AI Credits.", "",
           "| Client | cells | ok | tokens in (sum) | tokens in (avg) | tokens out (sum) | wall (sum) | wall (avg) | wall (min–max) | AI credits |",
           "|---|---:|---:|---:|---:|---:|---|---|---|---:|"]
    tot_in = tot_out = tot_w = 0; tot_n = 0
    for c in CLIENTS:
        rs = [r for r in rows if r["client"] == c]
        if not rs: continue
        ins = [x for x in (_int(r.get("tokens_in")) for r in rs) if x is not None]
        outs = [x for x in (_int(r.get("tokens_out")) for r in rs) if x is not None]
        ws = [x for x in (_int(r.get("wall_s")) for r in rs) if x is not None]
        cr = [float(r["credits"]) for r in rs if r.get("credits") not in (None, "", "-")]
        ok = sum(1 for r in rs if r["status"].startswith("ok"))
        out.append(f"| {c} | {len(rs)} | {ok} | {sum(ins):,} | {(sum(ins)//len(ins)) if ins else 0:,} | {sum(outs):,} | "
                   f"{fmt_s(sum(ws)) if ws else '-'} | {fmt_s(sum(ws)//len(ws)) if ws else '-'} | "
                   f"{(fmt_s(min(ws))+' – '+fmt_s(max(ws))) if ws else '-'} | {('%.2f' % sum(cr)) if cr else '-'} |")
        tot_in += sum(ins); tot_out += sum(outs); tot_w += sum(ws); tot_n += len(rs)
    out.append(f"| **all** | {tot_n} | | **{tot_in:,}** | | **{tot_out:,}** | **{fmt_s(tot_w)}** (cell-time) | | | |")
    wins = batch_windows()
    if wins:
        done = [(a, b) for a, b in wins if b]
        if done:
            out += ["", "Batch wall clock (completed runner invocations): " + "; ".join(f"{a[11:16]} → {b[11:16]} ({a[:10]})" for a, b in done)]
    out.append("")
    return out

def qs_v3_line():
    led = HERE / "coverage" / "quickstarts-v3" / "ledger.tsv"
    if not led.exists(): return []
    ls = [l.split("\t") for l in led.read_text().splitlines()[1:] if l.strip() and not l.startswith("#")]
    ok = sum(1 for c in ls if c[3].startswith("ok"))
    return [f"- **Quickstarts rerun to the v3 standard** (Claude, MCP on, harness-graded): **{ok}/{len(ls)} ok** — [`coverage/quickstarts-v3/SCORECARD.md`](coverage/quickstarts-v3/SCORECARD.md)", ""]

def status_cell(r):
    s = r.get("status", "")
    return f"**{s}**" if s == "ok" else f"**{s}** ❗" if s.startswith("fail") else s

def build():
    rows = read_ledger()
    plan = planned()
    now = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    done = {}
    for r in rows:
        done.setdefault((r["slug"], r["client"]), []).append(r)
    total_planned = sum(plan.values())
    total_done = sum(min(len(done.get(k, [])), n) for k, n in plan.items())
    ok = sum(1 for r in rows if r["status"].startswith("ok"))
    fails = [r for r in rows if r["status"].startswith("fail")]
    kinds = {"Agent": 0, "App": 0}
    for r in rows:
        if r.get("kind") in kinds:
            kinds[r["kind"]] += 1
    mcp_zero = sum(1 for r in rows if r["client"] == "claude" and r.get("mcp_calls") in ("0",))
    violations = [r for r in rows if r.get("violation", "-") not in ("-", "")]
    localhost = [r for r in rows if r.get("via") == "localhost"]

    # ---------- matrix ----------
    mat = ["| # | Framework | Claude | Codex | Copilot |", "|---|---|---|---|---|"]
    for n, slug in enumerate(ORDER, 1):
        cells = []
        for c in CLIENTS:
            want = plan.get((slug, c), 0)
            got = done.get((slug, c), [])
            if not want and not got:
                cells.append("—")
                continue
            parts = []
            for r in got:
                k = r.get("kind", "-")
                parts.append(("ok" if r["status"].startswith("ok") else r["status"]) + (f" · {k}" if k not in ("-", "") else ""))
            if len(got) < want:
                parts.append(f"pending {want - len(got)}")
            cells.append("<br>".join(parts))
        mat.append(f"| {n} | {NAMES[slug]} | " + " | ".join(cells) + " |")

    # ---------- run table ----------
    tab = ["| Framework | Client | # | Result | kind | via Catalyst | code | rule violation | id | MCP calls | tokens in | tokens out | model req | tools (all/catalyst/failed/rpt) | skills | wall |",
           "|---|---|---:|---|---|---|---|---|---|---:|---:|---:|---:|---|---|---|"]
    for r in rows:
        m = metrics_row(r["slug"], r["client"], r["attempt"])
        tab.append("| " + " | ".join([
            NAMES.get(r["slug"], r["slug"]), r["client"], r["attempt"], status_cell(r), r.get("kind", "-"),
            r.get("via", "-"), r.get("code", "-"), r.get("violation", "-"), f"`{r.get('agent_id','-')}`",
            r.get("mcp_calls", "-"), m.get("tokens in", r.get("tokens_in", "-")), m.get("tokens out", r.get("tokens_out", "-")),
            m.get("model requests", "-"), m.get("tool calls (all / catalyst / failed / repeated)", r.get("tools", "-")),
            m.get("skills (bytes)", "-"), m.get("wall time", fmt_s(_int(r.get("wall_s")))),
        ]) + " |")

    status_line = (f"**{total_done}/{total_planned} planned cells run** · ok {ok} · fail {len(fails)} · "
                   f"Agent {kinds['Agent']} · App {kinds['App']} · rule violations {len(violations)} · "
                   f"localhost-only proofs {len(localhost)} · Claude cells with 0 MCP calls {mcp_zero}")
    state = "complete" if total_done >= total_planned else "in progress"

    findings_link = "[`plugin-quality-v3/FINDINGS.md`](plugin-quality-v3/FINDINGS.md)" if FINDINGS.exists() else "_(findings file not written yet)_"

    # ---------- SCORECARD ----------
    sc = [
        "# Spike A v3 — plugin quality scorecard",
        "",
        f"_Updated {now} — {state}._ Regenerated by `results/build-v3-summary.py` after every cell.",
        "",
        "- Ticket: [CAP-2783](https://linear.app/diagrid/issue/CAP-2783) · triage [CAP-2785](https://linear.app/diagrid/issue/CAP-2785)",
        "- Prompt: canonical **v3** in [`../spike-prompt.md`](../spike-prompt.md) (user voice; no test framing, no plugin/class names; proof must go through Catalyst)",
        "- Env: staging Diagrid Cloud Plus, org `eileen-plus-test`, project `default`; Claude's plugin MCP pointed at staging via `DIAGRID_MCP_URL` ([CAP-2925](https://linear.app/diagrid/issue/CAP-2925)); CLI on the same org (preflight-checked)",
        "- Grading is outside the model: `git diff` of code/deps (runner/identity/diagrid SDK = `fail-rules`), proof path (`via`), session metrics",
        f"- Findings and their tickets: {findings_link}",
        "",
        status_line,
        "",
        "## Matrix (spec: every framework × Claude; LangGraph + BYOA × Codex/Copilot; LangGraph × Claude ×3)",
        "",
        *mat,
        "",
        *cost_section(rows),
        "## Runs",
        "",
        *tab,
        "",
        "## Per-run RESULT (redacted excerpt; full logs are local only)",
        "",
    ]
    for r in rows:
        log = OUT / r.get("log", "")
        sc += [f"<details><summary>{NAMES.get(r['slug'], r['slug'])} × {r['client']} #{r['attempt']} — {r['status']} — {headline(log)}</summary>",
               "", "```", result_excerpt(log), "```", "", "</details>", ""]
    (OUT / "SCORECARD.md").write_text("\n".join(sc) + "\n")

    # ---------- SUMMARY (whole file, one page) ----------
    def short_tok(v):
        n = _int(v)
        return f"{n/1e6:.1f}M" if n and n >= 1e6 else (f"{n/1e3:.0f}k" if n else "-")
    def cell_txt(r):
        m = metrics_row(r["slug"], r["client"], r["attempt"])
        tok = short_tok(m.get("tokens in", r.get("tokens_in")))
        w = _int(r.get("wall_s")); wall = f"{w//60}m{w%60:02d}s" if w else m.get("wall time", "-")
        st = "ok" if r["status"].startswith("ok") else f"**FAIL**"
        if r["status"] != "ok" and r["slug"] in FAIL_TICKET:
            st += f" [{FAIL_TICKET[r['slug']]}](https://linear.app/diagrid/issue/{FAIL_TICKET[r['slug']]})"
        kind = r.get("kind", "-")
        kind = "**App**" if kind == "App" else kind
        return f"{st} · {kind} · {tok} · {wall}"
    smat = ["| Framework | Claude | Codex | Copilot |", "|---|---|---|---|"]
    for slug in ORDER:
        cells = []
        for c in CLIENTS:
            want = plan.get((slug, c), 0); got = done.get((slug, c), [])
            if not want and not got: cells.append(""); continue
            parts = [(f"#{r['attempt']} " if want > 1 or len(got) > 1 else "") + cell_txt(r) for r in got]
            if len(got) < want: parts.append(f"_pending {want-len(got)}_")
            cells.append("<br>".join(parts))
        smat.append(f"| {NAMES[slug]} | " + " | ".join(cells) + " |")
    cost = ["| Client | cells | ok | avg tokens in | avg time | total tokens in | total time |", "|---|---:|---:|---:|---:|---:|---:|"]
    for c in CLIENTS:
        rs = [r for r in rows if r["client"] == c]
        if not rs: continue
        ins = [x for x in (_int(r.get("tokens_in")) for r in rs) if x]
        ws = [x for x in (_int(r.get("wall_s")) for r in rs) if x]
        ok_n = sum(1 for r in rs if r["status"].startswith("ok"))
        cost.append(f"| {c} | {len(rs)} | {ok_n} | {short_tok(sum(ins)//len(ins)) if ins else '-'} | "
                    f"{fmt_s(sum(ws)//len(ws)) if ws else '-'} | {short_tok(sum(ins)) if ins else '-'} | {fmt_s(sum(ws)) if ws else '-'} |")
    by_client = []
    for c in CLIENTS:
        rs = [r for r in rows if r["client"] == c]
        want = sum(n for (s_, cc), n in plan.items() if cc == c)
        if want:
            # per cell: a cell counts as ok if its LATEST attempt is ok (reruns replace earlier tries);
            # LangGraph × Claude needs all of its planned attempts, each counted
            cells_c = [k for k in plan if k[1] == c]
            ok_c = 0; ran_c = 0
            for k in cells_c:
                got = done.get(k, [])
                n = plan[k]
                if n > 1:
                    ok_c += sum(1 for r in got[:max(n, len(got))] if r["status"].startswith("ok")); ran_c += min(len(got), n) if len(got) <= n else len(got)
                    continue
                if got:
                    ran_c += 1; ok_c += got[-1]["status"].startswith("ok")
            want_c = sum(max(plan[k], len(done.get(k, []))) if plan[k] > 1 else 1 for k in cells_c)
            by_client.append(f"{c} {ok_c}/{want_c}" + ("" if ran_c >= want_c else f" ({want_c-ran_c} pending)"))
    page = [
        "# Spike A — results ([CAP-2783](https://linear.app/diagrid/issue/CAP-2783))",
        "",
        f"_Updated {now}. Regenerated after every cell by `results/build-v3-summary.py` — don't edit by hand._",
        "",
        "**Current run = v3:** user-voice prompt ([`spike-prompt.md`](spike-prompt.md)), plugin MCP signed in, staging Plus `eileen-plus-test`/`default`, graded outside the model (git diff, proof path). Plugin 0.10.2, Claude = claude-opus-5-5.",
        "",
        f"**Score (cells ok, latest attempt): {' · '.join(by_client)}** · landed on App instead of Agent: {kinds['App']} runs · rule violations: {len(violations)} · localhost proofs: {len(localhost)}",
        "",
        "## Each cell — result · resource kind · tokens in · time",
        "",
        *smat,
        "",
        "Tokens in = everything the model read (incl. cache). Time = harness clock per cell. Full per-run detail: [`plugin-quality-v3/SCORECARD.md`](plugin-quality-v3/SCORECARD.md).",
        "",
        "## Cost",
        "",
        *cost,
        "",
        "## Findings (7 tickets)",
        "",
        *TOP_FINDINGS,
        "",
        "Evidence counts per finding: [`plugin-quality-v3/FINDINGS.md`](plugin-quality-v3/FINDINGS.md).",
        '',
        '## Who fixes what',
        '',
        '| Ticket | Skill / plugin (this project) | Other teams |',
        '|---|---|---|',
        '| [CAP-2876](https://linear.app/diagrid/issue/CAP-2876) connect-an-existing-agent path | **Nearly all of it**: App vs Agent, where the code runs, proof recipe, name and project checks | MCP `invoke` tool (MCP server, follow-up) |',
        '| [CAP-2926](https://linear.app/diagrid/issue/CAP-2926) credentials in chat | "Never read `~/.diagrid/*`" rule, optional hook | `get_connection` returns the token inline (MCP server); base64 creds file (CLI) |',
        '| [CAP-2932](https://linear.app/diagrid/issue/CAP-2932) invisible quotas | Check usage first; say what to do at a cap; Dapr Agents hint | Topic cap missing from `get_usage`; unused topics never cleaned up (platform) |',
        '| [CAP-2921](https://linear.app/diagrid/issue/CAP-2921) MCP vs CLI env mismatch | Compare whoami, CLI fallback, document `DIAGRID_MCP_URL` | `invalid_client` error message (auth server) |',
        '| [CAP-2931](https://linear.app/diagrid/issue/CAP-2931) tunnel ~10s timeout | Troubleshooting note only | **Nearly all**: tunnel proxy timeout, Agent timeout field (platform). Verify on prod first |',
        '| [CAP-2929](https://linear.app/diagrid/issue/CAP-2929) MCP/CLI behaviour | Work around only | **Nearly all**: readiness, side effects, filters, dry run, exit code, console URL (MCP / CLI / API) |',
        '| [CAP-2920](https://linear.app/diagrid/issue/CAP-2920) example READMEs | — | **All**: `python-ai`, `rust-ai`, `catalyst-quickstarts` READMEs |',
        '',
        "In short, the main fix ([CAP-2876](https://linear.app/diagrid/issue/CAP-2876)) is entirely in the skills, and it's also what makes a connect slow.",
        "",
        "## Coverage (separate from the quality score, NOT run to the v3 standard)",
        "",
        "Run before v3 (2026-11-19 15:35–16:32 PT), Claude only, one run each, MCP not signed in (0 MCP calls), graded by the model's own RESULT. They answer \"does the README work\", not \"how good is the plugin\".",
        "",
        *qs_v3_line(),
        "- Official quickstarts `agents/*` (README happy path, staging Plus): **15/15 ok**. Their leftover topics later filled the pub/sub cap ([CAP-2932](https://linear.app/diagrid/issue/CAP-2932))",
        "- Crash recovery (LangGraph, CrewAI, Mastra): **3/3** crash + resume",
        "- `*-ai/examples` sample (mostly local `dapr run`): Mastra, Eino, Goose ok; python-ai LangGraph needs Dapr ≥ 1.18 ([CAP-2920](https://linear.app/diagrid/issue/CAP-2920))",
        "",
        "Ledgers: [`coverage/`](coverage/) · details in [`archive/SUMMARY-pre-v3.md`](archive/SUMMARY-pre-v3.md#official-quickstarts-coverage-plus).",
        "",
        "## Earlier runs (superseded, not a quality score)",
        "",
        "Week-1 57/57 and v1/v2 used prompts with CLI recipes; v1/v2 also ran with MCP not signed in (0 MCP calls, ~0.4–0.8M tokens/cell). Their token numbers are **not comparable** to v3 (different prompt and task, not just MCP). They still show one real scenario: with MCP unavailable an agent can finish via the CLI, but no skill tells it how ([CAP-2921](https://linear.app/diagrid/issue/CAP-2921)). Kept for history only: [`archive/SUMMARY-pre-v3.md`](archive/SUMMARY-pre-v3.md).",
        "",
    ]
    SUMMARY.write_text("\n".join(page))
    print(f"v3 summary: {status_line}")

if __name__ == "__main__":
    build()
