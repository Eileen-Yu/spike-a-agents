# Spike A — consolidated results matrix

Generated: 2026-11-18 15:53  
Org: `cattle-ackbar` · Plugin: `diagrid@diagrid` 0.10.2 · CLI: `diagrid` 1.130.0  
Self-contained: status, resource kind, id, and friction are inline. You should not need to open per-cell logs for the overview.

## Scoreboard

| ok | fail | blocked | missing | of which Agent | of which App | kind unclear |
|---:|---:|---:|---:|---:|---:|---:|
| 57 | 0 | 0 | 0 | 37 | 4 | 16 |

LangGraph × Claude variance (CAP-2783): **3/3**

## Matrix

| # | Framework | Claude | Codex | Copilot |
|---|---|---|---|---|
| 1 | LangGraph | ok · Agent · 3/3 | ok · App | ok · App |
| 2 | LangChain | ok | ok · Agent | ok |
| 3 | CrewAI | ok | ok · Agent | ok · Agent |
| 4 | Google ADK | ok | ok · Agent | ok · Agent · order-agent |
| 5 | Strands | ok · Agent | ok · Agent | ok |
| 6 | Pydantic AI | ok · Agent | ok · Agent | ok · Agent |
| 7 | OpenAI Agents | ok | ok · Agent | ok · Agent |
| 8 | Claude Agent SDK | ok · Agent | ok · Agent | ok |
| 9 | smolagents | ok · Agent | ok · Agent | ok |
| 10 | Deep Agents | ok · Agent | ok · Agent | ok |
| 11 | HolmesGPT | ok · Agent | ok · Agent | ok |
| 12 | Dapr Agents | ok · Agent | ok · Agent | ok · App |
| 13 | BYOA | ok · App · byoa-order-status | ok · Agent | ok · Agent |
| 14 | .NET MAF | ok · Agent | ok · Agent | ok |
| 15 | Spring AI | ok · Agent | ok · Agent | ok |
| 16 | LangChainGo | ok | ok · Agent | ok |
| 17 | Eino | ok · Agent | ok · Agent | ok |
| 18 | Mastra | ok · Agent | ok · Agent | ok · Agent |
| 19 | Goose | ok · Agent | ok · Agent | ok |

## Per-cell detail

### LangGraph (`python/langgraph`)

**claude** — ok · Agent · 3/3

- project `langgraph-spike` · kind `Agent`
- skills: diagrid-deploy, diagrid-app-tunnels
- friction: App ID quota is full (10/10: 9 Agents + `spike-caller`).: I could not create `langgraph-order-agent`, so I reused the generic `order-agent` Agent. It has no end
- friction: "Connected" comes before the app is serving.: `dev run` printed Connected while `uv` was still creating the venv, so the first invoke about 5s later returned 50
- friction: Port needed an override.: `main.py` only reads `PORT`, so I ran the command as `env PORT=8011 uv run --env-file .env main.py`; `main.py` itself is unmodified.
- friction: The `default` project is deleted in this org: , so the skill's "use `default`" guidance does not apply; `whoami` pointed to `langgraph-spike`.
- log: `langgraph-claude.log`

**codex** — ok · App

- kind `App`
- log: `langgraph-codex.log`

**copilot** — ok · App

- kind `App`
- friction: ** Port 8000 was occupied, so the app and tunnel use 8050. CLI 1.130.0. No workflow wrapper or OAuth middleware added.
- log: `langgraph-copilot.log`


### LangChain (`python/langchain`)

**claude** — ok

- friction: **
- log: `langchain-claude.log`

**codex** — ok · Agent

- kind `Agent`
- log: `langchain-codex.log`

**copilot** — ok

- skills: `diagrid-deploy`, `diagrid-agent-scaffold`, `diagrid-develop`, `diagrid-app-tunnels`.
- log: `langchain-copilot.log`


### CrewAI (`python/crewai`)

**claude** — ok

