# Spike A — results ([CAP-2783](https://linear.app/diagrid/issue/CAP-2783))

_Updated 2026-11-19 21:24 PST. Regenerated after every cell by `results/build-v3-summary.py` — don't edit by hand._

**Current run = v3:** user-voice prompt ([`spike-prompt.md`](spike-prompt.md)), plugin MCP signed in, staging Plus `eileen-plus-test`/`default`, graded outside the model (git diff, proof path). Plugin 0.10.2, Claude = claude-opus-5-5.

**Score (cells ok, latest attempt): claude 22/22 · codex 2/2 · copilot 2/2** · landed on App instead of Agent: 11 runs · rule violations: 0 · localhost proofs: 0

## Each cell — result · resource kind · tokens in · time

| Framework | Claude | Codex | Copilot |
|---|---|---|---|
| LangGraph | #1 ok · Agent · 1.8M · 2m13s<br>#2 ok · Agent · 2.0M · 3m06s<br>#3 ok · Agent · 2.0M · 2m39s<br>#4 ok · Agent · 1.8M · 2m31s | ok · **App** · 108k · 4m21s | ok · **App** · 1.9M · 8m02s |
| LangChain | ok · Agent · 2.5M · 3m05s |  |  |
| CrewAI | ok · **App** · 1.6M · 4m15s |  |  |
| Google ADK | ok · Agent · 1.6M · 3m03s |  |  |
| Strands | ok · Agent · 1.7M · 2m23s |  |  |
| Pydantic AI | ok · **App** · 2.1M · 2m34s |  |  |
| OpenAI Agents | ok · **App** · 1.5M · 2m11s |  |  |
| Claude Agent SDK | ok · Agent · 2.5M · 4m22s |  |  |
| smolagents | ok · **App** · 1.8M · 2m29s |  |  |
| Deep Agents | ok · Agent · 1.6M · 2m23s |  |  |
| HolmesGPT | ok · **App** · 2.0M · 3m08s |  |  |
| Dapr Agents | #1 **FAIL** [CAP-2932](https://linear.app/diagrid/issue/CAP-2932) · Agent · 2.8M · 3m23s<br>#2 ok · Agent · 3.8M · 5m11s |  |  |
| BYOA | ok · Agent · 1.6M · 2m51s | ok · **App** · 90k · 5m12s | ok · Agent · 1.2M · 4m11s |
| .NET MAF | ok · Agent · 1.8M · 2m27s |  |  |
| Spring AI | ok · Agent · 2.0M · 2m40s |  |  |
| LangChainGo | ok · **App** · 1.7M · 2m58s |  |  |
| Eino | ok · Agent · 1.9M · 3m19s |  |  |
| Mastra | ok · **App** · 1.6M · 2m56s |  |  |
| Goose | ok · **App** · 1.6M · 2m20s |  |  |

Tokens in = everything the model read (incl. cache). Time = harness clock per cell. Full per-run detail: [`plugin-quality-v3/SCORECARD.md`](plugin-quality-v3/SCORECARD.md).

## Cost

| Client | cells | ok | avg tokens in | avg time | total tokens in | total time |
|---|---:|---:|---:|---:|---:|---:|
| claude | 23 | 22 | 2.0M | 2m 58s | 45.1M | 68m 27s |
| codex | 2 | 2 | 99k | 4m 46s | 198k | 9m 33s |
| copilot | 2 | 2 | 1.6M | 6m 06s | 3.1M | 12m 13s |

## Findings (7 tickets)

