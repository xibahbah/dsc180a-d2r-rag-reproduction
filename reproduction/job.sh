#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"
stage="${1:?Specify check, setup, smoke, baseline, train, repair, metrics, or metrics-repaired}"
case "$stage" in
  check|setup|smoke|baseline|train|repair|metrics|metrics-repaired) ;;
  *) echo "Unknown stage: $stage" >&2; exit 2 ;;
esac
case "$stage" in
  baseline|train|repair|metrics|metrics-repaired)
    echo 'Full-size stages must use reproduction/full_run.py with a shared campaign budget.' >&2
    echo 'See reproduction/FULL_RUN_PLAN.md; these old unguarded shortcuts are disabled.' >&2
    exit 2 ;;
esac
mkdir -p results
run_dir="$(mktemp -d "results/$(date -u +%Y%m%dT%H%M%SZ)-${stage}-XXXXXX")"
exec > >(tee "$run_dir/run.log") 2>&1
echo "Stage: $stage; output: $run_dir"
export PYTHONPATH="$project_dir/D2R-RAG${PYTHONPATH:+:$PYTHONPATH}"
export JAX_PLATFORMS=cpu
export PYTHONUNBUFFERED=1
# Store an API key only on DSMLP, outside the synchronized project.
if [[ -f "$HOME/.config/d2r-rag/env.sh" ]]; then
  source "$HOME/.config/d2r-rag/env.sh"
fi
if [[ "$stage" == setup ]]; then
  python3 -m venv --system-site-packages .venv
  .venv/bin/python -m pip install -r D2R-RAG/requirements.txt -r reproduction/requirements-extra.txt
  .venv/bin/python -m pip freeze > "$run_dir/packages.txt"
  echo 'Environment installed. Run check next; dependency compatibility is not yet verified.'
  exit 0
fi
python_bin="$project_dir/.venv/bin/python"
if [[ ! -x "$python_bin" ]]; then python_bin=python3; fi
if [[ "$stage" == check ]]; then
  "$python_bin" reproduction/preflight.py --environment
  exit 0
fi
"$python_bin" reproduction/preflight.py --environment --require-gpu
cd D2R-RAG
mkdir -p files_hotpotqa_t files_hotpotqa_v
case "$stage" in
  smoke) script=../reproduction/smoke.py ;;
  baseline) script=experiments/analysis_shortanswer.py ;;
  train) script=src/train_shortanswer.py ;;
  repair) script=experiments/analysis_shortanswer_patched.py ;;
  metrics) script=src/report_metrics.py ;;
  metrics-repaired) script=src/report_metrics_patched.py ;;
esac
if [[ "$stage" == repair && ! -f files_hotpotqa_t/linucb_patcher.pkl ]]; then
  echo 'Training artifact missing. Complete train before repair.'; exit 1
fi
"$python_bin" -m pip freeze > "$project_dir/$run_dir/packages.txt"
nvidia-smi > "$project_dir/$run_dir/gpu.txt"
cp "$project_dir/reproduction/upstream.json" "$project_dir/$run_dir/upstream.json"
set +e
if [[ "$stage" == smoke ]]; then
  "$python_bin" "$script" "$project_dir/$run_dir/smoke"
else
  "$python_bin" "$script" hotpotqa
fi
code=$?
set -e
echo "$code" > "$project_dir/$run_dir/exit-code.txt"
# Preserve tabular results and trained policies even when the script fails.
for folder in files_hotpotqa_t files_hotpotqa_v; do
  mkdir -p "$project_dir/$run_dir/$folder"
  find "$folder" -maxdepth 1 -type f \( -name '*.csv' -o -name '*patcher*.pkl' \) -exec cp {} "$project_dir/$run_dir/$folder/" \;
done
exit "$code"
