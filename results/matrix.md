# Spike A results matrix

**One-page overview (use this):** [SUMMARY.md](SUMMARY.md)

# Spike A results matrix (CAP-2783 + related)

Prompt: [spike-prompt.md](spike-prompt.md)  
Plugin: `diagrid@diagrid` 0.10.2 · CLI: `~/.local/bin/diagrid` 1.130.0 · Org: `cattle-ackbar`  
**Scope now: fill every cell (meeting = all three clients).** Continuous loop: `./run-matrix-loop.sh`.

## Agent vs App

Spike A is an **agent** test. Correct Diagrid resource is `kind: Agent` (managed App ID underneath for tunnel/invoke).  
Several early runs drifted to plain `App` because "no workflow wrapper" was misread as "don't use Agent / scaffold". That is friction, not the intended path. New runs use the corrected prompt.

| Resource used | Examples |
|---|---|
| Agent (intended) | LangGraph Claude #1 → `order-agent` |
| App (drift) | LangGraph Codex/Copilot → `langgraph-order-status`; BYOA Claude → `byoa-order-status` |

---

## Full matrix (framework × client)

| # | Framework | Path | Claude | Codex | Copilot | Evidence / notes |
|---|---|---|---|---|---|---|
| 1 | LangGraph | `python/langgraph` | **ok** (1/3) | **ok** (App) | **ok** (App) | Need **2 more** Claude. Codex/Copilot used App not Agent. |
| 2 | LangChain | `python/langchain` | **ok** | | | |
| 3 | CrewAI | `python/crewai` | **ok** | | | |
| 4 | Google ADK | `python/adk` | **ok** | | | |
| 5 | Strands | `python/strands` | | | | |
| 6 | Pydantic AI | `python/pydantic-ai` | | | | |
| 7 | OpenAI Agents | `python/openai-agents` | | | | |
| 8 | Claude Agent SDK | `python/claude-agents` | | | | |
| 9 | smolagents | `python/smolagents` | | | | |
| 10 | Deep Agents | `python/deepagents` | | | | |
| 11 | HolmesGPT | `python/holmesgpt` | | | | |
| 12 | Dapr Agents | `python/dapr-agents` | | | | |
| 13 | BYOA | `python/byoa` | **ok** (App) | | | [byoa-claude.log](byoa-claude.log) — Agent skipped; plain App used |
| 14 | .NET MAF | `dotnet/microsoft-agent-framework` | | | | |
| 15 | Spring AI | `java/spring-ai` | | | | |
| 16 | LangChainGo | `go/langchaingo` | | | | |
| 17 | Eino | `go/eino` | | | | |
| 18 | Mastra | `typescript/mastra` | | | | |
| 19 | Goose | `rust/goose` | | | | |

Loop queue + live status: [queue-status.md](queue-status.md)

---

## Shared friction

| Class | Finding |
|---|---|
| Agent vs App | Skills push workflow durability; "no wrapper" → clients create plain App |
| sample/local env | Prefer `~/.local/bin/diagrid` 1.130.0; old `~/go/bin` edge times out |
| MCP tool gap | No MCP tunnel/invoke |
| platform | 3 projects; Connected ≠ healthy; wait for `/healthz` |
| sample | Need `GET /healthz` when probes on |
| Codex auth | ChatGPT login blocked models → API-key login for spike |
