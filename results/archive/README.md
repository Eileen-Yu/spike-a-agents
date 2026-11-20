# Archive (superseded, kept for history)

None of this is part of the Spike A result. Current: [`../SUMMARY.md`](../SUMMARY.md).

| Folder / file | What | Why superseded |
|---|---|---|
| `week1/` | Week-1 57/57 matrix (prod free `cattle-ackbar`, 3 clients), per-framework metrics, old builder | Prompts contained CLI/MCP recipes; many cells reused one Agent at the 10/10 identity cap |
| `v1-prefer-agent/` | Cookbook-free retest, 5 cells | Prompt still said "prefer Agent", which hid App drift; MCP not signed in (0 MCP calls) |
| `v2-no-prefer-agent/` | Same without "prefer Agent", 5 cells (2/5 App) | Named the test and the plugin, allowed localhost proof; MCP not signed in |
| `v3-invalid-runs/` | v3 runs that don't count: MCP on prod + CLI on staging (3), harness bugs (parallel runners killing cells, prompt-echo misgrade), shared identity | Environment or harness, not plugin behaviour |
| `SUMMARY-pre-v3.md` | The old long SUMMARY (week 1, v1, v2, coverage detail) | Replaced by the one-page SUMMARY |
| `spike-prompt-history.md` | All earlier prompts + coverage prompts (quickstarts, crash, `*-ai` examples) | Current prompt is `../spike-prompt.md` |
| `FINDINGS-working-notes.md` | Per-cell notes written during the run | Condensed into `../plugin-quality-v3/FINDINGS.md` |
| `scripts/` | `smoke-test.sh` (local sample check), `rerun-dapr-agents.sh` | One-off / replaced by `clean-project.sh` + `run-matrix-loop.sh` |

Logs are gitignored everywhere (they can contain credentials); they exist only on the machine that ran them.
