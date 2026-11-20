#!/bin/bash
# Regenerate the Spike A records and push them. Called by run-matrix-loop.sh after
# every cell (SPIKE_PUBLISH=0 to skip). Commits only record files — never logs,
# .env or run dirs (logs can contain credentials and stay local, gitignored).
#
#   ./publish.sh "message"
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE" || exit 1
OUT="${SPIKE_OUT:-$HERE/results/plugin-quality-v3}"
python3 results/build-v3-summary.py "$OUT" || echo "summary build failed (continuing)"

git add -- README.md .gitignore run-matrix-loop.sh publish.sh new-run.sh session_metrics.py \
  results/spike-prompt.md results/SUMMARY.md results/build-v3-summary.py 2>/dev/null
git add -u -- python dotnet java go typescript rust 2>/dev/null
for d in "$OUT" "$HERE/results/plugin-quality-v3-envmismatch"; do
  [[ -d "$d" ]] || continue
  git add -- "$d"/*.md "$d"/*.tsv "$d"/*.diff "$d"/*-metrics.json 2>/dev/null
done
# belt and braces: never commit a log or env file
git reset -q -- '*.log' '*.env' '.env' 2>/dev/null

if git diff --cached --quiet; then
  echo "publish: nothing to commit"; exit 0
fi
git -c user.name="${GIT_AUTHOR_NAME:-Eileen}" commit -q -m "Spike A v3: ${1:-update records}" && echo "publish: committed"
branch="${SPIKE_PUSH_BRANCH:-archive}"
if git push -q origin "HEAD:$branch" 2>&1; then echo "publish: pushed to $branch"; else echo "publish: push failed (will retry next cell)"; fi
