#!/bin/bash
# Continuously run Spike A matrix cells (framework × client) until the queue is empty.
# Skips cells already marked ok in results/done.tsv. Updates results/queue-status.md.
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
RESULTS="$HERE/results"
SPIKE_RUNS="${SPIKE_RUNS:-$HOME/spike-runs}"
DONE_TSV="$RESULTS/done.tsv"
STATUS="$RESULTS/queue-status.md"
PROMPT_FILE="$RESULTS/spike-prompt.md"
LOG_DIR="$RESULTS"
mkdir -p "$SPIKE_RUNS" "$RESULTS"

export PATH="$HOME/.local/bin:/Users/eileenyu/Library/Application Support/fnm/node-versions/v24.14.1/installation/bin:$PATH"

CLAUDE="${CLAUDE:-$(command -v claude)}"
CODEX="${CODEX:-$(command -v codex)}"
COPILOT="${COPILOT:-$(command -v copilot)}"

# framework_slug|sample_path|display_name
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

CLIENTS=(claude codex copilot)

# Seed done.tsv from known completed cells (meeting scope; LangGraph Claude still needs 2 more)
if [[ ! -f "$DONE_TSV" ]]; then
  cat >"$DONE_TSV" <<'EOF'
# slug	client	status	note
langgraph	claude	ok	1/3 Agent order-agent
langgraph	codex	ok	App drift
langgraph	copilot	ok	App drift
langchain	claude	ok	
crewai	claude	ok	
adk	claude	ok	
byoa	claude	ok	App drift
EOF
fi

is_done() {
  local slug="$1" client="$2"
  # langgraph claude needs 3 total — track via count file
  if [[ "$slug" == "langgraph" && "$client" == "claude" ]]; then
    local n
    n=$(rg -c "^langgraph\tclaude\tok" "$DONE_TSV" 2>/dev/null || echo 0)
    [[ "${n:-0}" -ge 3 ]]
    return
  fi
  rg -q "^${slug}"$'\t'"${client}"$'\t'ok "$DONE_TSV" 2>/dev/null
}

mark_done() {
  local slug="$1" client="$2" status="$3" note="$4"
  printf '%s\t%s\t%s\t%s\n' "$slug" "$client" "$status" "$note" >>"$DONE_TSV"
}

write_status() {
  local rem=0 entry f_slug f_path f_name client line
  local -a remaining=()
  for entry in "${FRAMEWORKS[@]}"; do
    IFS='|' read -r f_slug f_path f_name <<<"$entry"
    for client in "${CLIENTS[@]}"; do
      if ! is_done "$f_slug" "$client"; then
        remaining+=("- $f_name × $client")
        rem=$((rem + 1))
      fi
    done
  done
  {
    echo "# Matrix loop status"
    echo
    echo "Updated: $(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo
    echo "## Current"
    if [[ -f "$RESULTS/current-cell.txt" ]]; then
      cat "$RESULTS/current-cell.txt"
    else
      echo "(idle)"
    fi
    echo
    echo "## Queue remaining"
    for line in "${remaining[@]}"; do
      echo "$line"
    done
    echo
    echo "Remaining cells: $rem"
    echo
    echo "## Done (tail)"
    tail -n 20 "$DONE_TSV" | sed 's/^/    /'
  } >"$STATUS"
}

build_prompt() {
  local name="$1" slug="$2"
  # Extract canonical prompt between first ```text and closing ```
  awk '
    BEGIN{inblock=0}
    /^```text$/{inblock=1; next}
    /^```$/{if(inblock){exit} }
    {if(inblock) print}
  ' "$PROMPT_FILE" | sed "s/<FRAMEWORK>/${name}/g; s/<framework>/${slug}/g"
}

patch_healthz() {
  local run="$1"
  python3 - <<PY
from pathlib import Path
p = Path("$run/main.py")
if not p.exists():
    raise SystemExit(0)
t = p.read_text()
if "/healthz" in t:
    print("healthz ok")
elif '@app.post("/run")' in t:
    t = t.replace('@app.post("/run")', '@app.get("/healthz")\nasync def healthz() -> dict:\n    return {"ok": True}\n\n\n@app.post("/run")')
    p.write_text(t)
    print("patched healthz")
else:
    print("no fastapi /run pattern; leave as-is")
PY
}

