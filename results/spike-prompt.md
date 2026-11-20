# Spike A prompt (v3)

`run-matrix-loop.sh` sends this block verbatim, with `<FRAMEWORK>` swapped in. It's written the way a user would ask: no test framing, no plugin name, no class names, no CLI or MCP recipes. Routing to the skills is part of what's tested.

```text
This folder is my <FRAMEWORK> agent. It answers order questions over HTTP (POST /run).

Deploy it to Diagrid Catalyst and run it there, as-is. Don't change how the agent
works: don't make it durable and don't add auth/identity. I just want this exact
agent running on Catalyst.

Done means a request that goes through Catalyst (not straight to localhost) asking
about order 42 gets an answer that says "shipped".

When you're done, print a RESULT block with: deploy ok|fail, run ok|fail, org,
project, resource kind (Agent|App), agent/app id, the exact command or request that
proved the run and its response, the console URL if there is one, which Diagrid
skills and MCP tools you used, and every place the Diagrid instructions were wrong,
missing or pointed you the wrong way. Then stop everything you started.
```

## Quickstart prompt (coverage, `SPIKE_MODE=quickstart`)

Same rules, run against the official `catalyst-quickstarts/agents/*`. The README is the product, so the agent may follow it, but nothing beyond it is given.

```text-quickstart
This folder is a Diagrid quickstart: <FRAMEWORK>. Get it running on Diagrid Catalyst
the way its README describes, and send it one request through Catalyst (not straight
to localhost) that shows it works.

When you're done, print a RESULT block with: deploy ok|fail, run ok|fail, org,
project, resource kind (Agent|App), agent/app id(s), the exact command or request that
proved the run and its response, which Diagrid skills and MCP tools you used, and every
place the README or the Diagrid instructions were wrong, missing or pointed you the wrong
way. Then stop everything you started.
```

Graded like the plain samples, except that durable runners are expected, so the `fail-rules` diff check is off. Cells run one at a time, and everything a cell created (Agents, Apps, pub/sub topics) is deleted afterwards, so the 10-topic cap isn't refilled.

## Graded by the harness, not by the model

| Check | How | Outcome |
|---|---|---|
| Deployed and ran | `run: ok` / `deploy: ok` in the RESULT block | ok / fail |
| Went through Catalyst | the proof isn't a `curl localhost` | `fail-localhost` |
| Agent code untouched | `git diff` of code and dependency files (build and dependency dirs excluded): any `diagrid` SDK, `*Runner`, `DurableAgent`, workflow runtime or identity import | `fail-rules` |
| Agent vs App | RESULT `resource kind` | App = finding, not a fail |
| Cost | Claude `session_metrics.py`; Codex `tokens used`; Copilot `Tokens ↑/↓`, AI credits; harness wall clock | recorded |

## Never put these in the prompt

Agent-vs-App preference · CLI commands or flags · `/healthz` or readiness steps · CLI vs MCP, PATH, `whoami` tips · "reuse agent X / project Y" · pre-patching the sample. Each of these answers part of the test, so the skills have to supply them.

## History

v1 included "prefer Agent", which hid the App drift. v2 named the test, the plugin and `DaprWorkflow*Runner`, and accepted a localhost proof. Week 1 included CLI recipes. All are superseded. Their wording and the coverage prompts (quickstarts, crash recovery, `*-ai` examples) are in [`archive/spike-prompt-history.md`](archive/spike-prompt-history.md).
