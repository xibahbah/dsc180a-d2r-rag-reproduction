# Paper reproduction record

Copy this template for a paper. Keep unknown fields as UNKNOWN rather than guessing.

## 1. Exact target

- Paper title / canonical link:
- Responsible teammate:
- Selected table, figure or claim:
- Method / baseline / dataset / backbone:
- Status: PREPARATION | SMOKE ONLY | SCOPED REPRODUCTION COMPLETE | PARTIAL | ADAPTATION
- Are we reproducing inference, training, or both?
- Explicitly excluded experiments:

## 2. Inputs and environment

- Repository and commit:
- Dataset revision, split, filtering, size and example IDs:
- Corpus/index version:
- Model identifiers, revision and checkpoint source:
- Prompts, decoding parameters and seeds:
- Required annotation labels and their provenance:
- Evaluator implementation/version and matching/normalization rules:
- Python/framework/CUDA versions:
- GPU model/count/VRAM and driver:
- CPU/RAM/storage and estimated duration:
- Required API services and separately agreed monetary limit:
- Missing assets or access requirements:

## 3. Execution record

- Environment setup command:
- Tiny integration-test command and result:
- Original-size run command:
- Training schedule or released checkpoint used:
- Launch time, completion time and exit status:
- Resume method and preserved checkpoints/ledger:
- Changes to author setup and why:
- Which changes are compatibility fixes vs experimental adaptations?

## 4. Results

| Metric and population | Paper | Reproduced | Difference | Evidence file |
|---|---:|---:|---:|---|
| Fill in exact metric and unit | | | | |

- Recomputed from saved predictions?
- Missing/NaN outputs or failed cases?
- Same evaluated examples as comparison methods?
- Paid usage estimate vs actual billing vs reservations:
- Representative improvement, failure and metric edge case:
- Are findings causal, descriptive, or only integration checks?

## 5. Handoff and conclusion

- Source/provenance/attribution:
- Dependency file and full environment snapshot:
- Commands/configuration:
- Predictions, logs, metrics, checkpoints and checksums:
- Offline result verifier:
- Short conclusion: what was reproduced and what was not?
- Remaining uncertainty or missing experiment:
- Secrets/caches excluded and artifact license checked:
