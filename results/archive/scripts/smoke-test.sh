#!/bin/sh
# Start each sample, POST one prompt, check the answer mentions "shipped".
# Usage: ./smoke-test.sh [language/framework ...]
# Reads OPENAI_API_KEY from .env in this directory. Never prints the key.
set -eu

here="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
. "$here/.env"
: "${OPENAI_API_KEY:?set OPENAI_API_KEY in .env}"
export OPENAI_API_KEY OPENAI_MODEL="${OPENAI_MODEL:-gpt-4o-mini}"
# Optional — Claude Agent SDK and Goose use these when present.
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  export ANTHROPIC_API_KEY
fi
export PATH="${HOME}/bin:${PATH}"
export GOOSE_PROVIDER="${GOOSE_PROVIDER:-anthropic}"
export GOOSE_MODEL="${GOOSE_MODEL:-${CLAUDE_MODEL:-claude-sonnet-4-5}}"

prompt='What is the status of order 42? Reply with the tool result.'
pass=0
fail=0
skip=0
results="$here/smoke-results.md"
{
  echo "# Smoke results"
  echo
  echo "| Sample | Result | Notes |"
  echo "|---|---|---|"
} >"$results"

log() { printf '%s\n' "$*" >&2; }

record() {
  sample=$1 status=$2 notes=$3
  printf '| `%s` | %s | %s |\n' "$sample" "$status" "$notes" >>"$results"
  case $status in
    PASS) pass=$((pass + 1)) ;;
    FAIL) fail=$((fail + 1)) ;;
    SKIP) skip=$((skip + 1)) ;;
  esac
  log "[$status] $sample — $notes"
}

free_port() {
  python3 - <<'PY'
import socket
s = socket.socket()
s.bind(("127.0.0.1", 0))
print(s.getsockname()[1])
s.close()
PY
}

wait_http() {
  port=$1
  i=0
  while [ "$i" -lt 90 ]; do
    if python3 -c "import socket; s=socket.socket(); s.settimeout(0.5); s.connect(('127.0.0.1', int('$port'))); s.close()" 2>/dev/null; then
      # Give the app a beat after the socket opens (Spring Boot, uvicorn).
      sleep 1
      return 0
    fi
    # Process died before listening.
    if ! kill -0 "$pid" 2>/dev/null; then
      return 1
    fi
    i=$((i + 1))
    sleep 1
  done
  return 1
}

ask() {
  port=$1
  curl -sS --max-time 120 -X POST "http://127.0.0.1:$port/run" \
    -H 'Content-Type: application/json' \
    -d "$(python3 -c "import json,sys; print(json.dumps({'prompt':sys.argv[1]}))" "$prompt")"
}

check_answer() {
  body=$1
  printf '%s' "$body" | python3 -c "
import json,sys
raw=sys.stdin.read()
try:
    data=json.loads(raw)
except Exception as e:
    print('not-json:'+raw[:200]); sys.exit(2)
ans=(data.get('answer') or '')
print(ans[:300])
sys.exit(0 if 'shipped' in ans.lower() else 1)
"
}

