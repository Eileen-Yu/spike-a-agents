# Plugin quality retest (cookbook-free prompt)

Org: `eileen-plus-test` staging Plus · project `default` · plugin `diagrid@diagrid` 0.10.2
Prompt: Spike A canonical only. No CLI/MCP/auth crib. No sample `/healthz`.
Model: `claude-opus-5-5` via `claude -p`.
Eino wall from filesystem (session clock was truncated).

| Framework | Result | Agent id | tokens in | tools (all / MCP) | wall | writes via | skills used | log |
|---|---|---|---:|---:|---|---|---|---|
| langgraph | **ok** · Agent | `order-agent-spike-a` | 633,881 | 17 / 0 | 2m 03s | CLI (MCP auth refused) | diagrid-agent-scaffold | `langgraph.log` |
| byoa | **ok** · Agent | `order-agent-byoa` | 697,435 | 17 / 0 | 1m 55s | CLI (MCP auth refused) | diagrid-agent-scaffold | `byoa.log` |
| crewai | **ok** · Agent | `order-agent-crewai` | 716,768 | 18 / 0 | 3m 06s | CLI (MCP auth refused) | diagrid-agent-scaffold | `crewai.log` |
| mastra | **ok** · Agent | `order-agent-mastra` | 824,663 | 19 / 0 | 2m 13s | CLI (MCP auth refused) | diagrid-agent-scaffold, diagrid-app-tunnels | `mastra.log` |
| eino | **ok** · Agent | `order-agent-eino` | 421,113 | 12 / 0 | 5m 19s | CLI (MCP auth refused) | diagrid-agent-scaffold, diagrid-app-tunnels | `eino.log` |

**Scoreboard: 5/5 ok**

## Shared friction

1. MCP auth fails in non-interactive `claude -p` → CLI fallback; `tools_mcp=0`.
2. `diagrid-agent-scaffold` steers durable / kill-resume vs Spike A plain.
3. No skill path for proving plain HTTP `/run`.
4. Port 8000 collisions; readiness races without `/healthz`.
5. Eino: dry-run looks like real create; `agent get` prints API token in plaintext.

_Updated 2026-11-19 17:58 — batch complete._
