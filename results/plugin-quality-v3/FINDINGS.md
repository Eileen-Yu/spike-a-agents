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
| No guide for "plain HTTP agent, unchanged, called through Catalyst"; agent assembles it from app-tunnels §4 | LangGraph × claude #1 | [CAP-2876](https://linear.app/diagrid/issue/CAP-2876) → [CAP-2550](https://linear.app/diagrid/issue/CAP-2550), [CAP-2600](https://linear.app/diagrid/issue/CAP-2600) | High |
| Agent vs App unclear for a non-Dapr agent | LangGraph × claude #1 | [CAP-2876](https://linear.app/diagrid/issue/CAP-2876) | Medium |
| No MCP invoke; no caller app to prove a run (agent self-invokes with its own token) | LangGraph × claude #1 | [CAP-2878](https://linear.app/diagrid/issue/CAP-2878) | Medium |
| Console URL is prod on a staging org | LangGraph × claude #1 | [CAP-2922](https://linear.app/diagrid/issue/CAP-2922) | Low |
| `diagrid_get_agent` says ready before identity is; Agent create attaches undocumented appConfig; tunnel record `ready` after `dev stop` | LangGraph × claude #1 | [CAP-2929](https://linear.app/diagrid/issue/CAP-2929) | Medium |
| `diagrid-deploy` (deny-by-default) vs `diagrid-app-tunnels` (allowed by default) contradict on app-to-app access | env #1 | [CAP-2927](https://linear.app/diagrid/issue/CAP-2927) | Medium |
| Sidecar probes `GET /` and `/dapr/config` (404) though tunnel says `/healthz`, probing disabled | LangGraph × claude #1 | [CAP-2878](https://linear.app/diagrid/issue/CAP-2878) | Low |
| Connect-an-agent cost: 1.82M tokens in, 26 tool calls (13 MCP), 2m13s | LangGraph × claude #1 | [CAP-2541](https://linear.app/diagrid/issue/CAP-2541) | (speed baseline) |

_Last edited 2026-11-19 18:55 PT — after LangGraph × claude #1._
