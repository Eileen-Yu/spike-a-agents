#!/usr/bin/env python3
"""Build a self-contained Spike A summary matrix from done.tsv + per-cell logs."""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

RESULTS = Path(__file__).resolve().parent
DONE = RESULTS / "done.tsv"
OUT = RESULTS / "SUMMARY.md"

FRAMEWORKS = [
    ("langgraph", "LangGraph", "python/langgraph"),
    ("langchain", "LangChain", "python/langchain"),
    ("crewai", "CrewAI", "python/crewai"),
    ("adk", "Google ADK", "python/adk"),
    ("strands", "Strands", "python/strands"),
    ("pydantic-ai", "Pydantic AI", "python/pydantic-ai"),
    ("openai-agents", "OpenAI Agents", "python/openai-agents"),
    ("claude-agents", "Claude Agent SDK", "python/claude-agents"),
    ("smolagents", "smolagents", "python/smolagents"),
    ("deepagents", "Deep Agents", "python/deepagents"),
    ("holmesgpt", "HolmesGPT", "python/holmesgpt"),
    ("dapr-agents", "Dapr Agents", "python/dapr-agents"),
    ("byoa", "BYOA", "python/byoa"),
    ("microsoft-agent-framework", ".NET MAF", "dotnet/microsoft-agent-framework"),
    ("spring-ai", "Spring AI", "java/spring-ai"),
    ("langchaingo", "LangChainGo", "go/langchaingo"),
    ("eino", "Eino", "go/eino"),
    ("mastra", "Mastra", "typescript/mastra"),
    ("goose", "Goose", "rust/goose"),
]
CLIENTS = ("claude", "codex", "copilot")


def load_done_latest() -> dict[tuple[str, str], tuple[str, str]]:
    rows: dict[tuple[str, str], tuple[str, str]] = {}
    if not DONE.exists():
        return rows
    for line in DONE.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        rows[(parts[0], parts[1])] = (parts[2], parts[3] if len(parts) > 3 else "")
    return rows


def count_oks(slug: str, client: str) -> int:
    if not DONE.exists():
        return 0
    return sum(
        1
        for line in DONE.read_text().splitlines()
        if (p := line.split("\t"))
        and len(p) >= 3
        and p[0] == slug
        and p[1] == client
        and p[2] == "ok"
    )


