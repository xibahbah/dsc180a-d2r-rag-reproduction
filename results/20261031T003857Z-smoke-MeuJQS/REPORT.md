# D2R-RAG: initial execution results

**Status: the small baseline, training and policy-evaluation pipeline executed. The full paper results have not been reproduced.**

The test uses the first two HotpotQA questions per split and secondary contexts from five examples. The policy is trained for the original two epochs. The API generator is GPT-4o-mini with a test-only 512-token output cap.

| Stage | Cases | Correct by upstream matcher | Mean reported latency | Mean incremental VRAM |
|---|---:|---:|---:|---:|
| Baseline | 2 | 1/2 (50.0%) | 2.263 s | 1.218 MiB |
| Policy evaluation | 2 | 1/2 (50.0%) | 2.027 s | 1.218 MiB |

## Interpretation

These two cases cannot estimate the paper's 500-case validation results. The metric uses the authors' `qa_metrics.em.em_match` function. API generation is stochastic and the corpus is reduced.

Baseline diagnosis counts: {"NO_FAILURE": 2}.
Policy-evaluation diagnosis counts: {"NO_FAILURE": 2}.
Policy-evaluation action counts (-1 means no repair): {"-1": 2}.

A wrong answer labeled NO_FAILURE is a useful diagnostic example for TrustRAG; a two-case test cannot establish how often that occurs.

## Spending and reproducibility

The persistent ledger reserved **$0.020401** across **31** attempted API requests, including interrupted attempts. This is a conservative maximum reservation, not a report of actual billing. The $1 cap and 40-attempt test ceiling remain in effect.

A CPU-thread oversubscription issue was resolved by limiting the test to four threads. The wrapper also initializes a training-loop variable that can otherwise be used before assignment. Original upstream source files remain unchanged.

Reported latency and memory use follow the original code, whose measurement stops before diagnostic checks. The 6 MiB policy budget is incremental allocation, not the GPU memory needed to load all models.

## Remaining work

A guarded full-size campaign runner is prepared in `reproduction/full_run.py` for the original 500 training and 500 validation cases. Agree a separate API budget before launching it, then evaluate baseline, trained LinUCB repair, relevance and faithfulness. Thompson Sampling, ablations and FEVER remain separate reproduction stages. See `reproduction/PROTOCOL.md` for settings and reference results.