cleanup_tunnels() {
  # Best-effort: stop leftover tunnels so ports/identities free up
  pkill -f 'diagrid dev run --project langgraph-spike' 2>/dev/null || true
  pkill -f 'diagrid dev run' 2>/dev/null || true
  # Stop known spike agent ids if still connected
  local id
  for id in strands-order-agent pydantic-ai-order-agent order-agent byoa-order-status langgraph-order-status; do
    diagrid dev stop --id "$id" -p langgraph-spike >/dev/null 2>&1 || true
  done
  sleep 1
}

run_one() {
  local slug="$1" path="$2" name="$3" client="$4"
  local ts run logfile prompt rc note
  ts=$(date +%Y%m%d-%H%M%S)
  echo "=== START $name × $client @ $ts ===" | tee -a "$RESULTS/loop.log"
  printf 'running: %s × %s\nstarted: %s\n' "$name" "$client" "$(date -Iseconds)" >"$RESULTS/current-cell.txt"
  write_status

  cleanup_tunnels

  run=$("$HERE/new-run.sh" "$path")
  echo "RUN=$run" | tee -a "$RESULTS/loop.log"
  cp "$HERE/.env" "$run/.env"
  patch_healthz "$run"
  mkdir -p "$run/.agents/skills"
  if [[ -d "$HERE/.agents/skills" ]]; then
    rsync -a "$HERE/.agents/skills/" "$run/.agents/skills/"
  else
    rsync -a "$HOME/.agents/skills/diagrid-"*/ "$run/.agents/skills/" 2>/dev/null || true
  fi
  echo "$run" >"$RESULTS/current-${slug}-${client}.runpath"

  prompt=$(build_prompt "$name" "$slug")
  logfile="$LOG_DIR/${slug}-${client}.log"
  # rotate previous log
  if [[ -f "$logfile" ]]; then
    mv "$logfile" "${logfile%.log}-${ts}.log"
  fi

  # Clients often leave `diagrid dev run` attached and never exit.
  # Policy: once RESULT + ok/fail is in the log, grace briefly then kill the
  # whole process group and move on. Hard wall-clock cap as a backstop.
  local max_secs="${SPIKE_CELL_TIMEOUT_SECS:-1200}"
  local result_grace="${SPIKE_RESULT_GRACE_SECS:-20}"
  local poll=5
  local result_seen_at=0
  # New process group so we can kill client + leftover tunnels/children together.
  set -m
  (
    cd "$run" || exit 1
    set -a
    # shellcheck disable=SC1091
    . ./.env
    set +a
    case "$client" in
      claude)
        "$CLAUDE" -p --dangerously-skip-permissions --output-format text "$prompt"
        ;;
      codex)
        "$CODEX" exec -s danger-full-access -m gpt-5.4 "$prompt"
        ;;
      copilot)
        COPILOT_ALLOW_ALL=true "$COPILOT" -p "$prompt" --allow-all --disable-builtin-mcps
        ;;
      *)
        echo "unknown client $client" >&2
        exit 2
        ;;
    esac
  ) >"$logfile" 2>&1 &
  local client_pid=$!
  local waited=0
  result_has() {
    [[ -f "$logfile" ]] || return 1
    rg -q '^RESULT|^\*\*RESULT|RESULT deploy|RESULT —|RESULT:' "$logfile" 2>/dev/null || return 1
    rg -qi 'deploy[=:/ ].*ok|deploy[=:/ ].*fail|run[=:/ ].*ok|run[=:/ ].*fail|run:[[:space:]]*ok|run:[[:space:]]*fail' "$logfile" 2>/dev/null
  }
  kill_client_tree() {
    local why="$1"
    echo "$why (pid $client_pid)" | tee -a "$RESULTS/loop.log"
    # Kill process group first (client + background diagrid/uv children)
    kill -TERM -"$client_pid" 2>/dev/null || kill -TERM "$client_pid" 2>/dev/null || true
    sleep 2
    kill -KILL -"$client_pid" 2>/dev/null || kill -KILL "$client_pid" 2>/dev/null || true
    pkill -f 'diagrid dev run --project langgraph-spike' 2>/dev/null || true
  }
  while kill -0 "$client_pid" 2>/dev/null; do
    if result_has; then
      if [[ "$result_seen_at" -eq 0 ]]; then
        result_seen_at=$waited
        echo "RESULT detected at ${waited}s — grace ${result_grace}s then kick" | tee -a "$RESULTS/loop.log"
      elif [[ $((waited - result_seen_at)) -ge "$result_grace" ]]; then
        kill_client_tree "RESULT complete — kicking hung client"
        break
      fi
    fi
    if [[ "$waited" -ge "$max_secs" ]]; then
      kill_client_tree "timeout after ${max_secs}s — killing client"
      break
    fi
    sleep "$poll"
    waited=$((waited + poll))
  done
  wait "$client_pid" 2>/dev/null
  rc=$?
  set +m

  if rg -qi 'deploy[=:/ ].*ok|RESULT.*ok|run[=:/ ].*ok|run:[[:space:]]*ok' "$logfile"; then
    note="see $(basename "$logfile")"
    if rg -qi 'kind: Agent|resource kind:[[:space:]]*Agent|agent:[[:space:]]' "$logfile"; then
      note="Agent · $note"
    elif rg -qi 'plain App|kind: App|resource kind:[[:space:]]*App|app:[[:space:]]' "$logfile"; then
      note="App drift · $note"
    fi
    mark_done "$slug" "$client" "ok" "$note"
    echo "=== OK $name × $client ===" | tee -a "$RESULTS/loop.log"
  else
    mark_done "$slug" "$client" "fail" "rc=$rc see $(basename "$logfile")"
    echo "=== FAIL $name × $client rc=$rc ===" | tee -a "$RESULTS/loop.log"
  fi

  cleanup_tunnels
  printf 'last finished: %s × %s (%s)\n' "$name" "$client" "$(date -Iseconds)" >"$RESULTS/current-cell.txt"
  write_status
}

