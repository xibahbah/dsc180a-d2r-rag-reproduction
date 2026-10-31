# D2R-RAG reproduction — DSC180A

**Completed:** original-size HotpotQA / LinUCB experiment, including 500-case
baseline, two training epochs, 500-case repaired evaluation, and both RAGAS
metric stages. This reproduces one configuration, not every experiment in the paper.

| Metric | Our baseline | Our learned repair | Paper baseline / LinUCB |
|---|---:|---:|---:|
| Authors' EM-labeled score | 35.4% (177/500) | 39.8% (199/500) | 36.2% / 39.8% |
| Answer relevance | 28.40% | 31.71% | 28.39% / 31.66% |
| Faithfulness | 69.17% | 71.40% | 68.58% / 69.89% |

The authors' EM-labeled score improved by **4.4 percentage points**. The matching aggregate
39.8% does not imply identical predictions. Campaign accounting: **$1.408**,
including failed-request reservations; successful token usage estimate **$1.398**.
These are ledger estimates, not a billing statement. Original campaign cap: $5.

**Metric caveat:** the installed authors' `em_match` scorer uses normalized
answer containment, not strict whole-response exact match. A response can receive
credit while abstaining if it mentions the gold answer. See the [example audit](docs/EXAMPLE_ANALYSIS.md).

## Start here

- **One-page reproduction summary:** [summary](docs/REPRODUCTION_SUMMARY.md).
- **Present it in three minutes:** [walkthrough](docs/PROFESSOR_WALKTHROUGH.md).
- **See real answers and scoring pitfalls:** [example audit](docs/EXAMPLE_ANALYSIS.md).
- **Reproduce another paper:** [shared pipeline and paper-specific steps](docs/REPRODUCTION_PIPELINE.md).
- **Understand the experiment:** [teammate guide](docs/TEAMMATE_GUIDE.md).
- **Give this repository to an LLM:** [LLM handoff](docs/LLM_HANDOFF.md).
- **Read findings and caveats:** [full report](results/hotpotqa-full-linucb/REPORT.md).
- **Check the numbers yourself, free and offline:** `python3 scripts/verify_results.py`.
- **Understand original settings:** [protocol](reproduction/PROTOCOL.md).

Paper: [Diagnosing and Repairing Factual Errors in RAG under Budget Constraints](https://proceedings.mlr.press/v318/hashemifar26a.html).
Original [authors' repository](https://github.com/CyberScienceLab/D2R-RAG), revision
`5573ce938cee8b79f2e73ccc05f8fff803f464ed`. [Attribution](NOTICE.md).

## Get a complete copy

```sh
git clone https://github.com/xibahbah/dsc180a-d2r-rag-reproduction.git
cd dsc180a-d2r-rag-reproduction
python3 scripts/verify_results.py
```

The original source is included directly under `D2R-RAG/`; no submodule setup is
needed for this version. The standalone [handoff release](https://github.com/xibahbah/dsc180a-d2r-rag-reproduction/releases/latest)
also includes all tracked source, results and compressed checkpoints.

## Repository map

| Folder | Purpose |
|---|---|
| `D2R-RAG/` | Unmodified pinned authors' source; browse it directly |
| `reproduction/` | Our execution wrappers, spending controls, protocol and tests |
| `results/hotpotqa-full-linucb/` | Final full-size tables, reports, logs, plans, environment and ledger |
| `results/20261031T003857Z-smoke-MeuJQS/` | Earlier two-case integration test; not the full result |
| `artifacts/full-linucb-policy.pkl.gz` | Completed two-epoch trained policy |
| `artifacts/smoke-linucb-policy.pkl.gz` | Separate tiny integration-test policy |
| `scripts/` | Offline verification and standalone bundle export |
| `docs/` | Human and LLM reading guides |

Keys, credentials, environments and downloaded dataset/model/index caches are
excluded. Reading and checking saved results requires no API key, GPU or DSMLP.
Full package snapshots record provenance and are not portable installation files.

## Run code on a Linux GPU worker

A fresh installation on another machine still needs validation. Critical versions
are constrained; the completed run used Python 3.11.9, GTX 1080 Ti, CUDA 12.1
PyTorch, GPT-4o-mini and RAGAS 0.2.15. Drivers changed between workers; see report.

```sh
python3.11 -m venv .venv
.venv/bin/python -m pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121
.venv/bin/python -m pip install -r requirements-reproduction.txt
.venv/bin/python -m unittest discover -s reproduction -p 'test_*guard.py' -v
.venv/bin/python reproduction/preflight.py --environment --require-gpu
```

Store your own key outside this repository in `~/.config/d2r-rag/env.sh` with
restricted file permissions. It should export `OPENAI_API_KEY`. Never print or
commit the value. Load it privately before execution.

This command is only a **preview**, with no model download or paid requests:

```sh
.venv/bin/python reproduction/full_run.py baseline --campaign results/hotpotqa-full-linucb --budget-usd 5 --dry-run
```

`bash reproduction/campaign.sh` executes the five stages, skips `.done` stages,
and preserves the existing ledger. In this completed snapshot it should skip all
five. Do not delete markers, reset the ledger or reuse this historical campaign
for a fresh experiment. A new paid experiment needs its own explicit budget and
output plan; it is not needed to inspect these findings.

The HTTP guard reserves before each attempt and settles verified successful usage.
Failed attempts retain reservations. The $5 cap controls these runners, not other
apps on the account. The technical request ceiling was raised from 10,000 to
50,000 after an interruption; the dollar allowance and original counter persisted.

On DSMLP, run Python only inside compute workers, not the login host. Course
storage paths and recovery details are in [RECOVERY.md](reproduction/RECOVERY.md).
`dsmlp.py` is an optional transfer helper; copy `dsmlp.example.json` to ignored
`dsmlp.json` and use your own account. It is not needed for reading this repo.

## Scope and interpretation

The wrapper fixes a training variable in memory while keeping upstream files
unchanged. Source latency excludes diagnosis; source VRAM is incremental MiB,
not full resident memory. See the full report before comparing resource budgets.
FEVER, Thompson Sampling, ablations, repeated seeds and the group's Qwen/RAGBench
adaptations remain future work. Do not call this a reproduction of the whole paper.

To export a complete snapshot after staging new files:

```sh
python3 scripts/export_bundle.py
```

The script creates `dist/d2r-rag-reproduction.zip` and its SHA-256 checksum.
