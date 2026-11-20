# Spike A — results ([CAP-2783](https://linear.app/diagrid/issue/CAP-2783))

_Updated 2026-11-19 19:31 PST. Regenerated after every cell by `results/build-v3-summary.py` — don't edit by hand._

**Current run = v3:** user-voice prompt ([`spike-prompt.md`](spike-prompt.md)), plugin MCP signed in, staging Plus `eileen-plus-test`/`default`, graded outside the model (git diff, proof path). Plugin 0.10.2, Claude = claude-opus-5-5.

**Score: claude 20/21 · codex 2/2 · copilot 0/2** · App instead of Agent: 8 · rule violations: 0 · localhost proofs: 0

## Each cell — result · resource kind · tokens in · time

| Framework | Claude | Codex | Copilot |
|---|---|---|---|
| LangGraph | #1 ok · Agent · 1.8M · 2m13s<br>#2 ok · Agent · 2.0M · 3m06s<br>#3 ok · Agent · 2.0M · 2m39s | **FAIL** · - · - · 0m08s | #1 **FAIL** · - · 54k · 0m29s<br>#1 **FAIL** · - · 54k · 0m23s |
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
| Dapr Agents | #1 **FAIL** [CAP-2932](https://linear.app/diagrid/issue/CAP-2932) · Agent · 2.8M · 3m23s<br>#2 **FAIL** [CAP-2932](https://linear.app/diagrid/issue/CAP-2932) · - · 144k · 0m26s |  |  |
| BYOA | ok · Agent · 1.6M · 2m51s | #1 ok · Agent · - · 0m29s<br>#1 ok · Agent · - · 0m28s | _pending 1_ |
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
| claude | 22 | 20 | 1.8M | 2m 46s | 39.7M | 61m 11s |
| codex | 3 | 2 | - | 0m 21s | - | 1m 05s |
| copilot | 2 | 0 | 54k | 0m 26s | 108k | 0m 52s |

## Top findings

1. **Tunnel return path times out at ~10s → HTTP 502** for slow agent turns; Agent kind has no timeout setting — [CAP-2931](https://linear.app/diagrid/issue/CAP-2931)
2. **Dapr Agents crashes**: auto-subscribes to `agent-pubsub`, undocumented 10-topic cap — [CAP-2932](https://linear.app/diagrid/issue/CAP-2932)
3. **Security**: agent read `~/.diagrid/creds` and printed CLI tokens into the transcript — [CAP-2926](https://linear.app/diagrid/issue/CAP-2926)
4. **App vs Agent contradictory** in `diagrid-deploy` → 8/21 landed on App — [CAP-2876](https://linear.app/diagrid/issue/CAP-2876)
5. **Silent identity clobber**: `list_apps` hides Agent-owned App IDs, dry run says `would_replace` — [CAP-2930](https://linear.app/diagrid/issue/CAP-2930)
6. **No documented way to call / prove a plain agent through Catalyst**; readiness reads wrong — [CAP-2878](https://linear.app/diagrid/issue/CAP-2878), [CAP-2929](https://linear.app/diagrid/issue/CAP-2929), [CAP-2934](https://linear.app/diagrid/issue/CAP-2934)
7. **Cost**: ~1.9M tokens in per connect with MCP on, ~3× the CLI path — [CAP-2541](https://linear.app/diagrid/issue/CAP-2541)

All findings → tickets: [`plugin-quality-v3/FINDINGS.md`](plugin-quality-v3/FINDINGS.md).

## Coverage (separate from the quality score)

- Official quickstarts `agents/*` (README happy path, staging Plus): **15/15 ok**
- Crash recovery (LangGraph, CrewAI, Mastra): **3/3** crash + resume
- `*-ai/examples` sample: Mastra, Eino, Goose ok; python-ai LangGraph needs Dapr ≥ 1.18 ([CAP-2920](https://linear.app/diagrid/issue/CAP-2920))

Details: [`archive/SUMMARY-pre-v3.md`](archive/SUMMARY-pre-v3.md#official-quickstarts-coverage-plus).

## Earlier runs (superseded, not a quality score)

Week-1 57/57 and v1/v2 used prompts with CLI recipes and ran with MCP not signed in (0 MCP calls, ~0.4–0.8M tokens/cell). Kept for history only: [`archive/SUMMARY-pre-v3.md`](archive/SUMMARY-pre-v3.md).
