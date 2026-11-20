# Spike A v3 — queue status

Updated: 2026-11-19 20:41:26 PST · ledger: `ledger.tsv`

## Running now
- qs-openai-agents-claude-1

## Remaining (10)
- qs-openai-agents × claude
- qs-claude-agents × claude
- qs-deepagents × claude
- qs-mastra × claude
- qs-goose × claude
- qs-microsoft-dotnet × claude
- qs-langchaingo × claude
- qs-langgraphjs × claude
- qs-spring-ai-event-planner × claude
- qs-dapr-agents-durable × claude

## Ledger
```
# slug          client  attempt  status  kind   via       code       violation  agent_id               mcp_calls  tokens_in  tools  log                          finished                   wall_s  tokens_out  credits
qs-langgraph    claude  1        ok      Agent  catalyst  untouched  -          schedule-planner       3          1010627    16     qs-langgraph-claude-1.log    2026-11-19T20:27:40-08:00  174     6183        -
qs-crewai       claude  1        ok      Agent  catalyst  untouched  -          venue-scout            3          1457284    22     qs-crewai-claude-1.log       2026-11-19T20:31:44-08:00  239     7998        -
qs-adk          claude  1        ok      Agent  catalyst  untouched  -          entertainment-planner  4          999720     17     qs-adk-claude-1.log          2026-11-19T20:34:54-08:00  185     5952        -
qs-strands      claude  1        ok      Agent  catalyst  untouched  -          budget-planner         3          1055478    16     qs-strands-claude-1.log      2026-11-19T20:37:49-08:00  169     5556        -
qs-pydantic-ai  claude  1        ok      Agent  catalyst  untouched  -          decoration-planner     2          1370414    20     qs-pydantic-ai-claude-1.log  2026-11-19T20:41:19-08:00  204     6882        -
```
