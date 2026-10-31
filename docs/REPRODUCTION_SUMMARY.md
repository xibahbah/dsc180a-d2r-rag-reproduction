# D2R-RAG reproduction: one-page summary

**Assignment:** reproduce a published experiment by running its released code,
matching its settings, comparing results and documenting deviations. Developing
a new method or proving the TrustRAG group hypothesis is a separate task.

**Paper:** Diagnosing and Repairing Factual Errors in RAG under Budget Constraints
([paper](https://proceedings.mlr.press/v318/hashemifar26a.html), Canadian AI 2026).
**Completed scope:** HotpotQA / LinUCB, rather than every experiment in the paper.

## Method and execution

The system retrieves evidence and generates an answer. Knowledge-graph and NLI
checks produce a failure diagnosis. A learned LinUCB policy selects a repair
when a failure is detected. The pipeline evaluates the resulting answer.

We retained GPT-4o-mini, original prompts and loader, 500 training questions,
500 validation questions, two LinUCB epochs and the original reward settings.
Both baseline and repaired RAGAS stages produced 500 valid scores per metric.

| Metric (%) | Paper baseline | Our baseline | Paper LinUCB | Our LinUCB |
|---|---:|---:|---:|---:|
| Authors' EM-labeled score | 36.2 | 35.4 | 39.8 | 39.8 |
| Answer relevance | 28.39 | 28.40 | 31.66 | 31.71 |
| Faithfulness | 68.58 | 69.17 | 69.89 | 71.40 |

**Scoring caveat:** installed `qa-metrics==0.2.42` implements `em_match` using
normalized substring inclusion (`if ref in can`), not strict whole-response exact
match. An abstention mentioning the gold answer can receive credit. These are
faithful reproductions of the code's reported metric, not proof that every
credited answer is substantively correct. See [real examples](EXAMPLE_ANALYSIS.md).

## What we changed and preserved

Pinned upstream commit: `5573ce938cee8b79f2e73ccc05f8fff803f464ed`.
The 37 upstream files are unmodified. Wrappers repair a per-row training variable,
fix hash seed and CPU threads, save/validate outputs, and meter API spending.
Dependencies were repaired for compatibility. All deviations and interrupted
attempts are documented; completed training was not repeated after repair failed.

The source timing excludes parts of diagnosis and its memory metric is incremental
MiB. Do not interpret these as whole-pipeline efficiency or total GPU memory.
The API model alias, dependencies and GPU driver can differ from the authors'.

## Evidence and outcome

All five stages completed. The policy checkpoint, 500-row answer tables, metric
batches, logs, stage plans, environment and budget ledger are in this repository.
Successful campaign usage estimate: $1.3979; accounted amount including failed
reservation: $1.4080, under the unchanged $5 allowance. This is not a bill.

**Conclusion:** we executed and reproduced the reported configuration's aggregate
scores closely, including the authors' 39.8% LinUCB score. FEVER, Thompson Sampling,
ablations and multiple seeds remain outside this reproduction. The broader group
hypothesis remains future research, not a missing requirement for this assignment.

**Verify without spending:** `python3 scripts/verify_results.py`.
