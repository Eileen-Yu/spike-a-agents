# Spike A — plain agents through the Diagrid plugin

[CAP-2783](https://linear.app/diagrid/issue/CAP-2783): can the Diagrid plugin take a **plain** agent (no workflow wrapper, no identity) and get it running on Catalyst?

Pass = ask about order **42**, answer contains **shipped**.

## How to test

```sh
cp .env.example .env          # fill API keys
./new-run.sh python/langgraph # copies sample → ~/spike-runs/langgraph-<ts>
cd ~/spike-runs/langgraph-<ts>
```

In that directory, run Claude Code / Codex / Copilot with the Diagrid plugin and the prompt in [`results/spike-prompt.md`](results/spike-prompt.md).

Rules for this spike: prefer a Diagrid `Agent`; do **not** add a workflow runner or identity/OAuth middleware.

Samples live under `python/`, `dotnet/`, `java/`, `go/`, `typescript/`, `rust/` (one folder per framework, plus `python/byoa`). Batch re-run: `./run-matrix-loop.sh`.

## Results

**57/57** framework × client cells ok (Claude / Codex / Copilot). LangGraph × Claude variance **3/3**.

Full matrix, per-cell friction, and Claude session speed/tokens: [`results/SUMMARY.md`](results/SUMMARY.md).

LangGraph cold baseline (Week 2 yardstick): ~**1.4M–1.9M** input tokens, ~**30** tool calls, ~**4 min**.

## What to improve next

Filed for triage on [CAP-2785](https://linear.app/diagrid/issue/CAP-2785):

| Problem | Ticket |
|---|---|
| Skills steer toward durable workflows → clients create `App` instead of plain `Agent` | [CAP-2876](https://linear.app/diagrid/issue/CAP-2876) → [CAP-2550](https://linear.app/diagrid/issue/CAP-2550) |
| Skills say use `default` project; it may not exist | [CAP-2877](https://linear.app/diagrid/issue/CAP-2877) |
| No MCP invoke; “Connected” ≠ healthy; need `/healthz` + wait | [CAP-2878](https://linear.app/diagrid/issue/CAP-2878) → [CAP-2600](https://linear.app/diagrid/issue/CAP-2600) |
| Connect-an-agent is too slow / too many tokens | [CAP-2541](https://linear.app/diagrid/issue/CAP-2541) |
| Framework / BYOA / Goose docs | [CAP-2787](https://linear.app/diagrid/issue/CAP-2787), [CAP-2554](https://linear.app/diagrid/issue/CAP-2554) |

Week 2 re-run with durability + mcp-on-behalf-of: [CAP-2786](https://linear.app/diagrid/issue/CAP-2786).
