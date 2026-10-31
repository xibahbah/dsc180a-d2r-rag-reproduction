# Full HotpotQA / LinUCB reproduction

All five authorized stages completed on October 31, 2026: a 500-case baseline,
two epochs over 500 training cases, a 500-case repaired evaluation, and both
RAGAS evaluations. Each RAGAS metric has 500 non-missing scores.

| Metric | Paper baseline | Our baseline | Paper LinUCB | Our LinUCB |
|---|---:|---:|---:|---:|
| Exact match (%) | 36.2 | 35.4 (177/500) | 39.8 | 39.8 (199/500) |
| Answer relevance (%) | 28.39 | 28.3951 | 31.66 | 31.7062 |
| Faithfulness (%) | 68.58 | 69.1718 | 69.89 | 71.3962 |

The learned repair policy improves exact match by 4.4 percentage points
(22 additional correct answers in aggregate). Matching the reported 39.8%
aggregate does not establish identical per-question predictions or reproduce
the whole paper. This is one scoped HotpotQA/LinUCB reproduction, without
multiple seeds or a statistical robustness claim. FEVER, Thompson Sampling,
ablations and the group's Qwen/RAGBench adaptations remain outside this run.

## Spending

The original $5 campaign ledger remains unchanged in allowance. Across 17,351
attempts, successful reported token usage estimates $1.3979187; one unsettled
attempt retains its maximum reservation. Total accounted amount is $1.40798145.
These are usage estimates/reservations, not an OpenAI billing statement. Including
the separate initial smoke ledger's $0.0204006 reservation, the conservative
combined amount is $1.42838205. No cap was reset or new campaign created.

## Reproducibility and limitations

Upstream revision: 5573ce938cee8b79f2e73ccc05f8fff803f464ed. Original model,
prompts, 500/500 splits and two training epochs were retained. See PROTOCOL.md,
stage plans and packages.txt for configuration, dependency repairs and source
measurement caveats. Python hash seed is zero. An in-memory training fix resets
params_updates per row; upstream source is retained unmodified.

Hardware remained GTX 1080 Ti; the first worker driver was 535.161.08 and the
replacement driver was 580.126.20. Timing is hardware-sensitive. Source latency
and incremental MiB measurements exclude parts of diagnosis and do not represent
full pipeline wall time or total model memory. No claim of matching resource
measurements is made. API aliases and RAGAS versions can affect outcomes.

## Interruptions preserved

The first baseline stopped after progress 227/500 on malformed API JSON; its
partial work is not counted as a completed baseline. The HTTP guard now converts
such malformed successful responses to protocol errors for bounded SDK retries;
failed attempts keep their reservations. Seven mocked guard tests passed.

After successful baseline and two-epoch training, repair hit the technical
10,000-request ceiling at $0.53801295 accounted. Only that ceiling was increased
to 50,000, with the same request counter and $5 ledger preserved. Repair restarted
from the completed training checkpoint; completed baseline/training were skipped.
Old logs are retained. The final completed repair table is the reported result.

## Handoff

CSV tables, per-stage logs/plans/summaries, completion markers, environment and
budget records are included here. artifacts/full-linucb-policy.pkl.gz contains
the compressed completed two-epoch checkpoint. Unpickle only trusted artifacts;
loading it requires the compatible Python packages and upstream source.
Downloaded datasets, models, retrieval caches, credentials and virtual environments
are excluded. Use the standalone release ZIP for a copy that includes pinned
upstream source. A normal GitHub source ZIP does not include submodule contents.
