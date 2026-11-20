#!/bin/bash
# Spike A matrix runner (CAP-2783), v3.
#
# Runs framework × client cells with the canonical v3 prompt from
# results/spike-prompt.md, grades each run from outside the model, and writes
# one ledger per batch.
#
#   ./run-matrix-loop.sh                       # spec matrix into results/plugin-quality-v3
#   SPIKE_ONLY=langgraph,byoa ./run-matrix-loop.sh
#   SPIKE_CLIENTS=claude SPIKE_REPEATS=2 ./run-matrix-loop.sh
#   SPIKE_FULL_MATRIX=1 ./run-matrix-loop.sh   # Codex/Copilot on every framework
#   SPIKE_DRY=1 ./run-matrix-loop.sh           # print the queue and the prompt, run nothing
#
# Spec matrix (CAP-2783): every framework × Claude; LangGraph + BYOA also × Codex
# and Copilot; LangGraph × Claude three times. SPIKE_REPEATS raises every cell's
# attempt count (Casper: not a one-time run).
#
# Env:
#   SPIKE_OUT            ledger dir (default results/plugin-quality-v3)
#   SPIKE_PROJECT        Catalyst project the agent should land in (default "default"; grading only)
#   SPIKE_REPEATS        attempts per cell (default 1; LangGraph × Claude min 3)
#   SPIKE_ALLOW_NO_MCP=1 run even if the Diagrid MCP server is not signed in for Claude
#   SPIKE_DELETE_AGENTS=1 delete the agent id from RESULT after each cell (free-tier headroom)
#   SPIKE_EXPORT_ENV=1   old behaviour: export .env into the coding client's environment
#   SPIKE_MCP_URL        point Claude's Diagrid MCP at another env, e.g. staging:
#                        https://mcp.cloud.staging.diagrid.dev/mcp  (exported as DIAGRID_MCP_URL,
#                        which the plugin's own MCP config honours)
#   SPIKE_ORG            expected org name; preflight refuses to start if CLI or MCP is elsewhere
#   SPIKE_PUBLISH=0      don't regenerate SUMMARY/SCORECARD and commit+push after each cell
#   SPIKE_MAX_CELLS      stop after this many cells this invocation (e.g. 1 for a smoke run)
#   SPIKE_CELL_TIMEOUT_SECS (1200), SPIKE_RESULT_GRACE_SECS (20)
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${SPIKE_OUT:-$HERE/results/plugin-quality-v3}"
case "$OUT" in /*) ;; *) OUT="$HERE/$OUT" ;; esac
SPIKE_RUNS="${SPIKE_RUNS:-$HOME/spike-runs}"
PROJECT="${SPIKE_PROJECT:-default}"
REPEATS="${SPIKE_REPEATS:-1}"
LEDGER="$OUT/ledger.tsv"
STATUS="$OUT/queue-status.md"
PROMPT_FILE="$HERE/results/spike-prompt.md"
mkdir -p "$SPIKE_RUNS" "$OUT"

if [[ -n "${SPIKE_MCP_URL:-}" ]]; then
  # The diagrid plugin reads ${DIAGRID_MCP_URL:-prod} in its plugin.json, with its
  # own oauth clientId/scopes. Point it elsewhere through that, not a second server.
  export DIAGRID_MCP_URL="$SPIKE_MCP_URL"
fi

export PATH="$HOME/.local/bin:$HOME/Library/Application Support/fnm/node-versions/v24.14.1/installation/bin:$PATH"
CLAUDE="${CLAUDE:-$(command -v claude || true)}"
CODEX="${CODEX:-$(command -v codex || true)}"
COPILOT="${COPILOT:-$(command -v copilot || true)}"

# slug|sample_path|display_name
FRAMEWORKS=(
  "langgraph|python/langgraph|LangGraph"
  "langchain|python/langchain|LangChain"
  "crewai|python/crewai|CrewAI"
  "adk|python/adk|Google ADK"
  "strands|python/strands|Strands"
  "pydantic-ai|python/pydantic-ai|Pydantic AI"
  "openai-agents|python/openai-agents|OpenAI Agents"
  "claude-agents|python/claude-agents|Claude Agent SDK"
  "smolagents|python/smolagents|smolagents"
  "deepagents|python/deepagents|Deep Agents"
  "holmesgpt|python/holmesgpt|HolmesGPT"
  "dapr-agents|python/dapr-agents|Dapr Agents"
  "byoa|python/byoa|BYOA"
  "microsoft-agent-framework|dotnet/microsoft-agent-framework|.NET MAF"
  "spring-ai|java/spring-ai|Spring AI"
  "langchaingo|go/langchaingo|LangChainGo"
  "eino|go/eino|Eino"
  "mastra|typescript/mastra|Mastra"
  "goose|rust/goose|Goose"
)
IFS=',' read -r -a CLIENTS <<<"${SPIKE_CLIENTS:-claude,codex,copilot}"
IFS=',' read -r -a ONLY <<<"${SPIKE_ONLY:-}"

LEDGER_HEADER=$'# slug\tclient\tattempt\tstatus\tkind\tvia\tcode\tviolation\tagent_id\tmcp_calls\ttokens_in\ttools\tlog\tfinished'
[[ -f "$LEDGER" ]] || echo "$LEDGER_HEADER" >"$LEDGER"

# ---------- matrix ----------

in_scope() { # slug client
  local slug="$1" client="$2" o
  if [[ ${#ONLY[@]} -gt 0 && -n "${ONLY[0]}" ]]; then
    local hit=0
    for o in "${ONLY[@]}"; do [[ "$o" == "$slug" ]] && hit=1; done
    [[ $hit -eq 1 ]] || return 1
  fi
  [[ "$client" == "claude" ]] && return 0
  [[ "${SPIKE_FULL_MATRIX:-0}" == "1" ]] && return 0
  [[ "$slug" == "langgraph" || "$slug" == "byoa" ]]
}

target() { # slug client -> attempts wanted
  local n="$REPEATS"
  if [[ "$1" == "langgraph" && "$2" == "claude" && "$n" -lt 3 ]]; then n=3; fi
  echo "$n"
}

attempts() { # slug client -> attempts already in ledger (any status)
  awk -F'\t' -v s="$1" -v c="$2" '$1==s && $2==c {n++} END{print n+0}' "$LEDGER"
}

build_queue() {
  local entry f_slug f_path f_name client
  QUEUE=()
  for client in "${CLIENTS[@]}"; do
    for entry in "${FRAMEWORKS[@]}"; do
      IFS='|' read -r f_slug f_path f_name <<<"$entry"
      in_scope "$f_slug" "$client" || continue
      if [[ $(attempts "$f_slug" "$client") -lt $(target "$f_slug" "$client") ]]; then
        QUEUE+=("$f_slug|$f_path|$f_name|$client")
      fi
    done
  done
}

write_status() {
  build_queue
  {
    echo "# Spike A v3 — queue status"
    echo
    echo "Updated: $(date '+%Y-%m-%d %H:%M:%S %Z') · ledger: \`$(basename "$LEDGER")\`"
    echo
    echo "## Current"
    cat "$OUT/current-cell.txt" 2>/dev/null || echo "(idle)"
    echo
    echo "## Remaining (${#QUEUE[@]})"
    local q
    for q in ${QUEUE[@]+"${QUEUE[@]}"}; do echo "- ${q%%|*} × ${q##*|}"; done
    echo
    echo "## Ledger"
    echo '```'
    column -t -s $'\t' "$LEDGER" 2>/dev/null || cat "$LEDGER"
    echo '```'
  } >"$STATUS"
}

# ---------- prompt ----------

build_prompt() { # display_name slug
  awk '
    /^```text$/{inblock=1; next}
    /^```$/{if(inblock) exit}
    inblock{print}
  ' "$PROMPT_FILE" | sed "s/<FRAMEWORK>/${1}/g; s/<framework>/${2}/g"
}

# ---------- environment hygiene ----------

# Kill anything whose working directory is inside a spike run dir, plus any
# `diagrid dev run`. Earlier sessions' tunnels held port 8000 and contaminated runs.
cleanup_runs() {
  local pids
  pkill -f 'diagrid dev run' 2>/dev/null || true
  if command -v lsof >/dev/null; then
    pids=$(lsof -a -d cwd -Fpn 2>/dev/null | awk -v root="$SPIKE_RUNS/" '
      /^p/{pid=substr($0,2)} /^n/{ if (index(substr($0,2), root)==1) print pid }' | sort -u)
    [[ -n "$pids" ]] && kill $pids 2>/dev/null
  fi
  sleep 1
}

preflight() {
  local c
  for c in "${CLIENTS[@]}"; do
    case "$c" in
      claude)  [[ -x "$CLAUDE" ]]  || { echo "claude not found" >&2; exit 2; } ;;
      codex)   [[ -x "$CODEX" ]]   || { echo "codex not found" >&2; exit 2; } ;;
      copilot) [[ -x "$COPILOT" ]] || { echo "copilot not found" >&2; exit 2; } ;;
    esac
  done
  [[ -f "$HERE/.env" ]] || { echo "missing $HERE/.env (cp .env.example .env)" >&2; exit 2; }

  # The Diagrid MCP server needs an interactive OAuth sign-in. `claude -p` can't
  # do it, so every v2 cell fell back to the CLI and MCP was never tested.
  # Sign in once: run `claude` in any dir, `/mcp`, authenticate diagrid.
  if printf '%s\n' "${CLIENTS[@]}" | grep -qx claude; then
    local line
    if true; then
      line=$(cd "$SPIKE_RUNS" && env -u ANTHROPIC_API_KEY "$CLAUDE" mcp list 2>&1 | grep -i diagrid || true)
      echo "MCP (claude): ${line:-<no diagrid server listed>}" | tee -a "$OUT/loop.log"
      if [[ -n "${SPIKE_MCP_URL:-}" ]] && ! grep -qF "$SPIKE_MCP_URL" <<<"$line"; then
        echo "Claude's diagrid MCP is not on $SPIKE_MCP_URL." >&2; exit 3
      fi
      if ! grep -qiE 'connected|✓|✔' <<<"$line" || grep -qiE 'needs auth|failed|✗' <<<"$line"; then
        if [[ "${SPIKE_ALLOW_NO_MCP:-0}" != "1" ]]; then
          echo 'Diagrid MCP is not signed in for Claude. Run claude → /mcp → diagrid → authenticate, or set SPIKE_ALLOW_NO_MCP=1.' >&2
          exit 3
        fi
      fi
    fi
    # (mcp list shows the URL, not the org; the model reports org in RESULT)
  fi

  # CLI and MCP must be the same env/org: `dev run` tunnels only exist in the CLI.
  local cli
  cli=$(diagrid whoami 2>&1 | head -20)
  echo "CLI whoami:"; echo "$cli" | tee -a "$OUT/loop.log"
  if [[ -n "${SPIKE_ORG:-}" ]] && ! grep -q "$SPIKE_ORG" <<<"$cli"; then
    echo "CLI is not on org $SPIKE_ORG. Run diagrid login (and org use) first." >&2; exit 3
  fi
}

# ---------- grading ----------

result_has() { # log
  [[ -f "$1" ]] || return 1
  rg -q 'RESULT' "$1" 2>/dev/null || return 1
  rg -qi 'run[^a-z]{0,40}(ok|fail)' "$1" 2>/dev/null
}

field() { # log regex -> first match of the value after the label
  rg -o -i -m1 "$2" "$1" 2>/dev/null | head -1
}

# Code + dependency files only. Manifests (catalyst.yaml, agent yaml) are allowed.
CODE_GLOBS=(':(glob)**/*.py' ':(glob)**/pyproject.toml' ':(glob)**/requirements*.txt'
  ':(glob)**/*.ts' ':(glob)**/*.js' ':(glob)**/package.json'
  ':(glob)**/*.go' ':(glob)**/go.mod' ':(glob)**/*.java' ':(glob)**/pom.xml' ':(glob)**/build.gradle*'
  ':(glob)**/*.cs' ':(glob)**/*.csproj' ':(glob)**/*.rs' ':(glob)**/Cargo.toml')
