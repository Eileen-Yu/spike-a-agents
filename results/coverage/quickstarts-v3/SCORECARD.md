# Quickstart coverage — v3 standard

_Updated 2026-11-19 20:41 PST._ Prompt: `text-quickstart` block in [`../../spike-prompt.md`](../../spike-prompt.md). Claude, MCP signed in, graded by the harness (proof through Catalyst), one cell at a time with per-cell cleanup.

**5/5 ok** (pre-v3 README-follow run, self-graded: 15/15)

| Quickstart | Result | kind | via Catalyst | MCP calls | tokens in | time | id |
|---|---|---|---|---:|---:|---:|---|
| langgraph | ok | Agent | catalyst | 3 | 1.0M | 2m54s | `schedule-planner` |
| crewai | ok | Agent | catalyst | 3 | 1.5M | 3m59s | `venue-scout` |
| adk | ok | Agent | catalyst | 4 | 1000k | 3m05s | `entertainment-planner` |
| strands | ok | Agent | catalyst | 3 | 1.1M | 2m49s | `budget-planner` |
| pydantic-ai | ok | Agent | catalyst | 2 | 1.4M | 3m24s | `decoration-planner` |
