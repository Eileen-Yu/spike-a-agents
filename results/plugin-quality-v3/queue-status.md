# Spike A v3 — queue status

Updated: 2026-11-19 19:30:47 PST · ledger: `ledger.tsv`

## Running now
- langgraph-copilot-1

## Remaining (2)
- langgraph × copilot
- byoa × copilot

## Ledger
```
# slug                     client  attempt  status                 kind   via       code       violation  agent_id                    mcp_calls  tokens_in  tools  log                                     finished                   wall_s  tokens_out  credits
langgraph                  claude  1        ok                     Agent  catalyst  untouched  -          order-agent-lg-1847         13         1823790    26     langgraph-claude-1.log                  2026-11-19T18:50:06-08:00  133     7616        -
langgraph                  claude  2        ok                     Agent  catalyst  untouched  -          order-agent-lg-1855         16         1957451    30     langgraph-claude-2.log                  2026-11-19T18:58:24-08:00  186     10336       -
langgraph                  claude  3        ok                     Agent  catalyst  untouched  -          order-agent-lg-1858         14         1957335    28     langgraph-claude-3.log                  2026-11-19T19:01:18-08:00  159     7920        -
langchain                  claude  1        ok                     Agent  catalyst  untouched  -          order-agent-langchain-1907  15         2480197    33     langchain-claude-1.log                  2026-11-19T19:06:02-08:00  185     8686        -
strands                    claude  1        ok                     Agent  catalyst  untouched  -          order-agent-strands         12         1675414    25     strands-claude-1.log                    2026-11-19T19:06:52-08:00  143     7836        -
adk                        claude  1        ok                     Agent  catalyst  untouched  -          order-agent-adk             10         1570172    25     adk-claude-1.log                        2026-11-19T19:07:02-08:00  183     9024        -
crewai                     claude  1        ok                     App    catalyst  untouched  -          crewai-orders               8          1585944    23     crewai-claude-1.log                     2026-11-19T19:07:42-08:00  255     7712        -
pydantic-ai                claude  1        ok                     App    catalyst  untouched  -          order-agent-pydantic-ai     16         2108207    28     pydantic-ai-claude-1.log                2026-11-19T19:08:52-08:00  154     7772        -
openai-agents              claude  1        ok                     App    catalyst  untouched  -          order-agent-openai          12         1452833    23     openai-agents-claude-1.log              2026-11-19T19:09:17-08:00  131     7009        -
smolagents                 claude  1        ok                     App    catalyst  untouched  -          order-agent-smolagents      12         1787720    26     smolagents-claude-1.log                 2026-11-19T19:10:37-08:00  149     7663        -
deepagents                 claude  1        ok                     Agent  catalyst  untouched  -          order-agent-deepagents      11         1616268    24     deepagents-claude-1.log                 2026-11-19T19:11:32-08:00  143     7008        -
claude-agents              claude  1        ok                     Agent  catalyst  untouched  -          order-agent-claude          15         2543636    33     claude-agents-claude-1.log              2026-11-19T19:11:57-08:00  262     9953        -
holmesgpt                  claude  1        ok                     App    catalyst  untouched  -          order-agent-holmesgpt       12         2013171    30     holmesgpt-claude-1.log                  2026-11-19T19:12:48-08:00  188     8900        -
dapr-agents                claude  1        fail                   Agent  catalyst  untouched  -          order-agent-dapr-agents     16         2782215    34     dapr-agents-claude-1.log                2026-11-19T19:14:18-08:00  203     11283       -
byoa                       claude  1        ok                     Agent  catalyst  untouched  -          order-agent-byoa-1911       13         1599389    25     byoa-claude-1.log                       2026-11-19T19:14:37-08:00  171     7272        -
microsoft-agent-framework  claude  1        ok                     Agent  catalyst  untouched  -          order-agent-maf             14         1829496    27     microsoft-agent-framework-claude-1.log  2026-11-19T19:14:42-08:00  147     8570        -
spring-ai                  claude  1        ok                     Agent  catalyst  untouched  -          order-agent-spring-ai       13         2026608    28     spring-ai-claude-1.log                  2026-11-19T19:15:43-08:00  160     9153        -
langchaingo                claude  1        ok                     App    catalyst  untouched  -          order-agent-langchaingo     12         1657310    26     langchaingo-claude-1.log                2026-11-19T19:17:33-08:00  178     8429        -
eino                       claude  1        ok                     Agent  catalyst  untouched  -          order-agent-eino            13         1875157    27     eino-claude-1.log                       2026-11-19T19:18:23-08:00  199     9186        -
goose                      claude  1        ok                     App    catalyst  untouched  -          order-agent-goose           12         1585973    28     goose-claude-1.log                      2026-11-19T19:18:24-08:00  140     7621        -
mastra                     claude  1        ok                     App    catalyst  untouched  -          order-agent-mastra-1915     13         1589066    25     mastra-claude-1.log                     2026-11-19T19:18:46-08:00  176     7652        -
langgraph                  codex   1        fail-noresult(rc=143)  -      unknown   untouched  -          -                           -          -          -      langgraph-codex-1.log                   2026-11-19T19:30:01-08:00  8       (in total)  -
dapr-agents                claude  2        fail-noresult(rc=143)  -      unknown   untouched  -          -                           3          144016     7      dapr-agents-claude-2.log                2026-11-19T19:30:20-08:00  26      1251        -
byoa                       codex   1        ok                     Agent  catalyst  untouched  -          -                           -          -          -      byoa-codex-1.log                        2026-11-19T19:30:46-08:00  29      (in total)  -
```
