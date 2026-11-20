# Spike A v3 — queue status

Updated: 2026-11-19 19:08:57 PST · ledger: `ledger.tsv`

## Running now
- claude-agents-claude-1
- deepagents-claude-1
- openai-agents-claude-1
- smolagents-claude-1

## Remaining (13)
- openai-agents × claude
- claude-agents × claude
- smolagents × claude
- deepagents × claude
- holmesgpt × claude
- dapr-agents × claude
- byoa × claude
- microsoft-agent-framework × claude
- spring-ai × claude
- langchaingo × claude
- eino × claude
- mastra × claude
- goose × claude

## Ledger
```
# slug       client  attempt  status  kind   via       code       violation  agent_id                    mcp_calls  tokens_in  tools  log                       finished
langgraph    claude  1        ok      Agent  catalyst  untouched  -          order-agent-lg-1847         13         1823790    26     langgraph-claude-1.log    2026-11-19T18:50:06-08:00
langgraph    claude  2        ok      Agent  catalyst  untouched  -          order-agent-lg-1855         16         1957451    30     langgraph-claude-2.log    2026-11-19T18:58:24-08:00
langgraph    claude  3        ok      Agent  catalyst  untouched  -          order-agent-lg-1858         14         1957335    28     langgraph-claude-3.log    2026-11-19T19:01:18-08:00
langchain    claude  1        ok      Agent  catalyst  untouched  -          order-agent-langchain-1907  15         2480197    33     langchain-claude-1.log    2026-11-19T19:06:02-08:00
strands      claude  1        ok      Agent  catalyst  untouched  -          identity                    12         1675414    25     strands-claude-1.log      2026-11-19T19:06:52-08:00
adk          claude  1        ok      Agent  catalyst  untouched  -          order-agent-adk             10         1570172    25     adk-claude-1.log          2026-11-19T19:07:02-08:00
crewai       claude  1        ok      App    catalyst  untouched  -          crewai-orders               8          1585944    23     crewai-claude-1.log       2026-11-19T19:07:42-08:00
pydantic-ai  claude  1        ok      App    catalyst  untouched  -          order-agent-pydantic-ai     16         2108207    28     pydantic-ai-claude-1.log  2026-11-19T19:08:52-08:00
```
