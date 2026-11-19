# Spike A prompt (CAP-2783)

Used for Person A agent runs: plain agent → Diagrid plugin → Catalyst.
Hard rules keep the path **without** workflow runner wrapper or identity middleware.

## Agent vs App (read this)

Spike A tests a **plain agent** (framework loop / tools), not a generic app.

| Kind | Use? |
|---|---|
| Diagrid **`Agent`** resource | **Yes** — preferred. Front the sample with `kind: Agent`. Its managed App ID is fine for tunnel/invoke. |
| Plain Diagrid **`App`** | Only if Agent apply is blocked. Record that as friction. |
| Workflow runner / harness (`DaprWorkflow*Runner`, identity/OAuth middleware) | **No** — Spike A is the non-durable plain path. |

"No workflow wrapper" ≠ "no Agent resource". Creating an `App` because scaffold mentions workflows is the wrong escape hatch — that drift is itself a finding.

CLI wording (`--app-port`, `call invoke`, App ID) is normal: every Agent is backed by an identity. Still create/list via `diagrid agent`, not `diagrid app`, unless forced.

## Canonical prompt (latest)

Swap the framework name / sample description per run. Keep the Rules block unchanged.

```text
Spike A (CAP-2783): This directory is a plain <FRAMEWORK> agent with get_order_status.
Use the Diagrid skills/plugin (diagrid-deploy / diagrid-agent-scaffold /
diagrid-develop / diagrid-app-tunnels) and the connected Diagrid MCP to deploy
it to Catalyst and prove a run.

Rules:
- Prefer a Diagrid Agent resource (kind: Agent), NOT a plain App.
- NO workflow runner wrapper (no DaprWorkflow*Runner / harness rewrite).
- NO identity/OAuth middleware.
- The sample's HTTP /run loop stays as-is; tunnel it behind the Agent's App ID.

Org cattle-ackbar. Reuse project langgraph-spike when possible
(3 project max; do not create a new project unless reuse is impossible).
Reuse caller App spike-caller when it exists.

CLI must be ~/.local/bin/diagrid 1.130.0 first on PATH; flags --id and --yes.
Sample has GET /healthz. If port 8000 busy use another free port.

Create/reuse Agent (e.g. <framework>-order-agent). Tunnel on its managed App ID:
  diagrid dev run --project <p> --id <agent-app-id> --app-port <port>
  --enable-app-health-check --app-health-check-path /healthz --yes --
  uv run --env-file .env main.py.

After Connected wait ~5s then proof:
  diagrid call invoke post '<agent-app-id>.run' --id spike-caller -p <project>
  --data '{"prompt":"What is the status of order 42?"}' -v.

Success = answer contains shipped.
Print RESULT with deploy/run ok|fail, project, resource kind (Agent|App),
agent/app id, friction, which Diagrid skills you used.

After printing RESULT: stop any diagrid dev run / tunnels you started
(`diagrid dev stop --id <id> -p <project>`), then exit the session immediately.
Do not leave background processes running.
```

## Minimal first version (Claude + LangGraph)

```text
Spike A (CAP-2783): This directory is a plain LangGraph agent with one tool
get_order_status. Deploy it to Diagrid/Catalyst through the Diagrid plugin
skills and run it successfully.

Rules: do NOT add a workflow runner wrapper; do NOT add identity/OAuth middleware.
Prefer Diagrid Agent resource over plain App.
Use the default project if one exists.
Success = asking about order 42 gets an answer that says shipped.
When done, print a short RESULT block with: deploy ok/fail, run ok/fail,
project name, resource kind, any friction or skill gaps, and list files you changed.
```

## Notes

- Skills are guidance; the Rules line is what constrains scaffold away from workflow harness.
- Agent scaffold may push durability — keep the plain sample and still use an Agent resource.
- Later prompts added CLI path, healthz, port, and invoke proof after those became known friction.
