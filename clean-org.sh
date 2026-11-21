#!/bin/bash
# Free the org's per-region capacity: runs clean-project.sh on every project in the
# current org (lists each one and asks before deleting). Projects themselves are kept.
#   SPIKE_ORG=cattle-ackbar ./clean-org.sh
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
diagrid whoami | grep -E 'Organization|API'
[[ -n "${SPIKE_ORG:-}" ]] && ! diagrid whoami | grep -q "$SPIKE_ORG" && { echo "CLI not on $SPIKE_ORG — stop"; exit 3; }
PROJECTS=$(diagrid project list 2>/dev/null | awk 'NR>1 && NF && $1!~/^-+$/ {print $1}')
echo "Projects: $(echo $PROJECTS)"
for p in $PROJECTS; do
  echo; echo "################ $p"
  SPIKE_PROJECT="$p" "$HERE/clean-project.sh" </dev/tty
done
