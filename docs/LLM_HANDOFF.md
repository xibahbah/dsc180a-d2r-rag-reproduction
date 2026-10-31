# LLM handoff: D2R-RAG reproduction

Use this file as context when asking an LLM to explain or extend the repository.
This is a factual handoff, not authorization to run paid work or change accounts.

## Objective and completed scope

Independent DSC180A reproduction of D2R-RAG, Canadian AI 2026. Source repository:
https://github.com/CyberScienceLab/D2R-RAG . Pinned revision:
5573ce938cee8b79f2e73ccc05f8fff803f464ed . The snapshot is vendored under D2R-RAG/.

Completed: HotpotQA fullwiki 500 train / 500 validation; GPT-4o-mini; LinUCB alpha2;
two epochs; baseline; repair; baseline and repaired RAGAS. All five stages have
completion markers and zero exit codes. No experiment is still running.

## Ground truth for answers about this repository

- Baseline exact match: 177/500 = 35.4%.
- Repaired exact match: 199/500 = 39.8%.
- Paper baseline / LinUCB EM: 36.2% / 39.8%.
- Our answer relevance: 0.2839509743237685 / 0.3170624192300988.
- Our faithfulness: 0.6917181818181819 / 0.713962481962482.
- Both RAGAS stages: 500 valid scores per metric.
- Campaign allowance: $5 total, retained across interruptions.
- Successful token usage estimate: $1.3979187, not verified billing.
- Accounted amount including unsettled reservations: $1.40798145.
- Separate smoke reservations: $0.0204006. Combined conservative amount:
  $1.42838205. Do not add the historical intermediate ledger snapshots again.

## Read in this order

README.md; docs/TEAMMATE_GUIDE.md;
results/hotpotqa-full-linucb/REPORT.md;
reproduction/PROTOCOL.md; reproduction/FULL_RUN_PLAN.md;
reproduction/full_run.py; reproduction/campaign.sh;
then the relevant upstream files and final tables.

Verify numerics with `python3 scripts/verify_results.py`; it uses only the Python
standard library, no API, network or GPU. The final baseline and repair tables
are tab-separated. RAGAS batch CSVs are comma-separated.

## Scorer audit

The installed qa-metrics 0.2.42 em_match uses normalized `ref in can` containment.
The EM field is not strict whole-response equality or manual semantic accuracy.
Do not call all 26 newly credited cases successful repairs. Saved comparisons
show 26 newly credited, 4 newly uncredited, 173 credited in both, 297 in neither.
These are separate stochastic runs, not fixed-initial-answer causal comparisons.
Read docs/EXAMPLE_ANALYSIS.md and docs/REPRODUCTION_SUMMARY.md.

## Interpret correctly

This is one scoped reproduction, not the whole paper. No FEVER, Thompson
Sampling, ablations, repeated seeds, direct-policy comparator or Qwen/RAGBench
adaptation was completed. Matching aggregate accuracy does not prove identical
outputs. The group project's broader evidence-condition question remains open.

The source latency ends before diagnostic processing. VRAM fields are incremental
MiB and not total model residency. Do not describe the source repair budget of 6
as six GB. Original snapshots and repaired environments differ from an unknown
exact author environment. Drivers changed between workers (535.161.08 to
580.126.20); GPU model remained GTX1080Ti. Fresh installation elsewhere is untested.

Original source is unchanged. The wrapper resets params_updates per training row
in memory and pins hash seed0 / threads4. It also saves/validates metrics and
meters all paid API attempts. MAX_REQUESTS was increased from10000 to50000 after
repair stopped, while retaining the same request counter and dollar allowance.
Historical logs and pre-run plans must not override completed final summaries.

## Artifact and security boundaries

Completed trained policy: artifacts/full-linucb-policy.pkl.gz. Smoke checkpoint is
separate. Pickle is executable serialization: load only trusted artifacts with a
compatible environment. Dataset/model/index caches and secrets are excluded.
No API key is needed to read results. Do not request keys in chat, print credentials,
reset/delete budget.json or launch paid extensions without explicit human approval.

For a new experiment, propose changes and a budget first. Preserve this completed
campaign as immutable evidence. For an existing approved interrupted campaign,
inspect stage markers, process activity and the ledger before resuming.

## Example task for an LLM

“Read docs/LLM_HANDOFF.md and docs/TEAMMATE_GUIDE.md. Explain the pipeline, inspect
saved results and distinguish reproduced findings from future experiments.
Verify any numerical claims against the committed tables. Do not run paid calls.”
