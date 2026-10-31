## Completed HotpotQA / LinUCB campaign

Full 500-case evaluation: baseline EM **35.4%**, learned repair EM **39.8%**
(paper: 36.2% / 39.8%). Two training epochs and both 500-case RAGAS evaluations
completed. Campaign accounted amount **$1.408**, including failed-request
reservations, under the original $5 cap. This is a scoped reproduction, not all
paper experiments. See [full report](results/hotpotqa-full-linucb/REPORT.md).

# DSC 180A — D2R-RAG reproduction

Independent reproduction work for [Diagnosing and Repairing Factual Errors in RAG under Budget Constraints](https://proceedings.mlr.press/v318/hashemifar26a.html), Canadian AI 2026. See [attribution](NOTICE.md).

## Current status

- The two-question HotpotQA integration test completed: baseline, two training epochs, saved LinUCB policy, and policy evaluation.
- Baseline and policy evaluation each scored 1/2 with the authors' matcher. Both validation answers were diagnosed NO_FAILURE, so no repair was triggered on these two cases.
- The smoke ledger reserved at most $0.020401 across 31 attempted API requests, including interrupted attempts. This is an upper bound, not an actual billing report.
- The original-size HotpotQA/LinUCB campaign is running on DSMLP under a separately approved **$5 total cap**, shared across baseline, training, repair and RAGAS evaluation. It has not yet produced full-paper results.
- The whole paper also includes Thompson Sampling, FEVER, comparison methods and ablations. Those are not completed by the initial HotpotQA/LinUCB campaign.

[Small-run report](results/20261031T003857Z-smoke-MeuJQS/REPORT.md) · [Protocol and reference values](reproduction/PROTOCOL.md) · [Full-run plan](reproduction/FULL_RUN_PLAN.md)

## Files for teammates

| Path | Contents |
|---|---|
| `D2R-RAG/` | Authors' original source, pinned as a Git submodule |
| `reproduction/` | Budget guards, tested runners, protocol, configuration and tests |
| `results/` | Captured tables, logs, package versions, GPU details and reports |
| `artifacts/` | Compressed policy checkpoint from the small integration test |
| `scripts/export_bundle.py` | Produce a standalone ZIP including upstream source |
| `dsmlp.py` | Optional laptop upload/status/download helper |

API keys, SSH credentials, environments, downloaded datasets/models and retrieval-index caches are excluded. The original-size run's outputs will be added after they are collected. The full environment snapshot is provenance, not a portable pip installation file: it includes container-specific paths and unrelated preinstalled packages.

## Get all source files

```sh
git clone --recurse-submodules https://github.com/xibahbah/dsc180a-d2r-rag-reproduction.git
cd dsc180a-d2r-rag-reproduction
```

For an existing clone, run `git submodule update --init --recursive`. GitHub's ordinary source ZIP does not include submodule contents; use the standalone bundle when distributing a complete snapshot.

## Set up inside a Linux GPU compute container

The successful run used Python 3.11.9, an NVIDIA GTX 1080 Ti (11,264 MiB), driver 535.161.08 and CUDA 12.1 PyTorch wheels. Critical dependency versions are recorded in `reproduction/constraints.txt`. Those versions and a real small pipeline were tested on DSMLP; a fresh installation on other machines remains to be validated.

```sh
python3.11 -m venv .venv
.venv/bin/python -m pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121
.venv/bin/python -m pip install -r requirements-reproduction.txt
.venv/bin/python -m unittest discover -s reproduction -p 'test_*guard.py' -v
```

Keep an OpenAI API key outside the repository in `~/.config/d2r-rag/env.sh`, readable only by your account. It should export `OPENAI_API_KEY`. Load it privately with `source ~/.config/d2r-rag/env.sh`. Never commit a key or print its value.

```sh
.venv/bin/python reproduction/preflight.py --environment --require-gpu
```

Install and run Python only inside a DSMLP compute container. The login server is for connection and job submission. [UCSD instructions](https://support.ucsd.edu/services?id=kb_article_view&sysparm_article=KB0032269).

## Safe previews and runs

The full preview performs no model download or paid requests:

```sh
.venv/bin/python reproduction/full_run.py baseline --campaign results/hotpotqa-full-linucb --budget-usd 5 --dry-run
```

The approved DSMLP campaign uses `bash reproduction/campaign.sh`. It runs five stages sequentially, writes stage logs and `status.json`, and stops on an error or exhausted allowance. A file lock prevents launching two copies of that campaign. Existing completed stages are skipped. Do not launch it on a second machine or delete its spending ledger to reset an allowance.

The full guard reserves a conservative maximum before every HTTPX API attempt, then settles verified successful usage at the recorded GPT-4o-mini rates. Failed/unaccounted requests retain their maximum reservations. Budgets persist across stages and restarts; changing an existing allowance is rejected. This controls these runners, not other apps using the same OpenAI account. The cap can stop a campaign before completion.

The separate smoke runner uses two questions per split, a 512-token output cap, a 40-attempt ceiling and a persistent $1 ledger. See its source for stage options. Neither the small data nor its results should be reported as reproducing the paper's percentages.

The in-memory training wrapper initializes a variable that can otherwise be referenced before assignment. Original upstream source files remain unchanged. Timing and VRAM fields follow the original code; diagnostics are outside its timing snapshot, and the 6 MiB repair budget measures incremental allocation rather than all resident model memory.

## Transfer and share results

For the laptop helper, copy `dsmlp.example.json` to `dsmlp.json` and fill in your own UCSD username. Configure normal SSH access first. Your local configuration is ignored by Git.

On DSMLP, inspect `results/hotpotqa-full-linucb/status.json` and the campaign logs. Download reports/tables/checkpoints after a run, preserving the budget ledger even after errors. Large downloaded model/data/index caches are reproducible inputs and are not repository artifacts. Do not restart Jupyter while a stage is executing; a restart can terminate its process.

To produce a standalone snapshot from a Git checkout:

```sh
python3 scripts/export_bundle.py
```

This writes `dist/d2r-rag-reproduction.zip` and its SHA-256 checksum. It includes tracked results, compressed policy artifacts and the pinned upstream source, with no Git metadata or local environments.