run_dapr_agents() {
  sample=python/dapr-agents
  dir="$here/$sample"
  port=$(free_port)
  log_file=/tmp/spike-smoke-python-dapr-agents.log
  (
    cd "$dir"
    PORT="$port" dapr run --app-id order-agent-smoke --app-port "$port" \
      --resources-path ./resources -- uv run main.py >"$log_file" 2>&1
  ) &
  pid=$!
  if ! wait_http "$port"; then
    kill "$pid" 2>/dev/null || true
    dapr stop --app-id order-agent-smoke >/dev/null 2>&1 || true
    wait "$pid" 2>/dev/null || true
    record "$sample" FAIL "did not become ready; see $log_file"
    return
  fi
  start=$(curl -sS --max-time 60 -X POST "http://127.0.0.1:$port/agent/run" \
    -H 'Content-Type: application/json' \
    -d "$(python3 -c "import json,sys; print(json.dumps({'task':sys.argv[1]}))" "$prompt")" || true)
  url=$(printf '%s' "$start" | python3 -c "import sys,json
try:
  print(json.load(sys.stdin).get('status_url') or '')
except Exception:
  print('')")
  if [ -z "$url" ]; then
    record "$sample" FAIL "no status_url from /agent/run: $(printf '%s' "$start" | tr '\n' ' ' | cut -c1-120)"
  else
    body=""
    i=0
    while [ "$i" -lt 60 ]; do
      body=$(curl -sS "http://127.0.0.1:$port$url" || true)
      if printf '%s' "$body" | rg -qi shipped; then
        record "$sample" PASS "workflow completed; answer mentions shipped"
        body=""
        break
      fi
      status=$(printf '%s' "$body" | python3 -c "import sys,json
try:
  print(json.load(sys.stdin).get('runtime_status',''))
except Exception:
  print('')" 2>/dev/null || true)
      case $status in
        FAILED|TERMINATED) break ;;
      esac
      i=$((i + 1))
      sleep 2
    done
    if [ -n "$body" ]; then
      note=$(printf '%s' "$body" | tr '\n' ' ' | cut -c1-160)
      record "$sample" FAIL "no shipped in status: $note"
    fi
  fi
  dapr stop --app-id order-agent-smoke >/dev/null 2>&1 || true
  kill "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
}

run_http_sample() {
  sample=$1
  shift
  dir="$here/$sample"
  port=$(free_port)
  log_file="/tmp/spike-smoke-$(echo "$sample" | tr / -).log"
  (
    cd "$dir"
    PORT="$port" "$@" >"$log_file" 2>&1
  ) &
  pid=$!
  if ! wait_http "$port"; then
    kill "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
    record "$sample" FAIL "did not become ready; see $log_file"
    return
  fi
  body=$(ask "$port" || true)
  if out=$(check_answer "$body"); then
    record "$sample" PASS "answer mentions shipped"
  else
    code=$?
    note=$(printf '%s' "$out" | tr '\n' ' ' | cut -c1-160)
    record "$sample" FAIL "bad answer ($code): $note; log $log_file"
  fi
  kill "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
}

# Default set: everything that uses OPENAI_API_KEY over HTTP /run.
default_samples='
python/langgraph
python/langchain
python/crewai
python/adk
python/strands
python/pydantic-ai
python/openai-agents
python/smolagents
python/deepagents
python/byoa
python/holmesgpt
python/dapr-agents
python/claude-agents
go/langchaingo
go/eino
typescript/mastra
dotnet/microsoft-agent-framework
java/spring-ai
rust/goose
'

if [ "$#" -gt 0 ]; then
  samples="$*"
else
  samples=$default_samples
fi

for sample in $samples; do
  case $sample in
    python/claude-agents)
      if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
        record "$sample" SKIP "needs ANTHROPIC_API_KEY"
        continue
      fi
      run_http_sample "$sample" uv run main.py
      ;;
    rust/goose)
      if ! command -v goose >/dev/null 2>&1; then
        record "$sample" SKIP "goose CLI not on PATH"
        continue
      fi
      if [ -z "${ANTHROPIC_API_KEY:-}" ] && [ "${GOOSE_PROVIDER:-}" = anthropic ]; then
        record "$sample" SKIP "needs ANTHROPIC_API_KEY for anthropic provider"
        continue
      fi
      # Rebuild so the binary picks up env-driven provider flags.
      (cd "$here/$sample" && cargo build -q)
      run_http_sample "$sample" ./target/debug/order-agent-goose
      ;;
    python/dapr-agents)
      run_dapr_agents
      ;;
    python/*)
      run_http_sample "$sample" uv run main.py
      ;;
    go/*)
      run_http_sample "$sample" go run .
      ;;
    typescript/mastra)
      run_http_sample "$sample" npm start
      ;;
    dotnet/*)
      run_http_sample "$sample" dotnet run --no-build
      ;;
    java/spring-ai)
      run_http_sample "$sample" java -jar target/order-agent-0.1.0.jar
      ;;
    *)
      record "$sample" SKIP "unknown sample"
      ;;
  esac
done

{
  echo
  echo "PASS=$pass FAIL=$fail SKIP=$skip"
} >>"$results"
log "done: PASS=$pass FAIL=$fail SKIP=$skip — $results"
