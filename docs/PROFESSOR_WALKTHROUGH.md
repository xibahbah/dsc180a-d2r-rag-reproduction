# Three-minute professor walkthrough

## 0:00–0:30 — What I reproduced

“I reproduced the HotpotQA/LinUCB configuration from D2R-RAG. I used the released
code at a pinned revision, GPT-4o-mini, 500 training and 500 validation questions,
and two training epochs. I am not claiming every experiment in the paper.”

Open `docs/REPRODUCTION_SUMMARY.md`.

## 0:30–1:10 — How it works

“Evidence retrieval and answer generation are followed by knowledge-graph and
entailment checks. Those diagnostic signals feed a learned repair selector.
It can change retrieval, reranking or the prompt. We compare the final outputs
with the baseline and run the authors' relevance and faithfulness evaluation.”

Open the D2R-specific diagram in `docs/REPRODUCTION_PIPELINE.md`.

## 1:10–1:50 — Results and caveat

“The authors' EM-labeled score was 35.4% for our baseline and 39.8% after repair;
the paper reported 36.2% and 39.8%. Both full metric stages also completed.
The installed scorer uses normalized answer containment, so this is not strict
whole-answer exact match. Our manual examples show why that distinction matters.”

Open `docs/EXAMPLE_ANALYSIS.md`: show Animorphs, the misleading credited abstention,
and the NO_FAILURE missed answer. Do not say every score increase is a real fix.

## 1:50–2:30 — What was difficult

“We repaired incompatible dependencies and a training variable in the wrapper.
We also recovered from malformed API JSON and a request-count ceiling. The
original source and spending ledger were preserved. The complete training
checkpoint and all failed/successful logs are available.”

Open `reproduction/RECOVERY.md` and the full report if asked for evidence.

## 2:30–3:00 — Verify and conclude

Run `python3 scripts/verify_results.py`. It is offline and makes no paid calls.
It verifies stage completion, saved tables, metric means, budget bounds and the
pinned upstream snapshot. It verifies records, not semantic answer correctness
or independent reproducibility on another machine.

“This completes my scoped reproduction. It gives our group a working reference
for later controlled experiments; those extensions are separate from this task.”

## Questions to be ready for

- Why not identical baseline? Stochastic API generation, alias/dependency versions
  and environment differences can matter; we did not isolate each contribution.
- Did diagnosis cause the improvement? The experiment compares pipelines. It
  does not isolate diagnosis from retrieval changes or generation randomness.
- Did you reproduce efficiency? We retained source measurements but identified
  incomplete timing boundaries; we do not claim full end-to-end cost equivalence.
- Can teammates inspect it? Yes: source, guides, tables, logs and trained policy
  are committed. No key or GPU is needed for reading or offline verification.