- project `crewai-spike`
- friction: Port 8000 was taken: by another Python process, so I used `PORT=8043` with `--app-port 8043`.
- friction: `diagrid dev run` created a managed pub/sub and KV store anyway: , even though I created the project with both disabled. `--skip-managed-pubsub` and `--skip-man
- friction: `diagrid dev run` switched the CLI default project: to `crewai-spike` (it was `langgraph-spike`).
- friction: The plugin steers against creating a project:: `whoami` reports the `default` project as deleted and says "Do not create a project", and the deploy skill says t
- log: `crewai-claude.log`

**codex** — ok · Agent

- kind `Agent`
- log: `crewai-codex.log`

**copilot** — ok · Agent

- kind `Agent`
- friction: Port 8000 was busy, so used 8001. Reused the ready Agent because identity quota was full (10/10). The first invocation hit a health-check startup delay; retry s
- log: `crewai-copilot.log`


### Google ADK (`python/adk`)

**claude** — ok

- note: (no RESULT fields parsed)
- log: `adk-claude.log`

**codex** — ok · Agent

- kind `Agent`
- log: `adk-codex.log`

**copilot** — ok · Agent · order-agent

- project `langgraph-spike` · kind `Agent` · id `order-agent`
- skills: diagrid-deploy, diagrid-agent-scaffold, diagrid-develop, diagrid-app-tunnels.
- log: `adk-copilot.log`


### Strands (`python/strands`)

**claude** — ok · Agent

- project `langgraph-spike` · kind `Agent`
- skills: diagrid-deploy, diagrid-app-tunnels (+ Diagrid MCP: whoami, list_agents, list_apps,
- friction: Port 8000 busy:: another Python process holds it, so I ran with `PORT=8001` and `--app-port 8001`.
- friction: App ID not ready right after create:: the Agent reported `ready` immediately, but its managed App ID was still `processing`. `dev run` waited it out and connect
- friction: `default` project is gone:: the MCP `whoami` reports the org's `default` project as deleted, and the deploy skill says to use `default`. Your instruction to use
- friction: No registry record for the Agent:: the registered-agents list (`listAgents.agents`) was empty when checked before the create and was not re-checked afterwards. 
- log: `strands-claude.log`

**codex** — ok · Agent

- kind `Agent`
- log: `strands-codex.log`

**copilot** — ok

- note: see strands-copilot.log
- log: `strands-copilot.log`


### Pydantic AI (`python/pydantic-ai`)

**claude** — ok · Agent

- project `langgraph-spike` · kind `Agent`
- skills: diagrid-deploy, diagrid-agent-scaffold, diagrid-app-tunnels
- log: `pydantic-ai-claude.log`

**codex** — ok · Agent

- kind `Agent`
- log: `pydantic-ai-codex.log`

**copilot** — ok · Agent

- kind `Agent`
- friction: port 8000 was busy; used 8001. Reused the existing Agent and `spike-caller`.
- log: `pydantic-ai-copilot.log`


### OpenAI Agents (`python/openai-agents`)

**claude** — ok

- note: see openai-agents-claude.log
- log: `openai-agents-claude.log`

**codex** — ok · Agent

- kind `Agent`
- log: `openai-agents-codex.log`

**copilot** — ok · Agent

- kind `Agent`
- friction: ** Port 8000 was busy; used 8001.
- log: `openai-agents-copilot.log`


### Claude Agent SDK (`python/claude-agents`)

**claude** — ok · Agent

- project `langgraph-spike` · kind `Agent`
- skills: diagrid-deploy, diagrid-app-tunnels
- friction: First invoke 502:: ~5s after "Connected", the call returned `Post "http://tunnels-proxy.cloud.r1.diagrid.io:443/run": EOF`, even though the local app logged `PO
- friction: Port flag:: `main.py` reads `PORT`, so I had to add `-e PORT=8017` to your `dev run` command; `--app-port` alone does not tell the app where to listen.
- friction: Readiness gap:: right after the apply, the Agent read `ready` while its managed App ID was still `processing`. `dev run` waited it out without error.
- friction: No `default` project:: the org's default project was deleted, so the skill's "use `default`" guidance does not apply; `diagrid_whoami` pointed to `langgraph-spi
- log: `claude-agents-claude.log`

**codex** — ok · Agent

- kind `Agent`
- log: `claude-agents-codex.log`

**copilot** — ok

- note: see claude-agents-copilot.log
- log: `claude-agents-copilot.log`


### smolagents (`python/smolagents`)

**claude** — ok · Agent

- project `langgraph-spike` · kind `Agent`
- skills: diagrid:diagrid-deploy, diagrid:diagrid-app-tunnels
- log: `smolagents-claude.log`

**codex** — ok · Agent

- kind `Agent`
- log: `smolagents-codex.log`

**copilot** — ok

- friction: port 8000 was occupied, so I used 8001; the org’s App ID quota is full, so I reused the existing Agent; the default project was deleted, so I used the requested
- log: `smolagents-copilot.log`


### Deep Agents (`python/deepagents`)

**claude** — ok · Agent

- project `langgraph-spike` · kind `Agent`
- skills: diagrid:diagrid-deploy, diagrid:diagrid-app-tunnels (plus the Diagrid MCP:
- log: `deepagents-claude.log`

**codex** — ok · Agent

- kind `Agent`
- log: `deepagents-codex.log`

**copilot** — ok

- note: see deepagents-copilot.log
- log: `deepagents-copilot.log`


### HolmesGPT (`python/holmesgpt`)

**claude** — ok · Agent

- project `langgraph-spike` · kind `Agent`
- skills: diagrid-deploy, diagrid-app-tunnels
- log: `holmesgpt-claude.log`

**codex** — ok · Agent

- kind `Agent`
- log: `holmesgpt-codex.log`

**copilot** — ok

- friction: ** `default` was deleted, so I reused `langgraph-spike`. The existing Agent and caller were reused; the 10-ID quota was full. Port 8000 was busy, so I used 8001
- log: `holmesgpt-copilot.log`


### Dapr Agents (`python/dapr-agents`)

**claude** — ok · Agent

- project `langgraph-spike` · kind `Agent`
- skills: diagrid-deploy, diagrid-app-tunnels (+ Diagrid MCP tools)
- log: `dapr-agents-claude.log`

**codex** — ok · Agent

- kind `Agent`
- log: `dapr-agents-codex.log`

**copilot** — ok · App

- kind `App`
- friction: ** port 8000 was occupied, so I tried 8001. The repository’s `AgentRunner` exposes `/agent/run`; it does not provide the requested `/healthz`. The Diagrid MCP a
- log: `dapr-agents-copilot.log`


### BYOA (`python/byoa`)

**claude** — ok · App · byoa-order-status

- project `langgraph-spike` · kind `App` · id `byoa-order-status`
- skills: diagrid-deploy, diagrid-app-tunnels
- log: `byoa-claude.log`

**codex** — ok · Agent

- kind `Agent`
- log: `byoa-codex.log`

**copilot** — ok · Agent

- kind `Agent`
- friction: identity quota was full (10/10); reused the Agent. Port 8000 was occupied; used 8001. The sample loop stayed unchanged.
- log: `byoa-copilot.log`


### .NET MAF (`dotnet/microsoft-agent-framework`)

**claude** — ok · Agent

- project `langgraph-spike` · kind `Agent`
- skills: diagrid-deploy, diagrid-app-tunnels (+ Diagrid MCP: whoami, list_agents, list_apps,
- log: `microsoft-agent-framework-claude.log`

**codex** — ok · Agent

- kind `Agent`
- log: `microsoft-agent-framework-codex.log`

**copilot** — ok

- friction: reused existing identity at quota 10/10; port 8000 busy, so used 8001; added missing `/healthz` route | skills: diagrid-deploy, diagrid-agent-scaffold, diagrid-
- log: `microsoft-agent-framework-copilot.log`


### Spring AI (`java/spring-ai`)

**claude** — ok · Agent

- project `langgraph-spike` · kind `Agent`
- skills: diagrid-deploy, diagrid-app-tunnels (+ Diagrid MCP: whoami, list_agents, list_apps,
- friction: 1. **Could not create `spring-ai-order-agent`.** The org is at its cap of 10 identities (9 agents + 1 app), so `diagrid_apply` was rejected. I reused the existi
- log: `spring-ai-claude.log`

**codex** — ok · Agent

- kind `Agent`
- log: `spring-ai-codex.log`

**copilot** — ok

- friction: identity quota was full (10/10), `/healthz` was missing and added, and the first invoke hit the health transition (500); retry returned 200 with “shipped.” Skil
- log: `spring-ai-copilot.log`


### LangChainGo (`go/langchaingo`)

**claude** — ok

- note: see langchaingo-claude.log
- log: `langchaingo-claude.log`

**codex** — ok · Agent

- kind `Agent`
- log: `langchaingo-codex.log`

**copilot** — ok

- skills: `diagrid-deploy`, `diagrid-agent-scaffold`, `diagrid-develop`, `diagrid-app-tunnels`.
- friction: reused the existing ready Agent because the regional App ID quota is full (10/10); port 8000 was occupied, so I used 8001; `/healthz` was absent, so I added tha
- log: `langchaingo-copilot.log`


### Eino (`go/eino`)

**claude** — ok · Agent

- project `langgraph-spike` · kind `Agent`
- skills: diagrid-deploy, diagrid-app-tunnels (plus the Diagrid MCP tools)
- friction: Identity quota:: applying `eino-order-agent` was refused with "reached the maximum of 10 resources … currently using 10 (9 agents, 1 app)". I did not delete ano
- friction: Dry run missed it:: `diagrid_apply` with `dry_run` reported `would_create` for the same manifest that the real apply then rejected on quota.
- friction: Sample is Go, not Python:: the directory has `main.go` only, so `uv run --env-file .env main.py` cannot work. I ran `sh -c 'set -a; . ./.env; set +a; PORT=8011 
- friction: No `/healthz` in the sample:: `main.go` only serves `POST /run`, and `/healthz` returns 404. I dropped `--enable-app-health-check --app-health-check-path /healt
- log: `eino-claude.log`

**codex** — ok · Agent

- kind `Agent`
- log: `eino-codex.log`

**copilot** — ok

- friction: App ID quota already full, so reused the ready Agent; port 8000 was occupied and the checkout was Go rather than the described Python sample, so I added the mis
- log: `eino-copilot.log`


### Mastra (`typescript/mastra`)

**claude** — ok · Agent

- project `langgraph-spike` · kind `Agent`
- skills: diagrid:diagrid-deploy, diagrid:diagrid-app-tunnels
- friction: 1. **Identity quota was full.** The org is at 10/10 identities in the region (9 agents + 1 app), so applying `mastra-order-agent` was rejected. I tunnelled the 
- log: `mastra-claude.log`

**codex** — ok · Agent

- kind `Agent`
- log: `mastra-codex.log`

**copilot** — ok · Agent

- kind `Agent`
- friction: reused the existing Agent because identity quota was full; port 8000 was busy, so used 8001. Added missing `/healthz` without changing `/run`. First call hit a 
- log: `mastra-copilot.log`


### Goose (`rust/goose`)

**claude** — ok · Agent

- project `langgraph-spike` · kind `Agent`
- skills: diagrid-deploy, diagrid-app-tunnels (+ Diagrid MCP: whoami, get_usage,
- log: `goose-claude.log`

**codex** — ok · Agent

- kind `Agent`
- log: `goose-codex.log`

**copilot** — ok

- friction: identity quota was 10/10, so reused the existing ready Agent; port 8000 was busy, so used 8001; added the missing `/healthz` route. Skills used: `diagrid-deploy
- log: `goose-copilot.log`


## Shared friction (recurring across cells)

| Theme | What we saw |
|---|---|
| Agent vs App | Intended path is Diagrid `Agent`. Early / some Codex runs used plain `App` when “no workflow wrapper” was over-read. |
| Skills push durability | `diagrid-agent-scaffold` steers toward workflow runners; Spike A kept plain HTTP `/run`. |
| MCP gaps | No MCP tunnel/invoke — proof needed `diagrid call invoke`. |
| Quotas | 3-project cap; identity quota forced reusing `order-agent` on later frameworks. |
| Readiness | Connected ≠ healthy; App ID can lag Agent ready; need `/healthz` + short wait. |
| Ports | 8000 often busy → alternate port. |
| Client hang | Clients leave tunnels up; loop kicks ~20s after RESULT. |
| Claude API credit | `Credit balance is too low` blocked LangGraph variance until topped up. |

## Raw artifacts (optional)

- Per-cell transcripts: `results/<slug>-<client>.log`
- Run working copies: `~/spike-runs/<framework>-<timestamp>/`
- Loop ledger: `results/done.tsv`, `results/loop.stdout`

This file is the overview; open logs only if you need the full transcript.
