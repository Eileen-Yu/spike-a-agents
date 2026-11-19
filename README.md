# Spike A (CAP-2783) — plain agents through the Diagrid plugin

Person A week-1 spike: take a **plain** agent (no Catalyst / Dapr / workflow wrapper /
identity middleware), ask the Diagrid plugin to deploy it to Catalyst, and prove a run
(`order 42` → answer contains **shipped**).

Linear: [CAP-2783](https://linear.app/diagrid/issue/CAP-2783) · triage:
[CAP-2785](https://linear.app/diagrid/issue/CAP-2785)

**Results overview (start here):** [`results/SUMMARY.md`](results/SUMMARY.md)

---

## Should this be its own repo?

**Yes, as a private archive** (handoff, triage, CAP-2783 comment) — samples + summary +
scripts. This directory is already a local git repo; push to a **private** GitHub repo
when ready (personal or `diagridio`).

**No need to mirror live Catalyst projects** into git. The cloud org/project is
environment state; document names below, do not export tokens or full resource YAML
with secrets.

---

## What belongs in git

| Include | Why |
|---|---|
| `python/`, `dotnet/`, `java/`, `go/`, `typescript/`, `rust/` | Plain framework samples |
| `results/SUMMARY.md`, `results/spike-prompt.md`, `results/matrix.md` | One-page results + prompt |
| `results/done.tsv`, `results/queue-status.md`, `results/loop.stdout` | Machine ledger of the matrix |
| `results/*-metrics.md` | session_metrics rows (when present) |
| `new-run.sh`, `run-matrix-loop.sh`, `smoke-test.sh`, `session_metrics.py` | How runs were produced |
| `.env.example`, this README | Onboarding |

| Keep out of git | Why |
|---|---|
| `.env` | API keys (`OPENAI_*`, `ANTHROPIC_*`) |
| `**/.venv`, `node_modules`, `target`, `bin`, `obj` | Build junk (multi‑GB) |
| `~/spike-runs/**` | Timestamped working copies (~GB); recreate with `./new-run.sh` |
| Raw `results/*-{claude,codex,copilot}.log` | Full transcripts. **Codex logs embedded live API keys from `.env`** — stay on disk only; scrub before attaching to an issue |
| Live Catalyst API tokens / connection strings | Never |
| Diagrid org secrets, service-account keys | Never |

Catalyst **project names** (document only, not exported):

- Org used for the spike: `cattle-ackbar` (API `https://api.r1.diagrid.io`)
- Primary project reused: `langgraph-spike`
- Common identities: Agent `order-agent`, caller App `spike-caller` (plus per-run agents when quota allowed)

---

## Layout

```text
spike-a-agents/
  python|dotnet|java|go|typescript|rust/   # one sample per framework (+ BYOA)
  results/
    SUMMARY.md          # consolidated matrix — read this
    spike-prompt.md     # prompt used for plugin runs
    done.tsv            # ok/fail ledger
    *-claude|codex|copilot.log   # optional full transcripts
  new-run.sh            # copy a sample → ~/spike-runs/<fw>-<ts>
  run-matrix-loop.sh    # batch framework × client
  smoke-test.sh         # local HTTP smoke (no Catalyst)
  session_metrics.py    # CAP-2789-style metrics from client logs
  .env.example
```

Run copies are **outside** the repo:

```text
~/spike-runs/<framework>-<timestamp>/   # do not commit
```

---

## Samples

Every sample is the same agent shape so frameworks compare fairly:

- tool `get_order_status(order_id)` → `Order <id>: shipped, arriving Friday.`
- HTTP `POST /run {"prompt":"..."}` → `{"answer":"..."}` (plus `GET /healthz` where needed)
- pass when asking about order **42** returns **shipped**

| Language | Framework | Path |
|---|---|---|
| Python | LangGraph | `python/langgraph` |
| Python | LangChain | `python/langchain` |
| Python | CrewAI | `python/crewai` |
| Python | Google ADK | `python/adk` |
| Python | Strands | `python/strands` |
| Python | Pydantic AI | `python/pydantic-ai` |
| Python | OpenAI Agents | `python/openai-agents` |
| Python | Claude Agent SDK | `python/claude-agents` |
| Python | smolagents | `python/smolagents` |
| Python | Deep Agents | `python/deepagents` |
| Python | HolmesGPT | `python/holmesgpt` |
| Python | Dapr Agents | `python/dapr-agents` |
| Python | BYOA (no framework) | `python/byoa` |
| .NET | Microsoft Agent Framework | `dotnet/microsoft-agent-framework` |
| Java | Spring AI | `java/spring-ai` |
| Go | LangChainGo | `go/langchaingo` |
| Go | Eino | `go/eino` |
| TypeScript | Mastra | `typescript/mastra` |
| Rust | Goose | `rust/goose` |

```sh
cp .env.example .env   # fill keys
./smoke-test.sh        # local only — not Spike A
```

---

## Spike A run (plugin → Catalyst)

```sh
./new-run.sh python/langgraph    # prints ~/spike-runs/langgraph-<ts>
cd ~/spike-runs/langgraph-<ts>
# Use Claude Code / Codex / Copilot with Diagrid plugin + prompt in results/spike-prompt.md
```

Or batch: `./run-matrix-loop.sh` (kicks the client ~20s after `RESULT`).

**Rules for Spike A:** prefer Diagrid `Agent` resource; **no** workflow runner wrapper;
**no** identity/OAuth middleware. (Durable wrapper / identity = Week 2 skills.)

Clients used in the matrix:

| Client | Product | Model (this spike) |
|---|---|---|
| Claude | Claude Code | `claude-fable-5-2` |
| Codex | Codex CLI | `gpt-5.4` |
| Copilot | GitHub Copilot CLI | Fusion-selected (varied) |

---

## Person A checklist (Week 1)

- [x] Samples + local smoke
- [x] Matrix runs → [`results/SUMMARY.md`](results/SUMMARY.md)
- [ ] Comment SUMMARY on CAP-2783
- [ ] File distinct frictions as issues (spike milestone) for CAP-2785 triage
- [ ] Week 2 skill/plugin fixes only **after** triage — not part of this repo’s job

---

## Regenerating the summary

```sh
python3 results/build-summary-matrix.py   # rewrites results/SUMMARY.md
```
