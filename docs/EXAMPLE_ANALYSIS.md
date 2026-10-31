# Real answer examples and scoring audit

Generated from committed tables by `python3 scripts/analyze_examples.py`; no API calls.

## What the saved scores show

| Saved baseline credit | Saved repaired credit | Cases |
|---|---|---:|
| credited | credited | 173 |
| credited | uncredited | 4 |
| uncredited | credited | 26 |
| uncredited | uncredited | 297 |

**Interpretation:** 26 newly credited minus 4 newly uncredited = 22 net,
or 4.4 percentage points. These are scorer transitions, not 26 verified fixes.
The repair script generates a new initial answer; it does not consume the saved
baseline answer. The final CSV stores the post-repair diagnosis, so it does not
necessarily explain why that action was originally selected. Action -1 means no repair.

## Important metric implementation finding

The installed `qa_metrics/em.py` from qa-metrics 0.2.42 was inspected on DSMLP.
It normalizes reference and candidate strings and credits a match when `ref in can`.
This is substring inclusion, not strict equality. The upstream scripts lowercase
answers and call this function. We preserved it for reproduction comparability.
A response can earn credit while declining to answer; see example 2.
No new scores or human labels have been substituted for the authors' metric.

## Example 1 — data row 3

**Question:** What science fantasy young adult series, told in first person, has a set of companion books narrating the stories of enslaved worlds and alien species?

**Gold:** Animorphs

**Baseline response:** The provided context is insufficient regarding a science fantasy young adult series that has a set of companion books narrating the stories of enslaved worlds and alien species.

**Final response in repaired evaluation:** The science fantasy young adult series that is told in first person and features a set of companion books narrating the stories of enslaved worlds and alien species is "Animorphs." This series, written by K. A. Applegate, explores themes such as horror, war, dehumanization, sanity, morality, innocence, leadership, freedom, and growing up. The narrative is shared among six main characters who take turns providing their perspectives throughout the series.

**Saved credit:** False → True.
**Saved diagnosis:** INSUFFICIENT_EVIDENCE_FAILURE → WRONG_PREDICATE_FAILURE.
**Selected action:** 8; update: `{'reranker': True}`.

**Observation:** The final answer identifies Animorphs, unlike the baseline abstention. This is a plausible substantive improvement; reranking was selected. It is not a controlled causal attribution to diagnosis.

## Example 2 — data row 24

**Question:** Which performance act has a higher instrument to person ratio, Badly Drawn Boy or Wolf Alice? 

**Gold:** Badly Drawn Boy

**Baseline response:** The provided context is insufficient regarding the performance act of Wolf Alice and their instrument to person ratio. Therefore, I cannot determine which act has a higher instrument to person ratio based on the information provided.

**Final response in repaired evaluation:** The provided context is insufficient regarding the performance act of Wolf Alice and its instrument to person ratio. The context only provides information about Badly Drawn Boy and does not mention Wolf Alice at all.

**Saved credit:** False → True.
**Saved diagnosis:** INSUFFICIENT_EVIDENCE_FAILURE → INSUFFICIENT_EVIDENCE_FAILURE.
**Selected action:** 10; update: `{'prompt_edit': 'simplify_qa'}`.

**Observation:** The final response still says the evidence is insufficient, but includes “Badly Drawn Boy.” The containment scorer credits it. Do not present this as an unambiguous successful correction.

## Example 3 — data row 281

**Question:** Flyboys stars which actor who was nominated for an Academy Award for "127 Hours"?

**Gold:** James Franco

**Baseline response:** The provided context is insufficient regarding the actor who stars in "Flyboys." However, it does mention that James Franco was nominated for an Academy Award for his role in "127 Hours."

**Final response in repaired evaluation:** The provided context is insufficient regarding the actor who starred in "Flyboys" and was nominated for an Academy Award for "127 Hours".

**Saved credit:** True → False.
**Saved diagnosis:** NO_FAILURE → NO_FAILURE.
**Selected action:** 5; update: `{'retriever': 'bm25', 'topk': 10, 'reindex': True}`.

**Observation:** The baseline mentions James Franco while also expressing insufficient evidence. Its credit is lost in the final abstention. Both answers deserve semantic review rather than treating the initial credit as definitive correctness.

## Example 4 — data row 1

**Question:** Were Scott Derrickson and Ed Wood of the same nationality?

**Gold:** yes

**Baseline response:** The provided context is insufficient regarding Scott Derrickson's nationality. It only provides information about Ed Wood, who was an American filmmaker. Therefore, I cannot determine if Scott Derrickson and Ed Wood were of the same nationality based on the provided context.

**Final response in repaired evaluation:** The provided context is insufficient regarding Scott Derrickson's nationality. However, it does mention that Ed Wood is an American filmmaker. Therefore, without information about Scott Derrickson's nationality, I cannot determine if they were of the same nationality.

**Saved credit:** False → False.
**Saved diagnosis:** NO_FAILURE → NO_FAILURE.
**Selected action:** -1; update: `{'retriever': 'dense', 'topk': 5, 'reranker': False, 'prompt_edit': 'simple_qa', 'reindex': False}`.

**Observation:** Both outputs abstain instead of answering yes, yet both are labeled NO_FAILURE and action -1 is recorded. This illustrates a diagnostic blind spot, not an estimated diagnosis-error rate.

## Example 5 — data row 2

**Question:** What government position was held by the woman who portrayed Corliss Archer in the film Kiss and Tell?

**Gold:** Chief of Protocol

**Baseline response:** The provided context is insufficient regarding the government position held by the woman who portrayed Corliss Archer in the film Kiss and Tell.

**Final response in repaired evaluation:** The provided context is insufficient regarding the government position held by the woman who portrayed Corliss Archer in the film Kiss and Tell.

**Saved credit:** False → False.
**Saved diagnosis:** NO_FAILURE → NO_FAILURE.
**Selected action:** -1; update: `{'retriever': 'dense', 'topk': 5, 'reranker': False, 'prompt_edit': 'simple_qa', 'reindex': False}`.

**Observation:** Both outputs abstain and the final action is -1. The NO_FAILURE diagnosis does not establish gold-answer correctness.

## Limits

These five examples are purposively selected illustrations, not a random audit.
Data-row numbers are 1-based excluding the header. Baseline and repair rows were
joined and checked by exact question text. A clean repair-caused overcorrection
rate would require the same stored initial responses and an explicit changed-answer
definition. Gold strings alone do not establish passage support. No manual judgment
here was used to rewrite the original results.
