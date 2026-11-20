# Spike A findings (v3)

**27 valid runs** (Claude 23 · Codex 2 · Copilot 2) on staging Plus with plugin 0.10.2: **26 ok, 1 fail** (Dapr Agents attempt 1, environment). Per cell: Claude 22/22 · Codex 2/2 · Copilot 2/2. Every run used the MCP (Claude: 8–22 calls, avg 13).

The "seen in" counts are runs whose own RESULT/friction list mentions the problem (keyword match over the 27 transcripts), so they're lower bounds.

| # | Ticket | Finding | Seen in | Priority |
|---|---|---|---|---|
| 1 | [CAP-2876](https://linear.app/diagrid/issue/CAP-2876) | **No first-class "connect an existing agent" path.** App vs Agent contradicts itself in `diagrid-deploy` | **11/27 landed on App** (Claude 8/23, Codex 2/2, Copilot 1/2); 21/27 call it out | Urgent |
| | | Skills never say Catalyst doesn't host your code; the tunnel lives in a different skill | 11/27 (Copilot reported `deploy: fail` for this) | |
| | | No documented way to prove a run through Catalyst (no MCP invoke; agents improvised 3 different callers) | 20/27 | |
| | | Readiness: Agent says `ready` while its identity is `processing`; the first call after the tunnel attaches can 502 | 20/27 · 3/27 | |
| | | Name check misleads (`list_apps` leaves out Agent identities; dry run says `would_replace`; real apply refused) | 7/27 | |
| | | Skills contradict each other on app-to-app access (deny-by-default vs allowed) | 4/27 | |
| 2 | [CAP-2931](https://linear.app/diagrid/issue/CAP-2931) | **Tunnel return path times out at ~10s → HTTP 502** on slow agent turns (agent logs 200, caller gets 502 EOF); Agent kind has no timeout setting | Claude Agent SDK (repeated), first-call 502s in CrewAI/HolmesGPT | High |
| 3 | [CAP-2926](https://linear.app/diagrid/issue/CAP-2926) | **Credentials in transcripts**: the agent printed `~/.diagrid/creds` (access + refresh token) while debugging an env mismatch; `get_connection` returns the API token into chat | creds: 1 run (setup) · token-in-chat: 14/27 | High |
| 4 | [CAP-2932](https://linear.app/diagrid/issue/CAP-2932) | **Invisible quotas.** Managed pub/sub 10-topic cap (Dapr Agents crashed on 10 leftover topics, **ok after cleanup**); identity cap 10/10 on free with no path | Dapr Agents #1 fail → #2 ok; free org 10/10 | High |
| 5 | [CAP-2921](https://linear.app/diagrid/issue/CAP-2921) | **MCP and CLI on different env/org** (prod MCP + staging CLI → nothing deployed); no CLI fallback; `DIAGRID_MCP_URL` undocumented | 3 setup runs; v1/v2: 0 MCP calls in every run | High |
| 6 | [CAP-2929](https://linear.app/diagrid/issue/CAP-2929) | **MCP/CLI behaviour misleads**: prod console URL on a staging org; silent appConfig + endpoint rewrite; `list_agents` ignores filters; `dev run` exits 0 on app crash and prints "managed workflow enabled" for a plain agent | console URL 27/27 · filters 4/27 · "enabled" 4/27 | Medium |
| 7 | [CAP-2920](https://linear.app/diagrid/issue/CAP-2920) | **Example READMEs miss prerequisites** (coverage runs): python-ai needs Dapr ≥ 1.18 and a venv; Goose needs `GOOSE_PROVIDER`; "Uvicorn running" ≠ ready in the crash quickstarts | 3 READMEs | Medium |

## Cost (Week 2 baseline, [CAP-2541](https://linear.app/diagrid/issue/CAP-2541))

| | tokens in | tool calls | time |
|---|---:|---:|---:|
| Claude, 23 runs | avg **1.96M** (1.45–3.80M) | avg 28 (23–44) | avg **2m58s** (2m11s–5m11s) |
| LangGraph × Claude, 4 runs | 1.82–1.96M | 26–30 | 2m13s–3m06s |
| Codex, 2 runs | 90k–108k (Codex reports one total) | — | 4m21s–5m12s |
| Copilot, 2 runs | 1.2–1.9M + 2.7–4.8 AI credits | — | 4m11s–8m02s |

≈ the week-1 LangGraph cold baseline (1.44–1.87M, ~30 calls). Token counts aren't comparable across clients.

## Not product findings

Things the harness or the environment caused, already fixed or excluded from the counts above:

* **Invalid runs (in `../archive/v3-invalid-runs/`).** Runners started together killed each other's cells. Codex echoes the prompt, so the loose RESULT match killed it at 20s. BYOA × Codex and × Copilot ran in parallel and shared one App.
* **Harness fixes.** One runner at a time; one framework per client at a time; strict RESULT parsing; build and dependency dirs are excluded from the diff. The Mastra false `fail-rules` came from `node_modules`.
* **Clean-project check.** LangGraph × Claude #4 on a cleaned project used 1.82M tokens and 26 calls, the same as #1–3 on the dirty project, so the leftovers didn't skew cost.
* **Samples have no `.gitignore`.** 14/27 agents warned that `.env` could be committed.

Working notes from the run (longer, per-cell): [`../archive/FINDINGS-working-notes.md`](../archive/FINDINGS-working-notes.md).
