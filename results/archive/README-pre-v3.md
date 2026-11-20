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

Paste only the **canonical v3** prompt from [`results/spike-prompt.md`](results/spike-prompt.md). Do not pre-patch the sample. Do not coach CLI/MCP/auth or Agent-vs-App (skills must supply that).

**Batch (v3):** sign in to the Diagrid MCP server once (`claude` → `/mcp` → diagrid → authenticate; the runner refuses to start otherwise), then:

```sh
./run-matrix-loop.sh                          # spec matrix → results/plugin-quality-v3/ledger.tsv
SPIKE_ONLY=langgraph,byoa ./run-matrix-loop.sh
SPIKE_REPEATS=2 SPIKE_DELETE_AGENTS=1 ./run-matrix-loop.sh   # repeats; free-tier headroom
SPIKE_DRY=1 ./run-matrix-loop.sh              # show queue + prompt only
./clean-project.sh                            # reset the spike project (lists, asks, then deletes Agents/Apps/topics)
SPIKE_PARALLEL=4 ./run-matrix-loop.sh        # 4 cells at once (each cleans only its own run dir; port/tunnel contention is environment noise, not a skill finding)
```

The runner grades from outside the model: `git diff` of code/dependency files (any `diagrid` SDK, runner, durable or identity import = `fail-rules`), whether the proof went through Catalyst (`via`), resource kind, and Claude session metrics incl. MCP calls. `.env` is **not** exported into the coding client (it switched Claude to API-key auth in v2); the agent reads `.env` itself. Resumable: re-run and it continues from the ledger.

Samples: `python/`, `dotnet/`, `java/`, `go/`, `typescript/`, `rust/` (+ `python/byoa`). Batch: `./run-matrix-loop.sh`.

Quickstarts / `*-ai` examples: clone those repos and follow their READMEs (separate from this plain matrix).

## Results / conclusion

**Plugin quality v3 (current, staging Plus, MCP on):** live matrix in [`results/SUMMARY.md`](results/SUMMARY.md) § v3 · per-run table + redacted RESULTs in [`results/plugin-quality-v3/SCORECARD.md`](results/plugin-quality-v3/SCORECARD.md) · findings → tickets in [`results/plugin-quality-v3/FINDINGS.md`](results/plugin-quality-v3/FINDINGS.md). Both regenerate and push after every cell (`publish.sh`). Everything below is earlier, superseded evidence.

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

Spike A findings, consolidated into 7 tickets:

| Ticket | What | Priority |
|---|---|---|
| [CAP-2876](https://linear.app/diagrid/issue/CAP-2876) | Skills have no first-class "connect an existing agent" path (App vs Agent, where code runs, proving a run, naming, project) | Urgent |
| [CAP-2931](https://linear.app/diagrid/issue/CAP-2931) | Tunnel return path ~10s timeout → 502 on slow agent turns | High |
| [CAP-2926](https://linear.app/diagrid/issue/CAP-2926) | Credentials end up in agent transcripts | High |
| [CAP-2932](https://linear.app/diagrid/issue/CAP-2932) | Invisible quotas (pub/sub 10-topic cap, identity cap) | High |
| [CAP-2921](https://linear.app/diagrid/issue/CAP-2921) | MCP vs CLI env/org mismatch, no CLI fallback, `DIAGRID_MCP_URL` undocumented | High |
| [CAP-2929](https://linear.app/diagrid/issue/CAP-2929) | MCP/CLI behaviour misleads agents (readiness, side effects, filters, dry run, console URL) | Medium |
| [CAP-2920](https://linear.app/diagrid/issue/CAP-2920) | Quickstart / example READMEs miss prerequisites | Medium |

Merged on 2026-11-19 (marked duplicate): 2877, 2878, 2927, 2930, 2934 → 2876 · 2933, 2922 → 2929 · 2928 → 2932 · 2925 → 2921 · 2919, 2923 → 2920. CAP-2924 canceled.
