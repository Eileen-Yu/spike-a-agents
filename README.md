# Spike A — plugin / skills quality test

[CAP-2783](https://linear.app/diagrid/issue/CAP-2783): can the Diagrid plugin take a **plain** agent (no workflow wrapper, no identity middleware) and run it on Catalyst?

**Spike A = quality test** of the Diagrid plugin + skills. **Pass** = ask about order **42**, answer contains **shipped**.

Do **not** put how-to into the agent prompt (CLI recipes, MCP vs CLI, PATH, whoami, ports, healthz). Those are what the plugin must supply; crib notes invalidate the score.

| Layer | Role |
|---|---|
| Spike A plain samples (this repo) | **Quality score** — same `get_order_status` agent × client |
| [`catalyst-quickstarts`](https://github.com/diagridio/catalyst-quickstarts) `agents/*` | Coverage only (durable demos) |
| `*-ai` repo `examples/` | Coverage only (often local `dapr run`) |

Full tables: [`results/SUMMARY.md`](results/SUMMARY.md). Triage: [CAP-2785](https://linear.app/diagrid/issue/CAP-2785).

## How to test

**Experimenter setup** (you, not the prompt): use a plan with App ID headroom (e.g. Cloud Plus). Free **10/10** forces Agent reuse and muddies “create works”.

```sh
cp .env.example .env
./new-run.sh python/langgraph   # → ~/spike-runs/langgraph-<ts>
cd ~/spike-runs/langgraph-<ts>
```

Paste only the **canonical** prompt from [`results/spike-prompt.md`](results/spike-prompt.md). Do not pre-patch the sample. Do not coach CLI/MCP/auth or Agent-vs-App (skills must supply that).

Rules baked into that prompt: no workflow runner; no identity/OAuth middleware; keep the sample’s `/run` loop.

Samples: `python/`, `dotnet/`, `java/`, `go/`, `typescript/`, `rust/` (+ `python/byoa`). Batch: `./run-matrix-loop.sh`.

Quickstarts / `*-ai` examples: clone those repos and follow their READMEs (separate from this plain matrix).

## Results / conclusion

**Quality bar ≠ shipped.** Cookbook-free Plus runs can still get order-42 **shipped**, but via raw CLI (`tools_mcp=0`). Without Prefer-Agent in the prompt, cells drift to plain **`App`** (v2: LangGraph+CrewAI App, BYOA Agent so far).

Full tables + verdict: [`results/SUMMARY.md`](results/SUMMARY.md).

| Pass | What it means |
|---|---|
| Quality v2 (canonical prompt, no Prefer-Agent) | **5/5 shipped** · Agent 3 · App 2 — `plugin-quality-plus-v2-no-prefer-agent/` |
| Quality v1 (Prefer-Agent still in prompt) | 5/5 shipped · all Agent — App drift hidden · `plugin-quality-plus/` |
| Week-1 matrix 57/57 | Old crib prompts + free 10/10 reuse — **not** quality score |
| Quickstarts 15/15 · crash 3/3 · `*-ai` sample | Coverage only (durable / local dapr) |

Workflows = [Spike B / CAP-2784](https://linear.app/diagrid/issue/CAP-2784).

## What to improve next

| Problem | Ticket | Cookbook-free retest |
|---|---|---|
| Skills steer durable → plain path lands on `App` | [CAP-2876](https://linear.app/diagrid/issue/CAP-2876) → [CAP-2550](https://linear.app/diagrid/issue/CAP-2550) | **Confirmed** v2 (2/5 App) |
| Skills require MCP writes; MCP unusable / org mismatch in non-interactive | [CAP-2921](https://linear.app/diagrid/issue/CAP-2921) | **Confirmed** every cell `tools_mcp=0` |
| No MCP invoke; Connected ≠ healthy; `/healthz` | [CAP-2878](https://linear.app/diagrid/issue/CAP-2878) → [CAP-2600](https://linear.app/diagrid/issue/CAP-2600) | **Confirmed** |
| Connect-an-agent still heavy (tokens / tools) | [CAP-2541](https://linear.app/diagrid/issue/CAP-2541) | ~0.4–0.8M in / ~12–19 tools / ~2–5 min |
| Skills assume `default` project when missing | [CAP-2877](https://linear.app/diagrid/issue/CAP-2877) | (Plus had `default`) |
| Crash quickstart: Uvicorn ≠ ready | [CAP-2919](https://linear.app/diagrid/issue/CAP-2919) | coverage pass |
| python-ai Dapr ≥1.18 + venv | [CAP-2920](https://linear.app/diagrid/issue/CAP-2920) | coverage |
| Framework list / BYOA / Goose docs | [CAP-2787](https://linear.app/diagrid/issue/CAP-2787), [CAP-2554](https://linear.app/diagrid/issue/CAP-2554), [CAP-2923](https://linear.app/diagrid/issue/CAP-2923) | — |
| Staging `dev run` prints prod console URL | [CAP-2922](https://linear.app/diagrid/issue/CAP-2922) | still seen |

Free-plan **10/10 identity** is an environment ceiling, not evidence the plugin cannot create Agents.  
(`agent-registry` missing from `component list` is intentional — managed/reserved; [CAP-2924](https://linear.app/diagrid/issue/CAP-2924) canceled.)

Week 2 re-run: [CAP-2786](https://linear.app/diagrid/issue/CAP-2786).
