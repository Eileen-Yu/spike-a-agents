#!/bin/sh
# Copy one sample into a fresh, committed working copy for a spike run, so each
# run starts from the same tree and `git diff` shows what the plugin changed.
#
#   ./new-run.sh python/langgraph            -> ~/spike-runs/langgraph-<timestamp>
#   SPIKE_RUNS=/tmp/runs ./new-run.sh go/eino
set -eu

sample="${1:?usage: new-run.sh <language>/<framework>}"
here="$(cd "$(dirname "$0")" && pwd)"
case "$sample" in /*) src="$sample" ;; *) src="$here/$sample" ;; esac
[ -d "$src" ] || { echo "no sample at $src" >&2; exit 1; }

dest="${SPIKE_RUNS:-$HOME/spike-runs}/$(basename "$sample")-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$dest"
rsync -a --exclude .venv --exclude __pycache__ --exclude node_modules --exclude target --exclude bin --exclude obj \
  "$src/" "$dest/"

cd "$dest"
git init -q
git add -A
git -c user.name=spike -c user.email=spike@localhost commit -qm "sample: $sample"
echo "$dest"
