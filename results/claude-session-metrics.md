## Speed / session metrics (Week 1 baseline)

Source: `session_metrics.py` on Claude Code session logs ([CAP-2789](https://linear.app/diagrid/issue/CAP-2789)).
Week 2 comparison KPIs: **tokens in/out**, **model requests**, **tool calls**, **user turns**. Wall clock recorded but not the official KPI.

**Clients:** Codex / Copilot are **not** in these tables — the script only reads Claude Code logs. Pass/fail for all three clients is in the matrix above.

### LangGraph × Claude (connect-an-agent baseline + variance)

| # | run | tokens in | tokens out | model req | tool calls (all / catalyst / fail / rpt) | user turns | skills (bytes) | wall | note |
|---:|---|---:|---:|---:|---|---:|---|---|---|
| 1 | `langgraph-claude-metrics.md` | 1,441,613 | 9,381 | 14 | 30 / 12 / 1 / 1 | 0 | diagrid-agent-scaffold, diagrid-app-tunnels, diagrid-deploy, diagrid-develop (72,025) | 3m 58s | baseline (saved metrics file) |
| 2 | `langgraph-20261117-163038` | 1,874,346 | 10,248 | 17 | 30 / 12 / 1 / 1 | 0 | diagrid-debug (22,534) | 4m 34s | Claude session |
| 3 | `langgraph-20261118-154815` | 513,714 | 3,524 | 8 | 16 / 6 / 0 / 0 | 0 | diagrid-app-tunnels, diagrid-deploy (41,402) | 1m 18s | Claude session |
| 4 | `langgraph-20261118-154957` | 439,607 | 3,886 | 7 | 15 / 5 / 1 / 0 | 0 | diagrid-app-tunnels, diagrid-deploy (41,402) | 1m 36s | Claude session |
| 5 | `langgraph-20261118-145224` | 432,808 | 2,897 | 6 | 17 / 8 / 2 / 0 | 0 | diagrid-app-tunnels, diagrid-deploy (41,402) | 10m 24s | Claude session |

Cold / first-success style runs: **~1.4M–1.9M input tokens**, **~30 tool calls**, **~4 minutes** wall.
Reuse / warm variance runs (existing Agent/project): **~0.4M–0.5M tokens**, **~1–2 min** — use the heavy rows as the Week 2 speed baseline, not the reuse rows.

### Other frameworks × Claude (richest non-empty session each)

| Framework | tokens in | tokens out | model req | tool calls (all / catalyst / fail / rpt) | user turns | wall | source |
|---|---:|---:|---:|---|---:|---|---|
| LangChain | 957,838 | 5,216 | 15 | 20 / 8 / 1 / 0 | 0 | 10m 46s | `langchain-claude-metrics.md` |
| CrewAI | 556,358 | 3,539 | 10 | 13 / 6 / 0 / 0 | 0 | 10m 33s | `crewai-claude-metrics.md` |
| Google ADK | 275,989 | 2,726 | 8 | 7 / 0 / 1 / 0 | 0 | 155m 07s | `adk-claude-metrics.md` `wall clock includes long idle/hang; treat tokens as the useful signal` |
| Strands | 496,808 | 3,708 | 8 | 17 / 8 / 0 / 0 | 0 | 1m 21s | `strands-20261118-122254` |
| Pydantic AI | 631,359 | 3,861 | 8 | 18 / 9 / 0 / 0 | 0 | 1m 23s | `pydantic-ai-20261118-125512` |
| OpenAI Agents | 534,733 | 3,831 | 9 | 17 / 8 / 0 / 0 | 0 | 1m 27s | `openai-agents-20261118-125749` |
| Claude Agent SDK | 641,945 | 4,493 | 10 | 18 / 7 / 0 / 0 | 0 | 2m 06s | `claude-agents-20261118-125937` `picked richest successful session (≥100k tokens); short abort sessions discarded` |
| smolagents | 573,985 | 4,031 | 9 | 19 / 9 / 0 / 1 | 0 | 1m 36s | `smolagents-20261118-130200` |
| Deep Agents | 769,955 | 3,916 | 10 | 20 / 11 / 0 / 1 | 0 | 1m 28s | `deepagents-20261118-130354` |
| HolmesGPT | 752,886 | 4,748 | 11 | 20 / 9 / 0 / 0 | 0 | 2m 15s | `holmesgpt-20261118-130745` |
| Dapr Agents | 1,939,647 | 9,694 | 22 | 36 / 15 / 1 / 1 | 0 | 6m 32s | `dapr-agents-20261118-131019` |
| BYOA | 778,746 | 4,881 | 12 | 20 / 11 / 1 / 1 | 0 | 5m 51s | `byoa-20261118-120155` |
| .NET MAF | 601,381 | 5,666 | 9 | 18 / 8 / 1 / 0 | 0 | 1m 43s | `microsoft-agent-framework-20261118-131713` |
| Spring AI | 601,887 | 4,649 | 9 | 18 / 7 / 2 / 0 | 0 | 1m 53s | `spring-ai-20261118-131916` |
| LangChainGo | 900,150 | 6,458 | 13 | 23 / 9 / 2 / 0 | 0 | 2m 19s | `langchaingo-20261118-132134` |
| Eino | 1,088,659 | 7,797 | 15 | 29 / 9 / 3 / 1 | 0 | 2m 36s | `eino-20261118-132421` |
| Mastra | 752,709 | 5,621 | 11 | 23 / 9 / 1 / 2 | 0 | 2m 04s | `mastra-20261118-132937` |
| Goose | 1,173,343 | 6,556 | 14 | 25 / 9 / 2 / 0 | 0 | 2m 07s | `goose-20261118-133200` |

_Generated 2026-11-18 16:55. Typical client: Claude Code 2.1.327 / claude-fable-5-2 / diagrid plugin 0.10.2._