VIOLATION_RE='diagrid|WorkflowRunner|GraphRunner|DurableAgent|dapr[._-]ext[._-]workflow|Dapr\.Workflow|DaprWorkflow|workflow_runtime|WorkflowRuntime|oauth|identity|on_behalf|OnBehalf'

grade_diff() { # run_dir diff_out -> sets CODE_CHANGED, VIOLATION
  local run="$1" out="$2" added
  (cd "$run" && git add -A -N . >/dev/null 2>&1
   git diff --stat -- . ':!.env' ':!.agents' ':!.claude' ':!.codex'
   echo
   git diff -- "${CODE_GLOBS[@]}") >"$out" 2>/dev/null
  added=$(cd "$run" && git diff -U0 -- "${CODE_GLOBS[@]}" 2>/dev/null | grep '^+' | grep -v '^+++')
  if [[ -n "$added" ]] || (cd "$run" && ! git diff --quiet -- "${CODE_GLOBS[@]}" 2>/dev/null); then
    CODE_CHANGED=changed
  else
    CODE_CHANGED=untouched
  fi
  VIOLATION=$(grep -oiE "$VIOLATION_RE" <<<"$added" | tr 'A-Z' 'a-z' | sort -u | paste -sd, -)
  VIOLATION="${VIOLATION:--}"
}

