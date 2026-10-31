# Teammate reading guide

## What question does this experiment answer?

Can a learned policy diagnose and repair factual failures in a retrieval-augmented
answering system under the authors' resource-budget settings? The pipeline first
retrieves evidence and generates an answer. Knowledge-graph consistency and NLI
checks produce diagnostic signals. A LinUCB policy selects an available repair,
such as changing retrieval settings, expanding evidence or changing the prompt.
The repaired answer is then evaluated against the same validation questions.

This run establishes a reference implementation for our DSC180A project. It does
not yet answer the group's broader question about diagnose-first versus direct
selection under matched evidence, actions and compute. That needs controlled
comparison experiments beyond reproducing this configuration.

## What actually ran?

- Original HotpotQA fullwiki loader: 500 training and 500 validation questions.
- Original secondary corpus construction and prompts, GPT-4o-mini generator.
- LinUCB alpha=2, two training epochs; original latency/VRAM reward settings.
- Full baseline and learned-repair evaluation, followed by RAGAS relevance and
  faithfulness for each. Both metric stages have 500 scores for each metric.
- A GTX 1080 Ti on UCSD DSMLP, with package repairs documented in the protocol.

## Scoring caveat

The authors' installed em_match uses normalized substring containment rather
than strict equality. Treat these as authors' EM-labeled scores, not a count of
manually verified correct answers. See EXAMPLE_ANALYSIS.md for a credited
abstention, a plausible improvement and a diagnostic miss.

## Results to put in slides

Baseline EM: 177/500 = 35.4%. Learned repair EM: 199/500 = 39.8%.
Improvement: 4.4 percentage points, or 22 additional scorer-credited answers in aggregate.
Paper baseline: 36.2%; paper LinUCB: 39.8%.

Answer relevance: 28.3951% to 31.7062%.
Faithfulness: 69.1718% to 71.3962%.

These are one-run findings. We did not establish statistical significance,
multiple-seed stability, identical predictions, or full-paper replication.
Resource timings are especially sensitive to hardware and measurement boundaries.

## Evidence you can inspect

All paths below are relative to the repository root.

1. `results/hotpotqa-full-linucb/REPORT.md`: conclusions and caveats.
2. `files_hotpotqa_v/failure_statistics.csv` inside that campaign: all baseline
   answers, evidence, diagnoses, EM and source resource measurements.
3. `files_hotpotqa_v/bandit_eval_dataset.csv`: all repaired-evaluation rows.
4. `baseline-summary.json`, `repair-summary.json`: machine-readable aggregates.
5. `metrics*-ragas-*.csv` and `metrics*-summary.json`: individual and aggregate
   RAGAS outcomes. Scores are fractions; multiply by 100 for percentages.
6. `train-20261031T061315Z.log`: full training history; `train.done` and zero exit
   code record completion. The checkpoint is in `artifacts/full-linucb-policy.pkl.gz`.
7. `*-plan.json`, `packages.txt`, `gpu.txt`, `budget.json`: execution provenance.

Read tables with a **tab delimiter**, despite their `.csv` extension. RAGAS batch
exports use the standard comma delimiter. `scripts/verify_results.py` handles this.

## Code map

- `D2R-RAG/src/utils.py`: loaders and model settings.
- `rag_engine.py`, `knowledge_graph.py`, `entailment.py`: retrieval/generation and
  diagnostic checks (within the same upstream `src` directory).
- `bandits.py`, `patcher.py`: LinUCB and repair choices.
- `train_shortanswer.py`: policy training.
- `D2R-RAG/experiments/analysis_shortanswer*.py`: baseline and repair evaluation.
- `reproduction/full_run.py`: wrapper, compatibility fix and stage validation.
- `reproduction/metered_guard.py`, `budget_guard.py`: API accounting and limits.
- `reproduction/campaign.sh`: sequential execution and stage markers.

## What changed from upstream?

Source under `D2R-RAG/` is an unmodified snapshot at the pinned commit. Wrappers
reset `params_updates` on each training row, fix Python hash seed and CPU thread
counts, save evaluation artifacts, and guard paid calls. A malformed successful
API response is converted to a protocol error for bounded SDK retries; its full
reservation is retained. Dependency versions were repaired for compatibility.

The first baseline attempt failed before its final table; it is not included as
a second result. Repair later hit a technical request ceiling. We retained the
same $5 ledger, increased only the attempt ceiling and restarted repair using the
completed two-epoch policy. Both old and completed attempt logs are retained.

## Safe next steps

Reading files and running the offline verifier costs nothing. For analysis, join
baseline and repair rows by question, inspect changed answers and diagnostic
failures, then design separately budgeted comparison methods. FEVER, Thompson
Sampling, ablations and Qwen/RAGBench experiments have not been run here.
Do not launch the authors' unguarded scripts with an API key by accident.
