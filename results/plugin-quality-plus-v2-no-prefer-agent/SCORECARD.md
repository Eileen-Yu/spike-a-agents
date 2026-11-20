# Plugin quality v2 — no Prefer-Agent in prompt

Canonical Spike A quality prompt. Org `eileen-plus-test` / `default` · plugin 0.10.2 · `claude-opus-5-5`.

| Framework | Result | kind | id | tokens in | tools (all / MCP) | wall | writes via | log |
|---|---|---|---|---:|---:|---|---|---|
| langgraph | **ok** | **App** | `order-agent-lg-1119` | 615,663 | 16 / 0 | 2m 24s | CLI (MCP auth refused) | `langgraph.log` |
| byoa | **ok** | **Agent** | `order-agent-byoa-1813` | 606,350 | 19 / 0 | 2m 14s | CLI (MCP auth refused) | `byoa.log` |
| crewai | **ok** | **App** | `order-agent-crewai-1119` | 476,674 | 12 / 0 | 2m 49s | CLI (MCP auth refused) | `crewai.log` |
| mastra | **ok** | **Agent** | `order-agent-mastra-1829` | 1,361,411 | 24 / 0 | 3m 36s | CLI (MCP auth refused) | `mastra.log` |
| eino | **ok** | **Agent** | `order-agent-eino-1822` | 1,144,782 | 22 / 0 | 2m 59s | CLI (MCP auth refused) | `eino.log` |

**Scoreboard: 5/5 ok** · Agent 3 · App 2

v1 (`plugin-quality-plus/`) coached Prefer-Agent and hid App drift. All cells `tools_mcp=0` (CLI fallback).

_Updated 2026-11-19 18:25 — batch complete._