grade_via() { # log -> catalyst|localhost|unknown
  local log="$1"
  if rg -qi 'call invoke|/v1\.0/invoke|dapr-app-id|\.diagrid\.io|cloud\.d3e|http-[a-z0-9-]+\.' "$log"; then
    echo catalyst
  elif rg -qi 'curl[^\n]*(localhost|127\.0\.0\.1)[^\n]*/run' "$log"; then
    echo localhost
  else
    echo unknown
  fi
}

claude_metrics() { # run_dir slug attempt -> sets MCP_CALLS TOKENS_IN TOOLS
  MCP_CALLS=-; TOKENS_IN=-; TOOLS=-
  local base="$OUT/${2}-claude-${3}-metrics"
  (cd "$1" && python3 "$HERE/session_metrics.py" --latest) >"$base.md" 2>/dev/null || return 0
  (cd "$1" && python3 "$HERE/session_metrics.py" --latest --json) >"$base.json" 2>/dev/null || return 0
  read -r MCP_CALLS TOKENS_IN TOOLS < <(python3 - "$base.json" <<'PY' 2>/dev/null || echo "- - -"
import json, sys
d = json.load(open(sys.argv[1]))
def g(*ks):
    for k in ks:
        cur = d
        try:
            for p in k.split("."):
                cur = cur[p]
            return cur
        except (KeyError, TypeError):
            pass
    return "-"
mcp = g("tool_calls.catalyst", "catalyst_calls", "tools.catalyst")
if isinstance(mcp, dict):
    mcp = sum(mcp.values())
print(mcp, g("tokens.in", "tokens_in", "input_tokens"), g("tool_calls.total", "tool_calls_total", "tool_calls"))
PY
)
}

