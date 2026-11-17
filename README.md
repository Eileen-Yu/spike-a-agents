# Spike A: plain agents, one per framework

Starting points for [CAP-2783](https://linear.app/diagrid/issue/CAP-2783). Each
sample is an ordinary agent in one framework that knows nothing about Catalyst:
no Dapr, no `diagrid` package, no workflow wrapper, no identity middleware. The
spike asks the plugin to bring it to Catalyst and run it.

Every sample is the same agent, so results compare across frameworks:

- one tool, `get_order_status(order_id)`, which returns `Order <id>: shipped, arriving Friday.`
- served over HTTP on `PORT` (default 8000): `POST /run {"prompt": "..."}` returns `{"answer": "..."}`
- pass when `What's the status of order 42?` gets an answer that says **shipped**

## Samples

| Language | Framework | Path | Model key | Checked here |
|---|---|---|---|---|
| Python | LangGraph | `python/langgraph` | `OPENAI_API_KEY` | deps install, imports |
| Python | LangChain | `python/langchain` | `OPENAI_API_KEY` | deps install, imports |
| Python | CrewAI | `python/crewai` | `OPENAI_API_KEY` | deps install, imports |
| Python | Google ADK (via LiteLLM) | `python/adk` | `OPENAI_API_KEY` | deps install, imports |
| Python | Strands | `python/strands` | `OPENAI_API_KEY` | deps install, imports |
| Python | Pydantic AI | `python/pydantic-ai` | `OPENAI_API_KEY` | deps install, imports |
| Python | OpenAI Agents | `python/openai-agents` | `OPENAI_API_KEY` | deps install, imports |
| Python | Claude Agent SDK | `python/claude-agents` | `ANTHROPIC_API_KEY` | deps install, imports |
| Python | smolagents | `python/smolagents` | `OPENAI_API_KEY` | deps install, imports |
| Python | Deep Agents | `python/deepagents` | `OPENAI_API_KEY` | deps install, imports |
| Python | HolmesGPT (CLI + custom toolset) | `python/holmesgpt` | `OPENAI_API_KEY` | deps install, toolset loads |
| Python | Dapr Agents | `python/dapr-agents` | `OPENAI_API_KEY` | deps install, configs build |
| Python | none (BYOA, hand-written loop) | `python/byoa` | `OPENAI_API_KEY` | deps install, imports |
| .NET | Microsoft Agent Framework | `dotnet/microsoft-agent-framework` | `OPENAI_API_KEY` | `dotnet build` |
| Java | Spring AI | `java/spring-ai` | `OPENAI_API_KEY` | `mvn package`, app boots |
| Go | LangChainGo | `go/langchaingo` | `OPENAI_API_KEY` | `go build` |
| Go | Eino | `go/eino` | `OPENAI_API_KEY` | `go build` |
| TypeScript | Mastra | `typescript/mastra` | `OPENAI_API_KEY` | `tsc --noEmit` |
| Rust | Goose (CLI) | `rust/goose` | Goose's provider | not built: needs Cargo with edition 2024 |

None of them has been run against a model yet. Run each once locally with a real
key before its spike session, so a broken sample isn't logged as a plugin
problem.

Three differ from the rest:

- **Dapr Agents** has only `DurableAgent`, so the sample already runs on a local
  Dapr sidecar (`dapr run ... --resources-path ./resources`) and serves the
  framework's own `POST /agent/run {"task": "..."}`. What it lacks is Catalyst.
- **HolmesGPT** has no stable embedding API, so the service shells out to
  `holmes ask` with `toolsets.yaml`.
- **Goose** is a CLI agent too: the service runs `goose run --no-session --quiet`
  with the developer extension, which calls `./order-status.sh` as its tool.

## Running a spike case

```sh
./new-run.sh python/langgraph      # prints ~/spike-runs/langgraph-<timestamp>
cd ~/spike-runs/langgraph-<timestamp>
claude                             # fresh session, then: "deploy my agent to Diagrid and run it"
git diff                           # what the plugin changed
```

`new-run.sh` copies the sample without its build output and commits it, so
every run starts from the same tree.
