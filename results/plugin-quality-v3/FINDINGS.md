# Spike A v3 — findings → tickets

Hand-maintained (unlike `SCORECARD.md`). Each row: what the v3 runs showed, where, and the ticket.
Ticket parent: [CAP-2783](https://linear.app/diagrid/issue/CAP-2783) · triage: [CAP-2785](https://linear.app/diagrid/issue/CAP-2785).
"Seen in" names cells as `framework × client #attempt` (see [`SCORECARD.md`](SCORECARD.md)); `env` = the
[`../plugin-quality-v3-envmismatch/`](../plugin-quality-v3-envmismatch/) runs (MCP on prod free, CLI on staging).

## Setup / environment (found before the matrix could run)

| Finding | Seen in | Ticket | Severity |
|---|---|---|---|
| MCP org ≠ CLI org; tunnels need the CLI, so the run cannot finish | env #1–3 | [CAP-2921](https://linear.app/diagrid/issue/CAP-2921) | High |
| Agent read `~/.diagrid/creds` while debugging the mismatch and printed CLI access + refresh tokens (base64 slipped past its own filter) | env #1 | [CAP-2926](https://linear.app/diagrid/issue/CAP-2926) | **High (security)** |
| Plugin MCP can only be moved off prod via undocumented `DIAGRID_MCP_URL`; hand-written MCP config → `invalid_client: unknown client_id` | v3 setup | [CAP-2925](https://linear.app/diagrid/issue/CAP-2925) | Medium |
| No guidance at the identity cap (free 10/10): agent reused an unrelated Agent or stopped | env #1–2 | [CAP-2928](https://linear.app/diagrid/issue/CAP-2928) | High (hackathon = free tier) |
| `default` project deleted; skill still says "deploy into default" | env #1 | [CAP-2877](https://linear.app/diagrid/issue/CAP-2877) | Medium |
| Skill offers only browser `diagrid login`; CLI has `--no-browser` / `--api-key` | env #1 | [CAP-2921](https://linear.app/diagrid/issue/CAP-2921) (comment) | Low |

## Skill / product (from successful staging runs)

| Finding | Seen in | Ticket | Severity |
|---|---|---|---|
| No guide for "plain HTTP agent, unchanged, called through Catalyst"; deploy skill says "move from laptop" but nothing moves, and the tunnel lives in another skill | 16/16 | [CAP-2876](https://linear.app/diagrid/issue/CAP-2876) → [CAP-2550](https://linear.app/diagrid/issue/CAP-2550), [CAP-2600](https://linear.app/diagrid/issue/CAP-2600) | High |
| Agent vs App contradictory in `diagrid-deploy` → **5/16 drifted to App** (CrewAI, Pydantic AI, OpenAI Agents, smolagents, HolmesGPT) | 16/16 report it | [CAP-2876](https://linear.app/diagrid/issue/CAP-2876) | Medium |
| No MCP invoke; no caller pattern to prove a run (self-invoke with own token, or ad-hoc `dev run --rm-appids` caller) | 16/16 | [CAP-2878](https://linear.app/diagrid/issue/CAP-2878) | Medium |
| Console URL is prod on a staging org | 16/16 | [CAP-2922](https://linear.app/diagrid/issue/CAP-2922) | Low |
| `diagrid_get_agent` ready before identity; `get_connection` blocked ~1 min after `dev run`; undocumented appConfig + endpoint rewritten to `trust.diagrid.io`; tool description says "model configuration"; stale tunnel records stay `ready` | 5/5 | [CAP-2929](https://linear.app/diagrid/issue/CAP-2929) | Medium |
| `diagrid-deploy` (deny-by-default) vs `diagrid-app-tunnels` (allowed by default) contradict on app-to-app access | env #1 | [CAP-2927](https://linear.app/diagrid/issue/CAP-2927) | Medium |
| **Tunnel return path times out at ~10s → HTTP 502 EOF** for slow agent turns; Agent kind has no timeout setting | Claude Agent SDK | [CAP-2931](https://linear.app/diagrid/issue/CAP-2931) | **High** |
| **Dapr Agents crashes**: auto-subscribes to `agent-pubsub`, managed broker's undocumented 10-topic cap already used; develop skill wrong about state; `dev run` exits 0 when app exits 1 | Dapr Agents (**fail**) | [CAP-2932](https://linear.app/diagrid/issue/CAP-2932) | **High** |
| First call after tunnel attaches → 502 `context canceled`; `get_connection` refuses ~1 min while `updating` | CrewAI, HolmesGPT, Pydantic AI, OpenAI Agents, LangChain | [CAP-2878](https://linear.app/diagrid/issue/CAP-2878) (comment) | Medium |
| `diagrid_list_agents` ignores `appId` filter for Agent resources; partial data on `UPSTREAM_ERROR` | BYOA, .NET MAF, Dapr Agents | [CAP-2933](https://linear.app/diagrid/issue/CAP-2933) | Medium |
| `diagrid_list_apps` hides Agent-owned App IDs; dry run of an App on that name says `would_replace` without warning (clobber risk) | LangGraph #2, #3 | [CAP-2930](https://linear.app/diagrid/issue/CAP-2930) | High |
| `diagrid_get_connection` returns the API token into chat although app-tunnels says keep it out | LangGraph #3, Strands | [CAP-2901](https://linear.app/diagrid/issue/CAP-2901) (comment) | Medium |
| `dev run` prints "managed workflow / pub/sub / KV / resiliency enabled" for a plain agent — reads as if it became durable | LangChain | [CAP-2929](https://linear.app/diagrid/issue/CAP-2929) (to add) | Low |
| Skill examples use `timeout`, absent on macOS | LangGraph #3 | [CAP-2907](https://linear.app/diagrid/issue/CAP-2907) | Low |
| Sidecar probes `GET /` and `/dapr/config` (404) though tunnel says `/healthz`, probing disabled | LangGraph × claude #1 | [CAP-2878](https://linear.app/diagrid/issue/CAP-2878) | Low |
| Connect-an-agent cost with MCP on: 1.8–2.5M tokens in, 26–33 tool calls (13–16 MCP) — ~3× v2's CLI path | LangGraph #1–3, LangChain | [CAP-2541](https://linear.app/diagrid/issue/CAP-2541) (comment) | (speed baseline) |

_Last edited 2026-11-19 19:18 PT — after 16/21 Claude cells._

## Harness / environment notes (not skill findings)

| Note | Seen in | Action |
|---|---|---|
| Sample run dirs have no `.gitignore`, agents warn that `.env` (keys) could be committed | LangGraph #2, #3 | harness: add `.gitignore` to samples after this batch (would change the baseline mid-batch) |
| Parallel cells see each other's `dev run` / tunnels and pick other ports | LangChain, Strands | expected with `SPIKE_PARALLEL=4`; not filed |
| Runner mis-parsed agent id (`identity`, `app`) and only deletes **Agents**, not Apps → leftovers: `order-agent-strands`, Claude Agent SDK's agent, 5 Apps (`crewai-orders`, `order-agent-pydantic-ai`, `order-agent-openai`, `order-agent-smolagents`, `order-agent-holmesgpt`), `order-agent-dapr-agents` + `statestore` | Strands, Claude Agent SDK, App cells, Dapr Agents | harness fix after batch; clean up after batch |
| `.NET MAF` diff flagged `code=changed` — only `bin/`/`obj/` build output, no source change | .NET MAF | harness: exclude build dirs from diff |
| `default` project's pub/sub already at 10 topics from earlier quickstart runs | Dapr Agents | clean topics, rerun Dapr Agents cell |
| Identity usage 20→24 of 30 on staging Plus (old v1/v2 Agents still present) | LangGraph #3, Strands | clean old spike Agents |
