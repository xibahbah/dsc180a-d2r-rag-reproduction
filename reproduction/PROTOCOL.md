# D2R-RAG reproduction protocol

Paper: [Diagnosing and Repairing Factual Errors in RAG under Budget Constraints](https://proceedings.mlr.press/v318/hashemifar26a.html).
Detailed methods/tables: https://arxiv.org/html/2606.29377v1.
Source revision: `5573ce938cee8b79f2e73ccc05f8fff803f464ed`.

## What counts as reproduced

An integration test establishes that the pipeline executes. Reproducing the
paper requires running its training and evaluation configuration, comparing
metrics against Table 1, and explaining deviations. Do not interpret a two-case
test as a reproduction of the reported percentages.

Initial target: HotpotQA, LinUCB; extend to Thompson Sampling and FEVER after
measuring costs and agreeing a full-run budget. All paid initial tests share
the persistent $1 allowance; full-size scripts are not authorized by that test
allowance and must not be launched unguarded.

## Original settings and reference results

- GPT-4o-mini generator; original prompt YAML files.
- 128-token chunks, 16-token overlap; default dense retrieval k=5.
- DeBERTa NLI and REBEL triple extraction; original model identifiers in source.
- HotpotQA fullwiki: first 500 training examples and first 500 validation
  examples; secondary contexts from up to the first 100,000 examples per split.
- Two training epochs; LinUCB exploration alpha=2.
- Repair latency budget=3 seconds; VRAM budget=6 in the source's MiB units.
- Table 1 HotpotQA: baseline EM=36.2%; LinUCB EM=39.8%; Thompson EM=40.4%.
- Table 1 baseline relevance=28.39%, faithfulness=68.58%; LinUCB
  relevance=31.66%, faithfulness=69.89%.

## Measurement caveats found in the source

`src/rag_engine.py` computes `(peak_after - start_mem) / 1048576`:
this is incremental allocated GPU memory in MiB, not full model residency.
The allocation snapshot and latency timer end before KG/NLI diagnosis. Thus
the returned timing/memory fields do not measure the entire diagnostic
pipeline. Preserve these fields for comparison, and separately measure whole
stage wall time and GPU memory when interpreting practical cost.

`src/patcher.py:get_context` computes a remaining-memory feature from total
device usage against the budget value, while the reward uses incremental
allocation. Record this difference rather than silently rewriting the policy.

The HotpotQA loader builds context lists through `set`, which can vary ordering
with Python's hash seed. Record `PYTHONHASHSEED` and corpus ordering for final
runs. API alias updates, package versions, dataset revisions and a GTX 1080 Ti
can also affect results or timings. No numerical equivalence is assumed.

## Run ladder

1. Environment/import checks and simulated spending-control tests.
2. Two-question validation baseline smoke run; five-example secondary corpus.
   This uses the original code with a dataset-loader wrapper and a 512-token
   output cap. It is explicitly an adaptation for integration testing.
3. Bounded small training/repair run with separate artifacts, if affordable.
4. Full 500/500 baseline, two-epoch policy training, and repaired evaluation
   after cost measurement and a full-run budget decision.
5. Baselines/ablations and FEVER as separately budgeted extensions.

For each run preserve: stage command/configuration, upstream revision, patches,
package versions, dataset/model revisions where available, GPU/driver details,
exit status, outputs, correctness/diagnostic metrics and API reservations.
Reservations are conservative spending ceilings, not actual billed costs.

The smoke training wrapper initializes `params_updates = {}` at the beginning
of each training row in an in-memory copy of the training script. The original
script otherwise accesses an uninitialized variable if its first example is
diagnosed `NO_FAILURE`, and can reuse stale patch flags after later such rows.
This is a compatibility fix in the smoke wrapper; upstream files remain intact.

Smoke runs also set BLAS/OpenMP thread counts to four. An initial training
attempt created 82 threads and spent minutes in policy selection; a four-thread
786-by-786 inverse check took 0.385 seconds. The slow attempt was stopped,
retained in the logs, and restarted with the same budget ledger and cached
indices. It is not treated as a completed training result.

## Current hardware

DSMLP container `dsmlp-jupyter-x4gong`, NVIDIA GTX 1080 Ti (11,264 MiB),
driver 535.161.08; Python 3.11.9. Package repairs currently use
torch/vision/audio 2.5.1/0.20.1/2.5.1 with CUDA 12.1, NumPy 1.26.4,
PyArrow 21.0.0 and RAGAS 0.2.15. Capture the complete installed environment
before final runs. The initial setup's unpinned dependencies required repair;
do not claim this was the authors' published environment.
