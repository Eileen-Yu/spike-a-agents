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

Rules: prefer a Diagrid `Agent`; do **not** add a workflow runner or identity/OAuth middleware.

Use a **Cloud Plus** (or otherwise non-exhausted) org so dedicated Agent create is possible. Free 10/10 identity quota forces reuse and muddies results. Prompt targets org `eileen-plus-test` / project `default` on staging when that login is active (`diagrid whoami`).

Samples: `python/`, `dotnet/`, `java/`, `go/`, `typescript/`, `rust/` (+ `python/byoa`). Batch: `./run-matrix-loop.sh`.

## Results

**Week 1 (prod free `cattle-ackbar`):** **57/57** cells ok · LangGraph×Claude **3/3** — but many later cells **reused** a shared Agent because identity was 10/10.

**Plus retest (staging `eileen-plus-test`):** LangGraph, BYOA, Spring AI, Eino, Mastra — each got a **dedicated** Agent on `default` and invoke passed.

LangGraph Plus yardstick: **~709k** tokens in / **~19** tool calls / **~1m41s** (prefer this over free cold numbers for Week 2 speed work).

Details: [`results/SUMMARY.md`](results/SUMMARY.md).

## What to improve next

| Problem | Ticket / note |
|---|---|
| Skills steer toward durable workflows → `App` instead of plain `Agent` | [CAP-2876](https://linear.app/diagrid/issue/CAP-2876) → [CAP-2550](https://linear.app/diagrid/issue/CAP-2550) |
| Skills assume `default` project; may be missing (free orgs) | [CAP-2877](https://linear.app/diagrid/issue/CAP-2877) — Plus had `default`; still fix skill wording |
| No MCP invoke; Connected ≠ healthy; need `/healthz` + wait | [CAP-2878](https://linear.app/diagrid/issue/CAP-2878) → [CAP-2600](https://linear.app/diagrid/issue/CAP-2600) |
| MCP org ≠ CLI org (or MCP unauthenticated in non-interactive) | skills/MCP auth — blocks “MCP for all writes” |
| Connect-an-agent still heavy on tokens/tools | [CAP-2541](https://linear.app/diagrid/issue/CAP-2541) |
| Framework / BYOA / Goose docs | [CAP-2787](https://linear.app/diagrid/issue/CAP-2787), [CAP-2554](https://linear.app/diagrid/issue/CAP-2554) |

Free-plan **quota** is an env ceiling, not a plugin bug — do not treat “could not create Agent” from 10/10 as a product defect.

Week 2 re-run: [CAP-2786](https://linear.app/diagrid/issue/CAP-2786). Triage: [CAP-2785](https://linear.app/diagrid/issue/CAP-2785).