# ---------- one cell ----------

run_one() {
  local slug="$1" path="$2" name="$3" client="$4"
  local attempt ts run logfile prompt rc status kind via agent_id
  attempt=$(( $(attempts "$slug" "$client") + 1 ))
  ts=$(date +%Y%m%d-%H%M%S)
  echo "=== START $name × $client #$attempt @ $ts ===" | tee -a "$OUT/loop.log"
  printf 'running: %s × %s #%s\nstarted: %s\n' "$name" "$client" "$attempt" "$(date -Iseconds)" >"$OUT/current-cell.txt"
  write_status
  cleanup_runs
  AGENTS_BEFORE=""
  if [[ "${SPIKE_DELETE_AGENTS:-0}" == "1" ]]; then
    AGENTS_BEFORE=$(diagrid agent list --project "$PROJECT" 2>&1 || true)
  fi

  run=$("$HERE/new-run.sh" "$path") || { echo "new-run failed" | tee -a "$OUT/loop.log"; return 1; }
  echo "RUN=$run" | tee -a "$OUT/loop.log"
  cp "$HERE/.env" "$run/.env"   # untracked (sample .gitignore / not in commit); agent loads it like a user would
  if [[ -d "$HERE/.agents/skills" ]]; then
    mkdir -p "$run/.agents/skills"
    rsync -a "$HERE/.agents/skills/" "$run/.agents/skills/"
  fi
  echo "$run" >"$OUT/${slug}-${client}-${attempt}.runpath"

  prompt=$(build_prompt "$name" "$slug")
  logfile="$OUT/${slug}-${client}-${attempt}.log"

  local max_secs="${SPIKE_CELL_TIMEOUT_SECS:-1200}" grace="${SPIKE_RESULT_GRACE_SECS:-20}"
  local poll=5 waited=0 seen=0
  set -m
  (
    cd "$run" || exit 1
    if [[ "${SPIKE_EXPORT_ENV:-0}" == "1" ]]; then set -a; . ./.env; set +a; fi
    # Never let an API key switch the coding client's own auth (it disabled
    # claude.ai connectors in v2). The agent under test reads .env itself.
    unset ANTHROPIC_API_KEY
    case "$client" in
      claude)  "$CLAUDE" -p --dangerously-skip-permissions --output-format text "$prompt" ;;
      codex)   "$CODEX" exec -s danger-full-access -m "${CODEX_MODEL:-gpt-5.4}" "$prompt" ;;
      copilot) COPILOT_ALLOW_ALL=true "$COPILOT" -p "$prompt" --allow-all --disable-builtin-mcps ;;
    esac
  ) >"$logfile" 2>&1 &
  local pid=$!
  CHILD_PID=$pid
  while kill -0 "$pid" 2>/dev/null; do
    if result_has "$logfile"; then
      if [[ $seen -eq 0 ]]; then seen=$waited; echo "RESULT at ${waited}s" >>"$OUT/loop.log"
      elif (( waited - seen >= grace )); then echo "kick after RESULT" >>"$OUT/loop.log"; break; fi
    fi
    (( waited >= max_secs )) && { echo "timeout ${max_secs}s" | tee -a "$OUT/loop.log"; break; }
    sleep "$poll"; waited=$((waited + poll))
  done
  kill -TERM -"$pid" 2>/dev/null; sleep 2; kill -KILL -"$pid" 2>/dev/null
  wait "$pid" 2>/dev/null; rc=$?
  CHILD_PID=""
  set +m
  cleanup_runs

  # --- grade from outside the model ---
  grade_diff "$run" "$OUT/${slug}-${client}-${attempt}.diff"
  via=$(grade_via "$logfile")
  kind=$(field "$logfile" 'kind[^A-Za-z]{0,20}(Agent|App)\b' | grep -oE '(Agent|App)$' || true); kind="${kind:--}"
  agent_id=$(field "$logfile" '(agent/app|agent|app) id[^a-z0-9]{0,20}[a-z0-9][a-z0-9-]{2,}' | grep -oE '[a-z0-9][a-z0-9-]{2,}$' || true); agent_id="${agent_id:--}"

  if [[ "$VIOLATION" != "-" ]]; then
    status=fail-rules
  elif ! result_has "$logfile"; then
    status="fail-noresult(rc=$rc)"
  elif rg -qi '^\s*(run|deploy)[^a-z]{0,40}fail' "$logfile"; then
    status=fail
  elif [[ "$via" == localhost ]]; then
    status=fail-localhost
  else
    status=ok
  fi

  MCP_CALLS=-; TOKENS_IN=-; TOOLS=-
  [[ "$client" == claude ]] && claude_metrics "$run" "$slug" "$attempt"

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$slug" "$client" "$attempt" "$status" "$kind" "$via" "$CODE_CHANGED" "$VIOLATION" \
    "$agent_id" "$MCP_CALLS" "$TOKENS_IN" "$TOOLS" "$(basename "$logfile")" "$(date -Iseconds)" >>"$LEDGER"
  echo "=== $status $name × $client #$attempt (kind=$kind via=$via code=$CODE_CHANGED violation=$VIOLATION) ===" | tee -a "$OUT/loop.log"

  if [[ "${SPIKE_DELETE_AGENTS:-0}" == "1" && "$agent_id" != "-" ]]; then
    # Only delete what this cell created: if the model reused an Agent that was
    # already there (e.g. at the identity cap), leave it alone.
    if grep -qw -- "$agent_id" <<<"$AGENTS_BEFORE"; then
      echo "keep $agent_id (existed before this cell — reused)" | tee -a "$OUT/loop.log"
    else
      yes | diagrid agent delete "$agent_id" --project "$PROJECT" >>"$OUT/loop.log" 2>&1 || true
    fi
  fi
  printf 'last finished: %s × %s #%s (%s)\n' "$name" "$client" "$attempt" "$status" >"$OUT/current-cell.txt"
  if [[ "${SPIKE_PUBLISH:-1}" == "1" ]]; then
    SPIKE_OUT="$OUT" "$HERE/publish.sh" "$name × $client #$attempt $status" 2>&1 | tee -a "$OUT/loop.log"
  fi
}

