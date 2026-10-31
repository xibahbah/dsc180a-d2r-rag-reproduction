#!/usr/bin/env bash
# Run on a DSMLP compute container. One ledger covers all five stages.
set -euo pipefail
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"
campaign="$project_dir/results/hotpotqa-full-linucb"
mkdir -p "$campaign"
exec 9>"$campaign/campaign.lock"
if ! flock -n 9; then
  echo 'This campaign is already running.' >&2
  exit 2
fi
source "$HOME/.config/d2r-rag/env.sh"
python_bin="$project_dir/.venv/bin/python"
export PYTHONUNBUFFERED=1

status() {
  "$python_bin" - "$campaign/status.json" "$1" "$2" "$3" <<'PY'
import datetime, json, os, pathlib, sys
p = pathlib.Path(sys.argv[1])
state = dict(state=sys.argv[2], stage=sys.argv[3], exit_code=int(sys.argv[4]),
             pid=os.getppid(), updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
tmp = p.with_suffix('.tmp')
tmp.write_text(json.dumps(state, indent=2))
os.replace(tmp, p)
PY
}

"$python_bin" -m pip freeze > "$campaign/packages.txt"
nvidia-smi > "$campaign/gpu.txt"
for stage in baseline train repair metrics metrics-repaired; do
  if [[ -f "$campaign/$stage.done" ]]; then
    echo "Already completed: $stage"
    continue
  fi
  status running "$stage" 0
  echo "Starting $stage at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  attempt="$(date -u +%Y%m%dT%H%M%SZ)"
  set +e
  "$python_bin" reproduction/full_run.py "$stage" \
    --campaign "$campaign" --budget-usd 5 > "$campaign/$stage-$attempt.log" 2>&1
  code=$?
  set -e
  printf '%s\n' "$code" > "$campaign/$stage.exit-code"
  if [[ "$code" -ne 0 ]]; then
    status failed "$stage" "$code"
    echo "Stopped at $stage (exit $code). Review $campaign/$stage-$attempt.log"
    exit "$code"
  fi
  touch "$campaign/$stage.done"
  echo "Completed $stage"
done
status completed all 0
echo 'Full HotpotQA/LinUCB campaign completed.'