# Build queue: Claude-first for unfinished frameworks, then Codex/Copilot gaps,
# then extra LangGraph Claude runs (need 3 total).
build_queue() {
  local entry f_slug f_path f_name client n
  QUEUE=()
  # Pass 1: missing Claude cells (LangGraph Claude handled in pass 3 — needs 3 total)
  for entry in "${FRAMEWORKS[@]}"; do
    IFS='|' read -r f_slug f_path f_name <<<"$entry"
    [[ "$f_slug" == "langgraph" ]] && continue
    if ! is_done "$f_slug" "claude"; then
      QUEUE+=("$f_slug|$f_path|$f_name|claude")
    fi
  done
  # Pass 2: missing Codex/Copilot
  for entry in "${FRAMEWORKS[@]}"; do
    IFS='|' read -r f_slug f_path f_name <<<"$entry"
    for client in codex copilot; do
      if ! is_done "$f_slug" "$client"; then
        QUEUE+=("$f_slug|$f_path|$f_name|$client")
      fi
    done
  done
  # Pass 3: LangGraph Claude until 3 oks — but do not spin forever on hard fails
  # (e.g. Claude credit exhausted). Cap total attempts at 3 oks + 3 fails.
  n=$(rg -c $'^langgraph\tclaude\tok' "$DONE_TSV" 2>/dev/null || echo 0)
  local fails
  fails=$(rg -c $'^langgraph\tclaude\tfail' "$DONE_TSV" 2>/dev/null || echo 0)
  if rg -q $'^langgraph\tclaude\tblocked' "$DONE_TSV" 2>/dev/null; then
    :
  elif [[ "${n:-0}" -lt 3 && "${fails:-0}" -lt 3 ]]; then
    while [[ "${n:-0}" -lt 3 ]]; do
      QUEUE+=("langgraph|python/langgraph|LangGraph|claude")
      n=$((n + 1))
    done
  fi
}

echo "matrix loop starting $(date -Iseconds)" | tee -a "$RESULTS/loop.log"
write_status

while true; do
  build_queue
  write_status
  if [[ ${#QUEUE[@]} -eq 0 ]]; then
    echo "queue empty — matrix complete $(date -Iseconds)" | tee -a "$RESULTS/loop.log"
    printf 'idle: matrix complete\nfinished: %s\n' "$(date -Iseconds)" >"$RESULTS/current-cell.txt"
    write_status
    break
  fi
  IFS='|' read -r slug path name client <<<"${QUEUE[0]}"
  run_one "$slug" "$path" "$name" "$client" || true
done
