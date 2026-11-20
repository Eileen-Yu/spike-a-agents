#!/bin/bash
# Reset the spike project to a known state before a batch.
# Deletes: every Agent, every App, every pub/sub topic, and spike-made components
# (statestore). Keeps the managed components Diagrid provides (agent-*, kvstore, pubsub).
# Lists everything first and asks before deleting.
#
#   ./clean-project.sh                 # project from SPIKE_PROJECT (default: default)
set -u
P="${SPIKE_PROJECT:-default}"
names() { awk 'NR>1 && NF && $1!~/^-+$/ {print $1}'; }

echo "== whoami"; diagrid whoami | grep -E 'Organization|API'
[[ -n "${SPIKE_ORG:-}" ]] && ! diagrid whoami | grep -q "$SPIKE_ORG" && { echo "CLI not on $SPIKE_ORG — stop"; exit 3; }

echo; echo "== Agents in $P";     diagrid agent list -p "$P";     AGENTS=$(diagrid agent list -p "$P" 2>/dev/null | names)
echo; echo "== Apps in $P";       diagrid app list -p "$P";       APPS=$(diagrid app list -p "$P" 2>/dev/null | names)
echo; echo "== Components in $P"; diagrid component list -p "$P"; COMPS=$(diagrid component list -p "$P" 2>/dev/null | names | grep -E '^(statestore|.*-statestore|messagepubsub)$' || true)
BROKERS=$(diagrid pubsub list -p "$P" 2>/dev/null | names)
TOPICS=()
for b in $BROKERS; do
  echo; echo "== topics on $b"; diagrid pubsub topics list --pubsub "$b" -p "$P"
  for t in $(diagrid pubsub topics list --pubsub "$b" -p "$P" 2>/dev/null | names); do TOPICS+=("$b|$t"); done
done

# Agent-owned App IDs show up in app list too; delete Agents first, skip those Apps.
APPS=$(comm -23 <(printf '%s\n' $APPS | sort -u) <(printf '%s\n' $AGENTS | sort -u))

echo
echo "Will delete in $P:"
echo "  Agents ($(wc -w <<<"$AGENTS" | tr -d ' ')): $(echo $AGENTS)"
echo "  Apps ($(wc -w <<<"$APPS" | tr -d ' ')):   $(echo $APPS)"
echo "  Topics (${#TOPICS[@]}): $(printf '%s ' "${TOPICS[@]#*|}")"
echo "  Components: ${COMPS:-none}  (managed agent-*/kvstore/pubsub are kept)"
echo "Make sure no runner is running."
read -r -p "Proceed? [y/N] " ok; [[ "$ok" == y || "$ok" == Y ]] || { echo "aborted"; exit 1; }

pkill -f 'diagrid dev run' 2>/dev/null
for a in $AGENTS; do printf -- '- agent %s: ' "$a"; yes | diagrid agent delete "$a" --project "$P" 2>&1 | tail -1; done
for a in $APPS;   do printf -- '- app %s: '   "$a"; yes | diagrid app delete "$a" --project "$P" 2>&1 | tail -1; done
for bt in ${TOPICS[@]+"${TOPICS[@]}"}; do printf -- '- topic %s: ' "${bt#*|}"; yes | diagrid pubsub topics delete "${bt#*|}" --pubsub "${bt%%|*}" -p "$P" 2>&1 | tail -1; done
for c in $COMPS;  do printf -- '- component %s: ' "$c"; diagrid component delete "$c" -p "$P" --approve 2>&1 | tail -1; done

echo; echo "Deletes are async; waiting 60s, then the state after:"; sleep 60
diagrid agent list -p "$P"; diagrid app list -p "$P"
for b in $BROKERS; do diagrid pubsub topics list --pubsub "$b" -p "$P"; done