def pick_log(slug: str, client: str) -> Path | None:
    primary = RESULTS / f"{slug}-{client}.log"
    if primary.exists() and primary.stat().st_size > 0:
        return primary
    rotated = sorted(RESULTS.glob(f"{slug}-{client}-*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    for p in rotated:
        if p.stat().st_size > 40:  # skip "Credit balance is too low" stubs when better exists
            return p
    if primary.exists():
        return primary
    return rotated[0] if rotated else None


def result_section(text: str) -> str:
    """Prefer the last RESULT block; fall back to whole text."""
    # Structured block starting at RESULT line
    matches = list(re.finditer(r"(?im)^(?:\*\*)?RESULT(?:\*\*)?\b.*", text))
    if not matches:
        # Copilot one-liner
        m = re.search(r"(?im)\*\*RESULT\*\*[^\n]+", text)
        return m.group(0) if m else text[-4000:]
    start = matches[-1].start()
    # end at next major section or EOF
    rest = text[start:]
    m_end = re.search(r"(?im)\n(?=Correction to my last message:|Console:|# |\Z)", rest[20:])
    if m_end:
        return rest[: 20 + m_end.start()]
    return rest[:3500]


def parse_cell(slug: str, client: str, note: str) -> dict:
    out: dict = {
        "slug": slug,
        "client": client,
        "note": note,
        "kind": "",
        "id": "",
        "project": "",
        "skills": "",
        "friction": [],
        "ok": False,
        "log": "",
    }
    log = pick_log(slug, client)
    if not log:
        if "Agent" in note:
            out["kind"] = "Agent"
        elif "App" in note:
            out["kind"] = "App"
        out["ok"] = note.startswith("ok") or "ok" in note.lower()
        return out
    out["log"] = log.name
    text = log.read_text(errors="replace")
    sec = result_section(text)

    # one-line Copilot style
    m = re.search(
        r"RESULT[^\n]*deploy/run\s+\*\*?ok\*\*?[^\n]*project\s+`([^`]+)`[^\n]*resource kind\s+\*\*?(\w+)\*\*?[^\n]*(?:Agent/App ID|id)\s+`([^`]+)`[^\n]*(?:Friction:\s*([^\n]+))?.*?Skills used:\s*([^\n]+)",
        sec,
        re.I | re.S,
    )
    if m:
        out["ok"] = True
        out["project"] = m.group(1)
        out["kind"] = m.group(2)
        out["id"] = m.group(3)
        if m.group(4):
            out["friction"] = [m.group(4).strip()[:160]]
        out["skills"] = re.sub(r"[`*]", "", m.group(5))[:180]
    else:
        if re.search(r"(?im)deploy:\s*ok", sec) and re.search(r"(?im)run:\s*ok", sec):
            out["ok"] = True
        if re.search(r"(?im)RESULT[^\n]*\bok\b", sec):
            out["ok"] = True

        m = re.search(r"(?im)^resource kind:\s*(Agent|App)\b", sec)
        if m:
            out["kind"] = m.group(1)
        m = re.search(r"(?im)^(?:agent/app id|agent:|app:)\s*([A-Za-z0-9._-]+)", sec)
        if m:
            out["id"] = m.group(1)
        # BYOA style without resource kind
        if not out["kind"]:
            if re.search(r"(?im)^app:\s*", sec):
                out["kind"] = "App"
            elif re.search(r"(?im)^agent:\s*", sec):
                out["kind"] = "Agent"
        if not out["id"]:
            m = re.search(r"(?im)^app:\s*([A-Za-z0-9._-]+)", sec)
            if m:
                out["id"] = m.group(1)
                out["kind"] = out["kind"] or "App"
            m = re.search(r"(?im)^agent:\s*([A-Za-z0-9._-]+)", sec)
            if m:
                out["id"] = m.group(1)
                out["kind"] = out["kind"] or "Agent"

        m = re.search(r"(?im)^project:\s*([A-Za-z0-9._-]+)", sec)
        if m:
            out["project"] = m.group(1)

        m = re.search(r"(?im)^skills(?: used)?:\s*(.+)$", sec)
        if m:
            out["skills"] = re.sub(r"\s+", " ", m.group(1)).strip()[:180]

        # Friction section
        fm = re.search(r"(?is)(?:\*\*)?Friction(?:\*\*)?:\s*\n((?:[-*].+\n?)+)", sec)
        if fm:
            for line in fm.group(1).splitlines():
                line = re.sub(r"^[-*]\s+", "", line).strip()
                line = re.sub(r"\*\*([^*]+)\*\*:?\s*", r"\1: ", line)
                if line:
                    out["friction"].append(line[:160])
                if len(out["friction"]) >= 4:
                    break
        else:
            m = re.search(r"(?i)Friction:\s*(.+)", sec)
            if m:
                out["friction"] = [m.group(1).strip()[:160]]

    # Fallbacks from done.tsv note
    if not out["kind"]:
        if re.search(r"\bAgent\b", note):
            out["kind"] = "Agent"
        elif re.search(r"\bApp\b", note):
            out["kind"] = "App"
    if not out["ok"] and (note.startswith("ok") or note == "" and "ok" in note):
        pass
    if note and note.split("·")[0].strip() == "ok" or note.startswith("ok") or "see " in note and "fail" not in note.lower():
        # done.tsv says ok
        if "fail" not in note.lower() and "blocked" not in note.lower():
            # trust done status separately
            pass

    # Sanitize bogus ids
    if out["id"] in {"service", "entities", "entity", "no", "1", ",", "ok"}:
        out["id"] = ""

    return out


def cell_short(status: str | None, parsed: dict, slug: str, client: str) -> str:
    if status == "blocked":
        return "blocked (credit)"
    if status == "fail" and not parsed.get("ok"):
        return "fail"
    if status == "ok" or parsed.get("ok"):
        bits = ["ok"]
        if parsed.get("kind"):
            bits.append(parsed["kind"])
        if slug == "langgraph" and client == "claude":
            bits.append(f"{count_oks(slug, client)}/3")
        if parsed.get("id"):
            bits.append(parsed["id"])
        return " · ".join(bits)
    return "—"


def main() -> None:
    done = load_done_latest()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    parsed_all: dict[tuple[str, str], dict] = {}

    ok_n = fail_n = blocked_n = missing_n = 0
    agent_n = app_n = unknown_n = 0

    for slug, _name, _path in FRAMEWORKS:
        for client in CLIENTS:
            st, note = done.get((slug, client), (None, ""))
            p = parse_cell(slug, client, note)
            parsed_all[(slug, client)] = p
            label = cell_short(st, p, slug, client)
            if label.startswith("ok"):
                ok_n += 1
                if p.get("kind") == "Agent":
                    agent_n += 1
                elif p.get("kind") == "App":
                    app_n += 1
                else:
                    unknown_n += 1
            elif label.startswith("fail"):
                fail_n += 1
            elif label.startswith("blocked"):
                blocked_n += 1
            else:
                missing_n += 1

    lines: list[str] = []
    lines += [
        "# Spike A — consolidated results matrix",
        "",
        f"Generated: {now}  ",
        "Org: `cattle-ackbar` · Plugin: `diagrid@diagrid` 0.10.2 · CLI: `diagrid` 1.130.0  ",
        "Self-contained: status, resource kind, id, and friction are inline. You should not need to open per-cell logs for the overview.",
        "",
        "## Scoreboard",
        "",
        "| ok | fail | blocked | missing | of which Agent | of which App | kind unclear |",
        "|---:|---:|---:|---:|---:|---:|---:|",
        f"| {ok_n} | {fail_n} | {blocked_n} | {missing_n} | {agent_n} | {app_n} | {unknown_n} |",
        "",
        f"LangGraph × Claude variance (CAP-2783): **{count_oks('langgraph', 'claude')}/3**",
        "",
        "## Matrix",
        "",
        "| # | Framework | Claude | Codex | Copilot |",
        "|---|---|---|---|---|",
    ]
    for i, (slug, name, _path) in enumerate(FRAMEWORKS, 1):
        cells = []
        for client in CLIENTS:
            st, _note = done.get((slug, client), (None, ""))
            cells.append(cell_short(st, parsed_all[(slug, client)], slug, client).replace("|", "/"))
        lines.append(f"| {i} | {name} | {cells[0]} | {cells[1]} | {cells[2]} |")

    lines += ["", "## Per-cell detail", ""]
    for slug, name, path in FRAMEWORKS:
        lines.append(f"### {name} (`{path}`)")
        lines.append("")
        for client in CLIENTS:
            st, note = done.get((slug, client), (None, ""))
            p = parsed_all[(slug, client)]
            lines.append(f"**{client}** — {cell_short(st, p, slug, client)}")
            lines.append("")
            bits = []
            if p.get("project"):
                bits.append(f"project `{p['project']}`")
            if p.get("kind"):
                bits.append(f"kind `{p['kind']}`")
            if p.get("id"):
                bits.append(f"id `{p['id']}`")
            if bits:
                lines.append("- " + " · ".join(bits))
            if p.get("skills"):
                lines.append(f"- skills: {p['skills']}")
            for fr in p.get("friction") or []:
                lines.append(f"- friction: {fr}")
            if not bits and not p.get("friction") and not p.get("skills"):
                lines.append(f"- note: {note or '(no RESULT fields parsed)'}")
            if p.get("log"):
                lines.append(f"- log: `{p['log']}`")
            lines.append("")
        lines.append("")

    lines += [
        "## Shared friction (recurring across cells)",
        "",
        "| Theme | What we saw |",
        "|---|---|",
        "| Agent vs App | Intended path is Diagrid `Agent`. Early / some Codex runs used plain `App` when “no workflow wrapper” was over-read. |",
        "| Skills push durability | `diagrid-agent-scaffold` steers toward workflow runners; Spike A kept plain HTTP `/run`. |",
        "| MCP gaps | No MCP tunnel/invoke — proof needed `diagrid call invoke`. |",
        "| Quotas | 3-project cap; identity quota forced reusing `order-agent` on later frameworks. |",
        "| Readiness | Connected ≠ healthy; App ID can lag Agent ready; need `/healthz` + short wait. |",
        "| Ports | 8000 often busy → alternate port. |",
        "| Client hang | Clients leave tunnels up; loop kicks ~20s after RESULT. |",
        "| Claude API credit | `Credit balance is too low` blocked LangGraph variance until topped up. |",
        "",
        "## Raw artifacts (optional)",
        "",
        "- Per-cell transcripts: `results/<slug>-<client>.log`",
        "- Run working copies: `~/spike-runs/<framework>-<timestamp>/`",
        "- Loop ledger: `results/done.tsv`, `results/loop.stdout`",
        "",
        "This file is the overview; open logs only if you need the full transcript.",
        "",
    ]
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT} ({ok_n} ok, {fail_n} fail, {missing_n} missing; Agent={agent_n} App={app_n})")


if __name__ == "__main__":
    main()
