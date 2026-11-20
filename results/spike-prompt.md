# Spike A — prompt record

Different coverage layers used **different prompts**. Do not reuse the plain Spike A prompt on quickstarts or `*-ai/examples` (and vice versa).

| Layer | Source tree | Prompt below | Durable runners? | Success criteria |
|---|---|---|---|---|
| A. Plain samples | this repo `python/…` via `new-run.sh` | §1–2 | **No** — forbid wrapper | order **42** → **shipped** |
| B. Official quickstarts | `catalyst-quickstarts/agents/*` | §3 | **Yes** — keep them | README’s curl / one successful request |
| C. Crash recovery | same quickstarts + `dev-crash-test.yaml` | §4 | **Yes** | crash + resume same id |
| D. `*-ai` examples | `python-ai` / `go-ai` / … `examples/` | §5 | usually yes (adapter) | README primary example |

Org used for Plus passes: `eileen-plus-test` (staging) · project `default`. Week-1 plain matrix also ran on prod free `cattle-ackbar` with an older prompt (§2).

---

## Agent vs App (plain path only)

| Kind | Use on plain Spike A? |
|---|---|
| Diagrid **`Agent`** | **Yes** |
| Plain **`App`** | Only if Agent apply blocked — record friction |
| Workflow runner / identity middleware | **No** |

"No workflow wrapper" ≠ "no Agent resource".

---

## 1. Plain samples — canonical (Plus / dedicated Agent)

Used for Plus retests and the intended plain matrix. Swap `<FRAMEWORK>` / agent name.

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

Org eileen-plus-test (staging, Diagrid Cloud Plus). Use project `default`
(it exists). Create a dedicated Agent per run (e.g. <framework>-order-agent) —
do NOT reuse a generic shared Agent unless create is refused; if refused, record friction.
Create caller App spike-caller if missing.

CLI must be ~/.local/bin/diagrid first on PATH; flags --id and --yes.
API is https://api.staging.diagrid.dev (already selected via `diagrid whoami`).
Sample has GET /healthz. If port 8000 busy use another free port.

Create Agent (e.g. <framework>-order-agent). Tunnel on its managed App ID:
  diagrid dev run --project <p> --id <agent-app-id> --app-port <port>
  --enable-app-health-check --app-health-check-path /healthz --yes --
  uv run --env-file .env main.py.

After Connected wait ~5s then proof:
  diagrid call invoke post '<agent-app-id>.run' --id spike-caller -p <project>
  --data '{"prompt":"What is the status of order 42?"}' -v.

Success = answer contains shipped.
Print RESULT with deploy/run ok|fail, project, resource kind (Agent|App),
agent/app id, friction, which Diagrid skills you used.

After printing RESULT: stop any diagrid dev run / tunnels
(`diagrid dev stop --id <id> -p <project>`), then exit immediately.
```

Week-1 free-org variant replaced the org block with roughly:  
`Org cattle-ackbar. Reuse project langgraph-spike when possible (3 project max). Reuse caller spike-caller.`  
Same rules otherwise (no wrapper / no identity).

---

## 2. Plain samples — minimal first version (early LangGraph)

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

---

## 3. Official quickstarts — happy path (NOT plain Spike A)

`${rel}` = e.g. `agents/langgraph`. `${agent_hint}` = README agent name (e.g. `schedule-planner`).

```text
You are testing a Diagrid Catalyst official quickstart on Cloud Plus.

Directory: this folder is the quickstart from diagridio/catalyst-quickstarts/${rel}
Org: eileen-plus-test (staging API https://api.staging.diagrid.dev, plan Diagrid Cloud Plus).
Project: use existing project `default` — do NOT create a new project (region project limit).
CLI: ~/.local/bin/diagrid first on PATH. Prefer CLI if Diagrid MCP is on another org / unauthenticated; note that as friction.

Goal: follow this quickstart's README enough to get it running on Catalyst and prove one successful request (the README's curl/HTTP example, or equivalent diagrid call invoke). Offline/canned model is fine when the quickstart supports it.

Rules for THIS pass (quickstart coverage, not Spike A plain):
- The quickstart may already use durable workflow runners — that is expected; do not strip them.
- Create a dedicated Agent if needed (hint name: ${agent_hint}). Do not reuse unrelated Agents from other frameworks unless create is refused (then record friction).
- Apply any YAML/resources the README requires that fit in project default.
- After proof, stop diagrid dev run / tunnels and exit.

Print a RESULT block with:
deploy ok|fail, run ok|fail, project, agent/app id, how you proved it (status + short answer excerpt), friction, skills/CLI used.
```

---

## 4. Official quickstarts — crash recovery

```text
Test Diagrid quickstart CRASH RECOVERY on Cloud Plus (not happy-path).

Folder = catalyst-quickstarts/${rel}
Org eileen-plus-test staging Plus; project default; do not create projects.
CLI ~/.local/bin/diagrid; MCP may be unauth — use CLI and note friction.

Follow README crash section: create Agent ${agent} if needed; uv/npm/cargo as appropriate;
diagrid dev run -f dev-crash-test.yaml --approve --project default;
trigger crash with kill_after_seconds (or equivalent) on the crash endpoint;
restart; resume same id; prove completion.
Offline/canned OK. Keep durable runners.

RESULT: crash_path ok|fail, resume ok|fail, project, agent id, proof excerpt, friction.
Then stop tunnels and exit.
```

LangGraph-specific long form (same intent) also used: wait for crash mid-STEP2, restart, re-issue same id, prove booking confirmed / workflow completed.

---

## 5. `*-ai` adapter examples

### python-ai / examples/langgraph

```text
This directory is diagridio/python-ai/examples/langgraph (adapter SDK examples, often local dapr run — NOT catalyst-quickstarts).

On this machine: dapr CLI available. Org for any Catalyst steps: eileen-plus-test staging Plus, project default.

Goal: run the README examples that are practical here:
1) simple_graph.py via dapr run (as README)
2) test_crash_recovery.py two-run crash path if feasible
Record pass/fail for each. If something needs Catalyst instead of local dapr, try with diagrid CLI on project default and note the path difference.

Print RESULT table: example | ok/fail | how proved | friction.
Do not confuse this with Spike A plain samples.
```

### Other language samples (short)

```text
Directory is diagridio/${dir} (SDK example, may be local dapr or Catalyst).
Org eileen-plus-test staging Plus / project default if Catalyst needed.
Run the primary README example (or quickstart.rs for goose).
RESULT: ok|fail, proof, friction. Keep short.
```

(`${dir}` examples: `typescript-ai/examples/mastra`, `go-ai/examples/eino`, `rust-ai/crates/diagrid-goose/examples`.)

---

## Notes

- Skills are guidance; the **Rules** block is what constrains each layer.
- Plain vs quickstart is the big fork: plain forbids durable wrappers; quickstart expects them.
- Results live in `results/SUMMARY.md` (§ Scoreboard / Official quickstarts / Scenarios / `*-ai/examples`).