# ---------- main ----------

# Ctrl-C / kill: the client runs in its own process group (so timeouts can kill
# the whole tree), which means the terminal's SIGINT never reaches it. Forward it.
CHILD_PID=""
on_abort() {
  echo; echo "aborting — stopping client and tunnels" | tee -a "$OUT/loop.log"
  if [[ -n "$CHILD_PID" ]]; then
    kill -TERM -"$CHILD_PID" 2>/dev/null; sleep 2; kill -KILL -"$CHILD_PID" 2>/dev/null
  fi
  cleanup_runs
  printf 'aborted: %s\n' "$(date -Iseconds)" >"$OUT/current-cell.txt"
  exit 130
}
trap on_abort INT TERM

if [[ "${SPIKE_DRY:-0}" == "1" ]]; then
  build_queue
  echo "OUT=$OUT"; echo "queue (${#QUEUE[@]}):"; printf '  %s\n' ${QUEUE[@]+"${QUEUE[@]}"}
  echo "--- prompt (LangGraph) ---"; build_prompt LangGraph langgraph
  exit 0
fi

preflight
echo "matrix v3 start $(date -Iseconds) OUT=$OUT" | tee -a "$OUT/loop.log"
CELLS_RUN=0
while true; do
  if [[ -n "${SPIKE_MAX_CELLS:-}" && "$CELLS_RUN" -ge "$SPIKE_MAX_CELLS" ]]; then
    echo "SPIKE_MAX_CELLS=$SPIKE_MAX_CELLS reached" | tee -a "$OUT/loop.log"; write_status; break
  fi
  build_queue
  if [[ ${#QUEUE[@]} -eq 0 ]]; then
    echo "queue empty $(date -Iseconds)" | tee -a "$OUT/loop.log"
    printf 'idle: complete\nfinished: %s\n' "$(date -Iseconds)" >"$OUT/current-cell.txt"
    write_status
    break
  fi
  IFS='|' read -r slug path name client <<<"${QUEUE[0]}"
  run_one "$slug" "$path" "$name" "$client" || true
  CELLS_RUN=$((CELLS_RUN + 1))
  write_status
done
