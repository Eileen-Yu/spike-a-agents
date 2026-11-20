# Quickstart coverage — v3 standard

_Updated 2026-11-19 21:24 PST._ Prompt: `text-quickstart` block in [`../../spike-prompt.md`](../../spike-prompt.md). Claude, MCP signed in, graded by the harness (proof through Catalyst), one cell at a time with per-cell cleanup.

**14/14 ok** (pre-v3 README-follow run, self-graded: 15/15)

| Quickstart | Result | kind | via Catalyst | MCP calls | tokens in | time | id |
|---|---|---|---|---:|---:|---:|---|
| langgraph | ok | Agent | catalyst | 3 | 1.0M | 2m54s | `schedule-planner` |
| crewai | ok | Agent | catalyst | 3 | 1.5M | 3m59s | `venue-scout` |
| adk | ok | Agent | catalyst | 4 | 1000k | 3m05s | `entertainment-planner` |
| strands | ok | Agent | catalyst | 3 | 1.1M | 2m49s | `budget-planner` |
| pydantic-ai | ok | Agent | catalyst | 2 | 1.4M | 3m24s | `decoration-planner` |
| openai-agents | ok | Agent | catalyst | 3 | 1.3M | 2m54s | `catering-coordinator` |
| claude-agents | ok | Agent | catalyst | 5 | 1.8M | 4m40s | `photography-planner` |
| deepagents | ok | Agent | catalyst | 5 | 1.3M | 3m14s | `transportation-planner` |
| mastra | ok | Agent | catalyst | 6 | 1.1M | 3m24s | `sre-agent` |
| goose | ok | Agent | catalyst | 4 | 1.4M | 2m58s | `release-manager` |
| microsoft-dotnet | ok | Agent | catalyst | 5 | 2.3M | 15m02s | `event-planner` |
| langchaingo | ok | App | catalyst | 0 | 903k | 3m04s | `crm-mcp` |
| langgraphjs | ok | App | catalyst | 2 | 1.0M | 3m00s | `identity-agent` |
| spring-ai-event-planner | ok | Agent | catalyst | 4 | 1.6M | 4m08s | `spring-ai-event-planner` |
