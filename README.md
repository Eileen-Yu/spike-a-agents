# Spike A — plain agents through the Diagrid plugin

[CAP-2783](https://linear.app/diagrid/issue/CAP-2783): can the Diagrid plugin take a **plain** agent (no workflow wrapper, no identity middleware) and run it on Catalyst?

**Pass** = ask about order **42**, answer contains **shipped**.

Three coverage layers (do not mix conclusions):

| Layer | What we ran | Controlled same task? |
|---|---|---|
| Spike A plain samples (this repo) | Framework × Claude/Codex/Copilot | Yes — same `get_order_status` agent |
| [`catalyst-quickstarts`](https://github.com/diagridio/catalyst-quickstarts) `agents/*` | Official durable quickstarts | No — different demos per framework |
| `*-ai` repo `examples/` | Adapter SDK demos (often local `dapr run`) | No — different path from plugin plain-connect |

Full tables: [`results/SUMMARY.md`](results/SUMMARY.md). Triage: [CAP-2785](https://linear.app/diagrid/issue/CAP-2785).

## How to test

**Org:** use a plan with App ID / identity headroom (e.g. Cloud Plus). Free **10/10** forces Agent reuse and muddies “create works” conclusions. Check `diagrid whoami` before you start.

```sh
cp .env.example .env
./new-run.sh python/langgraph   # → ~/spike-runs/langgraph-<ts>
cd ~/spike-runs/langgraph-<ts>
```

In that directory, run Claude Code / Codex / Copilot with the Diagrid plugin and the **plain** prompt in [`results/spike-prompt.md`](results/spike-prompt.md) (§1) — **goal + Rules + success only** (no CLI cookbook). That file also records different prompts for quickstarts / crash / `*-ai/examples`.

Rules for the **plain** path: prefer Diagrid `Agent`; do **not** add a workflow runner or identity/OAuth middleware.

Samples: `python/`, `dotnet/`, `java/`, `go/`, `typescript/`, `rust/` (+ `python/byoa`). Batch: `./run-matrix-loop.sh`.

Quickstarts / `*-ai` examples: clone those repos and follow their READMEs (separate from this plain matrix).

## Results

**Plain matrix (Week 1, prod free `cattle-ackbar`):** **57/57** ok · LangGraph×Claude variance **3/3**. Many later cells **reused** a shared Agent (identity 10/10).

**Plain Plus check (`eileen-plus-test` staging):** dedicated Agents for LangGraph, BYOA, Spring AI, Eino, Mastra — create + invoke ok.

**LangGraph speed yardstick (Plus, dedicated create):** ~**709k** tokens in / ~**19** tool calls / ~**1m41s** (prefer over free-matrix cold numbers for [CAP-2541](https://linear.app/diagrid/issue/CAP-2541)).

**Official quickstarts (Plus):** **15/15** README happy-path ok.

**Crash recovery sample (Plus):** LangGraph, CrewAI, Mastra — **3/3** crash + resume ok.

**`*-ai/examples` sample:** typescript Mastra / go Eino / rust Goose ok; python-ai LangGraph needs Dapr runtime **≥1.18** (fails on 1.14).

Workflows = [Spike B / CAP-2784](https://linear.app/diagrid/issue/CAP-2784) (not this repo).

## What to improve next

| Problem | Ticket |
|---|---|
| Skills steer to durable workflows → `App` instead of plain `Agent` | [CAP-2876](https://linear.app/diagrid/issue/CAP-2876) → [CAP-2550](https://linear.app/diagrid/issue/CAP-2550) |
| Skills assume `default` project when it may be missing | [CAP-2877](https://linear.app/diagrid/issue/CAP-2877) |
| No MCP invoke; Connected ≠ healthy; need `/healthz` + wait | [CAP-2878](https://linear.app/diagrid/issue/CAP-2878) → [CAP-2600](https://linear.app/diagrid/issue/CAP-2600) |
| Crash quickstart: “Uvicorn running” ≠ ready to create workflows | [CAP-2919](https://linear.app/diagrid/issue/CAP-2919) |
| MCP org can differ from CLI org; skills still say “MCP for writes” | [CAP-2921](https://linear.app/diagrid/issue/CAP-2921) |
| Connect-an-agent still heavy (tokens / tools) | [CAP-2541](https://linear.app/diagrid/issue/CAP-2541) |
| python-ai examples: document Dapr ≥1.18 + venv | [CAP-2920](https://linear.app/diagrid/issue/CAP-2920) |
| Framework list / BYOA / Goose docs | [CAP-2787](https://linear.app/diagrid/issue/CAP-2787), [CAP-2554](https://linear.app/diagrid/issue/CAP-2554), [CAP-2923](https://linear.app/diagrid/issue/CAP-2923) |
| Staging `dev run` prints prod console URL | [CAP-2922](https://linear.app/diagrid/issue/CAP-2922) |

Free-plan **10/10 identity** is an environment ceiling, not evidence the plugin cannot create Agents.  
(`agent-registry` missing from `component list` is intentional — managed/reserved; [CAP-2924](https://linear.app/diagrid/issue/CAP-2924) canceled.)

Week 2 re-run: [CAP-2786](https://linear.app/diagrid/issue/CAP-2786).
