#!/bin/bash
# CAP-2931: does a request through Catalyst fail when the app takes > ~10s to answer?
#
#   ./run.sh <project>            # uses whatever env/org `diagrid whoami` is on
#   DELAYS="0 5 9 12 15 30" ./run.sh default
#
# Run it once logged in to prod, and (optionally) once on staging to compare.
# Needs one free App ID slot in the project (creates `tunnel-timeout-test`, deletes it at the end).
set -u
P="${1:?usage: ./run.sh <project>}"
ID="${APP_ID:-tunnel-timeout-test}"
PORT="${PORT:-8765}"
DELAYS="${DELAYS:-0 5 9 12 15 30}"
HERE="$(cd "$(dirname "$0")" && pwd)"
LOG="$HERE/run-$(date +%Y%m%d-%H%M%S).log"; RES="${LOG%.log}.md"

echo "== whoami"; diagrid whoami | grep -E 'Organization|Plan|API' | tee -a "$LOG"
API=$(diagrid whoami | awk '/API/{print $2}')

lsof -ti tcp:"$PORT" >/dev/null 2>&1 && { echo "port $PORT busy — set PORT=..." >&2; exit 2; }

echo "== starting tunnel (dev run) for $ID on :$PORT"
PORT=$PORT diagrid dev run --project "$P" --id "$ID" --app-port "$PORT" --yes -- python3 "$HERE/slow_server.py" >>"$LOG" 2>&1 &
DEV=$!
cleanup() {
  echo "== cleanup"
  kill -INT "$DEV" 2>/dev/null; sleep 3; kill "$DEV" 2>/dev/null
  diagrid dev stop --id "$ID" -p "$P" >>"$LOG" 2>&1
  [[ "${KEEP_APP:-0}" == 1 ]] || yes | diagrid app delete "$ID" --project "$P" >>"$LOG" 2>&1
}
trap cleanup EXIT INT TERM

call() { # delay -> "code|seconds|tail of output"
  local t0 t1 out rc
  t0=$(python3 -c 'import time;print(time.time())')
  out=$(diagrid call invoke post "$ID.run" --id "$ID" -p "$P" -d "{\"delay\":$1}" 2>&1); rc=$?
  { echo "--- invoke delay=$1 rc=$rc"; echo "$out"; } >>"$LOG.calls"
  t1=$(python3 -c 'import time;print(time.time())')
  printf '%s|%.1f|%s' "$rc" "$(python3 -c "print($t1-$t0)")" "$(echo "$out" | tr '\n' ' ' | cut -c1-140)"
}

echo "== waiting for the tunnel to answer (up to 180s)"
ok=0
for i in $(seq 1 36); do
  r=$(call 0); grep -q 'delay=0.0s answered 200' "$LOG" && { ok=1; echo "   first call: $r"; break; }; sleep 5
done
[[ $ok == 1 ]] || { echo "tunnel never answered; see $LOG" >&2; exit 3; }
echo "   ready"

{
  echo "# CAP-2931 tunnel timeout check — $(date '+%Y-%m-%d %H:%M %Z')"
  echo
  echo "API: \`$API\` · project: \`$P\` · app: \`$ID\` (plain HTTP app behind \`diagrid dev run\`) · call: \`diagrid call invoke post $ID.run\`"
  echo
  echo "| app delay | via Catalyst | time | output | direct localhost |"
  echo "|---:|---|---:|---|---|"
} > "$RES"

for d in $DELAYS; do
  r=$(call "$d"); rc=${r%%|*}; rest=${r#*|}; secs=${rest%%|*}; out=${rest#*|}
  if [[ "$rc" == 0 ]] && echo "$out" | grep -qE 'Status Code: +2[0-9][0-9]'; then v="**ok**"; else v="**FAIL** (rc=$rc)"; fi
  dl=$(curl -s -m $(( ${d%.*} + 10 )) -X POST "localhost:$PORT/run" -d "{\"delay\":$d}" | grep -q shipped && echo ok || echo fail)
  echo "| ${d}s | $v | ${secs}s | \`${out//|/\\|}\` | $dl |" | tee -a "$RES"
done
echo
echo "Result table: $RES   (raw invoke output: $LOG.calls)"
echo "App log (shows whether the app answered 200 even when the caller failed): grep '\[app\]' $LOG"
grep '\[app\]' "$LOG" | tail -n 20