1. **Skills have no first-class "connect an existing agent" path**: App vs Agent contradicts (landed on App: Claude 8/21, Codex 2/2, Copilot 1/2), skills never say Catalyst doesn't host your code, no documented way to prove a run, name checks mislead — [CAP-2876](https://linear.app/diagrid/issue/CAP-2876) (Urgent)
2. **Tunnel return path times out at ~10s → HTTP 502** on slow agent turns; Agent kind has no timeout setting — [CAP-2931](https://linear.app/diagrid/issue/CAP-2931)
3. **Credentials in transcripts**: agent printed `~/.diagrid/creds`; `get_connection` returns tokens into chat — [CAP-2926](https://linear.app/diagrid/issue/CAP-2926)
4. **Invisible quotas**: pub/sub 10-topic cap (Dapr Agents crashed on leftover topics, ok on a clean project) and identity cap — [CAP-2932](https://linear.app/diagrid/issue/CAP-2932)
5. **MCP vs CLI on different env/org**, no CLI fallback, `DIAGRID_MCP_URL` undocumented — [CAP-2921](https://linear.app/diagrid/issue/CAP-2921)
6. **MCP/CLI behaviour misleads**: readiness, silent side effects, list filters, dry run, console URL — [CAP-2929](https://linear.app/diagrid/issue/CAP-2929)
7. **Cost**: ~1.9M tokens / ~3 min per connect (≈ week-1 baseline); Copilot 4–8 min — [CAP-2541](https://linear.app/diagrid/issue/CAP-2541)

Evidence counts per finding: [`plugin-quality-v3/FINDINGS.md`](plugin-quality-v3/FINDINGS.md).

## Who fixes what

| Ticket | Skill / plugin (this project) | Other teams |
|---|---|---|
| [CAP-2876](https://linear.app/diagrid/issue/CAP-2876) connect-an-existing-agent path | **Nearly all of it**: App vs Agent, where the code runs, proof recipe, name and project checks | MCP `invoke` tool (MCP server, follow-up) |
| [CAP-2926](https://linear.app/diagrid/issue/CAP-2926) credentials in chat | "Never read `~/.diagrid/*`" rule, optional hook | `get_connection` returns the token inline (MCP server); base64 creds file (CLI) |
| [CAP-2932](https://linear.app/diagrid/issue/CAP-2932) invisible quotas | Check usage first; say what to do at a cap; Dapr Agents hint | Topic cap missing from `get_usage`; unused topics never cleaned up (platform) |
| [CAP-2921](https://linear.app/diagrid/issue/CAP-2921) MCP vs CLI env mismatch | Compare whoami, CLI fallback, document `DIAGRID_MCP_URL` | `invalid_client` error message (auth server) |
| [CAP-2931](https://linear.app/diagrid/issue/CAP-2931) tunnel ~10s timeout | Troubleshooting note only | **Nearly all**: tunnel proxy timeout, Agent timeout field (platform). Verify on prod first |
| [CAP-2929](https://linear.app/diagrid/issue/CAP-2929) MCP/CLI behaviour | Work around only | **Nearly all**: readiness, side effects, filters, dry run, exit code, console URL (MCP / CLI / API) |
| [CAP-2920](https://linear.app/diagrid/issue/CAP-2920) example READMEs | — | **All**: `python-ai`, `rust-ai`, `catalyst-quickstarts` READMEs |

In short, the main fix ([CAP-2876](https://linear.app/diagrid/issue/CAP-2876)) is entirely in the skills, and it's also what makes a connect slow.

## Coverage (separate from the quality score, NOT run to the v3 standard)

Run before v3 (2026-11-19 15:35–16:32 PT), Claude only, one run each, MCP not signed in (0 MCP calls), graded by the model's own RESULT. They answer "does the README work", not "how good is the plugin".

- **Quickstarts rerun to the v3 standard** (Claude, MCP on, harness-graded): **14/14 ok** — [`coverage/quickstarts-v3/SCORECARD.md`](coverage/quickstarts-v3/SCORECARD.md)

- Official quickstarts `agents/*` (README happy path, staging Plus): **15/15 ok**. Their leftover topics later filled the pub/sub cap ([CAP-2932](https://linear.app/diagrid/issue/CAP-2932))
- Crash recovery (LangGraph, CrewAI, Mastra): **3/3** crash + resume
- `*-ai/examples` sample (mostly local `dapr run`): Mastra, Eino, Goose ok; python-ai LangGraph needs Dapr ≥ 1.18 ([CAP-2920](https://linear.app/diagrid/issue/CAP-2920))

Ledgers: [`coverage/`](coverage/) · details in [`archive/SUMMARY-pre-v3.md`](archive/SUMMARY-pre-v3.md#official-quickstarts-coverage-plus).

## Earlier runs (superseded, not a quality score)

Week-1 57/57 and v1/v2 used prompts with CLI recipes; v1/v2 also ran with MCP not signed in (0 MCP calls, ~0.4–0.8M tokens/cell). Their token numbers are **not comparable** to v3 (different prompt and task, not just MCP). They still show one real scenario: with MCP unavailable an agent can finish via the CLI, but no skill tells it how ([CAP-2921](https://linear.app/diagrid/issue/CAP-2921)). Kept for history only: [`archive/SUMMARY-pre-v3.md`](archive/SUMMARY-pre-v3.md).
