# Spike A — plugin / skills quality test

[CAP-2783](https://linear.app/diagrid/issue/CAP-2783): can the Diagrid plugin take a **plain** agent and run it on Catalyst?

**Spike A is a quality test.** The prompt below is what a user would say.  
Do **not** put *how* to use Diagrid in the prompt (CLI flags, MCP vs CLI, PATH, whoami, ports, healthz, invoke recipes, Prefer Agent). Those belong in the plugin/skills — otherwise you grade a crib sheet.

| Layer | Role | Prompt |
|---|---|---|
| Plain samples (this repo) | **Quality score** | Canonical block below |
| Official quickstarts | Coverage only | Appendix B–C — follow that tree’s README |
| `*-ai/examples` | Coverage only | Appendix D — follow that tree’s README |

Experimenter setup (not for the agent prompt): Plus org `eileen-plus-test` / project `default`.  
Quality batch ledgers: `results/plugin-quality-plus/` (v1), `results/plugin-quality-plus-v2-no-prefer-agent/` (v2).

---

## How to score Agent vs App

Do **not** put Prefer-Agent in the prompt. Skills must steer. Record RESULT `resource kind`.

| Kind | Score |
|---|---|
| Diagrid **`Agent`** | Expected if skills work |
| Plain **`App`** | Finding / skill gap — not an automatic fail if shipped |
| Added workflow runner or identity middleware | **Fail** the cell |

---

## Canonical prompt (only paste this for Spike A)

Swap `<FRAMEWORK>`.

```text
Spike A (CAP-2783) — plugin and skills quality test.

This directory is a plain <FRAMEWORK> agent with get_order_status.
It knows nothing about Catalyst.

Use the Diagrid plugin to get it running on Catalyst and prove a run.

Rules:
- Do NOT add a workflow runner wrapper (no DaprWorkflow*Runner / harness rewrite).
- Do NOT add identity/OAuth middleware.
- Keep the sample's existing HTTP /run loop; do not rewrite the agent into a durable harness.

Success: asking about order 42 returns an answer that contains "shipped".

When done, print RESULT with:
deploy ok|fail, run ok|fail, project, resource kind (Agent|App), agent/app id,
what you used from the Diagrid plugin, and any friction or gaps you hit.
Stop anything you started, then exit.
```

### Keep out of the prompt

| Banned in prompt | Why |
|---|---|
| Prefer Agent vs App | Skills must supply product guidance |
| `agent create` / `dev run` / `call invoke` / flags / ports | CLI cookbook |
| `/healthz`, readiness waits, tunnel steps | Platform recipe |
| Prefer CLI vs MCP, PATH, `whoami`, org-mismatch tips | Auth/tool coaching |
| Pre-patching the sample (e.g. add `/healthz` before the run) | Answers for the plugin |
| “Reuse Agent X / project Y” | Feeds the environment answer |

`run-matrix-loop.sh` / quality batches extract **this** ```text``` block only and must **not** pre-patch samples.

---

## Appendix — coverage prompts (not Spike A quality score)

Still no CLI/MCP/auth cribs. Point at the tree’s README.

### A. Early minimal plain (historical)

```text
Spike A (CAP-2783): This directory is a plain LangGraph agent with one tool
get_order_status. Deploy it to Diagrid/Catalyst through the Diagrid plugin
and run it successfully.

Rules: do NOT add a workflow runner wrapper; do NOT add identity/OAuth middleware.
Success = asking about order 42 gets an answer that says shipped.
When done, print RESULT: deploy ok/fail, run ok/fail, project, resource kind (Agent|App),
friction or skill gaps, files changed.
```

### B. Official quickstarts — happy path

`${rel}` = e.g. `agents/langgraph`. Durable runners in the quickstart are expected.

```text
You are testing a Diagrid Catalyst official quickstart.

Directory: diagridio/catalyst-quickstarts/${rel}.

Goal: follow this quickstart's README enough to get it running on Catalyst and prove
one successful request (the README's example). Offline/canned model is fine when supported.

Rules:
- Keep durable workflow runners the quickstart already uses; do not strip them.
- Do not create a new project if the org is already at its project limit.

RESULT: deploy ok|fail, run ok|fail, project, agent/app id, how you proved it,
friction, what you used from the Diagrid plugin.
Stop anything you started, then exit.
```

### C. Official quickstarts — crash recovery

```text
Test this Diagrid quickstart's crash recovery (not the happy path).

Folder = catalyst-quickstarts/${rel}.

Follow the README crash section: trigger a crash, restart, resume the same id, prove completion.
Keep durable runners. Offline/canned OK.

RESULT: crash_path ok|fail, resume ok|fail, project, agent id, proof excerpt, friction.
Stop anything you started, then exit.
```

### D. `*-ai` adapter examples

```text
This directory is a Diagrid *-ai SDK example (often local dapr — not Spike A plain samples).

Goal: run the primary README example(s) practical here.
Record pass/fail, how proved, friction.
Do not treat this as Spike A plain plugin scoring.
```

---

## Deprecated

Pre-2026-11-19-evening prompts fed CLI recipes, Prefer-Agent, whoami/PATH, and CLI-vs-MCP tips. Do not use for quality scoring. See git history.
