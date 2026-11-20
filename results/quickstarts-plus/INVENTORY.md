# Diagrid agent quickstarts / examples inventory

Pulled locally under `~/programming/`.

## catalyst-quickstarts (customer-facing) — Plus retest target

Repo: https://github.com/diagridio/catalyst-quickstarts → `agents/`

| Dir | Notes |
|---|---|
| langgraph | Schedule Planner (durable LangGraph) |
| crewai | Venue Scout |
| adk | Entertainment Planner |
| strands | Budget Analyst |
| pydantic-ai | Decorations Planner |
| openai-agents | Catering Coordinator |
| claude-agents | Photography Planner |
| deepagents | Transportation Planner |
| mastra | SRE Agent |
| goose | Release Manager |
| microsoft-dotnet | Event Planner |
| langchaingo | Go |
| langgraphjs | JS LangGraph |
| spring-ai/* | nested (event-planner, enterprise-identity, …) |
| dapr-agents/* | nested (durable-agent, orchestrator, …) |
| base | shared, not a standalone case |

## *-ai adapter repos (examples — durable SDK demos)

| Repo | Examples path |
|---|---|
| python-ai | `examples/{adk,claude_agents,crewai,deepagents,holmesgpt,identity,langchain,langgraph,openai_agents,pydantic_ai,smolagents,strands}` |
| dotnet-ai | `examples/{AgentInvokerDemo,EmailGateDemo,IdentityDemo,…}` |
| java-ai | `diagrid-spring-ai/examples/{durable-chat,identity,travel-planner}` |
| go-ai | `examples/{eino,identity,langchaingo,mcp}` |
| typescript-ai | `examples/{identity,mastra,n8n}` |
| rust-ai | `crates/diagrid-goose/examples/{quickstart,crash_recovery,…}` |

These already embed Diagrid durable adapters. Coverage pass = run official quickstarts first; *-ai/examples are follow-up if quickstarts pass.
