# Spike A — can the Diagrid plugin connect an existing agent?

[CAP-2783](https://linear.app/diagrid/issue/CAP-2783). Give a coding agent a plain agent that knows nothing about Catalyst, in each supported framework, and say "deploy it to Diagrid Catalyst and run it there, as-is". Using **only the plugin's skills and MCP**, can it get one request **through Catalyst** to answer "order 42 → shipped"? No workflow runner and no identity middleware: those are week 2 (CAP-2550, CAP-2788).

## Result (v3, 2026-11-19)

**Claude 22/22 · Codex 2/2 · Copilot 2/2.** Every agent got there, but by improvising: **11/27 runs created an App instead of an Agent**, and a connect costs **~2M tokens / ~3 min** (Claude).

| | |
|---|---|
| One-page results (matrix, cost, findings) | [`results/SUMMARY.md`](results/SUMMARY.md) |
| Findings with evidence counts → 7 tickets | [`results/plugin-quality-v3/FINDINGS.md`](results/plugin-quality-v3/FINDINGS.md) |
| Every run (tokens, time, MCP calls, diff, RESULT) | [`results/plugin-quality-v3/SCORECARD.md`](results/plugin-quality-v3/SCORECARD.md) |
| The prompt and grading rules | [`results/spike-prompt.md`](results/spike-prompt.md) |
| Coverage (official quickstarts 15/15, crash recovery 3/3, `*-ai` examples) | [`results/coverage/`](results/coverage/) |
| Earlier, superseded runs (week-1 57/57, v1, v2) | [`results/archive/`](results/archive/) |

## What's here

```
python/ dotnet/ java/ go/ typescript/ rust/   19 plain sample agents + python/byoa (same order-status tool, POST /run)
run-matrix-loop.sh    runs framework × client cells, grades them, writes the ledger
clean-project.sh      resets the Catalyst project (Agents, Apps, topics) — lists and asks first
new-run.sh            copies one sample into a fresh git repo under ~/spike-runs
publish.sh            regenerates SUMMARY/SCORECARD and commits + pushes (logs never)
session_metrics.py    tokens / tool calls / skills from a Claude Code session log
results/build-v3-summary.py   builds SUMMARY.md and SCORECARD.md from the ledger
.agents/skills/ + skills-lock.json   pinned skill copy given to Codex/Copilot run dirs
```

## How to run

1. **One environment for everything.** Claude's plugin MCP, Codex, Copilot and the `diagrid` CLI must all point at the same org.
   ```sh
   cp .env.example .env    # OPENAI_API_KEY etc. — read by the sample, never passed to the coding client
   export SPIKE_MCP_URL=https://mcp.cloud.staging.diagrid.dev/mcp DIAGRID_MCP_URL=$SPIKE_MCP_URL \
          SPIKE_ORG=eileen-plus-test SPIKE_DELETE_AGENTS=1
   diagrid login                       # CLI on the same org
   claude                              # /mcp → plugin:diagrid:diagrid → authenticate
   # Codex: url in ~/.codex/config.toml (client_id "codex"), then: codex mcp login diagrid
   # Copilot: url in ~/.copilot/mcp-config.json (oauthClientId "copilot-cli"), then /mcp inside copilot
   ```
2. **Run.** The preflight refuses to start if any client or the CLI is on another environment or org.
   ```sh
   ./clean-project.sh
   SPIKE_DRY=1 ./run-matrix-loop.sh                       # show the queue and the prompt
   SPIKE_PARALLEL=6 ./run-matrix-loop.sh                   # spec matrix (25 cells)
   SPIKE_FULL_MATRIX=1 SPIKE_PARALLEL=6 ./run-matrix-loop.sh   # all 19 frameworks × 3 clients
   ```
   * Only one runner can run at a time; a second one exits.
   * Ctrl-C stops every client and tunnel.
   * A rerun picks up from `results/plugin-quality-v3/ledger.tsv`.
   * `SPIKE_EXTRA=slug:client:N` adds attempts to a cell.

How a run is graded is in [`results/spike-prompt.md`](results/spike-prompt.md#graded-by-the-harness-not-by-the-model). In short: the git diff, whether the proof went through Catalyst, the resource kind, and the cost.

**Logs never leave this machine.** They can contain credentials, so `*.log` is gitignored everywhere.
